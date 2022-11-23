import discord
import json
from yt_dlp import YoutubeDL
from discord.ext import commands

class YoutubeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def play(self, ctx, url):
        #get audio via youtubedl
        self.__get_audio(url)
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
        pass

    @commands.command()
    async def remove(self, ctx, url):
        pass

    @commands.command()
    async def disconnect(self, ctx, url):
        pass

    async def __get_audio(self, url):
        pass

    