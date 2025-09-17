"""
Announcements Cog for Monstrum Discord Bot
Handle game updates, news, and server announcements

Features:
- Post game updates with version numbers
- Post general announcements
- Post game news and development updates
- All posts go to configured announcements channel
"""

import discord
from discord.ext import commands
import logging
import config

logger = logging.getLogger(__name__)

class Announcements(commands.Cog):
    """Announcement and update posting system"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='announce', aliases=['announcement'])
    @commands.has_permissions(administrator=True)
    async def post_announcement(self, ctx, *, message):
        """Post an announcement to the announcements channel"""
        
        # Get announcements channel
        announcements_channel = self.bot.get_channel(config.ANNOUNCEMENTS_CHANNEL_ID)
        if not announcements_channel:
            await ctx.send("❌ Announcements channel not configured!")
            return
        
        embed = discord.Embed(
            title="📢 Server Announcement",
            description=message,
            color=config.EMBED_COLORS['info']
        )
        
        if ctx.guild.icon:
            embed.set_author(name=f"{ctx.guild.name} Announcement", icon_url=ctx.guild.icon.url)
        
        embed.set_footer(text=f"Posted by {ctx.author.display_name}")
        embed.timestamp = discord.utils.utcnow()
        
        await announcements_channel.send(embed=embed)
        await ctx.send(f"✅ Announcement posted to {announcements_channel.mention}")
        logger.info(f"📢 {ctx.author.name} posted announcement: {message[:50]}...")
    
    @commands.command(name='gameupdate', aliases=['update'])
    @commands.has_permissions(administrator=True)
    async def post_game_update(self, ctx, version, *, changes):
        """Post a game update to the announcements channel
        
        Usage: !gameupdate v1.2.3 Fixed monster AI bug\nAdded new map\nImproved performance
        """
        
        # Get announcements channel
        announcements_channel = self.bot.get_channel(config.ANNOUNCEMENTS_CHANNEL_ID)
        if not announcements_channel:
            await ctx.send("❌ Announcements channel not configured!")
            return
        
        embed = discord.Embed(
            title=f"🎮 Monstrum Update {version}",
            description="A new update has been released!",
            color=config.EMBED_COLORS['game_info']
        )
        
        if ctx.guild.icon:
            embed.set_author(name="Monstrum Development Team", icon_url=ctx.guild.icon.url)
        
        # Format changes
        changes_formatted = ""
        for line in changes.split('\n'):
            line = line.strip()
            if line:
                if not line.startswith('•') and not line.startswith('-') and not line.startswith('*'):
                    changes_formatted += f"• {line}\n"
                else:
                    changes_formatted += f"{line}\n"
        
        embed.add_field(
            name=f"📝 What's New in {version}",
            value=changes_formatted or changes,
            inline=False
        )
        
        embed.add_field(
            name="🔄 How to Update",
            value=(
                "📱 **Mobile:** Update through your app store\n"
                "💻 **PC:** Restart Steam for automatic update\n"
                "🎮 **Console:** Check for updates in your system"
            ),
            inline=False
        )
        
        embed.set_footer(text=f"Update posted by {ctx.author.display_name}")
        embed.timestamp = discord.utils.utcnow()
        
        await announcements_channel.send(embed=embed)
        await ctx.send(f"✅ Game update {version} posted to {announcements_channel.mention}")
        logger.info(f"🎮 {ctx.author.name} posted game update {version}")
    
    @commands.command(name='gamenews', aliases=['news'])
    @commands.has_permissions(administrator=True)
    async def post_game_news(self, ctx, *, content):
        """Post game news to the announcements channel
        
        Usage: !gamenews New Monster Revealed\nWe're excited to announce a new terrifying creature...
        """
        
        # Parse title and content
        lines = content.split('\n', 1)
        if len(lines) == 1:
            title = "🗞️ Monstrum News"
            news_content = lines[0]
        else:
            title = f"🗞️ {lines[0].strip()}"
            news_content = lines[1].strip()
        
        # Get announcements channel
        announcements_channel = self.bot.get_channel(config.ANNOUNCEMENTS_CHANNEL_ID)
        if not announcements_channel:
            await ctx.send("❌ Announcements channel not configured!")
            return
        
        embed = discord.Embed(
            title=title,
            description=news_content,
            color=config.EMBED_COLORS['game_info']
        )
        
        if ctx.guild.icon:
            embed.set_author(name="Monstrum Community", icon_url=ctx.guild.icon.url)
        
        embed.set_footer(text=f"News posted by {ctx.author.display_name}")
        embed.timestamp = discord.utils.utcnow()
        
        await announcements_channel.send(embed=embed)
        await ctx.send(f"✅ Game news posted to {announcements_channel.mention}")
        logger.info(f"🗞️ {ctx.author.name} posted game news: {title}")
    
    @commands.command(name='hotfix', aliases=['patch'])
    @commands.has_permissions(administrator=True)
    async def post_hotfix(self, ctx, version, *, fixes):
        """Post a hotfix/patch announcement
        
        Usage: !hotfix v1.2.3a Fixed critical bug\nResolved crash issue
        """
        
        # Get announcements channel
        announcements_channel = self.bot.get_channel(config.ANNOUNCEMENTS_CHANNEL_ID)
        if not announcements_channel:
            await ctx.send("❌ Announcements channel not configured!")
            return
        
        embed = discord.Embed(
            title=f"🔧 Hotfix {version} Released",
            description="A critical hotfix has been deployed!",
            color=config.EMBED_COLORS['warning']
        )
        
        if ctx.guild.icon:
            embed.set_author(name="Monstrum Development Team", icon_url=ctx.guild.icon.url)
        
        # Format fixes
        fixes_formatted = ""
        for line in fixes.split('\n'):
            line = line.strip()
            if line:
                if not line.startswith('•') and not line.startswith('-') and not line.startswith('*'):
                    fixes_formatted += f"🔧 {line}\n"
                else:
                    fixes_formatted += f"{line}\n"
        
        embed.add_field(
            name=f"🛠️ Fixes in {version}",
            value=fixes_formatted or fixes,
            inline=False
        )
        
        embed.add_field(
            name="⚡ Apply Update",
            value=(
                "This hotfix will be applied automatically.\n"
                "Restart your game to ensure all fixes are loaded."
            ),
            inline=False
        )
        
        embed.set_footer(text=f"Hotfix posted by {ctx.author.display_name}")
        embed.timestamp = discord.utils.utcnow()
        
        await announcements_channel.send(embed=embed)
        await ctx.send(f"✅ Hotfix {version} posted to {announcements_channel.mention}")
        logger.info(f"🔧 {ctx.author.name} posted hotfix {version}")

async def setup(bot):
    """Setup function for the cog"""
    await bot.add_cog(Announcements(bot))
    logger.info("✅ Announcements cog loaded successfully")