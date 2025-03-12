import asyncio
import random as rd
import discord
import os
from discord.ext import commands
from src.utils.api_client import ApiClient


class Trivia(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_client = ApiClient()
        self.trivia_sessions = {}
        self.fallback_riddles = [
            {"question": "What has keys but no locks, space but no room, and you can enter but not go in?",
             "answer": "keyboard"},
            {"question": "What gets wet while drying?", "answer": "towel"},
            {"question": "What can travel around the world while staying in a corner?", "answer": "stamp"},
            {"question": "What has a head and a tail, but no body?", "answer": "coin"}
        ]

    def cog_unload(self):
        self.bot.loop.create_task(self.api_client.close())

    @commands.command(name="trivia")
    async def trivia(self, ctx):
        if ctx.channel.id in self.trivia_sessions:
            await ctx.send("A trivia game is already active in this channel!")
            return

        self.trivia_sessions[ctx.channel.id] = True

        try:
            data = await self.api_client.get("https://opentdb.com/api.php?amount=1&encode=url3986")

            if not data or data["response_code"] != 0:
                await ctx.send("Failed to fetch a trivia question. Try again later.")
                return

            question_data = data["results"][0]

            from urllib.parse import unquote_plus
            question = unquote_plus(question_data["question"])
            correct_answer = unquote_plus(question_data["correct_answer"])
            incorrect_answers = [unquote_plus(a) for a in question_data["incorrect_answers"]]

            all_answers = incorrect_answers + [correct_answer]
            rd.shuffle(all_answers)

            embed = discord.Embed(
                title="Trivia Question",
                description=question,
                color=discord.Color.blue()
            )

            for i, answer in enumerate(all_answers):
                embed.add_field(name=f"Option {i + 1}", value=answer, inline=False)

            await ctx.send(embed=embed)
            await ctx.send("Type the number of your answer!")

            def check(message):
                return (message.channel == ctx.channel and
                        message.content.isdigit() and
                        1 <= int(message.content) <= len(all_answers))

            try:
                message = await self.bot.wait_for('message', timeout=30.0, check=check)
                user_answer = all_answers[int(message.content) - 1]

                if user_answer == correct_answer:
                    await ctx.send(f"🎉 Correct, {message.author.mention}! The answer is **{correct_answer}**.")
                else:
                    await ctx.send(
                        f"❌ Sorry {message.author.mention}, that's incorrect. The correct answer is **{correct_answer}**.")

            except asyncio.TimeoutError:
                await ctx.send(f"Time's up! The correct answer was **{correct_answer}**.")

        finally:
            if ctx.channel.id in self.trivia_sessions:
                del self.trivia_sessions[ctx.channel.id]

    @commands.command(name="riddle")
    async def riddle(self, ctx):
        try:
            data = await self.api_client.get("https://api.api-ninjas.com/v1/riddles",
                                           headers={"X-Api-Key": os.getenv("API_NINJAS_KEY")})

            if data and isinstance(data, list) and len(data) > 0:
                riddle = data[0]
                question = riddle.get("question", "")
                answer = riddle.get("answer", "")
            else:
                riddle = rd.choice(self.fallback_riddles)
                question = riddle["question"]
                answer = riddle["answer"]

            embed = discord.Embed(
                title="Brain Teaser",
                description=question,
                color=discord.Color.purple()
            )
            embed.set_footer(text="Type !answer to see the solution")

            await ctx.send(embed=embed)
            ctx.bot._last_riddle_answer = answer

        except Exception as e:
            riddle = rd.choice(self.fallback_riddles)

            embed = discord.Embed(
                title="Brain Teaser",
                description=riddle["question"],
                color=discord.Color.purple()
            )
            embed.set_footer(text="Type !answer to see the solution")

            await ctx.send(embed=embed)
            ctx.bot._last_riddle_answer = riddle["answer"]

    @commands.command(name="answer")
    async def answer(self, ctx):
        if hasattr(ctx.bot, '_last_riddle_answer'):
            await ctx.send(f"The answer to the riddle is: ||{ctx.bot._last_riddle_answer}||")
        else:
            await ctx.send("There hasn't been a riddle asked yet! Try using `!riddle` first.")


async def setup(bot):
    await bot.add_cog(Trivia(bot))