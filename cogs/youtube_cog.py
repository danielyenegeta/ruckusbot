from __future__ import annotations

import asyncio
import discord

from collections import deque
from youtube_dl import YoutubeDL
from discord.ext import commands
from discord import FFmpegOpusAudio
from dataclasses import dataclass
from typing import Deque

class YoutubeCog(commands.Cog):
    FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn',
        }
    
    YDL_OPTIONS = {
        'noplaylist': 'True'
        }
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.vc = None
        self.queue: RuckusQueue = RuckusQueue()

    @commands.command(description='plays audio given a youtube url. adds audio to the queue if already playing')
    async def play(self, ctx, url: str) -> None:
        if not self.vc:
            await self.__connect(ctx)

        await self.__add_to_queue(ctx, url)

        if not(self.vc.is_playing() or self.vc.is_paused()):
            await self.__play_next(ctx)
    
    @commands.command(description='pauses the audio player')
    async def pause(self, ctx) -> None:
        self.vc.pause()

    @commands.command(description='resumes playing audio')
    async def resume(self, ctx) -> None:
        if self.vc.is_paused():
            self.vc.resume()

    @commands.command(description='stops audio from playing')
    async def stop(self, ctx) -> None:
        if self.vc.is_playing():
            self.vc.stop()

    @commands.command(description='skips to the next audio in the queue')
    async def skip(self, ctx) -> None:
        if self.queue.is_empty:
            await ctx.send("queue is empty, add a youtube link using /play")
        else:
            await self.__play_next(ctx)

    # @commands.command(description='plays the previous audio')
    # async def back(self, ctx) -> None:
    #     await self.__play_ruckus_source(ctx, self.queue.previous)

    @commands.command(description='removes audio from the queue if present')
    async def remove(self, ctx, url: str) -> None:
        if url in self.queue.sources:
            await self.queue.remove(ctx, url)
        else:
            await ctx.send(f"the url is not in the queue")

    @commands.command(description='displays the items in the queue')
    async def showqueue(self, ctx) -> None:
        if self.queue.is_empty:
            await ctx.send("queue is empty, add a youtube link using /play")
        else:
            await self.__show_queue_msg(ctx)

    @commands.command(description='displays the next item in the queue')
    async def whatsnext(self, ctx) -> None:
        if self.queue.is_empty:
            await ctx.send("queue is empty, add a youtube link using /play")
        else:
            await ctx.send(f"Playing next: {self.queue.peek_next().title}")

    @commands.command(description='connects to a voice channel')
    async def connect(self, ctx: commands.Context) -> None:
        if self.vc:
            await ctx.send(f"already connected to voice channel: {self.vc.channel}")
        else:
            self.__connect(self, ctx)

    @commands.command(description='disconnects from a voice channel')
    async def disconnect(self, ctx: commands.Context) -> None:
        if self.vc:
            await self.vc.disconnect()
        else:
            await ctx.send("already disconnected. connect to a voice channel using /connect")
    
    async def __play_next(self, ctx) -> None:
        next_ruckus_source = self.queue.next
        await self.__play_ruckus_source(ctx, next_ruckus_source)

    async def __play_ruckus_source(self, ctx, ruckus_source: RuckusSource) -> None:
        if self.vc.is_playing():
            self.vc.stop()

        self.vc.play(ruckus_source.source, after = lambda e: asyncio.run_coroutine_threadsafe(self.__after_play(ctx, ruckus_source), self.bot.loop))
        await ctx.send(f"Now playing: {ruckus_source.title}")

    async def __after_play(self, ctx, ruckus_source: RuckusSource):
        # self.queue.add_to_history(ruckus_source)

        if self.queue.is_empty:
            await ctx.send("queue is empty, add a youtube link using /play")
        else:
            await self.__play_next(ctx)
    
    async def __add_to_queue(self, ctx, url: str) -> None:
        ruckus_source = await self.__get_ruckus_source(url)
        await self.queue.append(ctx, url, ruckus_source)

    async def __get_ruckus_source(self, url: str) -> RuckusSource:
        info = self.__extract_info(url)
        source = await FFmpegOpusAudio.from_probe(info['formats'][0]['url'], **self.FFMPEG_OPTIONS)
        return RuckusSource(info['title'], url, source)

    async def __show_queue_msg(self, ctx) -> None:
        msg = ""
        for i in range(len(self.queue)):
            msg += f"{i+1}: {self.queue[i].title}\n"

        await ctx.send(msg)

    async def __connect(self, ctx: commands.Context) -> None:
        self.vc: discord.VoiceClient = await ctx.message.channel.connect()

    def __extract_info(self, url: str) -> dict:
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            try:    
                return ydl.extract_info(url, download=False)
            except Exception as ex:
                print("exception..." + str(ex))

@dataclass
class RuckusSource:
    title: str
    url: str
    source: FFmpegOpusAudio

class RuckusQueue:
    def __init__(self) -> None:
        self.queue: Deque[RuckusSource] = deque()
        self.url_map: dict[str, RuckusSource] = {}
        # self.history: Deque[RuckusSource] = deque()

    @property
    def sources(self) -> dict:
        return self.url_map

    @property
    def next(self) -> RuckusSource:
        return self.queue.popleft()

    # @property
    # def previous(self) -> RuckusSource:
    #     return self.history.popleft()

    @property
    def is_empty(self) -> bool:
        return len(self.queue) == 0

    def peek_next(self) -> RuckusSource:
        return self.queue[0]
    
    async def append(self, ctx, url: str, item: RuckusSource) -> None:
        self.queue.append(item)
        self.url_map[url] = item
        await ctx.send(f"Added to queue: {item.title}")

    async def remove(self, ctx, url: str) -> None:
        source: RuckusSource = self.url_map[url]
        self.queue.remove(source)
        self.url_map.pop(url)
        await ctx.send(f"removed {source.title} from the queue")

    # def add_to_history(self, item: RuckusSource) -> None:
    #     self.history.append(item)
    
    def __len__(self) -> int:
        return len(self.queue)
    
    def __getitem__(self, index: str) -> RuckusSource:
        return self.queue[index]
        



        



    