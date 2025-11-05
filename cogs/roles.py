"""
Role Assignment Cog for Lua Corporation Discord Bot
Handles reaction roles and button-based role selection

Features:
- Reaction-based role assignment
- Button-based role selection with Discord UI
"""
Role Management Cog
==================
Manages server roles and role selection
- Professional role selection interface
- Admin controls for role management
"""

import discord
from discord.ext import commands
import logging
import config

logger = logging.getLogger(__name__)

class RoleSelectionView(discord.ui.View):
    """Persistent view for role selection buttons"""
    
    def __init__(self):
        super().__init__(timeout=None)  # Persistent view
        
    @discord.ui.button(
        label="Member", 
        emoji="🎮", 
        style=discord.ButtonStyle.primary,
        custom_id="role_member"
    )
    async def member_role(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.handle_role_toggle(interaction, "member", "🎮")
    
    async def handle_role_toggle(self, interaction: discord.Interaction, role_key: str, emoji: str):
        """Handle role assignment/removal"""
        try:
            # Get role mapping
            role_map = {
                "member": config.ROLE_SELECTION_ROLES.get('🎮'),
            }
            
            role_id = role_map.get(role_key)
            if not role_id:
                await interaction.response.send_message(
                    "❌ Role not configured properly!", 
                    ephemeral=True
                )
                return
            
            # Get the role
            role = interaction.guild.get_role(role_id)
            if not role:
                await interaction.response.send_message(
                    f"❌ Role not found! Please contact an administrator.", 
                    ephemeral=True
                )
                return
            
            # Check if user has the role
            if role in interaction.user.roles:
                # Remove role
                await interaction.user.remove_roles(role)
                await interaction.response.send_message(
                    f"➖ Removed the **{role.name}** {emoji} role!", 
                    ephemeral=True
                )
                logger.info(f"Removed {role.name} role from {interaction.user.name}")
            else:
                # Add role
                await interaction.user.add_roles(role)
                await interaction.response.send_message(
                    f"➕ Added the **{role.name}** {emoji} role!", 
                    ephemeral=True
                )
                logger.info(f"Added {role.name} role to {interaction.user.name}")
                
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ I don't have permission to manage roles!", 
                ephemeral=True
            )
        except Exception as e:
            logger.error(f"Error in role toggle: {e}")
            await interaction.response.send_message(
                "❌ An error occurred while managing your role.", 
                ephemeral=True
            )

class RoleAssignment(commands.Cog):
    """Role assignment system using reactions and buttons"""
    
    def __init__(self, bot):
        self.bot = bot
        
        # Add persistent view for role selection
        self.bot.add_view(RoleSelectionView())
    
    @commands.command(name='roles', aliases=['roleselect', 'rolesmenu'])
    @commands.cooldown(1, 30, commands.BucketType.guild)
    async def roles_menu(self, ctx):
        """Display the role selection menu"""
        embed = discord.Embed(
            title="🎭 Role Selection",
            description=(
                "Click the button below to assign yourself the Member role.\n"
                "This gives you access to exclusive content and discussions.\n\n"
                "**Available Role:**\n"
                "🎮 **Member** - Active community member"
            ),
            color=config.EMBED_COLORS['info']
        )
        
        embed.add_field(
            name="💡 How it works",
            value=(
                "• Click the button to **add** the role if you don't have it\n"
                "• Click the button to **remove** the role if you already have it\n"
                "• Changes are immediate!"
            ),
            inline=False
        )
        
        embed.set_footer(text=config.BOT_FOOTER)
        embed.timestamp = discord.utils.utcnow()
        
        view = RoleSelectionView()
        await ctx.send(embed=embed, view=view)
    
    @commands.command(name='reactionroles', hidden=True)
    @commands.has_permissions(administrator=True)
    async def setup_reaction_roles(self, ctx):
        """Set up reaction roles (Admin only)"""
        embed = discord.Embed(
            title="🎭 Reaction Role Setup",
            description=(
                "React to this message to get the Member role.\n\n"
                "🎮 - **Member Role**"
            ),
            color=config.EMBED_COLORS['info']
        )
        
        embed.set_footer(text="React to get your roles!")
        message = await ctx.send(embed=embed)
        
        # Add reactions
        for emoji in config.ROLE_SELECTION_ROLES.keys():
            try:
                await message.add_reaction(emoji)
            except Exception as e:
                logger.error(f"Failed to add reaction {emoji}: {e}")
    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """Handle reaction role additions"""
        if payload.user_id == self.bot.user.id:
            return
        
        # Check if it's a role selection reaction
        if str(payload.emoji) not in config.ROLE_SELECTION_ROLES:
            return
        
        try:
            guild = self.bot.get_guild(payload.guild_id)
            if not guild:
                return
            
            member = guild.get_member(payload.user_id)
            if not member:
                return
            
            role_id = config.ROLE_SELECTION_ROLES[str(payload.emoji)]
            role = guild.get_role(role_id)
            
            if role and role not in member.roles:
                await member.add_roles(role)
                logger.info(f"Added {role.name} role to {member.name} via reaction")
                
                # Send DM confirmation
                try:
                    embed = discord.Embed(
                        title="✅ Role Added!",
                        description=f"You now have the **{role.name}** role in **{guild.name}**!",
                        color=config.EMBED_COLORS['success']
                    )
                    await member.send(embed=embed)
                except discord.Forbidden:
                    pass  # User has DMs disabled
                    
        except Exception as e:
            logger.error(f"Error in reaction role add: {e}")
    
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        """Handle reaction role removals"""
        if payload.user_id == self.bot.user.id:
            return
        
        # Check if it's a role selection reaction
        if str(payload.emoji) not in config.ROLE_SELECTION_ROLES:
            return
        
        try:
            guild = self.bot.get_guild(payload.guild_id)
            if not guild:
                return
            
            member = guild.get_member(payload.user_id)
            if not member:
                return
            
            role_id = config.ROLE_SELECTION_ROLES[str(payload.emoji)]
            role = guild.get_role(role_id)
            
            if role and role in member.roles:
                await member.remove_roles(role)
                logger.info(f"Removed {role.name} role from {member.name} via reaction")
                
                # Send DM confirmation
                try:
                    embed = discord.Embed(
                        title="➖ Role Removed!",
                        description=f"You no longer have the **{role.name}** role in **{guild.name}**!",
                        color=config.EMBED_COLORS['warning']
                    )
                    await member.send(embed=embed)
                except discord.Forbidden:
                    pass  # User has DMs disabled
                    
        except Exception as e:
            logger.error(f"Error in reaction role remove: {e}")
    
    @commands.command(name='myroles')
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def my_roles(self, ctx):
        """Show your current roles"""
        user_roles = [role for role in ctx.author.roles if role != ctx.guild.default_role]
        
        if not user_roles:
            embed = discord.Embed(
                title="🎭 Your Roles",
                description="You don't have any special roles yet! Use the role selection menu to get some.",
                color=config.EMBED_COLORS['warning']
            )
        else:
            role_list = []
            for role in sorted(user_roles, key=lambda r: r.position, reverse=True):
                # Add emoji if it's a selectable role
                emoji = ""
                for reaction_emoji, role_id in config.ROLE_SELECTION_ROLES.items():
                    if role.id == role_id:
                        emoji = f"{reaction_emoji} "
                        break
                
                role_list.append(f"{emoji}**{role.name}**")
            
            embed = discord.Embed(
                title="🎭 Your Roles",
                description="\n".join(role_list),
                color=config.EMBED_COLORS['info']
            )
            
            embed.add_field(
                name="📊 Role Count",
                value=f"You have **{len(user_roles)}** special roles",
                inline=True
            )
        
        embed.set_thumbnail(url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        embed.set_footer(text=config.BOT_FOOTER)
        embed.timestamp = discord.utils.utcnow()
        
        await ctx.send(embed=embed)
    
    @commands.command(name='roleinfo')
    @commands.cooldown(1, 15, commands.BucketType.guild)
    async def role_info(self, ctx, *, role_name: str = None):
        """Get information about a role"""
        if not role_name:
            await ctx.send("Please specify a role name!")
            return
        
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        if not role:
            await ctx.send(f"Role '{role_name}' not found!")
            return
        
        embed = discord.Embed(
            title=f"🎭 Role Information: {role.name}",
            color=role.color if role.color != discord.Color.default() else config.EMBED_COLORS['info']
        )
        
        embed.add_field(
            name="📊 Statistics",
            value=(
                f"**ID:** {role.id}\n"
                f"**Members:** {len(role.members)}\n"
                f"**Position:** {role.position}\n"
                f"**Mentionable:** {'Yes' if role.mentionable else 'No'}\n"
                f"**Hoisted:** {'Yes' if role.hoist else 'No'}"
            ),
            inline=True
        )
        
        embed.add_field(
            name="🎨 Appearance",
            value=(
                f"**Color:** {str(role.color)}\n"
                f"**Created:** {discord.utils.format_dt(role.created_at, style='R')}"
            ),
            inline=True
        )
        
        # Check if it's a selectable role
        is_selectable = any(role.id == role_id for role_id in config.ROLE_SELECTION_ROLES.values())
        if is_selectable:
            embed.add_field(
                name="✨ Special Role",
                value="This is a self-assignable role! Use the role selection menu to get it.",
                inline=False
            )
        
        embed.set_footer(text=config.BOT_FOOTER)
        embed.timestamp = discord.utils.utcnow()
        
        await ctx.send(embed=embed)
    
    @commands.command(name='rolestats', hidden=True)
    @commands.has_permissions(administrator=True)
    async def role_stats(self, ctx):
        """Show role statistics (Admin only)"""
        embed = discord.Embed(
            title="📊 Server Role Statistics",
            description=f"Role overview for **{ctx.guild.name}**",
            color=config.EMBED_COLORS['info']
        )
        
        # Get selectable role stats
        selectable_stats = []
        for emoji, role_id in config.ROLE_SELECTION_ROLES.items():
            role = ctx.guild.get_role(role_id)
            if role:
                selectable_stats.append(f"{emoji} **{role.name}**: {len(role.members)} members")
            else:
                selectable_stats.append(f"{emoji} **Role not found** (ID: {role_id})")
        
        embed.add_field(
            name="🎭 Selectable Roles",
            value="\n".join(selectable_stats) if selectable_stats else "No selectable roles configured",
            inline=False
        )
        
        # Total role count
        embed.add_field(
            name="📈 Total Roles",
            value=f"**{len(ctx.guild.roles)}** total roles in server",
            inline=True
        )
        
        # Highest role
        highest_role = max(ctx.guild.roles, key=lambda r: r.position)
        embed.add_field(
            name="👑 Highest Role",
            value=f"**{highest_role.name}**",
            inline=True
        )
        
        embed.set_footer(text=config.BOT_FOOTER)
        embed.timestamp = discord.utils.utcnow()
        
        await ctx.send(embed=embed)
    
    # @discord.slash_command(name="roles", description="Open the role selection menu")
    # async def slash_roles(self, ctx):
    #     """Slash command for role selection"""
    #     embed = discord.Embed(
    #         title="🎭 Choose Your Roles",
    #         description=(
    #             "Select your roles to customize your experience in our cursed realm!\n"
    #             "Click the buttons below to add or remove roles.\n\n"
    #             "**Available Roles:**\n"
    #             "🎮 **Gamer** - General gaming discussions\n"
    #             "👻 **Horror Fan** - Horror game enthusiast\n"
    #             "🚢 **Monstrum Player** - Active Monstrum player\n"
    #             "📢 **Announcements** - Get notified of important updates\n"
    #             "🎉 **Events** - Participate in community events"
    #         ),
    #         color=config.EMBED_COLORS['info']
    #     )
    #     
    #     embed.set_footer(text="Choose wisely, the monsters are watching... 👁️")
    #     embed.timestamp = discord.utils.utcnow()
    #     
    #     view = RoleSelectionView()
    #     await ctx.respond(embed=embed, view=view)

async def setup(bot):
    """Setup function for the cog"""
    await bot.add_cog(RoleAssignment(bot))
    logger.info("✅ Role assignment cog loaded successfully")