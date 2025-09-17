import os
from typing import List, Dict

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# ================================
# BOT CONFIGURATION
# ================================

# Bot Token (NEVER commit the actual token to GitHub!)
TOKEN = os.getenv('DISCORD_TOKEN', 'YOUR_BOT_TOKEN_HERE')

# Command Prefix
PREFIX = '!'

# Bot Owner ID (Replace with your Discord user ID)
OWNER_ID = int(os.getenv('OWNER_ID', '1400112309766062181'))

# ================================
# SERVER CONFIGURATION
# ================================

# Main Guild ID (Replace with your server ID)
GUILD_ID = int(os.getenv('GUILD_ID', '1417462654821335050'))

# Channel IDs
WELCOME_CHANNEL_ID = int(os.getenv('WELCOME_CHANNEL_ID', '1417465985278939220'))
BOOST_CHANNEL_ID = int(os.getenv('BOOST_CHANNEL_ID', '1417466202883620894'))
GENERAL_CHANNEL_ID = int(os.getenv('GENERAL_CHANNEL_ID', '1417466202883620894'))
ANNOUNCEMENTS_CHANNEL_ID = int(os.getenv('ANNOUNCEMENTS_CHANNEL_ID', '1417466797724012544'))
LEADERBOARD_CHANNEL_ID = int(os.getenv('LEADERBOARD_CHANNEL_ID', '1417901003516411925'))

# Role IDs for auto-assignment
ROLE_SELECTION_ROLES = {
    '🚢': int(os.getenv('MONSTRUM_PLAYER_ROLE_ID', '1417471815147589642')),  # Your main Monstrum role
}

# Auto-assign role to new members
AUTO_ROLE_ID = int(os.getenv('AUTO_ROLE_ID', '1417470579774197800'))  # Role given to all new members automatically

# Admin/Moderator role IDs
ADMIN_ROLES = [
    int(os.getenv('ADMIN_ROLE_ID', '1417464869183291422')),
    int(os.getenv('MODERATOR_ROLE_ID', '1417465338278318100')),
]

# ================================
# WELCOME MESSAGES
# ================================

# Horror-themed welcome messages for new members
WELCOME_MESSAGES = [
    "🚢 **{mention}** has boarded the cursed vessel! Welcome to the depths of Monstrum... try not to get eaten! 🦑",
    "👻 A new soul, **{mention}**, has entered our haunted realm! The monsters are already watching... 👁️",
    "🎃 **{mention}** has awakened from the nightmare! Welcome to Monstrum - where horror meets the high seas! ⚓",
    "🕷️ Look what the tide washed ashore... **{mention}** has joined our crew of survivors! Mind the tentacles! 🐙",
    "⚡ **{mention}** has escaped the lab, only to find themselves here! Welcome to our twisted community! 🧪",
    "🔥 Another brave soul, **{mention}**, dares to face the unknown! The ship's engine is already rumbling... 🚢",
    "💀 **{mention}** has entered the belly of the beast! Welcome aboard - hope you brought a flashlight! 🔦",
    "🌊 The ocean has delivered **{mention}** to our shores! Welcome to Monstrum, where nightmares become reality! 🌙",
    "🦴 Fresh meat has arrived! Welcome **{mention}** to our horror-loving family! Try not to feed the monsters! 🍖",
    "🕸️ **{mention}** has stumbled into our web of terror! Welcome to the Monstrum community - enjoy your stay... if you can! 🕷️"
]

# Welcome embed colors (hex codes)
WELCOME_COLORS = [
    0x8B0000,  # Dark Red
    0x2F4F4F,  # Dark Slate Gray
    0x191970,  # Midnight Blue
    0x556B2F,  # Dark Olive Green
    0x483D8B,  # Dark Slate Blue
    0x8B4513,  # Saddle Brown
]

# ================================
# BOOST MESSAGES
# ================================

BOOST_MESSAGES = [
    "🚀 **{mention}** has supercharged our cursed vessel! The monsters are pleased with this offering! 💜",
    "⚡ **{mention}** has blessed us with a boost! The ship's power grows stronger! Thank you, brave soul! 🔋",
    "💎 **{mention}** has upgraded our nightmare! The crew salutes your dedication to our dark cause! 🫡",
    "🌟 **{mention}** has enhanced our haunted realm! The spirits whisper their gratitude! 👻",
    "🎉 **{mention}** just boosted our server! The Leviathan itself is impressed! 🐙",
]

# ================================
# GAME INFORMATION
# ================================

# Game-related constants for info commands
GAME_INFO = {
    'name': 'Monstrum',
    'developer': 'Lua Vayra Studio',
    'genre': 'Survival Horror',
    'platforms': ['Mobile (iOS/Android)', 'PC (Coming Soon)'],
    'release_date': '2025 (Mobile), TBA (PC)',
    'description': 'A survival horror mobile game featuring terrifying monsters across different maps. Escape, survive, and face your fears on mobile devices.',
    'official_website': 'https://www.monstrumgame.com/',
    'steam_url': 'https://store.steampowered.com/app/296350/Monstrum/',
    'mobile_stores': {
        'ios': 'https://apps.apple.com/app/monstrum-mobile',
        'android': 'https://play.google.com/store/apps/details?id=com.monstrum.mobile'
    }
}

