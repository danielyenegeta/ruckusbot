from discord.ext import commands

class ExampleCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def coghello(self, ctx):
        await ctx.send("hello from the cog")

