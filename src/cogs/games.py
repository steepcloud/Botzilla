import random as rd
import asyncio
import discord
from discord.ext import commands


class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.word_game_active = {}
        self.common_words = ["python", "discord", "bot", "game", "programming", "computer", "keyboard", "internet",
                             "server"]

    @commands.command(name="wordgame")
    async def word_game(self, ctx):
        if ctx.channel.id in self.word_game_active:
            await ctx.send("A word game is already active in this channel!")
            return

        self.word_game_active[ctx.channel.id] = True
        await ctx.send("**Word Chain Game Started!**\nEach word must start with the last letter of the previous word.")

        current_word = rd.choice(self.common_words)
        await ctx.send(f"I'll start with: **{current_word}**")

        used_words = {current_word}
        last_letter = current_word[-1]

        def check(message):
            return (message.channel == ctx.channel and
                    not message.author.bot and
                    message.content.lower().isalpha())

        try:
            while True:
                response = await self.bot.wait_for('message', timeout=30.0, check=check)
                word = response.content.lower()

                if not word.startswith(last_letter):
                    await ctx.send(f"Your word must start with the letter **{last_letter}**! Game over.")
                    break

                if word in used_words:
                    await ctx.send(f"The word **{word}** has already been used! Game over.")
                    break

                used_words.add(word)
                last_letter = word[-1]

                await response.add_reaction("✅")

        except asyncio.TimeoutError:
            await ctx.send("Time's up! No one responded in time. Game over.")
        finally:
            del self.word_game_active[ctx.channel.id]

    @commands.command(name="adventure")
    async def mini_adventure(self, ctx):
        await ctx.send("You find yourself at a crossroads in a mysterious forest. Which path do you take?")

        embed = discord.Embed(title="Choose Your Path", color=discord.Color.green())
        embed.add_field(name="1️⃣", value="The dark, overgrown path", inline=True)
        embed.add_field(name="2️⃣", value="The sunny, clear trail", inline=True)
        embed.add_field(name="3️⃣", value="The narrow, winding road", inline=True)

        message = await ctx.send(embed=embed)
        options = ["1️⃣", "2️⃣", "3️⃣"]

        for option in options:
            await message.add_reaction(option)

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in options and reaction.message.id == message.id

        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)

            if str(reaction.emoji) == "1️⃣":
                await ctx.send(
                    "You take the dark path and discover an ancient ruin filled with treasure! However, a dragon guards it...")
            elif str(reaction.emoji) == "2️⃣":
                await ctx.send(
                    "You follow the sunny trail to a peaceful village. The villagers welcome you and offer you a place to stay.")
            else:
                await ctx.send(
                    "You navigate the winding road and stumble upon a magical portal. Do you dare to step through?")

        except asyncio.TimeoutError:
            await ctx.send(
                "You stood at the crossroads too long and night fell. You decide to make camp and try again tomorrow.")


async def setup(bot):
    await bot.add_cog(Games(bot))