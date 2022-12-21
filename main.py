import discord
import asyncio
import os
from discord.ext import commands

from cogs.youtube_cog import YoutubeCog

intents: discord.Intents = discord.Intents.default()
intents.message_content = True

bot: commands.Bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.listen('on_message')
async def yo(message):
    if message.author == bot.user:
        return

    if message.content.startswith('hello'):
        await message.channel.send('yo')

asyncio.run(bot.add_cog(YoutubeCog(bot)))

bot.run(os.getenv('TOKEN'))