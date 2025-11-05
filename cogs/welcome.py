"""
Welcome System Cog for Lua Corporation Discord Bot
Handles new member welcomes and server boost thank you messages

Features:
- Professional corporate welcome messages
- Rich Discord embeds with corporate theming
- Server boost detection and thank you messages
- Member count tracking
"""

import discord
from discord.ext import commands
import random
import logging
import config

logger = logging.getLogger(__name__)

class Welcome(commands.Cog):
    """Welcome system for new members and server boosters"""
    
    def __init__(self, bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Handle new member joins"""
        try:
            # Get the welcome channel
            welcome_channel = self.bot.get_channel(config.WELCOME_CHANNEL_ID)
            if not welcome_channel:
                logger.warning(f"Welcome channel not found for guild {member.guild.name}")
                return
            
            # Auto-assign role to new member
            await self.assign_auto_role(member)
            
            # Create welcome embed
            embed = await self.create_welcome_embed(member)
            
            # Send welcome message
            await welcome_channel.send(embed=embed)
            logger.info(f"👋 Welcomed new member {member.name} in {member.guild.name}")
            
        except Exception as e:
            logger.error(f"Error in welcome message for {member.name}: {e}")
    
    async def assign_auto_role(self, member):
        """Automatically assign role to new members"""
        try:
            # Get the auto-assign role
            auto_role = member.guild.get_role(config.AUTO_ROLE_ID)
            if not auto_role:
                logger.warning(f"Auto-assign role {config.AUTO_ROLE_ID} not found in {member.guild.name}")
                return
            
            # Check if bot has permission to assign roles
            if not member.guild.me.guild_permissions.manage_roles:
                logger.error(f"Bot lacks 'Manage Roles' permission in {member.guild.name}")
                return
            
            # Check if the auto role is below bot's highest role
            if auto_role.position >= member.guild.me.top_role.position:
                logger.error(f"Auto-assign role {auto_role.name} is too high in hierarchy in {member.guild.name}")
                return
            
            # Assign the role
            await member.add_roles(auto_role, reason="Auto-assigned role for new member")
            logger.info(f"✅ Assigned role '{auto_role.name}' to new member {member.name}")
            
        except discord.Forbidden:
            logger.error(f"Bot lacks permission to assign role to {member.name}")
        except discord.HTTPException as e:
            logger.error(f"HTTP error while assigning role to {member.name}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error assigning role to {member.name}: {e}")
    
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        """Handle member updates (including server boosts)"""
        try:
            # Check if member started boosting
            if not before.premium_since and after.premium_since:
                await self.handle_server_boost(after)
                
        except Exception as e:
            logger.error(f"Error handling member update for {after.name}: {e}")
    
    async def create_welcome_embed(self, member):
        """Create a professional welcome embed"""
        # Get random welcome message and color
        welcome_message = config.get_random_welcome_message(member.mention)
        embed_color = config.get_random_color()
        
        # Create embed
        embed = discord.Embed(
            title=f"⚡ {config.COMPANY_NAME} - New Member",
            description=welcome_message,
            color=embed_color
        )
        
        # Add member avatar
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        
        # Add member info
        embed.add_field(
            name="🆔 User ID", 
            value=f"`{member.id}`", 
            inline=True
        )
        embed.add_field(
            name="📅 Account Created", 
            value=discord.utils.format_dt(member.created_at, style='R'), 
            inline=True
        )
        embed.add_field(
            name="👥 Total Members", 
            value=f"`{member.guild.member_count}`", 
            inline=True
        )
        
        # Add professional footer
        embed.set_footer(
            text=config.BOT_FOOTER,
            icon_url=member.guild.icon.url if member.guild.icon else None
        )
        
        # Add timestamp
        embed.timestamp = discord.utils.utcnow()
        
        return embed
    
    async def handle_server_boost(self, member):
        """Handle server boost thank you message"""
        try:
            # Get boost channel (fallback to welcome channel)
            boost_channel = (self.bot.get_channel(config.BOOST_CHANNEL_ID) or 
                           self.bot.get_channel(config.WELCOME_CHANNEL_ID))
            
            if not boost_channel:
                logger.warning(f"No boost/welcome channel found for guild {member.guild.name}")
                return
            
            # Create boost thank you embed
            embed = await self.create_boost_embed(member)
            
            # Send boost message
            await boost_channel.send(embed=embed)
            logger.info(f"🚀 Thanked {member.name} for boosting {member.guild.name}")
            
        except Exception as e:
            logger.error(f"Error in boost thank you for {member.name}: {e}")
    
    async def create_boost_embed(self, member):
        """Create a boost thank you embed"""
        # Get random boost message
        boost_message = config.get_random_boost_message(member.mention)
        
        # Create embed with boost theme
        embed = discord.Embed(
            title="🚀 Server Boost Detected!",
            description=boost_message,
            color=config.EMBED_COLORS['boost']
        )
        
        # Add booster avatar
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        
        # Add boost info
        embed.add_field(
            name="⚡ Boost Level", 
            value=f"Level {member.guild.premium_tier}", 
            inline=True
        )
        embed.add_field(
            name="💎 Total Boosts", 
            value=f"{member.guild.premium_subscription_count} boosts", 
            inline=True
        )
        embed.add_field(
            name="🌟 Your Contribution", 
            value="Powering our excellence!", 
            inline=True
        )
        
        # Add special boost perks message
        perks = [
            "🔊 Enhanced audio quality",
            "📁 Larger file uploads", 
            "🎨 Custom server banner",
            "📺 Higher quality streams",
            "💜 Our eternal gratitude"
        ]
        
        embed.add_field(
            name="🎁 Boost Perks Active",
            value="\n".join(perks[:member.guild.premium_tier + 2]),
            inline=False
        )
        
        # Add footer
        embed.set_footer(
            text=f"Thank you for supporting {member.guild.name}!",
            icon_url=member.guild.icon.url if member.guild.icon else None
        )
        
        # Add timestamp
        embed.timestamp = discord.utils.utcnow()
        
        return embed
    
    @commands.command(name='testwelcome', hidden=True)
    @commands.has_permissions(administrator=True)
    async def test_welcome(self, ctx, member: discord.Member = None):
        """Test the welcome message (Admin only)"""
        if member is None:
            member = ctx.author
            
        embed = await self.create_welcome_embed(member)
        await ctx.send("🧪 **Testing welcome message:**", embed=embed)
    
    @commands.command(name='testboost', hidden=True)
    @commands.has_permissions(administrator=True)
    async def test_boost(self, ctx, member: discord.Member = None):
        """Test the boost message (Admin only)"""
        if member is None:
            member = ctx.author
            
        embed = await self.create_boost_embed(member)
        await ctx.send("🧪 **Testing boost message:**", embed=embed)
    
    @commands.command(name='testrole', hidden=True)
    @commands.has_permissions(administrator=True)
    async def test_auto_role(self, ctx, member: discord.Member = None):
        """Test the auto-role assignment (Admin only)"""
        if member is None:
            member = ctx.author
        
        # Test role assignment
        await self.assign_auto_role(member)
        
        # Get the role name for confirmation
        auto_role = member.guild.get_role(config.AUTO_ROLE_ID)
        role_name = auto_role.name if auto_role else "Unknown Role"
        
        await ctx.send(f"🧪 **Testing auto-role assignment:** Attempted to assign `{role_name}` to {member.mention}")
    
    # @commands.slash_command(name="welcome", description="Test the welcome system")
    # @commands.has_permissions(administrator=True)
    # async def slash_welcome_test(self, ctx, member: discord.Member = None):
    #     """Test welcome message with slash command"""
    #     if member is None:
    #         member = ctx.author
    #         
    #     embed = await self.create_welcome_embed(member)
    #     await ctx.respond("🧪 **Testing welcome message:**", embed=embed, ephemeral=True)
    
    @commands.command(name='assignrole')
    @commands.has_permissions(administrator=True)
    async def manual_assign_role(self, ctx, member: discord.Member = None):
        """Manually assign the auto-role to a member (Admin only)"""
        if member is None:
            await ctx.send("❌ **Error:** Please mention a member to assign the role to.\n**Usage:** `!assignrole @member`")
            return
        
        # Get the auto-assign role
        auto_role = ctx.guild.get_role(config.AUTO_ROLE_ID)
        if not auto_role:
            await ctx.send(f"❌ **Error:** Auto-assign role (ID: {config.AUTO_ROLE_ID}) not found in this server.")
            return
        
        # Check if member already has the role
        if auto_role in member.roles:
            await ctx.send(f"ℹ️ **Info:** {member.mention} already has the `{auto_role.name}` role.")
            return
        
        # Assign the role
        try:
            await member.add_roles(auto_role, reason=f"Manual assignment by {ctx.author}")
            await ctx.send(f"✅ **Success:** Assigned `{auto_role.name}` role to {member.mention}")
            logger.info(f"👤 Manually assigned role '{auto_role.name}' to {member.name} by {ctx.author.name}")
        except discord.Forbidden:
            await ctx.send("❌ **Error:** I don't have permission to assign roles to this member.")
        except discord.HTTPException as e:
            await ctx.send(f"❌ **Error:** Failed to assign role: {e}")
    
    @commands.command(name='welcomestats')
    @commands.cooldown(1, 30, commands.BucketType.guild)
    async def welcome_stats(self, ctx):
        """Show server welcome statistics"""
        guild = ctx.guild
        
        embed = discord.Embed(
            title="📊 Server Statistics",
            description="Current server overview",
            color=config.EMBED_COLORS['info']
        )
        
        # Basic stats
        embed.add_field(
            name="👥 Total Members", 
            value=f"`{guild.member_count}`", 
            inline=True
        )
        embed.add_field(
            name="🤖 Bots", 
            value=f"`{len([m for m in guild.members if m.bot])}`", 
            inline=True
        )
        embed.add_field(
            name="👤 Humans", 
            value=f"`{len([m for m in guild.members if not m.bot])}`", 
            inline=True
        )
        
        # Boost stats
        embed.add_field(
            name="🚀 Boost Level", 
            value=f"Level {guild.premium_tier}", 
            inline=True
        )
        embed.add_field(
            name="💎 Boosts", 
            value=f"`{guild.premium_subscription_count}`", 
            inline=True
        )
        embed.add_field(
            name="⭐ Boosters", 
            value=f"`{len(guild.premium_subscribers)}`", 
            inline=True
        )
        
        # Server info
        embed.add_field(
            name="📅 Server Created", 
            value=discord.utils.format_dt(guild.created_at, style='F'), 
            inline=False
        )
        
        # Set server icon
        embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
        embed.set_footer(text=config.BOT_FOOTER)
        embed.timestamp = discord.utils.utcnow()
        
        await ctx.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        """Handle bot joining a new guild"""
        logger.info(f"🏰 Joined new guild: {guild.name} ({guild.id})")
        
        # Try to find a general channel to send a greeting
        general_channels = [
            discord.utils.get(guild.text_channels, name='general'),
            discord.utils.get(guild.text_channels, name='welcome'),
            discord.utils.get(guild.text_channels, name='bot-commands'),
            guild.system_channel,
        ]
        
        for channel in general_channels:
            if channel and channel.permissions_for(guild.me).send_messages:
                embed = discord.Embed(
                    title=f"⚡ {config.COMPANY_NAME} Bot Online",
                    description=(
                        f"Thank you for adding **{config.COMPANY_NAME} Bot** to your server.\n\n"
                        "**� Bot Capabilities:**\n"
                        "• Professional welcome system for new members\n"
                        "• Server boost recognition\n"
                        "• Invite tracking and statistics\n"
                        "• Role management system\n"
                        "• Professional support ticket system\n\n"
                        "**⚙️ Setup Required:**\n"
                        "Please configure the bot by updating the channel IDs in `config.py` "
                        "to match your server's channels.\n\n"
                        "Use `!help` to see all available commands."
                    ),
                    color=config.EMBED_COLORS['welcome']
                )
                embed.set_footer(text=config.BOT_FOOTER)
                await channel.send(embed=embed)
                break

async def setup(bot):
    """Setup function for the cog"""
    await bot.add_cog(Welcome(bot))
    logger.info("✅ Welcome cog loaded successfully")