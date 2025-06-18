from typing import List

from discord.ext.commands import Cog
from discord import Interaction
from discord.app_commands import command, describe, autocomplete
# from discord.app_commands import Choice

import logging; from logger import create_console_handler, create_file_handler
from main import PPBdpy
import asyncio
# import time

class AIchat(Cog):
    def __init__(self, bot: PPBdpy):
        self.bot = bot
        self.setup_log()
    def setup_log(self):
        ai_chat = logging.getLogger("cogs.single.ai_chat")
        ai_chat.setLevel(logging.DEBUG)
        ai_chat.addHandler(create_console_handler(logging.INFO))
        ai_chat.addHandler(create_file_handler("./logs/cogs/single/ai_chat", "ai_chat"))
        self.logger = ai_chat
    @Cog.listener()
    async def on_ready(self):
        return
    @command(name="chat", description="Chat with AI.")
    async def chatAI(self, interaction: Interaction, prompt: str):
        await interaction.response.defer(ephemeral=False)
        _ai_response = await self.bot.gemini.models.generate_content(model='gemini-2.0-flash-001', contents=prompt)
        ai_response = _ai_response.text
        # Split the response into chunks of 1999 characters
        chunks = [ai_response[i:i+1999] for i in range(0, len(ai_response), 1999)]
        for idx, chunk in enumerate(chunks):
            await asyncio.sleep(0.1)
            await interaction.followup.send(content=chunk)

async def setup(bot: PPBdpy):
    await bot.add_cog(AIchat(bot))
