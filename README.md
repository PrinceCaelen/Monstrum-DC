# 🎃 Monstrum Discord Bot

A professional, horror-themed Discord bot designed for the Monstrum game community. Built with Python and discord.py, featuring modular architecture and rich Discord integrations.

## ✨ Features

### 🎭 Welcome System
- **Horror-themed welcome messages** - Random spooky greetings for new members
- **Server boost detection** - Thank you messages for boosters
- **Rich embeds** with member information and server stats

### 📨 Invite Tracking
- **Advanced invite tracking** - See who invited new members
- **Attribution messages** - Credit inviters when members join
- **Statistics tracking** - Total invites, current members, retention rates
- **Horror-themed ranks** - From "Fresh Recruit" to "Leviathan Summoner"

### 🏆 Leaderboard System
- **Invite leaderboards** - Multiple sorting options (total, current, retention)
- **Personal statistics** - Check your own recruitment record
- **Server overview** - Community recruitment health metrics
- **Paginated results** for large servers

### 🎭 Role Assignment
- **Button-based role selection** - Modern Discord UI components
- **Reaction roles** - Classic emoji-based role assignment
- **Self-service roles** - Members can manage their own roles
- **Horror-themed interface** with custom emojis

### 🎮 Game Information
- **Monstrum game data** - Comprehensive game information
- **Monster profiles** - Detailed info about each creature
- **Survival tips** - Help players improve their gameplay
- **Admin announcements** - Post updates, news, and patch notes

## 🚀 Setup Instructions

### Prerequisites
- Python 3.8 or higher
- A Discord bot token
- A Discord server with appropriate permissions

### Installation

1. **Clone or download** this bot to your server
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the bot**:
   - Copy `.env.example` to `.env`
   - Fill in your bot token and server IDs
   - Update `config.py` with your specific settings

4. **Set up Discord permissions**:
   - `Manage Roles` - For role assignment
   - `Manage Messages` - For reaction roles
   - `View Server Insights` - For invite tracking
   - `Send Messages` - Basic functionality
   - `Use Slash Commands` - Modern command interface

5. **Run the bot**:
   ```bash
   python main.py
   ```

## ⚙️ Configuration

### Required Setup
Edit `config.py` and replace placeholder values:

```python
# Bot token (use environment variable in production)
TOKEN = 'your_bot_token_here'

# Server and channel IDs
GUILD_ID = 123456789012345678
WELCOME_CHANNEL_ID = 123456789012345678
ANNOUNCEMENTS_CHANNEL_ID = 123456789012345678

# Role IDs for role selection
ROLE_SELECTION_ROLES = {
    '🎮': 123456789012345678,  # Gamer role
    '👻': 123456789012345678,  # Horror Fan role
    # ... etc
}
```

### Environment Variables (Recommended)
Create a `.env` file:
```env
DISCORD_TOKEN=your_bot_token_here
GUILD_ID=123456789012345678
WELCOME_CHANNEL_ID=123456789012345678
# ... other IDs
```

## 📁 Project Structure

```
DiscordBot/
├── main.py                 # Bot entry point
├── config.py              # Configuration and settings
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── .env.example          # Environment template
└── cogs/                 # Bot modules
    ├── welcome.py        # Welcome system
    ├── invites.py        # Invite tracking
    ├── leaderboard.py    # Statistics and rankings
    ├── roles.py          # Role management
    └── info.py           # Game information
```

## 🎯 Commands

### General Commands
- `!leaderboard` / `!lb` - Show invite leaderboard
- `!invites [@user]` - Check invite statistics
- `!mystats` - Your recruitment record
- `!roles` - Role selection menu
- `!myroles` - Show your current roles

### Game Information
- `!game about` - General Monstrum information
- `!game monsters` - All monster information
- `!game monster <name>` - Specific monster details
- `!game tips` - Survival strategies
- `!game links` - Official resources

### Admin Commands
- `!game announce <message>` - Post announcements
- `!game update <version> <changes>` - Post updates
- `!game news <title> <content>` - Post news
- `!reactionroles` - Set up reaction roles
- `!resetinvites [@user]` - Reset invite stats

### Slash Commands
- `/leaderboard` - Modern leaderboard interface
- `/roles` - Modern role selection
- `/invites` - Check invitation stats
- `/gameinfo` - Game information menu

## 🔧 Customization

### Adding New Welcome Messages
Edit `config.py`:
```python
WELCOME_MESSAGES = [
    "Your new horror-themed message here with {mention}!",
    # Add more messages...
]
```

### Modifying Role Selection
Update `ROLE_SELECTION_ROLES` in `config.py`:
```python
ROLE_SELECTION_ROLES = {
    '🎮': YOUR_ROLE_ID,
    '👻': YOUR_ROLE_ID,
    # Add more emoji/role pairs...
}
```

### Custom Game Information
Modify `GAME_INFO` and `MONSTERS` dictionaries in `config.py`.

## 🐛 Troubleshooting

### Common Issues

**Bot doesn't respond to commands**
- Check bot permissions
- Verify bot token is correct
- Ensure bot is online and in your server

**Invite tracking not working**
- Bot needs "View Server Insights" permission
- Check if `WELCOME_CHANNEL_ID` is configured

**Role assignment failing**
- Bot needs "Manage Roles" permission
- Bot's role must be above roles it manages
- Verify role IDs in `config.py`

**Welcome messages not sending**
- Check `WELCOME_CHANNEL_ID` configuration
- Verify bot has send message permissions in that channel

### Logs
Check `bot.log` for detailed error information.

## 🔒 Security

- **Never commit your bot token** to version control
- Use environment variables for sensitive data
- Regularly rotate your bot token
- Review bot permissions regularly

## 🤝 Contributing

This bot is designed to be easily extensible:

1. **New features** go in the `cogs/` directory
2. **Configuration** goes in `config.py`
3. **Follow the existing code style** and patterns
4. **Test thoroughly** before deploying

## 📝 License

This project is provided as-is for educational and community use. Monstrum is a trademark of Team Junkfish.

## 🆘 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the bot logs
3. Ensure all configuration is correct
4. Check Discord.py documentation for API issues

---

*Built with ❤️ for the Monstrum horror gaming community* 🦑