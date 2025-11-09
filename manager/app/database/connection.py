# rootdir manager/app/database/connection.py
# ======================================================

import asyncpg
from typing import Optional
from app.config import ENV, QUERIES, MESSAGES, ERRORS
from app.utils.logger import get_logger

logger = get_logger("database")


class Database:
    """مدیریت اتصال PostgreSQL"""
    
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
    
    async def connect(self):
        """اتصال به دیتابیس"""
        try:
            self.pool = await asyncpg.create_pool(
                host=ENV["db_host"],
                port=ENV["db_port"],
                user=ENV["db_user"],
                password=ENV["db_password"],
                database=ENV["db_name"],
                min_size=ENV["db_pool_min"],
                max_size=ENV["db_pool_max"]
            )
            logger.info(MESSAGES["db_connected"])
        except Exception as e:
            logger.error(ERRORS["db_connection_failed"])
            raise
    
    async def execute(self, query_key: str, *args):
        """اجرای کوئری"""
        query = QUERIES[query_key]
        async with self.pool.acquire() as conn:
            return await conn.execute(query, *args)
    
    async def fetch(self, query_key: str, *args):
        """دریافت رکوردها"""
        query = QUERIES[query_key]
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args)
    
    async def fetchrow(self, query_key: str, *args):
        """دریافت یک رکورد"""
        query = QUERIES[query_key]
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, *args)
    
    async def close(self):
        """بستن اتصال"""
        if self.pool:
            await self.pool.close()
            logger.info(MESSAGES["db_closed"])
