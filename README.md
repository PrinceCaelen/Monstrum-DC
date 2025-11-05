# ⚡ Lua Corporation Discord Bot

A professional Discord bot for Lua Corporation with Umbrella Corporation-inspired design. Built with Python and discord.py, featuring streamlined modular architecture and corporate-grade functionality.

## ✨ Features

### � Professional Welcome System
- **Corporate-themed welcome messages** - Professional greetings for new members
- **Server boost recognition** - Acknowledge member contributions
- **Clean embeds** with member information and server stats

### � Invite Tracking
- **Advanced invite tracking** - Monitor who invited new members
- **Attribution system** - Credit inviters automatically
- **Statistics tracking** - Total invites, current members, retention metrics
- **Professional ranks** - Recognition system for top recruiters

### � Role Management
- **Button-based role selection** - Modern Discord UI components
- **Self-service roles** - Members manage their own roles
- **Professional interface** - Clean, corporate design

### 📢 Announcement System
- **Unified announcement command** - Single command for all announcements
- **Professional formatting** - Corporate-grade embeds
- **Image attachment support** - Visual announcements
- **Admin-only access** - Controlled communication

### � Support Ticket System
- **Professional ticket system** - Dropdown menu interface
- **Automated organization** - Category-based channel management
- **Staff notifications** - Alert system for urgent requests
- **Transcript generation** - Complete ticket history logging

## 🚀 Setup Instructions

### Prerequisites
- Python 3.8 or higher
- A Discord bot token
- A Discord server with appropriate permissions

### Installation

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure the bot**:
   - Update `config.py` with your bot token and server IDs
   - Customize company name and branding in config.py
   - Set channel IDs for welcome, announcements, etc.

3. **Required Discord Bot Permissions**:
   - `Manage Roles` - For role assignment
   - `Manage Channels` - For ticket system
   - `View Server Insights` - For invite tracking
   - `Send Messages` & `Embed Links` - Basic functionality
   - `Manage Messages` - For ticket management

4. **Run the bot**:
   ```bash
   python main.py
   ```

## ⚙️ Configuration

### Required Setup
Edit `config.py`:

```python
# Bot Configuration
TOKEN = 'your_bot_token_here'
PREFIX = '!'

# Branding
COMPANY_NAME = "Lua Corporation"
COMPANY_TAGLINE = "Excellence Through Innovation"

# Server Configuration
GUILD_ID = your_server_id
WELCOME_CHANNEL_ID = your_welcome_channel_id
ANNOUNCEMENTS_CHANNEL_ID = your_announcements_channel_id

# Role IDs
ROLE_SELECTION_ROLES = {
    '🎮': your_role_id,  # Member role
}
AUTO_ROLE_ID = your_auto_role_id

# Admin Roles
ADMIN_ROLES = [
    your_admin_role_id,
    your_moderator_role_id,
]
```

## 📁 Project Structure

```
Lua-Corporation-Bot/
├── main.py                 # Bot entry point
├── config.py              # Centralized configuration
├── requirements.txt       # Python dependencies
├── README.md             # Documentation
└── cogs/                 # Bot modules
    ├── welcome.py        # Welcome system
    ├── invites.py        # Invite tracking
    ├── roles.py          # Role management
    ├── tickets.py        # Support ticket system
    ├── announcements.py  # Announcement system
    └── help.py           # Help command
```

## 🎯 Essential Commands

### User Commands
- `!help` - Show all available commands
- `!roles` - Role selection menu
- `!myroles` - Show your current roles
- `!invites [@user]` - Check invite statistics
- `!mystats` - Your recruitment record

### Admin Commands
- `!announce <message>` - Post professional announcements
- `!setup ticketpanel` - Create support ticket panel
- `!setup ticketlog <#channel>` - Set ticket logging channel
- `!invitemod @user <amount>` - Modify user invite count
- `!resetinvites [@user]` - Reset invite statistics

## 🔧 Customization

### Theme Colors (Umbrella Corporation Style)
Edit `THEME_COLORS` in `config.py`:
```python
THEME_COLORS = {
    'primary': 0x000000,      # Black
    'secondary': 0x8B0000,    # Dark Red
    'accent': 0xFFFFFF,       # White
    'success': 0x00FF00,      # Green
    'warning': 0xFFAA00,      # Amber
    'error': 0xFF0000,        # Red
}
```

### Welcome Messages
Edit `WELCOME_MESSAGES` in `config.py`:
```python
WELCOME_MESSAGES = [
    "⚡ **{mention}** has joined {company}. Welcome to excellence.",
    # Add more professional messages...
]
```

### Ticket Types
Modify `TICKET_CONFIG` in `config.py`:
```python
'ticket_types': {
    '❓': {'name': 'General Support', 'description': 'Questions...'},
    '⚠️': {'name': 'Report Issue', 'description': 'Report...'},
    # Add custom ticket types...
}
```

## 🐛 Troubleshooting

### Common Issues

**Bot doesn't respond to commands**
- Verify bot token is correct in `config.py`
- Check bot has required permissions
- Ensure bot is online and in your server

**Invite tracking not working**
- Bot needs "View Server Insights" permission
- Verify `WELCOME_CHANNEL_ID` is configured correctly

**Role assignment failing**
- Bot needs "Manage Roles" permission
- Bot's role must be higher than roles it manages
- Check role IDs in `config.py`

**Ticket system not working**
- Run `!setup ticketpanel` to create the ticket interface
- Ensure bot has "Manage Channels" permission
- Verify admin roles are configured correctly

### Logs
Check `bot.log` for detailed error information and debugging.

## 🔒 Security Best Practices

- **Never commit bot token** to version control
- Store sensitive data in environment variables
- Regularly review bot permissions
- Keep dependencies updated
- Monitor bot logs for suspicious activity

## 🎨 Design Philosophy

This bot embodies professional corporate design inspired by the Umbrella Corporation:
- **Clean, minimalist interfaces**
- **Professional black and red color scheme**
- **Streamlined, essential commands only**
- **No unnecessary features or bloat**
- **Corporate-grade reliability**

## 📝 License

This project is provided for Lua Corporation. All rights reserved.

## 🆘 Support

For technical support:
1. Check troubleshooting section
2. Review `bot.log` for errors
3. Verify configuration in `config.py`
4. Consult Discord.py documentation

---

**Lua Corporation** • *Excellence Through Innovation* ⚡