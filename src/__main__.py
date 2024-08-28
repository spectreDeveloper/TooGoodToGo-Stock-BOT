import asyncio
import logging
import dotenv

from tgtgo_api import TooGoodToGoAPI, TooGoodToGoProduct
from telegram import Bot

async def load_dotenv():
    dotenv.load_dotenv()

async def main():
    await load_dotenv()
    print('TooGoodToGo Bot Box Stock - Telegram Bot')
    tgtg: TooGoodToGoAPI = TooGoodToGoAPI()
    telegram_bot: Bot = Bot()

    tokens: bool | str | None = await tgtg.retrieve_datadome_tokens()
    if isinstance(tokens, bool):
        logging.info('Tokens retrieved successfully, authed to TooGoodToGo')        
    elif isinstance(tokens, str):
        print(f'Please load the following URL in your browser to solve the captcha: {tokens} and retrieve the datadome cookie from Developer Tools -> Network and save it in the .env file as DATADOME_COOKIE')
        await tgtg.aiohttp_session.close()
        exit(1)
    else:
        print('Error retrieving tokens')
    await tgtg.aiohttp_session.close()

    tasks: list[asyncio.Task] = []
    tasks.append(asyncio.create_task(telegram_bot.run()))

    await asyncio.gather(*tasks)



    

if __name__ == '__main__':
    asyncio.run(main())