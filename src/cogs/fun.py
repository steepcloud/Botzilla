import random as rd
import discord
from discord.ext import commands
import aiohttp


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()

    def cog_unload(self):
        self.bot.loop.create_task(self.session.close())

    @commands.command(name="joke")
    async def joke(self, ctx):
        async with self.session.get("https://official-joke-api.appspot.com/random_joke") as response:
            if response.status == 200:
                data = await response.json()
                setup = data["setup"]
                punchline = data["punchline"]
                await ctx.send(f"{setup}\n\n||{punchline}||")
            else:
                await ctx.send("Failed to fetch a joke. Try again later.")

    @commands.command(name="gif")
    async def gif(self, ctx, *, query: str = None):
        if not query:
            query = rd.choice(["funny", "cool", "amazing", "wow", "cute"])

        # Using Tenor API (would need an API key in production)
        # For now, just inform the user
        await ctx.send(f"This would search for a '{query}' GIF with proper API integration")

async def setup(bot):
    await bot.add_cog(Fun(bot))