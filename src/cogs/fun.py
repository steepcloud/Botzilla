import random as rd
import discord
import os
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

        api_key = os.getenv("GIPHY_API_KEY")
        if not api_key:
            await ctx.send("GIPHY API key not configured.")
            return

        try:
            url = "https://api.giphy.com/v1/gifs/search"
            params = {
                "q": query,
                "api_key": api_key,
                "limit": 25,
                "rating": "g"
            }

            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data["data"]:
                        gif = rd.choice(data["data"])
                        gif_url = gif["images"]["original"]["url"]

                        embed = discord.Embed(color=discord.Color.random())
                        embed.set_image(url=gif_url)
                        embed.set_footer(text=f"Search: {query} | Powered by GIPHY")
                        await ctx.send(embed=embed)
                    else:
                        await ctx.send(f"No GIFs found for '{query}'.")
                else:
                    await ctx.send(f"Failed to fetch a GIF. Status code: {response.status}")
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")

async def setup(bot):
    await bot.add_cog(Fun(bot))