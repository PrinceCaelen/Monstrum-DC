"""
Invite Tracking Cog for Monstrum Discord Bot
Tracks who invited new members and maintains statistics

Features:
- Track invite usage and who invited whom
- Store invite statistics in a simple database
- Attribution messages when members join
- Integration with welcome system
"""

import discord
from discord.ext import commands
import json
import os
import logging
from datetime import datetime, timezone
import config

logger = logging.getLogger(__name__)

class InviteTracker(commands.Cog):
    """Track invites and member attribution"""
    
    def __init__(self, bot):
        self.bot = bot
        self.invite_data_file = 'invite_data.json'
        self.invite_stats = self.load_invite_data()
        
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
    
    def save_invite_data(self):
        """Save invite statistics to JSON file"""
        try:
            with open(self.invite_data_file, 'w') as f:
                json.dump(self.invite_stats, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving invite data: {e}")
    
    def get_user_stats(self, guild_id, user_id):
        """Get invite statistics for a user"""
        guild_str = str(guild_id)
        user_str = str(user_id)
        
        if guild_str not in self.invite_stats:
            self.invite_stats[guild_str] = {}
        
        if user_str not in self.invite_stats[guild_str]:
            self.invite_stats[guild_str][user_str] = {
                'total_invites': 0,
                'current_invites': 0,
                'left_members': 0,
                'fake_invites': 0,
                'invited_users': [],
                'last_updated': datetime.now(timezone.utc).isoformat()
            }
        
        return self.invite_stats[guild_str][user_str]
    
    def update_user_stats(self, guild_id, user_id, invited_user_id=None, action='invite'):
        """Update invite statistics for a user"""
        stats = self.get_user_stats(guild_id, user_id)
        
        if action == 'invite' and invited_user_id:
            stats['total_invites'] += 1
            stats['current_invites'] += 1
            stats['invited_users'].append({
                'user_id': invited_user_id,
                'joined_at': datetime.now(timezone.utc).isoformat()
            })
        elif action == 'leave' and invited_user_id:
            stats['current_invites'] -= 1
            stats['left_members'] += 1
            # Remove from invited_users list
            stats['invited_users'] = [
                user for user in stats['invited_users'] 
                if user['user_id'] != invited_user_id
            ]
        elif action == 'fake':
            stats['fake_invites'] += 1
            stats['total_invites'] -= 1
            stats['current_invites'] -= 1
        
        stats['last_updated'] = datetime.now(timezone.utc).isoformat()
        self.save_invite_data()
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Track which invite was used when someone joins"""
        try:
            guild = member.guild
            
            # Skip bots
            if member.bot:
                return
            
            # Get current invites
            try:
                current_invites = await guild.invites()
            except discord.Forbidden:
                logger.warning(f"No permission to view invites in {guild.name}")
                return
            
            # Compare with cached invites
            used_invite = None
            cached_invites = self.bot.invite_cache.get(guild.id, {})
            
            for invite in current_invites:
                cached_uses = cached_invites.get(invite.code, 0)
                if invite.uses > cached_uses:
                    used_invite = invite
                    break
            
            # Update cache
            self.bot.invite_cache[guild.id] = {
                invite.code: invite.uses for invite in current_invites
            }
            
            # Track the invite
            if used_invite and used_invite.inviter:
                self.update_user_stats(
                    guild.id, 
                    used_invite.inviter.id, 
                    member.id, 
                    'invite'
                )
                
                # Send attribution message
                await self.send_invite_attribution(member, used_invite.inviter)
                
                logger.info(f"📨 {member.name} joined via invite from {used_invite.inviter.name}")
            else:
                logger.info(f"📨 {member.name} joined but couldn't determine invite source")
                
        except Exception as e:
            logger.error(f"Error tracking invite for {member.name}: {e}")
    
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """Update stats when someone leaves"""
        try:
            # Skip bots
            if member.bot:
                return
            
            guild = member.guild
            
            # Find who invited this member
            for user_id, stats in self.invite_stats.get(str(guild.id), {}).items():
                for invited_user in stats['invited_users']:
                    if invited_user['user_id'] == member.id:
                        self.update_user_stats(guild.id, int(user_id), member.id, 'leave')
                        logger.info(f"📤 {member.name} left, updated stats for inviter {user_id}")
                        return
                        
        except Exception as e:
            logger.error(f"Error handling member leave for {member.name}: {e}")
    
    async def send_invite_attribution(self, member, inviter):
        """Send a message attributing the new member to their inviter"""
        try:
            # Get the welcome channel or general channel
            channel = (self.bot.get_channel(config.WELCOME_CHANNEL_ID) or
                      self.bot.get_channel(config.GENERAL_CHANNEL_ID))
            
            if not channel:
                return
            
            # Get inviter stats
            stats = self.get_user_stats(member.guild.id, inviter.id)
            
            # Create attribution embed
            embed = discord.Embed(
                title="📨 Invitation Traced!",
                description=f"🕵️ **{member.mention}** was summoned by **{inviter.mention}**!",
                color=config.EMBED_COLORS['info']
            )
            
            embed.add_field(
                name="🎯 Inviter Stats",
                value=(
                    f"📊 **Total Invites:** {stats['total_invites']}\n"
                    f"👥 **Current Members:** {stats['current_invites']}\n"
                    f"📤 **Left Members:** {stats['left_members']}"
                ),
                inline=True
            )
            
            embed.add_field(
                name="🏆 Recruitment Level",
                value=self.get_recruitment_rank(stats['total_invites']),
                inline=True
            )
            
            embed.set_thumbnail(url=inviter.avatar.url if inviter.avatar else inviter.default_avatar.url)
            embed.set_footer(text="Building our cursed crew, one soul at a time...")
            embed.timestamp = discord.utils.utcnow()
            
            await channel.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error sending invite attribution: {e}")
    
    def get_recruitment_rank(self, total_invites):
        """Get a horror-themed rank based on invite count"""
        if total_invites >= 100:
            return "🦑 **Leviathan Summoner**"
        elif total_invites >= 50:
            return "👹 **Demon Recruiter**"
        elif total_invites >= 25:
            return "🕷️ **Spider's Web Master**"
        elif total_invites >= 10:
            return "👻 **Ghost Whisperer**"
        elif total_invites >= 5:
            return "🧟 **Zombie Herder**"
        elif total_invites >= 1:
            return "🎃 **Novice Cultist**"
        else:
            return "💀 **Fresh Recruit**"
    
    @commands.command(name='invites', aliases=['inv'])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def check_invites(self, ctx, member: discord.Member = None):
        """Check invite statistics for a member"""
        if member is None:
            member = ctx.author
        
        stats = self.get_user_stats(ctx.guild.id, member.id)
        
        embed = discord.Embed(
            title=f"📨 {member.display_name}'s Recruitment Record",
            color=config.EMBED_COLORS['info']
        )
        
        embed.add_field(
            name="📊 Statistics",
            value=(
                f"🎯 **Total Invites:** {stats['total_invites']}\n"
                f"👥 **Current Members:** {stats['current_invites']}\n"
                f"📤 **Left Members:** {stats['left_members']}\n"
                f"❌ **Fake Invites:** {stats['fake_invites']}"
            ),
            inline=True
        )
        
        embed.add_field(
            name="🏆 Rank",
            value=self.get_recruitment_rank(stats['total_invites']),
            inline=True
        )
        
        # Calculate success rate
        if stats['total_invites'] > 0:
            success_rate = (stats['current_invites'] / stats['total_invites']) * 100
            embed.add_field(
                name="📈 Retention Rate",
                value=f"{success_rate:.1f}%",
                inline=True
            )
        
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        embed.set_footer(text=config.BOT_FOOTER)
        embed.timestamp = discord.utils.utcnow()
        
        await ctx.send(embed=embed)
    
    @commands.command(name='resetinvites', hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_invites(self, ctx, member: discord.Member = None):
        """Reset invite statistics for a member (Admin only)"""
        if member is None:
            # Reset all stats for the guild
            guild_str = str(ctx.guild.id)
            if guild_str in self.invite_stats:
                del self.invite_stats[guild_str]
            self.save_invite_data()
            
            embed = discord.Embed(
                title="🧹 Statistics Purged",
                description="All invite statistics have been reset for this server.",
                color=config.EMBED_COLORS['warning']
            )
        else:
            # Reset stats for specific member
            guild_str = str(ctx.guild.id)
            user_str = str(member.id)
            
            if guild_str in self.invite_stats and user_str in self.invite_stats[guild_str]:
                del self.invite_stats[guild_str][user_str]
                self.save_invite_data()
            
            embed = discord.Embed(
                title="🧹 Statistics Purged",
                description=f"Invite statistics reset for {member.mention}.",
                color=config.EMBED_COLORS['warning']
            )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='cacheinvites', hidden=True)
    @commands.has_permissions(administrator=True)
    async def cache_invites(self, ctx):
        """Manually refresh the invite cache (Admin only)"""
        try:
            invites = await ctx.guild.invites()
            self.bot.invite_cache[ctx.guild.id] = {
                invite.code: invite.uses for invite in invites
            }
            
            embed = discord.Embed(
                title="🔄 Cache Refreshed",
                description=f"Cached {len(invites)} invites for tracking.",
                color=config.EMBED_COLORS['success']
            )
            await ctx.send(embed=embed)
            
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Permission Error",
                description="I don't have permission to view server invites.",
                color=config.EMBED_COLORS['error']
            )
            await ctx.send(embed=embed)
    
    # @commands.slash_command(name="invites", description="Check invite statistics")
    async def slash_invites(self, ctx, member: discord.Member = None):
        """Check invite statistics with slash command"""
        if member is None:
            member = ctx.author
        
        stats = self.get_user_stats(ctx.guild.id, member.id)
        
        embed = discord.Embed(
            title=f"📨 {member.display_name}'s Recruitment Record",
            color=config.EMBED_COLORS['info']
        )
        
        embed.add_field(
            name="📊 Statistics",
            value=(
                f"🎯 **Total Invites:** {stats['total_invites']}\n"
                f"👥 **Current Members:** {stats['current_invites']}\n"
                f"📤 **Left Members:** {stats['left_members']}\n"
                f"❌ **Fake Invites:** {stats['fake_invites']}"
            ),
            inline=True
        )
        
        embed.add_field(
            name="🏆 Rank",
            value=self.get_recruitment_rank(stats['total_invites']),
            inline=True
        )
        
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        embed.set_footer(text=config.BOT_FOOTER)
        embed.timestamp = discord.utils.utcnow()
        
        await ctx.respond(embed=embed)

async def setup(bot):
    """Setup function for the cog"""
    await bot.add_cog(InviteTracker(bot))
    logger.info("✅ Invite tracker cog loaded successfully")