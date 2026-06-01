import random
import json
import asyncpg
from config import MIN_WORDS, GENERATE_LENGTH
import database

# Локальный кэш цепей для быстрой генерации
_cache: dict[str, list] = {}
_total_trained: int = 0
_dirty_keys: set = set()  # ключи которые нужно сохранить в БД

async def load():
    global _total_trained
    pool = await database.get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT key, values FROM markov_chain")
        for row in rows:
            _cache[row["key"]] = json.loads(row["values"])
        stat = await conn.fetchrow("SELECT total_trained FROM bot_stats WHERE id = 1")
        if stat:
            _total_trained = stat["total_trained"]

    # Загружаем начальную базу если цепи пустые
    if len(_cache) < 10:
        from seed_data import get_seed_phrases
        for phrase in get_seed_phrases():
            train(phrase)
        await flush()
        print(f"📚 Начальная база загружена: {len(_cache)} пар слов")

async def flush():
    """Сохраняет накопленные изменения в БД."""
    if not _dirty_keys:
        return
    pool = await database.get_pool()
    async with pool.acquire() as conn:
        for key in list(_dirty_keys):
            values = _cache.get(key, [])
            await conn.execute("""
                INSERT INTO markov_chain (key, values)
                VALUES ($1, $2::jsonb)
                ON CONFLICT (key) DO UPDATE SET values = $2::jsonb
            """, key, json.dumps(values))
        await conn.execute(
            "UPDATE bot_stats SET total_trained = $1 WHERE id = 1",
            _total_trained
        )
    _dirty_keys.clear()

def train(text: str) -> bool:
    global _total_trained
    words = text.lower().split()
    if len(words) < MIN_WORDS:
        return False
    for i in range(len(words) - 2):
        key = f"{words[i]} {words[i+1]}"
        if key not in _cache:
            _cache[key] = []
        _cache[key].append(words[i + 2])
        _dirty_keys.add(key)
    _total_trained += 1
    return True

def _extract_keywords(text: str) -> list[str]:
    """Извлекает значимые слова из текста (длиннее 3 букв)."""
    words = text.lower().split()
    return [w for w in words if len(w) > 3]

def generate(seed: str = None) -> str | None:
    if len(_cache) < 5:
        return None

    start_key = None

    if seed:
        keywords = _extract_keywords(seed)
        # Ищем ключ который содержит одно из ключевых слов
        random.shuffle(keywords)
        for word in keywords:
            matching = [k for k in _cache if word in k]
            if matching:
                start_key = random.choice(matching)
                break

    if not start_key:
        start_key = random.choice(list(_cache.keys()))

    words = start_key.split()
    result = words[:]
    for _ in range(GENERATE_LENGTH):
        key = f"{result[-2]} {result[-1]}"
        next_words = _cache.get(key)
        if not next_words:
            break
        result.append(random.choice(next_words))
    if len(result) < 3:
        return None
    result[0] = result[0].capitalize()
    text = " ".join(result)
    if text[-1] not in ".!?":
        text += "."
    return text

def word_count() -> int:
    return len(_cache)

def messages_trained() -> int:
    return _total_trained

async def reset():
    global _total_trained
    _cache.clear()
    _dirty_keys.clear()
    _total_trained = 0
    pool = await database.get_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM markov_chain")
        await conn.execute("UPDATE bot_stats SET total_trained = 0 WHERE id = 1")
