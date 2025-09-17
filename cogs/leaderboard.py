"""
Leaderboard Cog for Monstrum Discord Bot
Clean, streamlined invite leaderboard with auto-posting

Features:
- Invite tracking and scoring (+33 points per invite)
- Auto-update leaderboard every 15 minutes
- Single message editing (no duplicates)
- Admin commands for setup and moderation
"""

import discord
from discord.ext import commands, tasks
import json
import os
import logging
from datetime import datetime
import config

logger = logging.getLogger(__name__)

class Leaderboard(commands.Cog):
    """Invite leaderboard system"""
    
    def __init__(self, bot):
        self.bot = bot
        self.invite_data_file = 'invite_data.json'
        self.leaderboard_message_id = None  # Store the message ID to edit
        
        # Start auto-posting
        if config.FEATURES.get('auto_leaderboard', True):
            self.auto_post_leaderboard.start()
    
    def cog_unload(self):
        """Clean up when cog is unloaded"""
        self.auto_post_leaderboard.cancel()
    
    def load_invite_data(self):
        """Load invite statistics from JSON file"""
        try:
            if os.path.exists(self.invite_data_file):
                with open(self.invite_data_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Error loading invite data: {e}")
            return {}
    
    def get_leaderboard_data(self, guild_id, sort_by='total'):
        """Get sorted leaderboard data with points calculation"""
        invite_data = self.load_invite_data()
        guild_str = str(guild_id)
        
        if guild_str not in invite_data:
            return []
        
        leaderboard = []
        for user_id, stats in invite_data[guild_str].items():
            # Calculate points (33 per invite)
            total_points = stats['total_invites'] * 33
            current_points = stats['current_invites'] * 33
            retention_rate = (stats['current_invites'] / stats['total_invites'] * 100) if stats['total_invites'] > 0 else 0
            
            leaderboard.append({
                'user_id': int(user_id),
                'total_invites': stats['total_invites'],
                'current_invites': stats['current_invites'],
                'left_members': stats['left_members'],
                'fake_invites': stats['fake_invites'],
                'total_points': total_points,
                'current_points': current_points,
                'retention_rate': retention_rate
            })
        
        # Sort by total invites (default)
        leaderboard.sort(key=lambda x: x['total_invites'], reverse=True)
        return leaderboard
    
    def get_rank_emoji(self, position):
        """Get emoji for leaderboard position"""
        if position == 1:
            return "🥇"
        elif position == 2:
            return "🥈"
        elif position == 3:
            return "🥉"
        elif position <= 10:
            return "🏆"
        else:
            return "📊"
    
    def get_recruitment_rank(self, total_invites):
        """Get horror-themed rank based on invite count"""
        if total_invites >= 100:
            return "🦑 Leviathan Summoner"
        elif total_invites >= 50:
            return "👹 Demon Recruiter"
        elif total_invites >= 25:
            return "🕷️ Spider's Web Master"
        elif total_invites >= 10:
            return "👻 Ghost Whisperer"
        elif total_invites >= 5:
            return "🧟 Zombie Herder"
        elif total_invites >= 1:
            return "🎃 Novice Cultist"
        else:
            return "💀 Fresh Recruit"
    
    async def create_leaderboard_embed(self, guild):
        """Create the leaderboard embed"""
        leaderboard_data = self.get_leaderboard_data(guild.id)
        
        if not leaderboard_data:
            return None
        
        # Get top 10 users
        top_users = leaderboard_data[:10]
        
        embed = discord.Embed(
            title="👑 Monstrum Leaderboard - Top Survivors",
            description="The bravest souls who have recruited the most victims...",
            color=config.EMBED_COLORS['info']
        )
        
        # Add server branding
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
            embed.set_author(name=f"{guild.name} Community", icon_url=guild.icon.url)
        
        # Add leaderboard entries
        leaderboard_text = ""
        for i, user_data in enumerate(top_users, 1):
            try:
                user = self.bot.get_user(user_data['user_id'])
                if not user:
                    user = await self.bot.fetch_user(user_data['user_id'])
                
                rank_emoji = self.get_rank_emoji(i)
                username = user.display_name if user else f"User {user_data['user_id']}"
                
                leaderboard_text += (
                    f"{rank_emoji} **#{i}** {username}\n"
                    f"└ {user_data['total_invites']} invites • {user_data['total_points']} pts • "
                    f"{self.get_recruitment_rank(user_data['total_invites'])}\n\n"
                )
                
            except Exception as e:
                logger.error(f"Error fetching user {user_data['user_id']}: {e}")
                continue
        
        if leaderboard_text:
            embed.add_field(name="🏆 Top Recruiters", value=leaderboard_text, inline=False)
        
        # Add server stats
        total_invites = sum(user['total_invites'] for user in leaderboard_data)
        total_points = sum(user['total_points'] for user in leaderboard_data)
        total_current = sum(user['current_invites'] for user in leaderboard_data)
        
        embed.add_field(
            name="📊 Server Statistics",
            value=(
                f"🎯 **Total Invites:** {total_invites:,}\n"
                f"💰 **Total Points:** {total_points:,}\n"
                f"👥 **Active Members:** {total_current:,}\n"
                f"👑 **Active Recruiters:** {len(leaderboard_data)}"
            ),
            inline=True
        )
        
        embed.add_field(
            name="🎮 Join the Hunt!",
            value=(
                f"Invite friends to join **{guild.name}**!\n"
                f"💰 Each invite = +33 points\n"
                f"• Use `!mystats` to check your rank\n"
                f"• Climb the ranks! 🦑"
            ),
            inline=True
        )
        
        embed.set_footer(
            text=f"🔄 Auto-updates every 15 minutes • {config.BOT_FOOTER}",
            icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None
        )
        embed.timestamp = discord.utils.utcnow()
        
        return embed
    
    async def find_existing_leaderboard(self, channel):
        """Find existing leaderboard message in channel"""
        async for message in channel.history(limit=100):
            if (message.author == self.bot.user and 
                message.embeds and 
                len(message.embeds) > 0 and
                "Top Survivors" in message.embeds[0].title):
                return message
        return None
    
    async def post_or_update_leaderboard(self, channel, embed):
        """Post new leaderboard or update existing one"""
        try:
            # Find existing leaderboard
            existing_message = await self.find_existing_leaderboard(channel)
            
            if existing_message:
                # Update existing message
                await existing_message.edit(embed=embed)
                self.leaderboard_message_id = existing_message.id
                logger.info(f"✅ Updated leaderboard in {channel.name}")
            else:
                # Post new message
                message = await channel.send(embed=embed)
                self.leaderboard_message_id = message.id
                logger.info(f"✅ Posted new leaderboard in {channel.name}")
                
        except Exception as e:
            logger.error(f"❌ Error posting leaderboard: {e}")
    
    @tasks.loop(seconds=config.LEADERBOARD_CONFIG['auto_update_interval'])
    async def auto_post_leaderboard(self):
        """Auto-update leaderboard every 15 minutes"""
        try:
            channel = self.bot.get_channel(config.LEADERBOARD_CHANNEL_ID)
            if not channel:
                logger.warning(f"❌ Leaderboard channel {config.LEADERBOARD_CHANNEL_ID} not found")
                return
            
            embed = await self.create_leaderboard_embed(channel.guild)
            if embed:
                await self.post_or_update_leaderboard(channel, embed)
            
        except Exception as e:
            logger.error(f"❌ Error in auto_post_leaderboard: {e}")
    
    @auto_post_leaderboard.before_loop
    async def before_auto_post(self):
        """Wait for bot to be ready"""
        await self.bot.wait_until_ready()
        logger.info("🔄 Started automatic leaderboard posting")
    
    # Commands
    @commands.command(name='leaderboard', aliases=['lb', 'top'])
    @commands.cooldown(1, 30, commands.BucketType.guild)
    async def show_leaderboard(self, ctx):
        """Show the current leaderboard"""
        embed = await self.create_leaderboard_embed(ctx.guild)
        if embed:
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ No leaderboard data available yet!")
    
    @commands.command(name='mystats', aliases=['me', 'myrank'])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def my_stats(self, ctx):
        """Show your personal stats"""
        leaderboard_data = self.get_leaderboard_data(ctx.guild.id)
        user_stats = None
        user_position = 0
        
        for i, user_data in enumerate(leaderboard_data, 1):
            if user_data['user_id'] == ctx.author.id:
                user_stats = user_data
                user_position = i
                break
        
        if not user_stats:
            embed = discord.Embed(
                title="📊 Your Recruitment Record",
                description="You haven't invited anyone yet!\n💰 Each invite = +33 points",
                color=config.EMBED_COLORS['warning']
            )
            await ctx.send(embed=embed)
            return
        
        embed = discord.Embed(
            title=f"📊 {ctx.author.display_name}'s Stats",
            color=config.EMBED_COLORS['info']
        )
        
        embed.add_field(
            name="📈 Your Statistics",
            value=(
                f"🎯 **Total Invites:** {user_stats['total_invites']}\n"
                f"💰 **Total Points:** {user_stats['total_points']}\n"
                f"👥 **Current Members:** {user_stats['current_invites']}\n"
                f"📊 **Retention Rate:** {user_stats['retention_rate']:.1f}%"
            ),
            inline=True
        )
        
        embed.add_field(
            name="🏆 Your Ranking",
            value=(
                f"🥇 **Server Rank:** #{user_position}/{len(leaderboard_data)}\n"
                f"👑 **Title:** {self.get_recruitment_rank(user_stats['total_invites'])}"
            ),
            inline=True
        )
        
        embed.set_thumbnail(url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        embed.timestamp = discord.utils.utcnow()
        
        await ctx.send(embed=embed)
    
    @commands.command(name='invitemod', aliases=['modinvites', 'setinvites'])
    @commands.has_permissions(administrator=True)
    async def moderate_invites(self, ctx, member: discord.Member, amount: int):
        """Modify a user's invite count (Admin only)"""
        
        # Load current invite data
        invite_data = self.load_invite_data()
        guild_str = str(ctx.guild.id)
        user_str = str(member.id)
        
        # Initialize if needed
        if guild_str not in invite_data:
            invite_data[guild_str] = {}
        
        if user_str not in invite_data[guild_str]:
            invite_data[guild_str][user_str] = {
                'total_invites': 0,
                'current_invites': 0,
                'left_members': 0,
                'fake_invites': 0
            }
        
        # Get old values
        old_total = invite_data[guild_str][user_str]['total_invites']
        
        # Set new values
        invite_data[guild_str][user_str]['total_invites'] = max(0, amount)
        invite_data[guild_str][user_str]['current_invites'] = max(0, amount)
        
        # Save the data
        try:
            with open(self.invite_data_file, 'w') as f:
                json.dump(invite_data, f, indent=2)
        except Exception as e:
            await ctx.send(f"❌ Error saving invite data: {e}")
            return
        
        # Calculate points (33 per invite)
        new_points = amount * 33
        old_points = old_total * 33
        points_change = new_points - old_points
        
        embed = discord.Embed(
            title="🛡️ Invite Count Modified",
            description=f"Updated invite statistics for {member.mention}",
            color=config.EMBED_COLORS['warning']
        )
        
        embed.add_field(
            name="📊 Changes",
            value=(
                f"**Old Invites:** {old_total}\n"
                f"**New Invites:** {amount}\n"
                f"**Points Change:** {points_change:+d} points\n"
                f"**New Total Points:** {new_points} points"
            ),
            inline=True
        )
        
        embed.add_field(
            name="🏆 New Rank",
            value=self.get_recruitment_rank(amount),
            inline=True
        )
        
        embed.set_footer(text=f"Modified by {ctx.author.display_name}")
        embed.timestamp = discord.utils.utcnow()
        
        await ctx.send(embed=embed)
        logger.info(f"🛡️ {ctx.author.name} modified {member.name}'s invites: {old_total} → {amount}")
    
    @commands.command(name='postleaderboard')
    @commands.has_permissions(administrator=True)
    async def post_leaderboard_here(self, ctx):
        """Post leaderboard in current channel (Admin only)"""
        embed = await self.create_leaderboard_embed(ctx.guild)
        if embed:
            await ctx.send(embed=embed)
            await ctx.message.add_reaction("✅")
        else:
            await ctx.send("❌ No leaderboard data available!")
    
    @commands.command(name='refreshleaderboard')
    @commands.has_permissions(administrator=True)
    async def refresh_leaderboard(self, ctx):
        """Force refresh the auto leaderboard (Admin only)"""
        channel = self.bot.get_channel(config.LEADERBOARD_CHANNEL_ID)
        if not channel:
            await ctx.send("❌ Leaderboard channel not configured!")
            return
        
        embed = await self.create_leaderboard_embed(ctx.guild)
        if embed:
            await self.post_or_update_leaderboard(channel, embed)
            await ctx.send(f"✅ Refreshed leaderboard in {channel.mention}")
        else:
            await ctx.send("❌ No leaderboard data available!")
    
    @commands.command(name='cleanleaderboards')
    @commands.has_permissions(administrator=True)
    async def clean_leaderboards(self, ctx):
        """Remove all duplicate leaderboards, keep only one (Admin only)"""
        channel = self.bot.get_channel(config.LEADERBOARD_CHANNEL_ID)
        if not channel:
            await ctx.send("❌ Leaderboard channel not configured!")
            return
        
        # Find all leaderboard messages
        leaderboard_messages = []
        async for message in channel.history(limit=200):
            if (message.author == self.bot.user and 
                message.embeds and 
                len(message.embeds) > 0 and
                "Top Survivors" in message.embeds[0].title):
                leaderboard_messages.append(message)
        
        if len(leaderboard_messages) <= 1:
            await ctx.send("✅ No duplicate leaderboards found!")
            return
        
        # Keep newest, delete rest
        newest = leaderboard_messages[0]
        duplicates = leaderboard_messages[1:]
        
        deleted = 0
        for msg in duplicates:
            try:
                await msg.delete()
                deleted += 1
            except:
                pass
        
        await ctx.send(f"🧹 Cleaned up {deleted} duplicate leaderboards!")
        logger.info(f"🧹 Cleaned {deleted} duplicate leaderboards")

async def setup(bot):
    """Setup function for the cog"""
    await bot.add_cog(Leaderboard(bot))
    logger.info("✅ Leaderboard cog loaded successfully")