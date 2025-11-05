import os
from typing import List, Dict

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# ================================
# BOT CONFIGURATION
# ================================

# Bot Token (NEVER commit the actual token to GitHub!)
TOKEN = os.getenv('DISCORD_TOKEN')

# Command Prefix
PREFIX = '!'

# Bot Owner ID (Replace with your Discord user ID)
OWNER_ID = int(os.getenv('OWNER_ID', '1400112309766062181'))

# ================================
# BRANDING CONFIGURATION
# ================================

# Company/Studio Name
COMPANY_NAME = "Lua Corporation"
COMPANY_TAGLINE = "Excellence Through Innovation"
BOT_NAME = "Lua Corporation Bot"

# Visual Theme (Umbrella Corporation inspired - Professional, Dark, Corporate)
THEME_COLORS = {
    'primary': 0x000000,      # Black
    'secondary': 0x8B0000,    # Dark Red
    'accent': 0xFFFFFF,       # White
    'success': 0x00FF00,      # Green
    'warning': 0xFFAA00,      # Amber
    'error': 0xFF0000,        # Red
    'info': 0x1E90FF,         # Dodger Blue
}

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

# Role IDs for auto-assignment
ROLE_SELECTION_ROLES = {
    '🎮': int(os.getenv('MEMBER_ROLE_ID', '1417471815147589642')),  # Member role
}

# Auto-assign role to new members (Member role)
AUTO_ROLE_ID = int(os.getenv('AUTO_ROLE_ID', '1417470579774197800'))  # Role given to all new members automatically

# Admin/Moderator role IDs
ADMIN_ROLES = [
    int(os.getenv('ADMIN_ROLE_ID', '1417464869183291422')),
    int(os.getenv('MODERATOR_ROLE_ID', '1417465338278318100')),
]

# Announcement role - users with this role can post announcements
ANNOUNCEMENT_ROLE_ID = int(os.getenv('ANNOUNCEMENT_ROLE_ID', '1435285314129231964'))

# ================================
# WELCOME MESSAGES
# ================================

# Professional welcome messages for new members (Umbrella Corporation inspired)
WELCOME_MESSAGES = [
    "⚡ **{mention}** has joined {company}. Access granted.",
    "🏢 **{mention}** has been cleared for entry to {company}. Welcome.",
    "🔬 **{mention}** has been registered in our database. Welcome to {company}.",
    "⚙️ **{mention}** has entered the facility. Welcome to {company}.",
    "🎯 **{mention}** has been assigned clearance level: Member. Welcome.",
    "💼 **{mention}** has joined {company}. Excellence is our standard.",
    "🛡️ **{mention}** has accessed the network. Systems updated.",
    "📊 **{mention}** has been added to the roster. Welcome to {company}.",
    "🔐 **{mention}** - Identity verified. Access to {company} granted.",
    "⚗️ **{mention}** has joined our operations. Welcome to the corporation.",
]

# ================================
# BOOST MESSAGES
# ================================

BOOST_MESSAGES = [
    "⚡ **{mention}** has upgraded our server capabilities. {company} thanks you for your contribution.",
    "🚀 **{mention}** has enhanced our systems. Your support strengthens our operations.",
    "💎 **{mention}** has invested in our infrastructure. {company} recognizes your dedication.",
    "🌟 **{mention}** has boosted our server. Excellence rewarded with excellence.",
    "🎉 **{mention}** has amplified our reach. Your contribution is valued.",
]

# ================================
# EMBED STYLING
# ================================

# Standard embed colors for different types of messages (Umbrella Corporation theme)
EMBED_COLORS = {
    'success': THEME_COLORS['success'],
    'error': THEME_COLORS['error'],
    'warning': THEME_COLORS['warning'],
    'info': THEME_COLORS['info'],
    'default': THEME_COLORS['primary'],
    'boost': THEME_COLORS['secondary'],
    'welcome': THEME_COLORS['primary'],
}

# Bot footer text
BOT_FOOTER = f"{COMPANY_NAME} • {COMPANY_TAGLINE}"

# ================================
# DATABASE SETTINGS (for future use)
# ================================

# SQLite database file name
DATABASE_FILE = 'lua_corporation_bot.db'

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
    'auto_moderation': False,  # For future implementation
    'ticket_system': True,
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
    'embed_color': THEME_COLORS['primary'],  # Professional black theme
    'server_name': COMPANY_NAME,
    'log_channel_id': None,  # Will be set via !setup ticketlog command
    'ticket_types': {
        '❓': {'name': 'General Support', 'description': 'Questions about the server or community'},
        '⚠️': {'name': 'Report Issue', 'description': 'Report problematic behavior or content'},
        '💡': {'name': 'Suggestions', 'description': 'Suggest new features or improvements'},
        '👨‍💼': {'name': 'Admin Contact', 'description': 'Direct contact with administration'},
    }
}

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
    'role_select': 5,
    'ticket_create': 300,  # 5 minutes between ticket creation
}

# ================================
# HELPER FUNCTIONS
# ================================

def get_random_color() -> int:
    """Get a random color from the theme colors"""
    import random
    colors = [THEME_COLORS['primary'], THEME_COLORS['secondary'], THEME_COLORS['info']]
    return random.choice(colors)

def get_random_welcome_message(mention: str, company: str = COMPANY_NAME) -> str:
    """Get a random welcome message with the user mention"""
    import random
    message = random.choice(WELCOME_MESSAGES)
    return message.format(mention=mention, company=company)

def get_random_boost_message(mention: str, company: str = COMPANY_NAME) -> str:
    """Get a random boost message with the user mention"""
    import random
    message = random.choice(BOOST_MESSAGES)
    return message.format(mention=mention, company=company)

def is_admin(user_roles: List[int]) -> bool:
    """Check if user has admin permissions"""
    return any(role_id in ADMIN_ROLES for role_id in user_roles)