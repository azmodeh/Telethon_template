from app.database.connection import Database
from app.config import MESSAGES
from app.utils.logger import get_logger

logger = get_logger("stats_service")


class StatsService:
    """سرویس آمار"""
    
    def __init__(self, db: Database):
        self.db = db
    
    async def get_stats(self) -> dict:
        """دریافت آمار کلی"""
        total_users = await self.db.fetchrow("count_users")
        active_sessions = await self.db.fetchrow(
            "count_active_sessions"
        )
        
        stats = {
            "total_users": total_users["count"],
            "active_sessions": active_sessions["count"]
        }
        
        logger.info(f"Stats: {stats}")
        return stats
