from typing import List, Optional

from discord import Interaction, Embed, Colour, User
from discord.ext.commands import GroupCog, Bot
# from discord import Guild, Message
from discord.app_commands import command, describe, autocomplete, check, checks
# from discord.app_commands import Choice

import logging; from logger import create_console_handler, create_file_handler
# import asyncio, aiohttp
# import time
# import json

class _ExampleGroup(GroupCog, group_name='examplegroup'):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.setup_log()
        
    def setup_log(self):
        example_logger = logging.getLogger("cogs.group._example")
        example_logger.setLevel(logging.DEBUG)
        example_logger.addHandler(create_console_handler(logging.INFO))
        example_logger.addHandler(create_file_handler("./logs/cogs/group/_example", "_example"))
        self.logger = example_logger
        
    @GroupCog.listener()
    async def on_ready(self):
        self.logger.info(f'{self.__class__.__name__} cog is ready')

    @command(name="info", description="Get information about this example group.")
    async def cmd_info(self, interaction: Interaction):
        """Example command within the group that provides information."""
        await interaction.response.defer()
        
        embed = Embed(
            title="Example Group Command",
            description="This is an example of a command within a command group.",
            color=Colour.blue()
        )
        embed.add_field(name="Usage", value="Use `/examplegroup` commands to interact with this group.")
        embed.set_footer(text=f"Requested by {interaction.user}")
        
        await interaction.followup.send(embed=embed)    
    @command(name="greet", description="Greet a user with a custom message.")
    @describe(user="The user to greet", message="Optional custom message")
    async def cmd_greet(self, interaction: Interaction, user: User, message: Optional[str] = None):
        """Example command that greets a specified user with an optional custom message."""
        await interaction.response.defer()
        
        if message:
            greeting = f"Hello {user.mention}! {message}"
        else:
            greeting = f"Hello {user.mention}! Welcome to our example group command."
        
        self.logger.info(f"User {interaction.user} greeted {user} with message: {message}")
        await interaction.followup.send(greeting)

    @command(name="admin", description="An example admin-only command.")
    @checks.has_permissions(administrator=True)
    async def cmd_admin(self, interaction: Interaction):
        """Example command that demonstrates permission checks."""
        await interaction.response.defer()
        
        embed = Embed(
            title="Admin Command",
            description="This is an admin-only command within the example group.",
            color=Colour.gold()
        )
        embed.add_field(name="Authorization", value="You have administrator permissions.")
        
        self.logger.info(f"Admin command used by {interaction.user}")
        await interaction.followup.send(embed=embed)

async def setup(bot: Bot):
    await bot.add_cog(_ExampleGroup(bot))
