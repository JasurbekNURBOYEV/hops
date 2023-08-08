"""Used to filter new chat members."""
import re


def is_chinese_name(name: str) -> bool:
    """Check if there are at least 3 chinese letters in a row"""
    return bool(re.search("[\u4e00-\u9fff]{3,}", name))
