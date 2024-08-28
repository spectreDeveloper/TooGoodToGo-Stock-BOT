import aiosqlite

class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._connection = None

    async def initialize(self):
        self._connection = await aiosqlite.connect(self.db_path)
        await self._connection.execute('''
        CREATE TABLE IF NOT EXISTS products (
            item_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            original_price REAL NOT NULL,
            stock_quantity INTEGER NOT NULL DEFAULT 0,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        ''')
        await self._connection.commit()

    async def upsert_product(self, item_id: str, name: str, price: float, original_price: float, stock_quantity: int):
        await self._connection.execute('''
        INSERT INTO products (item_id, name, price, original_price, stock_quantity, last_updated)
        VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(item_id) DO UPDATE SET
            name = excluded.name,
            price = excluded.price,
            original_price = excluded.original_price,
            stock_quantity = excluded.stock_quantity,
            last_updated = CURRENT_TIMESTAMP;
        ''', (item_id, name, price, original_price, stock_quantity))
        await self._connection.commit()

    async def get_product(self, item_id: str) -> tuple | None:
        async with self._connection.execute('''
        SELECT item_id, name, price, original_price, stock_quantity, last_updated
        FROM products
        WHERE item_id = ?;
        ''' , (item_id,)) as cursor:
            return await cursor.fetchone()
        
        

    async def close(self):
        if self._connection:
            await self._connection.close()
