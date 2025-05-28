from discord.ext.commands import Cog

class Events(Cog):
    pass

async def setup(bot):
    await bot.add_cog(Events(bot))


