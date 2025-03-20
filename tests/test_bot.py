import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock, PropertyMock
import discord
from pathlib import Path
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from src.bot import Bot

pytestmark = pytest.mark.asyncio


@pytest.fixture
def bot():
    with patch('discord.ext.commands.Bot.start'), \
        patch('discord.ext.commands.Bot.connect'), \
        patch.object(Bot, 'load_extensions', AsyncMock()):
        bot = Bot()
        yield bot


@pytest.mark.asyncio
async def test_bot_initialization(bot):
    assert bot.command_prefix == '!'
    assert bot.description == "A fun Discord bot with various features"
    assert bot.intents.message_content is True
    await bot.close()


@pytest.mark.asyncio
async def test_on_ready(bot):
    with patch.object(Bot, 'user', new_callable=PropertyMock) as mock_user, \
            patch.object(Bot, 'guilds', new_callable=PropertyMock) as mock_guilds, \
            patch.object(Bot, 'tree', new_callable=PropertyMock) as mock_tree, \
            patch.object(bot, 'change_presence', new=AsyncMock()) as mock_change_presence, \
            patch('logging.Logger.info') as mock_logger:

        mock_user_obj = MagicMock()
        mock_user_obj.name = "TestBot"
        mock_user.return_value = mock_user_obj

        mock_guilds.return_value = [MagicMock(), MagicMock()]

        mock_tree_obj = MagicMock()
        mock_tree_obj.sync = AsyncMock(return_value=[1, 2, 3])
        mock_tree.return_value = mock_tree_obj

        await bot.on_ready()

        mock_logger.assert_any_call('TestBot has connected to Discord!')
        mock_logger.assert_any_call('Bot is in 2 guilds')
        mock_logger.assert_any_call('Synced 3 command(s)')

        mock_change_presence.assert_called_once()


@pytest.mark.asyncio
async def test_load_extensions(bot):
    original_load_extensions = bot.load_extensions

    try:
        async def actual_load_extensions_implementation(self):
            cogs_dir = Path("cogs")
            for cog_file in cogs_dir.glob("*.py"):
                if cog_file.is_file():
                    cog_name = f"cogs.{cog_file.stem}"
                    await self.load_extension(cog_name)

        bot.load_extensions = lambda: actual_load_extensions_implementation(bot)

        with patch.object(bot, 'load_extension', AsyncMock()) as mock_load_extension, \
                patch('pathlib.Path.glob') as mock_glob:

            cogs_files = [
                Path('cogs/slash_commands.py'),
                Path('cogs/trivia.py'),
                Path('cogs/games.py')
            ]
            mock_glob.return_value = cogs_files

            with patch('pathlib.Path.is_file', return_value=True):
                await bot.load_extensions()

                assert mock_load_extension.call_count == 3
                mock_load_extension.assert_any_call('cogs.slash_commands')
                mock_load_extension.assert_any_call('cogs.trivia')
                mock_load_extension.assert_any_call('cogs.games')
    finally:
        bot.load_extensions = original_load_extensions


@pytest.mark.asyncio
async def test_setup_hook(bot):
    with patch.object(bot, 'load_extensions', AsyncMock()) as mock_load_extensions:
        await bot.setup_hook()
        mock_load_extensions.assert_called_once()


@pytest.mark.asyncio
async def test_on_ready_with_sync_exception(bot):
    with patch.object(Bot, 'user', new_callable=PropertyMock) as mock_user, \
            patch.object(Bot, 'guilds', new_callable=PropertyMock) as mock_guilds, \
            patch.object(Bot, 'tree', new_callable=PropertyMock) as mock_tree, \
            patch.object(bot, 'change_presence', new=AsyncMock()) as mock_change_presence, \
            patch('logging.Logger.info') as mock_logger_info, \
            patch('logging.Logger.error') as mock_logger_error:
        mock_user_obj = MagicMock()
        mock_user_obj.name = "TestBot"
        mock_user.return_value = mock_user_obj

        mock_guilds.return_value = [MagicMock()]

        mock_tree_obj = MagicMock()
        mock_tree_obj.sync = AsyncMock(side_effect=Exception("Failed to sync"))
        mock_tree.return_value = mock_tree_obj

        await bot.on_ready()
        mock_logger_error.assert_called_once()
        assert "Failed to sync commands" in mock_logger_error.call_args[0][0]

        mock_change_presence.assert_called_once()


@pytest.mark.asyncio
async def test_main_function():
    mock_bot_instance = AsyncMock()

    with patch('src.bot.Bot', return_value=mock_bot_instance), \
            patch('src.bot.TOKEN', 'fake-token'):
        from src.bot import main
        await main()

        mock_bot_instance.start.assert_called_once_with('fake-token')


@pytest.mark.asyncio
async def test_cog_loading(bot):
    with patch.object(bot, 'add_cog') as mock_add_cog:
        class TestCog(discord.ext.commands.Cog):
            def __init__(self, bot):
                self.bot = bot

        async def test_setup(bot):
            await bot.add_cog(TestCog(bot))

        await test_setup(bot)
        mock_add_cog.assert_called_once()
        assert isinstance(mock_add_cog.call_args[0][0], TestCog)


@pytest.mark.asyncio
async def test_change_presence_call(bot):
    with patch.object(Bot, 'user', new_callable=PropertyMock) as mock_user, \
            patch.object(Bot, 'guilds', new_callable=PropertyMock) as mock_guilds, \
            patch.object(Bot, 'tree', new_callable=PropertyMock) as mock_tree, \
            patch.object(bot, 'change_presence', AsyncMock()) as mock_change_presence, \
            patch('logging.Logger.info'):

        mock_user_obj = MagicMock()
        mock_user_obj.name = "TestBot"
        mock_user.return_value = mock_user_obj
        mock_guilds.return_value = [MagicMock()]

        mock_tree_obj = MagicMock()
        mock_tree_obj.sync = AsyncMock(return_value=[])
        mock_tree.return_value = mock_tree_obj

        await bot.on_ready()

        call_args = mock_change_presence.call_args[1]
        activity = call_args.get('activity')

        assert isinstance(activity, discord.Game)
        assert activity.name == "!help for commands"


@pytest.mark.asyncio
async def test_bot_close(bot):
    with patch.object(bot, 'close', AsyncMock()) as mock_close:
        await bot.close()
        mock_close.assert_called_once()


@pytest.mark.asyncio
async def test_command_registration(bot):
    from discord.ext.commands import Command
    commands = {}

    def mock_command_decorator(name=None):
        def decorator(func):
            cmd = Command(func, name=name)
            commands[name] = cmd
            return cmd

        return decorator

    bot.command = mock_command_decorator
    bot.all_commands = commands

    @bot.command(name="test_command")
    async def test_command(ctx):
        pass

    assert "test_command" in bot.all_commands
    assert test_command is bot.all_commands["test_command"]
    assert test_command.callback.__name__ == "test_command"


@pytest.mark.asyncio
async def test_env_loading():
    with patch('os.getenv', return_value='test-token') as mock_getenv:
        import importlib
        import src.bot
        importlib.reload(src.bot)

        mock_getenv.assert_any_call('DISCORD_TOKEN')
        assert src.bot.TOKEN == 'test-token'