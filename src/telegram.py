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

    async def run(self):
        await self.client.start()
        while self.client.is_connected is False:
            logging.info('Connecting to Telegram...')

        await idle()
        
        
            
    