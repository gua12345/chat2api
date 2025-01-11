# api/tokens.py - Token计算和处理模块

import math
import tiktoken

async def calculate_image_tokens(width, height, detail):
    """
    计算图片所需的token数量
    
    Args:
        width (int): 图片宽度
        height (int): 图片高度
        detail (str): 细节级别 ('low' 或其他)
    
    Returns:
        int: 所需的token数量
    """
    # 低细节模式固定返回85个token
    if detail == "low":
        return 85
    
    # 处理大尺寸图片，将最大边限制在2048像素
    max_dimension = max(width, height)
    if max_dimension > 2048:
        scale_factor = 2048 / max_dimension
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)
    else:
        new_width = width
        new_height = height
    width, height = new_width, new_height

    # 处理小尺寸，将最小边限制在768像素
    min_dimension = min(width, height)
    if min_dimension > 768:
        scale_factor = 768 / min_dimension
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)
    else:
        new_width = width
        new_height = height
    width, height = new_width, new_height

    # 计算需要的掩码数量
    num_masks_w = math.ceil(width / 512)
    num_masks_h = math.ceil(height / 512)
    total_masks = num_masks_w * num_masks_h
    
    # 计算总token数（每个掩码170 tokens，基础85 tokens）
    tokens_per_mask = 170
    total_tokens = total_masks * tokens_per_mask + 85
    
    return total_tokens

async def num_tokens_from_messages(messages, model=''):
    """
    计算消息列表中的token数量
    
    Args:
        messages (list): 消息列表
        model (str): 模型名称
    
    Returns:
        int: 总token数量
    """
    # 获取适当的编码器
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")

    # 根据模型确定每条消息的基础token数
    if model == "gpt-3.5-turbo-0301":
        tokens_per_message = 4
    else:
        tokens_per_message = 3

    num_tokens = 0
    # 遍历消息列表计算token
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            if isinstance(value, list):
                # 处理列表类型的值（如多模态内容）
                for item in value:
                    if item.get("type") == "text":
                        num_tokens += len(encoding.encode(item.get("text")))
                    if item.get("type") == "image_url":
                        pass  # 图片URL的token在其他地方计算
            else:
                # 处理普通文本内容
                num_tokens += len(encoding.encode(value))
        num_tokens += 3  # 每条消息的结束标记
    
    return num_tokens

async def num_tokens_from_content(content, model=None):
    """
    计算单个文本内容的token数量
    
    Args:
        content (str): 文本内容
        model (str, optional): 模型名称
    
    Returns:
        int: token数量
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
        
    encoded_content = encoding.encode(content)
    len_encoded_content = len(encoded_content)
    return len_encoded_content

async def split_tokens_from_content(content, max_tokens, model=None):
    """
    将内容按最大token数量分割
    
    Args:
        content (str): 要分割的文本内容
        max_tokens (int): 最大token数量
        model (str, optional): 模型名称
    
    Returns:
        tuple: (处理后的内容, token数量, 终止原因)
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
        
    encoded_content = encoding.encode(content)
    len_encoded_content = len(encoded_content)
    
    # 如果内容超过最大token限制，截取到最大限制
    if len_encoded_content >= max_tokens:
        content = encoding.decode(encoded_content[:max_tokens])
        return content, max_tokens, "length"
    else:
        return content, len_encoded_content, "stop"
