import os
import asyncpg
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class SupabaseClient:
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL")
        self.pool: Optional[asyncpg.Pool] = None
    
    async def connect(self):
        """Create connection pool to Supabase"""
        try:
            self.pool = await asyncpg.create_pool(
                self.database_url,
                min_size=1,
                max_size=10,
                command_timeout=60
            )
            logger.info("Connected to Supabase database")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    async def close(self):
        """Close connection pool"""
        if self.pool:
            await self.pool.close()
    
    async def execute_query(self, query: str, *args):
        """Execute a query with parameters"""
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args)
    
    async def execute_command(self, command: str, *args):
        """Execute a command (INSERT, UPDATE, DELETE)"""
        async with self.pool.acquire() as conn:
            return await conn.execute(command, *args)

# Global database client
db_client = SupabaseClient()
