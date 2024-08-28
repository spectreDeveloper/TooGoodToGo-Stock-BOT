import asyncio
import logging
import dotenv
import os

from tgtgo_api import TooGoodToGoAPI, TooGoodToGoProduct
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from database import Database

logging.getLogger("pyrogram").setLevel(logging.WARNING)
logging.basicConfig(level=logging.INFO)

async def load_dotenv():
    dotenv.load_dotenv()

async def iterate_products(TooGoodToGoAPI:TooGoodToGoAPI, products_queue: asyncio.Queue) -> list[TooGoodToGoProduct]:
    while True:
        print('Iterating products')
        tgtg_products: list[TooGoodToGoProduct] = await TooGoodToGoAPI.retrieve_products_shippable()
        logging.info(f'Found {len(tgtg_products)} products')
        for product in tgtg_products:
            await products_queue.put(product)
        await asyncio.sleep(int(os.getenv('REFRESH_INTERVAL')))
        logging.info(f'List was refreshed, found {len(tgtg_products)} products, sleeping for {os.getenv("REFRESH_INTERVAL")} seconds')


async def process_product_queue(products_queue: asyncio.Queue, telegram_bot_queue: asyncio.Queue, db: Database):
    while True:
        need_notifications: bool = False
        product: TooGoodToGoProduct = await products_queue.get()
        if isinstance(product, TooGoodToGoProduct):
            db_product: tuple | None = await db.get_product(product.item_id)
            if db_product is None:
                logging.info(f'Product {product.name} is not in the database, adding it [{product.item_id} - {product.name} - {product.price}€ - {product.original_price}€ - {product.available_stock}]')
                await db.upsert_product(product.item_id, product.name, product.price, product.original_price, product.available_stock)
                if product.available_stock > 0:
                    need_notifications = True
                elif product.available_stock <= 0:
                    need_notifications = True
            elif db_product is not None:
                    if db_product[4] == product.available_stock:
                        logging.info(f'Product {product.name} is already in the database, stock quantity is the same [{product.available_stock}] skipping')
                        continue

                    if db_product[4] != product.available_stock and product.available_stock > 0:
                        need_notifications = True
                    else:
                        need_notifications = False
                    logging.info(f'Product {product.name} is already in the database, updating stock quantity from {db_product[4]} to {product.available_stock}')
                    await db.upsert_product(product.item_id, product.name, product.price, product.original_price, product.available_stock)
            if need_notifications:
                await telegram_bot_queue.put(product)

async def process_telegram_queue(telegram_bot_queue: asyncio.Queue, bot: Bot):
    chat_ids: list[int] = [int(chat_id) for chat_id in os.getenv('TELEGRAM_CHAT_IDS').split(',')]
    while True:
        continue
        product: TooGoodToGoProduct = await telegram_bot_queue.get()
        for chat_id in chat_ids:
            await bot.send_message(chat_id, f'<a href="{product.cover_picture_url}">⁣</a>\n📦 <b>DISPONIBILE ORA {str(product.name).upper()}</b>\n\nA Soli {product.price}€ invece di <strike>{product.original_price}€</strike>\n\nDisponibilità di <b>{product.available_stock}</b> pezzi.',
                                   reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('🛒 Acquista', url=f'https://share.toogoodtogo.com/item/{product.item_id}/delivery')]])
                                   )

async def main():
    await load_dotenv()
    print('TooGoodToGo Bot Box Stock - Telegram Bot')

    db: Database = Database('/persistent/products.db')
    await db.initialize()

    tgtg: TooGoodToGoAPI = TooGoodToGoAPI()
    products_queue: asyncio.Queue = asyncio.Queue()
    telegram_products_queue: asyncio.Queue = asyncio.Queue()

    telegram_bot: Bot = Bot()
    while telegram_bot.client.is_connected is False:
        logging.info('Connecting to Telegram...')

    tokens: bool | str | None = await tgtg.retrieve_datadome_tokens()
    if isinstance(tokens, bool):
        logging.info('Tokens retrieved successfully, authed to TooGoodToGo')  
    elif isinstance(tokens, str):
        print(f'Please load the following URL in your browser to solve the captcha: {tokens} and retrieve the datadome cookie from Developer Tools -> Network and save it in the .env file as DATADOME_COOKIE')
        await tgtg.aiohttp_session.close()
        exit(1)
    else:
        print('Error retrieving tokens')

    tasks: list[asyncio.Task] = []
    tasks.append(asyncio.create_task(telegram_bot.run()))
    tasks.append(asyncio.create_task(process_product_queue(products_queue, telegram_products_queue, db)))
    tasks.append(asyncio.create_task(iterate_products(tgtg, products_queue)))
    tasks.append(asyncio.create_task(process_telegram_queue(telegram_products_queue, telegram_bot)))

    await asyncio.gather(*tasks)



    

if __name__ == '__main__':
    asyncio.run(main())