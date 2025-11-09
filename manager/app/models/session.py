# rootdir: manager/app/models/session.py
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Session:
    """مدل نشست"""
    id: int
    user_id: int
    session_string: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
