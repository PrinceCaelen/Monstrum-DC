"""
Help Command Cog for Lua Corporation Discord Bot
Custom help system with professional theming and organized commands

Features:
- Professional help interface
- Organized command categories
- Interactive help menus
- Admin command filtering
"""

import discord
from discord.ext import commands
import logging
import config

logger = logging.getLogger(__name__)

class HelpCommand(commands.Cog):
    """Custom help command system"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='help', aliases=['h', 'commands'])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def help_command(self, ctx, category: str = None):
        """Show help information for bot commands"""
        
        if category:
            await self.show_category_help(ctx, category.lower())
        else:
            await self.show_main_help(ctx)
    
    async def show_main_help(self, ctx):
        """Show the main help menu"""
        embed = discord.Embed(
            title=f"⚡ {config.COMPANY_NAME} Bot - Command Help",
            description=(
                f"Welcome to {config.COMPANY_NAME} help system! Use the commands below to navigate "
                "through our bot features.\n\n"
                f"**Prefix:** `{ctx.prefix}`\n"
                f"**Use:** `{ctx.prefix}help <category>` for detailed information"
            ),
            color=config.EMBED_COLORS['info']
        )
        
        # Command categories
        categories = {
            "🎭 **General**": {
                "description": "Basic bot functionality and information",
                "command": f"`{ctx.prefix}help general`"
            },
            "📨 **Invites**": {
                "description": "Invite tracking and leaderboards",
                "command": f"`{ctx.prefix}help invites`"
            },
            "🎮 **Roles**": {
                "description": "Role selection and management",
                "command": f"`{ctx.prefix}help roles`"
            },
            "🎫 **Tickets**": {
                "description": "Support ticket system",
                "command": f"`{ctx.prefix}help tickets`"
            }
        }
        
        # Check if user is admin
        is_admin = any(role.id in config.ADMIN_ROLES for role in ctx.author.roles)
        if is_admin:
            categories["⚙️ **Admin**"] = {
                "description": "Administrator commands",
                "command": f"`{ctx.prefix}help admin`"
            }
        
        # Add categories to embed
        for category_name, category_info in categories.items():
            embed.add_field(
                name=category_name,
                value=f"{category_info['description']}\n{category_info['command']}",
                inline=True
            )
        
        # Add useful information
        embed.add_field(
            name="🔗 Quick Links",
            value=(
                f"• `{ctx.prefix}roles` - Role selection menu\n"
                f"• `{ctx.prefix}leaderboard` - Invite rankings\n"
                f"• `{ctx.prefix}game about` - Game information\n"
                f"• `{ctx.prefix}mystats` - Your statistics"
            ),
            inline=False
        )
        
        embed.add_field(
            name="💡 Tips",
            value=(
                "• Most commands have aliases (shorter versions)\n"
                "• Use slash commands with `/` for modern interface\n"
                "• Commands are case-insensitive\n"
                "• Some commands have cooldowns to prevent spam"
            ),
            inline=False
        )
        
        embed.set_footer(
            text=f"{len(self.bot.commands)} commands available • {config.BOT_FOOTER}"
        )
        embed.timestamp = discord.utils.utcnow()
        
        await ctx.send(embed=embed)
    
    async def show_category_help(self, ctx, category):
        """Show help for a specific category"""
        
        if category in ['general', 'basic', 'main']:
            await self.show_general_help(ctx)
        elif category in ['invites', 'invite', 'tracking', 'leaderboard']:
            await self.show_invites_help(ctx)
        elif category in ['roles', 'role', 'selection']:
            await self.show_roles_help(ctx)
        elif category in ['tickets', 'ticket', 'support']:
            await self.show_tickets_help(ctx)
        elif category in ['admin', 'administrator', 'mod']:
            await self.show_admin_help(ctx)
        else:
            embed = discord.Embed(
                title="❌ Category Not Found",
                description=(
                    f"Unknown category: `{category}`\n\n"
                    "**Available categories:**\n"
                    "• `general` - Basic commands\n"
                    "• `invites` - Invite tracking\n"
                    "• `roles` - Role management\n"
                    "• `tickets` - Support system\n"
                    "• `admin` - Admin commands"
                ),
                color=config.EMBED_COLORS['error']
            )
            await ctx.send(embed=embed)
    
    async def show_general_help(self, ctx):
        """Show general commands help"""
        embed = discord.Embed(
            title="🎭 General Commands",
            description="Basic bot functionality and utilities",
            color=config.EMBED_COLORS['info']
        )
        
        commands_info = [
            (f"`{ctx.prefix}help [category]`", "Show this help menu"),
            (f"`{ctx.prefix}mystats`", "Show your personal statistics"),
            (f"`{ctx.prefix}welcomestats`", "Show server statistics"),
            (f"`{ctx.prefix}myroles`", "Show your current roles"),
            (f"`{ctx.prefix}roleinfo <role>`", "Get information about a role"),
        ]
        
        embed.add_field(
            name="📋 Available Commands",
            value="\n".join([f"**{cmd}**\n└ {desc}" for cmd, desc in commands_info]),
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    async def show_invites_help(self, ctx):
        """Show invite tracking commands help"""
        embed = discord.Embed(
            title="📨 Invite Tracking Commands",
            description="Track invitations and view recruitment statistics",
            color=config.EMBED_COLORS['info']
        )
        
        commands_info = [
            (f"`{ctx.prefix}invites [@user]`", "Check invite statistics for you or another user"),
            (f"`{ctx.prefix}leaderboard`", "Show invite leaderboard (aliases: !lb, !top)"),
            (f"`{ctx.prefix}mystats`", "Show your detailed recruitment record (aliases: !me, !myrank)"),
            (f"`{ctx.prefix}welcomestats`", "Show overall server recruitment statistics"),
        ]
        
        embed.add_field(
            name="📋 Available Commands",
            value="\n".join([f"**{cmd}**\n└ {desc}" for cmd, desc in commands_info]),
            inline=False
        )
        
        embed.add_field(
            name="🏆 Recruitment Ranks",
            value=(
                "🦑 **Leviathan Summoner** (100+ invites)\n"
                "👹 **Demon Recruiter** (50+ invites)\n"
                "🕷️ **Spider's Web Master** (25+ invites)\n"
                "👻 **Ghost Whisperer** (10+ invites)\n"
                "🧟 **Zombie Herder** (5+ invites)\n"
                "🎃 **Novice Cultist** (1+ invites)"
            ),
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    async def show_roles_help(self, ctx):
        """Show role management commands help"""
        embed = discord.Embed(
            title="🎭 Role Management Commands",
            description="Manage your roles and customize your server experience",
            color=config.EMBED_COLORS['info']
        )
        
        commands_info = [
            (f"`{ctx.prefix}roles`", "Open the role selection menu (buttons)"),
            (f"`{ctx.prefix}myroles`", "Show your current roles"),
            (f"`{ctx.prefix}roleinfo <role>`", "Get detailed information about a role"),
        ]
        
        embed.add_field(
            name="📋 Available Commands",
            value="\n".join([f"**{cmd}**\n└ {desc}" for cmd, desc in commands_info]),
            inline=False
        )
        
        embed.add_field(
            name="🎮 Available Role",
            value="**Member** - Active community member",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    async def show_tickets_help(self, ctx):
        """Show ticket system commands help"""
        embed = discord.Embed(
            title="🎫 Ticket System Commands",
            description="Professional support ticket system for users and staff",
            color=config.EMBED_COLORS['info']
        )
        
        user_commands = [
            ("**Ticket Panel**", "Click the dropdown menu in the ticket channel to create tickets"),
            ("**Ticket Types**", "🎮 Game Support • ❓ General Help • ⚠️ Report Issue • 💡 Suggestions • 🛡️ Moderator Help"),
        ]
        
        embed.add_field(
            name="👥 User Features",
            value="\n".join([f"**{cmd}**\n└ {desc}" for cmd, desc in user_commands]),
            inline=False
        )
        
        # Check if user is admin/moderator
        is_staff = any(role.id in config.ADMIN_ROLES for role in ctx.author.roles)
        if is_staff:
            admin_commands = [
                (f"`{ctx.prefix}setup ticketlog [#channel]`", "Set ticket logging channel"),
                (f"`{ctx.prefix}setup ticketpanel`", "Create ticket selection panel"),
            ]
            
            embed.add_field(
                name="⚙️ Staff Setup",
                value="\n".join([f"**{cmd}**\n└ {desc}" for cmd, desc in admin_commands]),
                inline=False
            )
        
        embed.add_field(
            name="🔧 Ticket Features",
            value=(
                "• **Smart Categories** - Automatic channel organization\n"
                "• **Role Permissions** - Staff-only access\n"
                "• **Logging System** - Complete ticket history\n"
                "• **Auto-Close** - Inactive tickets auto-close\n"
                "• **User Limits** - Prevent ticket spam"
            ),
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    async def show_admin_help(self, ctx):
        """Show admin commands help (admin only)"""
        # Check if user is admin
        is_admin = any(role.id in config.ADMIN_ROLES for role in ctx.author.roles)
        if not is_admin:
            embed = discord.Embed(
                title="🚫 Access Denied",
                description="You don't have permission to view admin commands!",
                color=config.EMBED_COLORS['error']
            )
            await ctx.send(embed=embed)
            return
        
        embed = discord.Embed(
            title="⚙️ Administrator Commands",
            description="Commands for server administrators and moderators",
            color=config.EMBED_COLORS['warning']
        )
        
        commands_info = [
            (f"`{ctx.prefix}announce <message>`", "Post announcements to announcements channel"),
            (f"`{ctx.prefix}gameupdate <version> <changes>`", "Post game update information"),
            (f"`{ctx.prefix}gamenews <title>\n<content>`", "Post game news updates"),
            (f"`{ctx.prefix}hotfix <version> <fixes>`", "Post hotfix/patch announcements"),
            (f"`{ctx.prefix}setupgameinfo`", "Setup game info in current channel"),
            (f"`{ctx.prefix}setup ticketlog [#channel]`", "Setup ticket logging channel"),
            (f"`{ctx.prefix}setup ticketpanel`", "Create ticket panel with dropdown"),
            (f"`{ctx.prefix}invitemod @user <amount>`", "Modify user's invite count"),
            (f"`{ctx.prefix}postleaderboard`", "Post leaderboard in current channel"),
            (f"`{ctx.prefix}refreshleaderboard`", "Force refresh auto-leaderboard"),
            (f"`{ctx.prefix}cleanleaderboards`", "Remove duplicate leaderboards"),
            (f"`{ctx.prefix}reactionroles`", "Set up reaction role message"),
            (f"`{ctx.prefix}resetinvites [@user]`", "Reset invite statistics"),
            (f"`{ctx.prefix}cacheinvites`", "Refresh invite cache"),
            (f"`{ctx.prefix}rolestats`", "Show role statistics"),
            (f"`{ctx.prefix}testwelcome [@user]`", "Test welcome message"),
            (f"`{ctx.prefix}testboost [@user]`", "Test boost message"),
        ]
        
        embed.add_field(
            name="📋 Available Commands",
            value="\n".join([f"**{cmd}**\n└ {desc}" for cmd, desc in commands_info]),
            inline=False
        )
        
        embed.add_field(
            name="⚠️ Important Notes",
            value=(
                "• These commands require administrator permissions\n"
                "• Announcement commands post to configured channels\n"
                "• Be careful with reset commands - they delete data\n"
                "• Test commands are useful for debugging"
            ),
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    # @discord.slash_command(name="help", description="Show bot help information")
    async def slash_help(self, ctx, category: str = None):
        """Slash command version of help"""
        await ctx.defer()
        
        if category:
            await self.show_category_help(ctx, category.lower())
        else:
            await self.show_main_help(ctx)

async def setup(bot):
    """Setup function for the cog"""
    await bot.add_cog(HelpCommand(bot))
    logger.info("✅ Help command cog loaded successfully")