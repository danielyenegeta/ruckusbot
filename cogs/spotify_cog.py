import discord
from yt_dlp import YoutubeDL
from discord.ext import commands

class SpotifyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot