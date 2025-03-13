import os
import asyncio
import logging
from pathlib import Path
import discord
from discord.ext import commands
from dotenv import load_dotenv


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')


class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(
            command_prefix='!',
            intents=intents,
            help_command=commands.DefaultHelpCommand(),
            description="A fun Discord bot with various features",
            application_id=os.getenv('APPLICATION_ID')
        )

    async def setup_hook(self):
        await self.load_extensions()

    async def load_extensions(self):
        cogs_dir = Path(__file__).parent / "cogs"
        for file in cogs_dir.glob("*.py"):
            if file.name != "__init__.py":
                extension = f"cogs.{file.stem}"
                try:
                    await self.load_extension(extension)
                    logger.info(f"Loaded extension: {extension}")
                except Exception as e:
                    logger.error(f"Failed to load extension {extension}: {e}")

    async def on_ready(self):
        logger.info(f'{self.user.name} has connected to Discord!')
        logger.info(f'Bot is in {len(self.guilds)} guilds')

        try:
            synced = await self.tree.sync()
            logger.info(f"Synced {len(synced)} command(s)")
        except Exception as e:
            logger.error(f"Failed to sync commands: {e}")

        await self.change_presence(activity=discord.Game(name="!help for commands"))


async def main():
    bot = Bot()
    async with bot:
        await bot.start(TOKEN)


if __name__ == '__main__':
    asyncio.run(main())
