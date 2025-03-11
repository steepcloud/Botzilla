import datetime
import random as rd
import os
import discord
from discord.ext import commands, tasks
import aiohttp


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.birthdays = {}
        self.session = aiohttp.ClientSession()
        self.check_birthdays.start()

    def cog_unload(self):
        self.check_birthdays.cancel()
        self.bot.loop.create_task(self.session.close())

    @commands.command(name="setbirthday")
    async def set_birthday(self, ctx, date: str):
        try:
            month, day = map(int, date.split('-'))
            if not (1 <= month <= 12 and 1 <= day <= 31):
                raise ValueError("Invalid month or day")

            self.birthdays[ctx.author.id] = {'month': month, 'day': day, 'channel_id': ctx.channel.id}
            await ctx.send(f"Birthday set for {ctx.author.mention}: {date}")

        except (ValueError, IndexError):
            await ctx.send("Please use the format MM-DD (e.g., 12-25 for December 25th)")

    @tasks.loop(hours=24)
    async def check_birthdays(self):
        today = datetime.datetime.now()
        current_month, current_day = today.month, today.day

        for user_id, birthday in self.birthdays.items():
            if birthday['month'] == current_month and birthday['day'] == current_day:
                channel = self.bot.get_channel(birthday['channel_id'])
                if channel:
                    user = self.bot.get_user(user_id)
                    if user:
                        await channel.send(f"🎂 Happy Birthday, {user.mention}! 🎉")

    @check_birthdays.before_loop
    async def before_check_birthdays(self):
        await self.bot.wait_until_ready()

    @commands.command(name="fact")
    async def daily_fact(self, ctx):
        async with self.session.get("https://uselessfacts.jsph.pl/api/v2/facts/random") as response:
            if response.status == 200:
                data = await response.json()
                fact = data["text"]
                await ctx.send(f"📚 **Random Fact:** {fact}")
            else:
                await ctx.send("Failed to fetch a fact. Try again later.")

    @commands.command(name="today")
    async def this_day_in_history(self, ctx):
        today = datetime.datetime.now()
        month, day = today.month, today.day

        async with self.session.get(f"https://byabbe.se/on-this-day/{month}/{day}/events.json") as response:
            if response.status == 200:
                data = await response.json()
                events = data.get("events", [])

                if events:
                    event = rd.choice(events)
                    year = event["year"]
                    description = event["description"]

                    embed = discord.Embed(
                        title=f"This Day in History: {month}/{day}",
                        description=f"**{year}**: {description}",
                        color=discord.Color.gold()
                    )
                    await ctx.send(embed=embed)
                else:
                    await ctx.send(f"No historical events found for {month}/{day}.")
            else:
                await ctx.send("Failed to fetch historical events. Try again later.")

    @commands.command(name="music")
    async def music_recommendation(self, ctx, genre: str = None):
        """Get a music recommendation, optionally by genre"""
        try:
            auth_response = await self.session.post(
                'https://accounts.spotify.com/api/token',
                data={'grant_type': 'client_credentials'},
                headers={'Authorization': f'Basic {os.getenv("SPOTIFY_AUTH")}'}
            )

            auth_data = await auth_response.json()
            access_token = auth_data['access_token']
            headers = {'Authorization': f'Bearer {access_token}'}

            if not genre:
                genres_response = await self.session.get(
                    'https://api.spotify.com/v1/recommendations/available-genre-seeds',
                    headers=headers
                )

                genres_data = await genres_response.json()
                available_genres = genres_data.get('genres', [])

                if available_genres:
                    genre = rd.choice(available_genres)
                else:
                    basic_genres = ["rock", "pop", "hip-hop", "jazz", "classical", "electronic", "country"]
                    genre = rd.choice(basic_genres)

            params = {
                'q': f'genre:"{genre}"',
                'type': 'track',
                'limit': 20,
                'market': 'US'
            }

            search_response = await self.session.get(
                'https://api.spotify.com/v1/search',
                params=params,
                headers=headers
            )

            search_data = await search_response.json()

            if search_response.status == 200 and search_data['tracks']['items']:
                track = rd.choice(search_data['tracks']['items'])
                artist = track['artists'][0]['name']
                title = track['name']
                track_url = track['external_urls']['spotify']

                embed = discord.Embed(
                    title=f"Music Recommendation ({genre})",
                    description=f"**{title}** by {artist}\n[Listen on Spotify]({track_url})",
                    color=discord.Color.green()
                )

                if track['album']['images']:
                    embed.set_thumbnail(url=track['album']['images'][0]['url'])

                await ctx.send(embed=embed)
            else:
                await self._fallback_recommendation(ctx, genre)

        except Exception as e:
            print(f"Error accessing Spotify API: {e}")
            await self._fallback_recommendation(ctx, genre)

    async def _fallback_recommendation(self, ctx, genre):
        recommendations = {
            "rock": ["Led Zeppelin - Stairway to Heaven", "Queen - Bohemian Rhapsody"],
            "pop": ["Michael Jackson - Thriller", "Taylor Swift - Blank Space"],
            "hip-hop": ["Kendrick Lamar - HUMBLE.", "Eminem - Lose Yourself"],
            "jazz": ["Miles Davis - So What", "John Coltrane - My Favorite Things"],
            "classical": ["Beethoven - Symphony No. 9", "Mozart - Eine kleine Nachtmusik"],
            "electronic": ["Daft Punk - Get Lucky", "Avicii - Wake Me Up"],
            "country": ["Johnny Cash - Ring of Fire", "Dolly Parton - Jolene"]
        }

        if genre in recommendations:
            song = rd.choice(recommendations[genre])
            await ctx.send(f"🎵 **Music Recommendation ({genre})**: {song}")
        else:
            basic_genres = list(recommendations.keys())
            await ctx.send(f"Genre not recognized. Try one of: {', '.join(basic_genres)}")

async def setup(bot):
    await bot.add_cog(Utility(bot))