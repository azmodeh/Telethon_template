import re
from app.config import PATTERNS, ERRORS
from app.utils.logger import get_logger

logger = get_logger("validators")


def validate_phone(phone: str) -> bool:
    """اعتبارسنجی شماره تلفن"""
    pattern = PATTERNS["phone_intl"]
    if not re.match(pattern, phone):
        logger.error(ERRORS["invalid_phone"])
        raise ValueError(ERRORS["invalid_phone"])
    return True


def validate_username(username: str) -> bool:
    """اعتبارسنجی نام کاربری"""
    pattern = PATTERNS["username"]
    if not re.match(pattern, username):
        logger.error(f"Invalid username: {username}")
        raise ValueError("Invalid username format")
    return True


def validate_chat_id(chat_id: str) -> bool:
    """اعتبارسنجی شناسه چت"""
    pattern = PATTERNS["chat_id"]
    if not re.match(pattern, str(chat_id)):
        logger.error(ERRORS["invalid_chat_id"])
        raise ValueError(ERRORS["invalid_chat_id"])
    return True


def validate_message_length(text: str, max_len: int) -> bool:
    """بررسی طول پیام"""
    if len(text) > max_len:
        logger.error(ERRORS["message_too_long"])
        raise ValueError(ERRORS["message_too_long"])
    return True

