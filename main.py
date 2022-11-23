import discord
import os
from discord.ext import commands
from discord.app_commands.tree import CommandTree

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

@bot.command()
async def hello(ctx):
    await ctx.reply('hello')

@bot.command()
async def test(ctx, arg):
    await ctx.send(arg)

CommandTree(bot).sync()

bot.run(os.getenv('TOKEN'))