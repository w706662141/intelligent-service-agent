import hashlib


def md5(text: str) -> str:
    """计算字符串 MD5"""
    return hashlib.md5(text.encode('utf-8')).hexdigest()


def file_md5(path: str) -> str:
    """计算文件 MD5"""
    with open(path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()
