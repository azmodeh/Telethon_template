from app.database.connection import Database
from app.models.session import Session
from app.config import MESSAGES, ERRORS
from app.utils.logger import get_logger

logger = get_logger("session_manager")


class SessionManager:
    """مدیریت نشست‌ها"""
    
    def __init__(self, db: Database):
        self.db = db
    
    async def create_session(
        self,
        user_id: int,
        session_string: str
    ) -> int:
        """ساخت نشست جدید"""
        await self.db.execute("deactivate_session", user_id)
        
        row = await self.db.fetchrow(
            "insert_session",
            user_id,
            session_string
        )
        
        session_id = row["id"]
        logger.info(MESSAGES["session_created"])
        return session_id
    
    async def get_active_session(self, user_id: int):
        """دریافت نشست فعال"""
        row = await self.db.fetchrow("select_session", user_id)
        
        if not row:
            logger.warning(ERRORS["session_not_found"])
            return None
        
        return Session(**dict(row))
    
    async def deactivate(self, user_id: int):
        """غیرفعال کردن نشست"""
        await self.db.execute("deactivate_session", user_id)
        logger.info(MESSAGES["session_expired"])