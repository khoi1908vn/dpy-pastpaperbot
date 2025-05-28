from typing import List

from discord.ext.commands import Cog
# from discord import Guild, Interaction, Message
from discord.app_commands import command, describe, autocomplete
# from discord.app_commands import Choice

import logging; from logger import create_console_handler, create_file_handler
from main import ExampleBot
# import asyncio, aiohttp
# import time

class ExampleCog(Cog):
    def __init__(self, bot: ExampleBot):
        self.bot = bot
        self.setup_log()
    def setup_log(self):
        example_logger = logging.getLogger("cogs.single._example")
        example_logger.setLevel(logging.DEBUG)
        example_logger.addHandler(create_console_handler(logging.INFO))
        example_logger.addHandler(create_file_handler("./logs/cogs/single/_example", "_example"))
        self.logger = example_logger
    @Cog.listener()
    async def on_ready(self):
        raise NotImplementedError
    @command(name="example", description="Example command.")
    async def example(self, interaction):
        raise NotImplementedError

async def setup(bot: ExampleBot):
    await bot.add_cog(ExampleCog(bot))
