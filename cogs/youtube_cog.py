import discord
import json
from collections import deque
from yt_dlp import YoutubeDL
from discord.ext import commands
from discord.state import ConnectionState
from discord.guild import Guild
from discord import AudioSource, VoiceChannel

class YoutubeCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.vc = None
        self.queue = deque()
        self.curr = 0

    @commands.command()
    async def play(self, ctx, url):
        #get audio via youtubedl
        self.connect(ctx)
        self.__get_audio(url)
        pass

    @commands.command()
    async def play(self, ctx):
        pass

    @commands.command()
    async def pause(self, ctx):
        pass

    @commands.command()
    async def skip(self, ctx):
        pass

    @commands.command()
    async def back(self, ctx):
        pass

    @commands.command()
    async def add(self, ctx, url):
        self.queue.append(url)

    @commands.command()
    async def remove(self, ctx, url):
        if url in self.queue:
            self.queue.remove(url)

    @commands.command()
    async def showqueue(self, ctx):
        for item in self.queue:
            await ctx.send(str(item))

    @commands.command()
    async def whatsnext(self, ctx):
        if len(self.queue) == 0:
            print("queue is empty, add a youtube link")
        else:
            print(self.queue[0])

    @commands.command()
    async def connect(self, ctx: commands.Context):
        # await ctx.send(f"current guild: {ctx.guild()}")
        # ruckus_channel = ctx.guild.get_channel(1044885042335334441)
        self.vc: discord.VoiceClient = await ctx.message.channel.connect()
        # await ctx.guild.voice_client.connect()

    @commands.command()
    async def disconnect(self, ctx: commands.Context):
        # await ctx.send(f"current guild: {ctx.guild()}")
        # ruckus_channel = ctx.guild.get_channel(1044885042335334441)
        await self.vc.disconnect()
        # await ctx.guild.voice_client.connect()

    @commands.command()
    async def ythello(self, ctx):
        await ctx.send("hello from youtube cog")
    
    async def __get_audio(self, url):
        pass

    class _YoutubeQueue():
        def __init__(self) -> None:
            self.queue = deque()

        async def add(self, ctx, url):
            self.queue.append(url)

        async def remove(self, ctx, url):
            pass



        



    