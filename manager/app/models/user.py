# rootdir: manager/app/models/user.py
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class User:
    """مدل کاربر"""
    id: int
    user_id: int
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    phone: Optional[str]
    is_bot: bool
    is_premium: bool
    created_at: datetime
    updated_at: datetime
