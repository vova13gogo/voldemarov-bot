import asyncpg
import json
from config import DATABASE_URL

_pool = None

async def init():
    global _pool
    _pool = await asyncpg.create_pool(DATABASE_URL)
    async with _pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS markov_chain (
                key TEXT PRIMARY KEY,
                values JSONB NOT NULL
            )
        """)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS bot_settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS bot_stats (
                id INT PRIMARY KEY DEFAULT 1,
                total_trained INT DEFAULT 0
            )
        """)
        # Инициализируем счётчик если нет
        await conn.execute("""
            INSERT INTO bot_stats (id, total_trained)
            VALUES (1, 0)
            ON CONFLICT DO NOTHING
        """)

async def get_pool():
    return _pool

async def close():
    if _pool:
        await _pool.close()
