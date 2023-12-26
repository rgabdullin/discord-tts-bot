import asyncio
import discord
import torch
import os
from discord.ext import commands


class TTSCog(commands.Cog):
    def __init__(self, bot, model, sample_rate, speaker):
        self.bot = bot
        self.model = model
        self.sample_rate = sample_rate
        self.speaker = speaker
        self.idx = 0

    def generate(self, text):
        path = self.model.save_wav(text=text, 
                            speaker=self.speaker, 
                            sample_rate=self.sample_rate,
                            put_accent=False, 
                            put_yo=False,
                            audio_path=f'audio/{self.idx}.wav')
        self.idx = (self.idx + 1) % 10
        print(path)
        return path

    @commands.command()
    async def join(self, ctx, *, channel: discord.VoiceChannel):
        """Joins a voice channel"""
        print('join')
        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)

        await channel.connect()

    @commands.command()
    async def say(self, ctx, *, query):
        """Plays a file from the local filesystem"""
        print('say', query)
        path = self.generate(query)
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(path))
        ctx.voice_client.play(source, 
                              after=lambda e: print(f'Player error: {e}') if e else print(f'Finished playing {path}'))

    @commands.command()
    async def stop(self, ctx):
        """Stops and disconnects the bot from voice"""
        print('stop')
        await ctx.voice_client.disconnect()

    @say.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()

# run bot
os.makedirs('audio/', exist_ok=True)

language = 'ru'
model_id = 'v4_ru'
device = torch.device('cpu')
model, example_text = torch.hub.load(repo_or_dir='snakers4/silero-models',
                                     model='silero_tts',
                                     language=language,
                                     speaker=model_id,
                                     trust_repo=True)
model.to(device)  # gpu or cpu
sample_rate = 48000
speaker = 'aidar'

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or("%"),
    description='TTS bot',
    intents=intents,
)
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')

async def main():
    async with bot:
        await bot.add_cog(TTSCog(bot, model, sample_rate, speaker))
        await bot.start(os.environ['DISCORD_TOKEN'])

if __name__ == "__main__":
    print(1)
    asyncio.run(main())