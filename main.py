import asyncio
#import aiosqlite
import youtube_dl
import discord
from discord.ext import commands

# Import Discord Bot Token:
token = open('mooseToken.txt', 'r').read()

# Suppress noise about console usage from errors:
youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',  # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn',
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            # Take first item from a playlist:
            data = data['entries'][0]
        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


# Construct the bot class:
class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def join(self, ctx):
        """Joins a voice channel"""
        if ctx.author.voice:
            await ctx.author.voice.channel.connect()

    @commands.command()
    async def stream(self, ctx, *, url):
        """Streams a video from Youtube without predownloading"""
        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            ctx.voice_client.play(player, after=lambda e: print(f'Player error: {e}') if e else None)
        await ctx.send(f'Now playing: {player.title}')

    @commands.command()
    async def stop(self, ctx):
        """Stops and disconnects the bot from voice"""
        await ctx.voice_client.disconnect()

    @stream.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()


class Moose(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        intents.message_content = True
        super().__init__(command_prefix='!',
                        description='Versatile bot with music capabilities',
                        intents=intents)

    async def on_ready(self):
        print(f'Logged in as {bot.user} (ID: {bot.user.id})')
        print('Moose Up')

    # Database Functionality WIP
        '''async with aiosqlite.connect("moose.db") as db:
            async with db.cursor() as cursor:
                await cursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER, guild INTEGER)')
            await db.commit()

    @commands.command()
    async def adduser(self, ctx, member:discord.Member):
        async with aiosqlite.connect("moose.db") as db:
            async with db.cursor() as cursor:
                await cursor.execute('SELECT id FROM users WHERE guild = ?', (ctx.guild.id,))
                data = await cursor.fetchone()
                if data:
                    # Existing Table/Data
                    await cursor.execute('UPDATE users SET id = ? WHERE guild = ?', (member.id, ctx.guild.id,))
                else:
                    # New Table/Data
                    await cursor.execute('INSERT INTO users (id, guild) VALUES (?,?)', (member.id, ctx.guild.id,))
            await db.commit()'''

    '''@commands.Bot.event
        async def on_voice_state_update(self, member, before, after):
            """Plays the Japanese Yoo meme sound when I join a specific channel"""
            path = "yoo.mp3"
            if not before.channel and after.channel and member.id == INSERT ID:
                vc = await member.voice.channel.connect()
                vc.play(discord.FFmpegPCMAudio(path))
                await vc.disconnect()'''


bot = Moose()

async def main():
    async with bot:
        await bot.add_cog(Music(bot))
        await bot.start(token)

asyncio.run(main())