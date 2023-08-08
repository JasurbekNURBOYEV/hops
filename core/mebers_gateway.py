"""Used to filter new chat members."""
import re
from telebot.types import User


def make_full_user_name(user: User) -> str:
    name = user.first_name
    if user.last_name:
        name = f"{name} {user.last_name}"
    return name


def is_chinese_name(user: User) -> bool:
    """Check if there are at least 3 chinese letters in a row"""
    return bool(re.search("[\u4e00-\u9fff]{3,}", make_full_user_name(user)))
