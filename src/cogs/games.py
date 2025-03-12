import random as rd
import asyncio
import discord
import os
from discord.ext import commands


class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.word_game_active = {}
        self.common_words = ["python", "discord", "bot", "game", "programming", "computer", "keyboard", "internet",
                             "server"]
        self.api_client = None

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
        try:
            from openai import AsyncOpenAI
            success = await self._adventure_openai(ctx)

            if not success:
                await self._adventure_api_ninjas(ctx)

        except Exception as e:
            print(f"Adventure error: {e}")
            await self._fallback_adventure(ctx)

    async def _adventure_openai(self, ctx):
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

            response = await client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{
                    "role": "system",
                    "content": "Generate a short adventure scenario with three choices. Keep it under 100 words."
                }],
                max_tokens=150,
                temperature=0.8
            )

            scenario = response.choices[0].message.content
            parts = scenario.split("\n")
            main_scenario = parts[0]

            embed = discord.Embed(title="Adventure", description=main_scenario, color=discord.Color.green())

            choices = ["Proceed carefully", "Take a bold approach", "Find another way"]
            if len(parts) > 3:
                for i in range(1, min(4, len(parts))):
                    if parts[i].strip():
                        choices[i - 1] = parts[i].strip()

            embed.add_field(name="1️⃣", value=choices[0], inline=True)
            embed.add_field(name="2️⃣", value=choices[1], inline=True)
            embed.add_field(name="3️⃣", value=choices[2], inline=True)

            message = await ctx.send(embed=embed)
            options = ["1️⃣", "2️⃣", "3️⃣"]

            for option in options:
                await message.add_reaction(option)

            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in options and reaction.message.id == message.id

            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
                choice_idx = options.index(str(reaction.emoji))

                outcome_response = await client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "Generate a brief outcome for an adventure choice."},
                        {"role": "user", "content": f"Scenario: {scenario}\n\nChosen option: {choices[choice_idx]}"}
                    ],
                    max_tokens=100,
                    temperature=0.8
                )

                outcome = outcome_response.choices[0].message.content
                await ctx.send(outcome)
                return True

            except asyncio.TimeoutError:
                await ctx.send(
                    "You stood at the crossroads too long and night fell. You decide to make camp and try again tomorrow.")
                return True

        except Exception as e:
            print(f"OpenAI adventure error: {e}")
            return False

    async def _adventure_api_ninjas(self, ctx):
        try:
            if self.api_client is None:
                from src.utils.api_client import ApiClient
                self.api_client = ApiClient()

            prompt = "A short fantasy adventure scenario with choices"
            data = await self.api_client.get("https://api.api-ninjas.com/v1/facts",
                                             #params={"limit": 1},
                                             headers={"X-Api-Key": os.getenv("API_NINJAS_KEY")})

            if data and isinstance(data, list) and len(data) > 0:
                fact = data[0]["fact"]

                scenario = f"In your journey, you encounter an ancient stone with this inscription: '{fact}' As you \
                ponder its meaning, you face a decision."

                embed = discord.Embed(title="Adventure", description=scenario, color=discord.Color.green())
                embed.add_field(name="1️⃣", value="The heroic approach", inline=True)
                embed.add_field(name="2️⃣", value="The cautious strategy", inline=True)
                embed.add_field(name="3️⃣", value="The clever solution", inline=True)

                message = await ctx.send(embed=embed)
                options = ["1️⃣", "2️⃣", "3️⃣"]

                for option in options:
                    await message.add_reaction(option)

                def check(reaction, user):
                    return user == ctx.author and str(reaction.emoji) in options and reaction.message.id == message.id

                try:
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
                    choice_idx = options.index(str(reaction.emoji))

                    outcomes = [
                        "Your heroic approach leads you to face the challenge directly. After a fierce struggle, you emerge victorious and gain valuable treasure and recognition!",
                        "Your cautious strategy pays off. By carefully planning each step, you navigate through the dangers safely and discover a hidden path that others had missed.",
                        "Your clever solution surprises everyone! Using your wits instead of brawn, you find an elegant way to resolve the situation that nobody had considered before."
                    ]

                    await ctx.send(outcomes[choice_idx])
                    return True

                except asyncio.TimeoutError:
                    await ctx.send("You took too long to decide. The opportunity passes.")
                    return True
            else:
                return False

        except Exception as e:
            print(f"API Ninjas adventure error: {e}")
            return False

    async def _fallback_adventure(self, ctx):
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

    def cog_unload(self):
        if self.api_client is not None:
            self.bot.loop.create_task(self.api_client.close())

async def setup(bot):
    await bot.add_cog(Games(bot))