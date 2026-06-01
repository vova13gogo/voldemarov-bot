import json
import asyncpg
import database
from config import DEFAULT_REPLY_CHANCE

_settings = {
    "reply_chance": DEFAULT_REPLY_CHANCE,
    "enabled": True,
    "learn_enabled": True,
}

async def load():
    pool = await database.get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT key, value FROM bot_settings")
        for row in rows:
            try:
                _settings[row["key"]] = json.loads(row["value"])
            except Exception:
                _settings[row["key"]] = row["value"]

async def _save_key(key: str, value):
    pool = await database.get_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO bot_settings (key, value)
            VALUES ($1, $2)
            ON CONFLICT (key) DO UPDATE SET value = $2
        """, key, json.dumps(value))

def get_chance() -> int:
    return _settings.get("reply_chance", DEFAULT_REPLY_CHANCE)

async def set_chance(value: int):
    _settings["reply_chance"] = value
    await _save_key("reply_chance", value)

def is_enabled() -> bool:
    return _settings.get("enabled", True)

async def set_enabled(value: bool):
    _settings["enabled"] = value
    await _save_key("enabled", value)

def is_learning() -> bool:
    return _settings.get("learn_enabled", True)

async def set_learning(value: bool):
    _settings["learn_enabled"] = value
    await _save_key("learn_enabled", value)
