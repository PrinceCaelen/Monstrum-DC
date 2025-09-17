"""
Monstrum Discord Bot - Main Entry Point
A professional Discord bot for the horror game community

Author: Discord Bot Assistant
Version: 1.0.0
"""

import discord
from discord.ext import commands
import asyncio
import logging
import os
from pathlib import Path
import config

# Configure logging with UTF-8 encoding support
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class MonstrumBot(commands.Bot):
    """Custom bot class for the Monstrum community"""
    
    def __init__(self):
        # Define intents
        intents = discord.Intents.default()
        # Note: The following intents require approval in Discord Developer Portal
        # intents.members = True  # Required for welcome messages and invite tracking  
        # intents.invites = True  # Required for invite tracking
        intents.message_content = True  # Required for message commands
        
        super().__init__(
            command_prefix=config.PREFIX,
            intents=intents,
            help_command=None,  # We'll create a custom help command
            case_insensitive=True,
            description="A horror-themed Discord bot for the Monstrum community 🎃"
        )
        
        # Store invite cache for tracking (will be empty without invite intent)
        self.invite_cache = {}
        
    async def setup_hook(self):
        """Called when the bot is starting up"""
        logger.info("🎃 Monstrum Bot is awakening from the shadows...")
        
        # Load all cogs
        await self.load_cogs()
        
        # Sync slash commands
        try:
            synced = await self.tree.sync()
            logger.info(f"✅ Synced {len(synced)} slash command(s)")
        except Exception as e:
            logger.error(f"❌ Failed to sync commands: {e}")
    
    async def load_cogs(self):
        """Load all cog files from the cogs directory"""
        cogs_dir = Path(__file__).parent / "cogs"
        
        if not cogs_dir.exists():
            logger.warning("❌ Cogs directory not found!")
            return
        
        # Load each Python file in the cogs directory
        for cog_file in cogs_dir.glob("*.py"):
            if cog_file.name.startswith("__"):
                continue
                
            cog_name = f"cogs.{cog_file.stem}"
            try:
                await self.load_extension(cog_name)
                logger.info(f"✅ Loaded cog: {cog_name}")
            except Exception as e:
                logger.error(f"❌ Failed to load cog {cog_name}: {e}")
    
    async def on_ready(self):
        """Called when the bot is ready and connected"""
        logger.info(f"👻 {self.user} has risen from the depths!")
        logger.info(f"🏰 Connected to {len(self.guilds)} server(s)")
        logger.info(f"👥 Watching over {len(self.users)} souls")
        
        # Set bot status
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name="for new victims in Monstrum 🦑"
        )
        await self.change_presence(activity=activity)
        
        # Cache invites for all guilds
        await self.cache_invites()
    
    async def cache_invites(self):
        """Cache current invites for invite tracking"""
        for guild in self.guilds:
            try:
                invites = await guild.invites()
                self.invite_cache[guild.id] = {invite.code: invite.uses for invite in invites}
                logger.info(f"📨 Cached {len(invites)} invites for {guild.name}")
            except discord.Forbidden:
                logger.warning(f"❌ No permission to view invites in {guild.name} (invite intent disabled)")
                self.invite_cache[guild.id] = {}
            except Exception as e:
                logger.error(f"❌ Error caching invites for {guild.name}: {e}")
                self.invite_cache[guild.id] = {}
    
    async def on_command_error(self, ctx, error):
        """Global error handler"""
        if isinstance(error, commands.CommandNotFound):
            return  # Ignore unknown commands
        
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                title="🚫 Forbidden Ritual",
                description="You lack the dark powers required for this command!",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
                title="📜 Incomplete Incantation",
                description=f"Missing required argument: `{error.param.name}`",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed)
            return
        
        # Log unexpected errors
        logger.error(f"Unexpected error in {ctx.command}: {error}")
        
        embed = discord.Embed(
            title="💀 Something Went Wrong",
            description="The spirits are restless. Try again later...",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

async def main():
    """Main function to run the bot"""
    # Check if token is provided
    if not config.TOKEN:
        logger.error("❌ No bot token provided! Please set TOKEN in config.py")
        return
    
    # Create and run the bot
    bot = MonstrumBot()
    
    try:
        async with bot:
            await bot.start(config.TOKEN)
    except discord.LoginFailure:
        logger.error("❌ Invalid bot token!")
    except KeyboardInterrupt:
        logger.info("👋 Bot shutdown requested")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
    finally:
        logger.info("💀 Monstrum Bot has returned to the shadows...")

if __name__ == "__main__":
    # Fix for Windows event loop issue with discord.py and aiodns
    if os.name == 'nt':  # Windows
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    # Run the bot
    asyncio.run(main())
