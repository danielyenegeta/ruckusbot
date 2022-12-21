import asyncio
import discord
import tempfile
import pathlib
import json

from collections import deque
from youtube_dl import YoutubeDL
from discord.ext import commands
from discord.state import ConnectionState
from discord.guild import Guild
from discord import AudioSource, VoiceChannel, FFmpegPCMAudio, FFmpegOpusAudio
from dataclasses import dataclass
from typing import Deque

class YoutubeCog(commands.Cog):
    FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn',
        }
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.vc = None
        self.queue: Deque[self.RuckusSource] = deque()
        self.url_map: dict[str, self.RuckusSource] = {}

    @commands.command(description='plays audio given a youtube url. adds audio to the queue if already playing')
    async def play(self, ctx, url):
        await self.__add_to_queue(ctx, url)
        await self.connect(ctx)
        if not(self.vc.is_playing() or self.vc.is_paused()):
            await self.play_next(ctx)
        
    async def play_next(self, ctx):
        if len(self.queue) == 0:
            await ctx.send("queue is empty, add a youtube link using /play")
        else:
            next_video = self.queue.popleft()
            if self.vc.is_playing():
                self.vc.stop()

            self.vc.play(next_video.source, after = lambda e: asyncio.run_coroutine_threadsafe(self.play_next(ctx), self.bot.loop))
            await ctx.send(f"Now playing: {next_video.title}")
    
    @commands.command(description='pauses the audio player')
    async def pause(self, ctx):
        self.vc.pause()

    @commands.command(description='resumes playing audio')
    async def resume(self, ctx):
        if self.vc.is_paused():
            self.vc.resume()

    @commands.command(description='skips to the next audio in the queue')
    async def skip(self, ctx):
        await self.play_next(ctx)

    @commands.command(description='removes audio from the queue if present')
    async def remove(self, ctx, url):
        if url in self.url_map:
            ruckus_source: self.RuckusSource = self.url_map[url]
            self.queue.remove(ruckus_source)
            self.url_map.pop(url)
            await ctx.send(f"removed {ruckus_source.title} from the queue")
        else:
            await ctx.send(f"the url is not in the queue")

    @commands.command(description='displays the items in the queue')
    async def showqueue(self, ctx):
        if len(self.queue) == 0:
            await ctx.send("queue is empty, add a youtube link using /play")
        else:
            msg = ""
            for i in range(len(self.queue)):
                msg += f"{i+1}: {self.queue[i].title}\n"
            await ctx.send(msg)

    @commands.command(description='displays the next item in the queue')
    async def whatsnext(self, ctx):
        if len(self.queue) == 0:
            await ctx.send("queue is empty, add a youtube link using /play")
        else:
            await ctx.send(f"Playing next: {self.queue[0].title}")

    @commands.command(description='connects to a voice channel')
    async def connect(self, ctx: commands.Context):
        if not self.vc:
            self.vc: discord.VoiceClient = await ctx.message.channel.connect()

    @commands.command(description='disconnects from a voice channel')
    async def disconnect(self, ctx: commands.Context):
        if self.vc:
            await self.vc.disconnect()
    
    async def __add_to_queue(self, ctx, url):
        info = self.download(url)
        source = await FFmpegOpusAudio.from_probe(info['formats'][0]['url'], **self.FFMPEG_OPTIONS)
        ruckus_source: self.RuckusSource = self.RuckusSource(info['title'], url, source)
        self.queue.append(ruckus_source)
        self.url_map[url] = ruckus_source
        await ctx.send(f"Added to queue: {info['title']}")

    def download(self, url: str) -> dict:
        YDL_OPTIONS = {
        'noplaylist': 'True'
        }
        with YoutubeDL(YDL_OPTIONS) as ydl:
            try:    
                info = ydl.extract_info(url, download=False)
                return info   
            except Exception as ex:
                print("exception..." + str(ex))

    @dataclass
    class RuckusSource:
        title: str
        url: str
        source: FFmpegOpusAudio

        



        



    