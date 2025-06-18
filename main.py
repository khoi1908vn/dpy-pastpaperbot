"""
ENTRYPOINT FILE
"""

from discord.ext.commands import Bot
from discord.ext.commands import when_mentioned_or
from discord.app_commands import CommandTree
from discord import Intents
import os, json
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
# File imports
import logging; from logger import create_console_handler, create_file_handler
from google import genai

class Constants:
    BOT_TOKEN: str
    BOT_PREFIX: str
    BOT_OWNER_IDS: str
    #CLIENT_ID: str
    #CLIENT_SECRET: str
    MONGO_URI: str
    GEMINI_API_KEY: str

class ExampleCommandTree(CommandTree):
    async def interaction_check(self, interaction):
        #bot = interaction.client
        return True # ALLOW ALL INTERACTIONS
class PPBdpy(Bot):
    def __init__(self):
        self.load_constant()
        super().__init__(
            intents=Intents.all(),
            command_prefix=when_mentioned_or(self.const.BOT_PREFIX),
            owner_ids=json.loads(self.const.BOT_OWNER_IDS),
            tree_cls=ExampleCommandTree
        )
        self.setup_log()
    def load_constant(self):
        self.const = Constants()
        # Bot Constants
        self.const.BOT_TOKEN = os.getenv('BOT_TOKEN')
        self.const.BOT_PREFIX = os.getenv('BOT_PREFIX')
        self.const.BOT_OWNER_IDS = os.getenv('BOT_OWNER_IDS')
        #self.const.CLIENT_ID = os.getenv('CLIENT_ID')
        #self.const.CLIENT_SECRET = os.getenv('CLIENT_SECRET')
        # API Constants
        self.const.MONGO_URI = os.getenv('MONGO_URI')
        self.const.GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
        
    def run(self):
        super().run(self.const.BOT_TOKEN, log_handler=None)
    def setup_log(self):
        discord_logger = logging.getLogger("discord")
        discord_logger.setLevel(logging.INFO)
        discord_logger.addHandler(create_console_handler())
        discord_logger.addHandler(create_file_handler("./logs", "discord"))

        bot_logger = logging.getLogger("main")
        bot_logger.setLevel(logging.DEBUG)
        bot_logger.addHandler(create_console_handler()) 
        bot_logger.addHandler(create_file_handler("./logs", "main"))
        self.logger = bot_logger
    async def setup_hook(self):
        # --- SETUP LOGGING ---
        self.logger.info("SETTING UP BOT...")
        # --- LOAD COGS ---
        self.logger.info("Loading cogs...")
        for fd in ['single', 'group']:
            for fn in os.listdir(f"cogs/{fd}"):
                if fn.endswith(".py") and not fn.startswith("_"):
                    cog_name = f"cogs.single.{fn[:-3]}"
                    await self.load_extension(cog_name)
        #await self.load_extension('cogs.events')
        await self.load_extension('jishaku')
        # --- PRE-LOAD DATABASE ---
        self.logger.info("Pre-loading database...")
        self.db = AsyncIOMotorClient(self.const.MONGO_URI)
        # --- SETUP API ---
        self.logger.info("Setting up APIs...")
        self.logger.info(f"Setting up Google AI... Using API key ...{self.const.GEMINI_API_KEY[-3:]}")
        self.gemini = genai.Client(api_key=self.const.GEMINI_API_KEY).aio

        self.logger.info(f"Bot is ready. {self.user.name} Joined {len(self.guilds)} guilds.")

    async def on_command_error(self, context, exception):
        return await super().on_command_error(context, exception)
        # TODO: (not necessary) Handle errors from checks (e.g. missing permissions)
        # CommandInvokeError | CommandNotFound, CommandSignatureMismatch |
    # on_message
    

if __name__ == '__main__':
    load_dotenv() # testing onli eheheh
    bot = PPBdpy()
    bot.run()