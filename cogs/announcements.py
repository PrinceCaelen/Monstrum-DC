"""
Announcements Cog for Lua Corporation Discord Bot
Professional announcement system with Umbrella Corporation inspired design

Features:
- Single unified announcement command
- Professional embed formatting
- Image attachment support
- Admin-only access
- Announcement channel protection
- News command with title and message
"""

import discord
from discord.ext import commands
import logging
import config

logger = logging.getLogger(__name__)

class Announcements(commands.Cog):
    """Professional announcement system"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Monitor announcement channel and delete non-command messages"""
        # Ignore bot messages
        if message.author.bot:
            return
        
        # Check if message is in announcements channel
        if message.channel.id == config.ANNOUNCEMENTS_CHANNEL_ID:
            # Check if message is an !announce or !addnews command
            if not message.content.startswith(('!announce', '!addnews')):
                # Delete the message
                try:
                    await message.delete()
                    
                    # Send warning as DM to the user
                    warning_embed = discord.Embed(
                        title="⚠️ Announcement Channel Warning",
                        description=(
                            f"Your message in {message.channel.mention} was deleted.\n\n"
                            "This is an **announcement-only** channel. "
                            "Only messages created with the `!announce` or `!addnews` commands are allowed.\n\n"
                            "**To post an announcement:**\n"
                            "• Use `!announce <message>` for general announcements\n"
                            "• Use `!addnews <title> | <message>` for news updates"
                        ),
                        color=config.EMBED_COLORS['warning']
                    )
                    warning_embed.set_footer(text=config.BOT_FOOTER)
                    
                    # Try to send DM to the user
                    try:
                        await message.author.send(embed=warning_embed)
                    except discord.Forbidden:
                        # If DM fails, send a brief message in channel that auto-deletes
                        temp_msg = await message.channel.send(
                            f"⚠️ {message.author.mention} - Your message was deleted. "
                            "Only `!announce` and `!addnews` commands are allowed here."
                        )
                        await temp_msg.delete(delay=5)
                    
                    logger.info(f"🚫 Deleted unauthorized message from {message.author.name} in announcements channel")
                except discord.Forbidden:
                    logger.error(f"Missing permissions to delete messages in announcements channel")
                except Exception as e:
                    logger.error(f"Error handling announcement channel protection: {e}")
    
    @commands.command(name='announce')
    async def post_announcement(self, ctx, *, message):
        """Post an announcement to the announcements channel
        
        Usage: !announce Your message here
        Note: You can attach images to your message and they will be included!
        """
        
        # Check if user has permission (admin or announcement role)
        has_permission = (
            ctx.author.guild_permissions.administrator or
            any(role.id == config.ANNOUNCEMENT_ROLE_ID for role in ctx.author.roles)
        )
        
        if not has_permission:
            await ctx.send("❌ You don't have permission to post announcements!")
            return
        
        # Get announcements channel
        announcements_channel = self.bot.get_channel(config.ANNOUNCEMENTS_CHANNEL_ID)
        if not announcements_channel:
            await ctx.send("❌ Announcements channel not configured!")
            return
        
        embed = discord.Embed(
            title=f"📢 {config.COMPANY_NAME} Announcement",
            description=message,
            color=config.EMBED_COLORS['info']
        )
        
        if ctx.guild.icon:
            embed.set_author(
                name=f"{config.COMPANY_NAME}",
                icon_url=ctx.guild.icon.url
            )
        
        embed.set_footer(
            text=f"Posted by {ctx.author.display_name} • {config.BOT_FOOTER}"
        )
        embed.timestamp = discord.utils.utcnow()
        
        # Check for image attachments and add to embed
        if ctx.message.attachments:
            for attachment in ctx.message.attachments:
                if any(attachment.filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']):
                    embed.set_image(url=attachment.url)
                    break  # Only use the first image
        
        await announcements_channel.send(embed=embed)
        await ctx.send(f"✅ Announcement posted to {announcements_channel.mention}")
        logger.info(f"📢 {ctx.author.name} posted announcement: {message[:50]}...")
    
    @commands.command(name='addnews')
    async def add_news(self, ctx, *, content):
        """Post a news update with a custom title and message
        
        Usage: !addnews Title Here | Message content here
        Example: !addnews Server Update | We've added new features!
        """
        
        # Check if user has permission (admin or announcement role)
        has_permission = (
            ctx.author.guild_permissions.administrator or
            any(role.id == config.ANNOUNCEMENT_ROLE_ID for role in ctx.author.roles)
        )
        
        if not has_permission:
            await ctx.send("❌ You don't have permission to post announcements!")
            return
        
        # Check if content has the pipe separator
        if '|' not in content:
            await ctx.send("❌ **Invalid format!** Use: `!addnews <title> | <message>`\nExample: `!addnews Server Update | We've added new features!`")
            return
        
        # Split title and message
        parts = content.split('|', 1)
        title = parts[0].strip()
        message = parts[1].strip()
        
        if not title or not message:
            await ctx.send("❌ **Error:** Both title and message are required!")
            return
        
        # Get announcements channel
        announcements_channel = self.bot.get_channel(config.ANNOUNCEMENTS_CHANNEL_ID)
        if not announcements_channel:
            await ctx.send("❌ Announcements channel not configured!")
            return
        
        # Create news embed
        embed = discord.Embed(
            title=f"📰 {title}",
            description=message,
            color=config.EMBED_COLORS['info']
        )
        
        if ctx.guild.icon:
            embed.set_author(
                name=f"{config.COMPANY_NAME} News",
                icon_url=ctx.guild.icon.url
            )
        
        embed.set_footer(
            text=f"Posted by {ctx.author.display_name} • {config.BOT_FOOTER}"
        )
        embed.timestamp = discord.utils.utcnow()
        
        # Check for image attachments
        if ctx.message.attachments:
            for attachment in ctx.message.attachments:
                if any(attachment.filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']):
                    embed.set_image(url=attachment.url)
                    break
        
        # Post to announcements channel
        await announcements_channel.send(embed=embed)
        await ctx.send(f"✅ News posted to {announcements_channel.mention}")
        logger.info(f"📰 {ctx.author.name} posted news: {title}")
    
    @commands.command(name='setannounce')
    @commands.has_permissions(administrator=True)
    async def set_announce_channel(self, ctx, channel: discord.TextChannel = None):
        """Set the announcement channel for the bot
        
        Usage: !setannounce #channel-name
        Example: !setannounce #announcements
        """
        
        if channel is None:
            await ctx.send("❌ **Error:** Please mention a channel!\n**Usage:** `!setannounce #channel-name`")
            return
        
        # Update the config file
        try:
            with open('config.py', 'r', encoding='utf-8') as f:
                config_content = f.read()
            
            # Replace the ANNOUNCEMENTS_CHANNEL_ID value
            import re
            pattern = r"ANNOUNCEMENTS_CHANNEL_ID = int\(os\.getenv\('ANNOUNCEMENTS_CHANNEL_ID', '\d+'\)\)"
            replacement = f"ANNOUNCEMENTS_CHANNEL_ID = int(os.getenv('ANNOUNCEMENTS_CHANNEL_ID', '{channel.id}'))"
            
            new_content = re.sub(pattern, replacement, config_content)
            
            with open('config.py', 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            # Update the config module in memory
            config.ANNOUNCEMENTS_CHANNEL_ID = channel.id
            
            # Send confirmation
            embed = discord.Embed(
                title="✅ Announcement Channel Updated",
                description=f"The announcement channel has been set to {channel.mention}\n\n"
                           f"**Channel Protection Active:**\n"
                           f"• Only `!announce` and `!addnews` commands allowed\n"
                           f"• Other messages will be automatically deleted\n"
                           f"• Users will receive a warning",
                color=config.EMBED_COLORS['success']
            )
            embed.set_footer(text=config.BOT_FOOTER)
            
            await ctx.send(embed=embed)
            logger.info(f"📢 Announcement channel set to {channel.name} (ID: {channel.id}) by {ctx.author.name}")
            
        except Exception as e:
            await ctx.send(f"❌ **Error updating config:** {e}")
            logger.error(f"Error setting announcement channel: {e}")

async def setup(bot):
    """Setup function for the cog"""
    await bot.add_cog(Announcements(bot))
    logger.info("✅ Announcements cog loaded successfully")