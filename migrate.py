"""
Скрипт для переноса локальной базы chain.json в PostgreSQL.
Запускать один раз перед деплоем на Railway.

Использование:
  set DATABASE_URL=postgresql://user:pass@host:5432/dbname
  python migrate.py
"""

import asyncio
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

import asyncpg

LOCAL_CHAIN = os.path.join(os.path.dirname(__file__), "data", "chain.json")
DATABASE_URL = os.getenv("DATABASE_URL", "")

async def migrate():
    if not DATABASE_URL:
        print("❌ Переменная DATABASE_URL не задана.")
        print("Задай её: set DATABASE_URL=postgresql://...")
        return

    if not os.path.exists(LOCAL_CHAIN):
        print(f"❌ Файл {LOCAL_CHAIN} не найден.")
        return

    with open(LOCAL_CHAIN, "r", encoding="utf-8") as f:
        data = json.load(f)

    chain = data.get("chain", {})
    total_trained = data.get("total_trained", 0)

    if not chain:
        print("⚠️ База пустая, нечего переносить.")
        return

    print(f"📦 Найдено пар слов: {len(chain)}")
    print(f"📚 Обучено сообщений: {total_trained}")
    print("🔌 Подключаюсь к базе данных...")

    conn = await asyncpg.connect(DATABASE_URL)

    # Создаём таблицы если нет
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS markov_chain (
            key TEXT PRIMARY KEY,
            values JSONB NOT NULL
        )
    """)
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS bot_stats (
            id INT PRIMARY KEY DEFAULT 1,
            total_trained INT DEFAULT 0
        )
    """)
    await conn.execute("""
        INSERT INTO bot_stats (id, total_trained)
        VALUES (1, 0)
        ON CONFLICT DO NOTHING
    """)

    print("⬆️ Загружаю данные...")

    # Загружаем батчами по 500
    items = list(chain.items())
    batch_size = 500
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        await conn.executemany("""
            INSERT INTO markov_chain (key, values)
            VALUES ($1, $2::jsonb)
            ON CONFLICT (key) DO UPDATE SET values = $2::jsonb
        """, [(k, json.dumps(v)) for k, v in batch])
        print(f"  {min(i + batch_size, len(items))}/{len(items)}")

    await conn.execute(
        "UPDATE bot_stats SET total_trained = $1 WHERE id = 1",
        total_trained
    )

    await conn.close()
    print("✅ Готово! База перенесена в PostgreSQL.")

if __name__ == "__main__":
    asyncio.run(migrate())