# Monster information for game info commands
MONSTERS = {
    'hutman': {
        'name': 'The Hutman',
        'description': 'A deranged sheriff who chose to remain in Dusty Town and descended into madness.',
        'abilities': ['Armed with a revolver', 'Knowledge of the town layout', 'Unpredictable behavior', 'Quick draw skills'],
        'weakness': 'Limited to Dusty Town area',
        'emoji': '�',
        'map': 'Dusty Town'
    },
    'shaytan': {
        'name': 'Shaytan',
        'description': 'A true demonic entity that has made the Resident map her domain, summoning lesser demons to aid in the hunt.',
        'abilities': ['Summons demons', 'Supernatural presence', 'Reality manipulation', 'Demonic corruption'],
        'weakness': 'Holy or blessed items',
        'emoji': '👹',
        'map': 'Resident'
    }
}

# ================================
# EMBED STYLING
# ================================

# Standard embed colors for different types of messages
EMBED_COLORS = {
    'success': 0x00FF00,
    'error': 0xFF0000,
    'warning': 0xFFFF00,
    'info': 0x00BFFF,
    'default': 0x8B0000,  # Dark red theme
    'boost': 0xFF69B4,
    'welcome': 0x2F4F4F,
    'game_info': 0x4B0082,
}

# Bot footer text
BOT_FOOTER = "Monstrum Bot • Powered by nightmares and caffeine"

# ================================
# DATABASE SETTINGS (for future use)
# ================================

# SQLite database file name
DATABASE_FILE = 'monstrum_bot.db'

# Database tables we'll need
DATABASE_TABLES = [
    'invites',      # Track invite statistics
    'user_stats',   # User activity and stats
    'server_config' # Server-specific configuration
]

# ================================
# FEATURE FLAGS
# ================================

# Enable/disable bot features
FEATURES = {
    'welcome_messages': True,
    'boost_tracking': True,
    'invite_tracking': True,
    'role_selection': True,
    'leaderboard': True,
    'game_info': True,
    'auto_moderation': False,  # For future implementation
    'ticket_system': True,
    'auto_leaderboard': True,
}

# ================================
# LEADERBOARD CONFIGURATION
# ================================

# Leaderboard settings
LEADERBOARD_CONFIG = {
    'auto_update_interval': 900,  # Update every 15 minutes (in seconds)
    'top_users_count': 10,  # Show top 10 users
    'points_per_message': 1,
    'points_per_reaction': 2,
    'points_per_invite': 33,  # Each invite gives +33 points
    'embed_title': '👑 Monstrum Leaderboard - Top Survivors',
    'embed_description': 'The bravest souls who have survived the longest in our cursed realm...',
}

# ================================
# TICKET SYSTEM CONFIGURATION
# ================================

# Ticket system settings
TICKET_CONFIG = {
    'category_name': 'SUPPORT TICKETS',
    'support_roles': ADMIN_ROLES,  # Roles that can view all tickets
    'auto_close_hours': 72,  # Auto-close inactive tickets after 72 hours
    'max_tickets_per_user': 3,  # Maximum open tickets per user
    'embed_color': 0x8B0000,  # Dark red theme
    'server_name': 'Monstrum',
    'log_channel_id': None,  # Will be set via !setup ticketlog command
    'ticket_types': {
        '🎮': {'name': 'Game Support', 'description': 'Issues with gameplay, bugs, or technical problems'},
        '❓': {'name': 'General Help', 'description': 'Questions about the server or community'},
        '⚠️': {'name': 'Report Issue', 'description': 'Report problematic behavior or content'},
        '💡': {'name': 'Suggestions', 'description': 'Suggest new features or improvements'},
        '🛡️': {'name': 'Moderator Help', 'description': 'Need assistance from a moderator'},
    }
}

# ================================
# API ENDPOINTS (for future game data integration)
# ================================

# Steam API endpoints for game data
STEAM_API_BASE = 'https://api.steampowered.com'
STEAM_APP_ID = '296350'  # Monstrum's Steam App ID

# Game news/update sources
NEWS_SOURCES = [
    'https://store.steampowered.com/news/app/296350/',
    'https://twitter.com/TeamJunkfish',
]

# ================================
# LOGGING CONFIGURATION
# ================================

LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = 'bot.log'
MAX_LOG_SIZE = 10 * 1024 * 1024  # 10MB

# ================================
# RATE LIMITING
# ================================

# Cooldowns for commands (in seconds)
COMMAND_COOLDOWNS = {
    'leaderboard': 30,
    'game_info': 10,
    'role_select': 5,
    'ticket_create': 300,  # 5 minutes between ticket creation
}

# ================================
# HELPER FUNCTIONS
# ================================

def get_random_color() -> int:
    """Get a random color from the welcome colors list"""
    import random
    return random.choice(WELCOME_COLORS)

def get_random_welcome_message(mention: str) -> str:
    """Get a random welcome message with the user mention"""
    import random
    message = random.choice(WELCOME_MESSAGES)
    return message.format(mention=mention)

def get_random_boost_message(mention: str) -> str:
    """Get a random boost message with the user mention"""
    import random
    message = random.choice(BOOST_MESSAGES)
    return message.format(mention=mention)

def is_admin(user_roles: List[int]) -> bool:
    """Check if user has admin permissions"""
    return any(role_id in ADMIN_ROLES for role_id in user_roles)

# ================================
# ENVIRONMENT VALIDATION
# ================================

def validate_config():
    """Validate that all required configuration is present"""
    errors = []
    
    # Check if token is still the placeholder
    actual_token = os.getenv('DISCORD_TOKEN', 'YOUR_BOT_TOKEN_HERE')
    if actual_token == 'YOUR_BOT_TOKEN_HERE':
        errors.append("Bot token not configured")
    
    if GUILD_ID == 123456789012345678:
        errors.append("Guild ID not configured")
    
    return errors

# Run validation when module is imported
_validation_errors = validate_config()
if _validation_errors:
    print("⚠️ Configuration warnings:")
    for error in _validation_errors:
        print(f"  - {error}")
    print("Please update config.py with your actual values!")