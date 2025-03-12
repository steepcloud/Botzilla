import random as rd
import discord
import os
from discord.ext import commands
import aiohttp
import asyncio


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

    @commands.command(name="meme")
    async def meme(self, ctx):
        try:
            async with self.session.get("https://meme-api.herokuapp.com/gimme") as response:
                if response.status == 200:
                    data = await response.json()
                    embed = discord.Embed(title=data["title"], color=discord.Color.random())
                    embed.set_image(url=data["url"])
                    embed.set_footer(text=f" {data['ups']} | From r/{data['subreddit']}")
                    await ctx.send(embed=embed)
                else:
                    await ctx.send("Failed to fetch a meme. Try again later.")
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")

    @commands.command(name="8ball", aliases=["eightball", "fortune"])
    async def eightball(self, ctx, *, question=None):
        if not question:
            await ctx.send("Please ask a question for the magic 8-ball!")
            return

        responses = [
            "It is certain.", "It is decidedly so.", "Without a doubt.",
            "Yes, definitely.", "You may rely on it.", "As I see it, yes.",
            "Most likely.", "Outlook good.", "Yes.", "Signs point to yes.",
            "Reply hazy, try again.", "Ask again later.", "Better not tell you now.",
            "Cannot predict now.", "Concentrate and ask again.",
            "Don't count on it.", "My reply is no.", "My sources say no.",
            "Outlook not so good.", "Very doubtful."
        ]

        response = rd.choice(responses)
        embed = discord.Embed(color=discord.Color.blue())
        embed.add_field(name="Question", value=question, inline=False)
        embed.add_field(name="Magic 8-Ball says", value=response, inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="flip", aliases=["coin"])
    async def flip(self, ctx):
        result = rd.choice(["Heads", "Tails"])

        heads_image = "https://i.imgur.com/jTGm7MF.png"
        tails_image = "https://www.nicepng.com/png/full/146-1464848_quarter-tail-png-tails-on-a-coin.png"

        embed = discord.Embed(
            title="Coin Flip",
            description=f"The coin landed on **{result}**!",
            color=discord.Color.gold()
        )

        if result == "Heads":
            embed.set_thumbnail(url=heads_image)
        else:
            embed.set_thumbnail(url=tails_image)

        await ctx.send(embed=embed)

    @commands.command(name="fireworks")
    async def fireworks(self, ctx):
        await ctx.send("💥 **Fireworks ready!** The next message will get a surprise...")

        def check(message):
            return message.channel == ctx.channel and not message.author.bot

        try:
            message = await self.bot.wait_for('message', check=check, timeout=60.0)

            emoji_ranges = [
                (0x1F600, 0x1F64F),  # Emoticons
                (0x1F300, 0x1F5FF),  # Misc Symbols and Pictographs
                (0x1F680, 0x1F6FF),  # Transport and Map
                (0x2600, 0x26FF),  # Misc symbols
                (0x1F700, 0x1F77F),  # Alchemical Symbols
            ]

            emoji_list = []
            for start, end in emoji_ranges:
                for codepoint in range(start, end + 1):
                    try:
                        emoji = chr(codepoint)
                        emoji_list.append(emoji)
                    except (ValueError, UnicodeEncodeError):
                        continue

            selected_emojis = rd.sample(emoji_list, min(20, len(emoji_list)))

            for emoji in selected_emojis:
                try:
                    await message.add_reaction(emoji)
                    #await asyncio.sleep(0.1)
                except discord.HTTPException:
                    continue

            await ctx.send(f"💥 Fireworks for {message.author.mention}! 🎉")

        except asyncio.TimeoutError:
            await ctx.send("No one sent a message in time. Fireworks fizzled out... 💨")

async def setup(bot):
    await bot.add_cog(Fun(bot))