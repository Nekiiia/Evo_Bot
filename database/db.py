import aiosqlite
from typing import List, Dict

DB_NAME = "bot.db"


async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        # Удаляем старую таблицу и создаём новую с нужными колонками
        await db.execute("DROP TABLE IF EXISTS cart")
        
        await db.execute("""
            CREATE TABLE cart (
                user_id INTEGER,
                product_id INTEGER,
                quantity INTEGER DEFAULT 1,
                price_type TEXT DEFAULT 'normal',
                PRIMARY KEY (user_id, product_id, price_type)
            )
        """)
        await db.commit()
    print("✅ База данных успешно обновлена (с поддержкой price_type)")


async def add_to_cart(user_id: int, product_id: int, is_debt: bool = False):
    price_type = "debt" if is_debt else "normal"
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            INSERT INTO cart (user_id, product_id, quantity, price_type) 
            VALUES (?, ?, 1, ?) 
            ON CONFLICT(user_id, product_id, price_type) 
            DO UPDATE SET quantity = quantity + 1
        """, (user_id, product_id, price_type))
        await db.commit()


async def get_cart(user_id: int) -> List[Dict]:
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("""
            SELECT product_id, quantity, price_type 
            FROM cart WHERE user_id = ?
        """, (user_id,)) as cursor:
            rows = await cursor.fetchall()
            return [{"product_id": r[0], "quantity": r[1], "price_type": r[2]} for r in rows]


async def remove_from_cart(user_id: int, product_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "UPDATE cart SET quantity = quantity - 1 WHERE user_id = ? AND product_id = ?",
            (user_id, product_id)
        )
        await db.execute(
            "DELETE FROM cart WHERE user_id = ? AND product_id = ? AND quantity <= 0",
            (user_id, product_id)
        )
        await db.commit()


async def clear_cart(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("DELETE FROM cart WHERE user_id = ?", (user_id,))
        await db.commit()


async def clear_all_carts():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("DELETE FROM cart")
        await db.commit()
    print("🧹 Все корзины очищены")