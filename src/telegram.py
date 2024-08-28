import asyncio
import os

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ChatMember
from pyrogram.enums import ParseMode, ChatMemberStatus
from pyrogram.errors import FloodWait
from pyrogram import idle

import logging

class Bot:
    def __init__(self):
        
        self.client = Client(
            name='toogoodtogo_bot',
            api_id=os.getenv('TELEGRAM_API_ID'),
            api_hash=os.getenv('TELEGRAM_API_HASH'),
            bot_token=os.getenv('TELEGRAM_BOT_TOKEN'),
            workdir='/persistent',
            in_memory=False
        )
           
        @self.client.on_message(filters.command('start'))
        async def start(client, message):
            await message.reply_text('Welcome to TooGoodToGo Bot Box Stock.')

    async def send_message(self, chat_id: int, text: str, reply_markup: InlineKeyboardMarkup = None, parse_mode: ParseMode = ParseMode.HTML):
        try:
            await self.client.send_message(chat_id, text, reply_markup=reply_markup, parse_mode=parse_mode)
        except FloodWait as e:
            logging.error(f'FloodWait exception, sleeping for {e.value} seconds')
            await asyncio.sleep(e.value)
            await self.send_message(chat_id, text, reply_markup=reply_markup, parse_mode=parse_mode)
        except Exception as e:
            logging.error(f'Error while sending message: {e}')


    async def run(self):
        await self.client.start()
        logging.info('Connected to Telegram, bot is running.')
        await idle()
        
        
            
    