# Botzilla - a fun discord bot

A feature-rich Discord bot with various entertainment and utility features. Built with Python and discord.py.

## Features

- **Slash Commands**: Simple utility commands like `/ping`
- **Trivia**: Test your knowledge with trivia games
- **Games**: Various fun games to play in your server
- **API Integrations**: Connects with Spotify, OpenAI, Giphy, and more

## Installation

```bash
# Clone the repository
git clone https://github.com/steepcloud/Botzilla.git
cd Botzilla

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Configuration

1. Create a `.env` file in the `src` directory with the following variables:

```
DISCORD_TOKEN=your_discord_bot_token
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
SPOTIFY_AUTH=base64_encoded_credentials
API_NINJAS_KEY=your_api_ninjas_key
OPENAI_API_KEY=your_openai_api_key
GIPHY_API_KEY=your_giphy_api_key
APPLICATION_ID=your_discord_application_id
```

2. Create a Discord application and bot at [Discord Developer Portal](https://discord.com/developers/applications)

## Usage

```bash
# Run the bot
python src/bot.py
```

Use `!help` to see available text commands or `/` to access slash commands in Discord.

## Testing

```bash
# Run tests
pytest tests/
```

## License

[MIT](LICENSE)
