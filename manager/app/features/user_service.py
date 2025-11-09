# rootdir: manager/app/features/user_service.py
# ======================================================
from app.database.connection import Database
from app.models.user import User
from app.config import MESSAGES, ERRORS
from app.utils.logger import get_logger

logger = get_logger("user_service")


class UserService:
    """سرویس مدیریت کاربران"""
    
    def __init__(self, db: Database):
        self.db = db
    
    async def create_user(self, user_data: dict) -> User:
        """ساخت کاربر"""
        await self.db.execute(
            "insert_user",
            user_data["user_id"],
            user_data.get("username"),
            user_data.get("first_name"),
            user_data.get("last_name"),
            user_data.get("phone"),
            user_data.get("is_bot", False),
            user_data.get("is_premium", False)
        )
        logger.info(MESSAGES["user_created"])
        return await self.get_user(user_data["user_id"])
    
    async def get_user(self, user_id: int):
        """دریافت کاربر"""
        row = await self.db.fetchrow("select_user", user_id)
        if not row:
            logger.error(ERRORS["user_not_found"])
            return None
        return User(**dict(row))
    
    async def update_user(self, user_id: int, data: dict):
        """به‌روزرسانی کاربر"""
        await self.db.execute(
            "update_user",
            data.get("username"),
            data.get("first_name"),
            user_id
        )
        logger.info(MESSAGES["user_updated"])
