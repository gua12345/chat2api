# api/files.py - 文件处理工具模块

import io
import pybase64
from PIL import Image
from utils.Client import Client
from utils.configs import export_proxy_url, cf_file_url

async def get_file_content(url):
    """
    获取文件内容和MIME类型
    
    Args:
        url (str): 文件URL或base64编码的数据URL
        
    Returns:
        tuple: (file_content, mime_type) 文件内容和MIME类型
        如果获取失败返回 (None, None)
    """
    # 处理base64编码的数据URL
    if url.startswith("data:"):
        mime_type, base64_data = url.split(';')[0].split(':')[1], url.split(',')[1]
        file_content = pybase64.b64decode(base64_data)
        return file_content, mime_type
    
    # 处理普通URL
    client = Client()
    try:
        # 使用云函数下载（如果配置了cf_file_url）
        if cf_file_url:
            body = {"file_url": url}
            r = await client.post(cf_file_url, timeout=60, json=body)
        else:
            # 直接下载（可能使用代理）
            r = await client.get(url, proxy=export_proxy_url, timeout=60)
            
        if r.status_code != 200:
            return None, None
            
        file_content = r.content
        mime_type = r.headers.get('Content-Type', '').split(';')[0].strip()
        return file_content, mime_type
    finally:
        # 确保资源释放
        await client.close()
        del client

async def determine_file_use_case(mime_type):
    """
    根据MIME类型确定文件用途
    
    Args:
        mime_type (str): 文件的MIME类型
        
    Returns:
        str: 'multimodal'(图片), 'my_files'(文档), 或 'ace_upload'(其他)
    """
    # 支持的图片类型
    multimodal_types = [
        "image/jpeg", 
        "image/webp", 
        "image/png", 
        "image/gif"
    ]
    
    # 支持的文档类型
    my_files_types = [
        "text/x-php",
        "application/msword",
        "text/x-c",
        "text/html",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/json",
        "text/javascript",
        "application/pdf",
        "text/x-java",
        "text/x-tex",
        "text/x-typescript",
        "text/x-sh",
        "text/x-csharp",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "text/x-c++",
        "application/x-latext",
        "text/markdown",
        "text/plain",
        "text/x-ruby",
        "text/x-script.python"
    ]

    if mime_type in multimodal_types:
        return "multimodal"
    elif mime_type in my_files_types:
        return "my_files"
    else:
        return "ace_upload"

async def get_image_size(file_content):
    """
    获取图片尺寸
    
    Args:
        file_content (bytes): 图片文件的二进制内容
        
    Returns:
        tuple: (width, height) 图片的宽度和高度
    """
    with Image.open(io.BytesIO(file_content)) as img:
        return img.width, img.height

async def get_file_extension(mime_type):
    """
    根据MIME类型获取文件扩展名
    
    Args:
        mime_type (str): 文件的MIME类型
        
    Returns:
        str: 对应的文件扩展名（包含点号），如果未找到返回空字符串
    """
    extension_mapping = {
        # 图片文件
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/gif": ".gif",
        "image/webp": ".webp",
        
        # 文本和编程文件
        "text/x-php": ".php",
        "text/x-c": ".c",
        "text/html": ".html",
        "text/javascript": ".js",
        "text/x-java": ".java",
        "text/x-typescript": ".ts",
        "text/x-sh": ".sh",
        "text/x-csharp": ".cs",
        "text/x-c++": ".cpp",
        "text/markdown": ".md",
        "text/plain": ".txt",
        "text/x-ruby": ".rb",
        "text/x-script.python": ".py",
        
        # 办公文档
        "application/msword": ".doc",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
        "application/json": ".json",
        "application/pdf": ".pdf",
        "text/x-tex": ".tex",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation": ".pptx",
        "application/x-latex": ".latex",
        
        # 压缩文件
        "application/zip": ".zip",
        "application/x-zip-compressed": ".zip",
        "application/x-tar": ".tar",
        "application/x-compressed-tar": ".tar.gz",
        "application/vnd.rar": ".rar",
        "application/x-rar-compressed": ".rar",
        "application/x-7z-compressed": ".7z",
        "application/octet-stream": ".bin",
        
        # 音频文件
        "audio/mpeg": ".mp3",
        "audio/wav": ".wav",
        "audio/ogg": ".ogg",
        "audio/aac": ".aac",
        
        # 视频文件
        "video/mp4": ".mp4",
        "video/x-msvideo": ".avi",
        "video/x-matroska": ".mkv",
        "video/webm": ".webm",
        
        # 其他常用格式
        "application/rtf": ".rtf",
        "application/vnd.ms-excel": ".xls",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ".xlsx",
        "text/css": ".css",
        "text/xml": ".xml",
        "application/xml": ".xml",
        "application/vnd.android.package-archive": ".apk",
        "application/vnd.apple.installer+xml": ".mpkg",
        "application/x-bzip": ".bz",
        "application/x-bzip2": ".bz2",
        "application/x-csh": ".csh",
        "application/x-debian-package": ".deb",
        "application/x-dvi": ".dvi",
        "application/java-archive": ".jar",
        "application/x-java-jnlp-file": ".jnlp",
        "application/vnd.mozilla.xul+xml": ".xul",
        "application/vnd.ms-fontobject": ".eot",
        "application/ogg": ".ogx",
        "application/x-font-ttf": ".ttf",
        "application/font-woff": ".woff",
        "application/x-shockwave-flash": ".swf",
        "application/vnd.visio": ".vsd",
        "application/xhtml+xml": ".xhtml",
        "application/vnd.ms-powerpoint": ".ppt",
        "application/vnd.oasis.opendocument.text": ".odt",
        "application/vnd.oasis.opendocument.spreadsheet": ".ods",
        "application/x-xpinstall": ".xpi",
        "application/vnd.google-earth.kml+xml": ".kml",
        "application/vnd.google-earth.kmz": ".kmz",
        "application/x-font-otf": ".otf",
        
        # Microsoft Office 相关格式
        "application/vnd.ms-excel.addin.macroEnabled.12": ".xlam",
        "application/vnd.ms-excel.sheet.binary.macroEnabled.12": ".xlsb",
        "application/vnd.ms-excel.template.macroEnabled.12": ".xltm",
        "application/vnd.ms-powerpoint.addin.macroEnabled.12": ".ppam",
        "application/vnd.ms-powerpoint.presentation.macroEnabled.12": ".pptm",
        "application/vnd.ms-powerpoint.slideshow.macroEnabled.12": ".ppsm",
        "application/vnd.ms-powerpoint.template.macroEnabled.12": ".potm",
        "application/vnd.ms-word.document.macroEnabled.12": ".docm",
        "application/vnd.ms-word.template.macroEnabled.12": ".dotm",
        
        # Microsoft 应用程序相关格式
        "application/x-ms-application": ".application",
        "application/x-ms-wmd": ".wmd",
        "application/x-ms-wmz": ".wmz",
        "application/x-ms-xbap": ".xbap",
        "application/vnd.ms-xpsdocument": ".xps",
        "application/x-silverlight-app": ".xap"
    }
    
    return extension_mapping.get(mime_type, "")
