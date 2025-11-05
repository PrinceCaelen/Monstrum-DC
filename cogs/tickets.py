"""
Advanced Ticket System for Lua Corporation Discord Bot
Professional ticket system with dropdown menu and proper channel management

Features:
- Clean dropdown menu interface
- Professional ticket creation and management
- Proper channel isolation and privacy
- Staff notification system
- Transcript generation with proper routing
"""

import discord
from discord.ext import commands, tasks
import logging
import asyncio
import json
import os
from datetime import datetime, timedelta, timezone
import config

logger = logging.getLogger(__name__)

class TicketDropdown(discord.ui.Select):
    """Dropdown menu for ticket type selection"""
    
    def __init__(self, bot):
        self.bot = bot
        
        # Create options for the dropdown
        options = []
        for emoji, ticket_info in config.TICKET_CONFIG['ticket_types'].items():
            options.append(discord.SelectOption(
                label=ticket_info['name'],
                description=ticket_info['description'][:100],  # Discord limit
                emoji=emoji,
                value=f"{emoji}|{ticket_info['name']}"
            ))
        
        super().__init__(
            placeholder="🎫 Select a ticket type to get started...",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="ticket_dropdown"  # Required for persistent views
        )
    
    async def callback(self, interaction: discord.Interaction):
        """Handle dropdown selection"""
        try:
            # Parse the selected value
            emoji, ticket_type = interaction.data['values'][0].split('|', 1)
            
            # Get the ticket system cog
            ticket_cog = self.bot.get_cog('TicketSystem')
            if not ticket_cog:
                await interaction.response.send_message("❌ Ticket system not available!", ephemeral=True)
                return
            
            # Check if user has too many open tickets
            user_id = str(interaction.user.id)
            user_ticket_count = len(ticket_cog.user_tickets.get(user_id, []))
            
            if user_ticket_count >= config.TICKET_CONFIG['max_tickets_per_user']:
                embed = discord.Embed(
                    title="🚫 Ticket Limit Reached",
                    description=f"You have reached the maximum limit of **{config.TICKET_CONFIG['max_tickets_per_user']}** open tickets.\n\nPlease close an existing ticket before creating a new one.",
                    color=0xFF0000
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            # Show loading message
            await interaction.response.send_message("🎫 Creating your support ticket...", ephemeral=True)
            
            # Create the ticket
            reason = f"Support request: {ticket_type}"
            channel = await ticket_cog._create_ticket_channel(interaction.guild, interaction.user, emoji, reason)
            
            # Send success message
            embed = discord.Embed(
                title="✅ Ticket Created Successfully!",
                description=f"Your **{ticket_type}** ticket has been created!\n\n📎 **Channel:** {channel.mention}\n\nOur support team will assist you shortly.",
                color=0x00FF00
            )
            
            try:
                # Try to edit the interaction response
                await interaction.edit_original_response(content=None, embed=embed)
            except:
                # If that fails, send a new message
                await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error in ticket dropdown callback: {e}")
            try:
                if not interaction.response.is_done():
                    await interaction.response.send_message("❌ An error occurred while creating your ticket. Please try again or contact an administrator.", ephemeral=True)
                else:
                    await interaction.followup.send("❌ An error occurred while creating your ticket. Please try again or contact an administrator.", ephemeral=True)
            except:
                pass

class TicketActionView(discord.ui.View):
    """View with ticket action buttons"""
    
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.danger, emoji="🔒", custom_id="close_ticket")
    async def close_ticket_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Close ticket button"""
        # Check if user has permission to close
        ticket_cog = interaction.client.get_cog('TicketSystem')
        if not ticket_cog:
            await interaction.response.send_message("❌ Ticket system not available!", ephemeral=True)
            return
        
        channel_id = str(interaction.channel.id)
        if channel_id not in ticket_cog.active_tickets:
            await interaction.response.send_message("❌ This is not a valid ticket channel!", ephemeral=True)
            return
        
        ticket_data = ticket_cog.active_tickets[channel_id]
        
        # Only ticket creator or staff can close
        is_staff = any(role.id in config.TICKET_CONFIG['support_roles'] for role in interaction.user.roles)
        is_creator = interaction.user.id == ticket_data['user_id']
        
        if not (is_staff or is_creator):
            await interaction.response.send_message("❌ You don't have permission to close this ticket!", ephemeral=True)
            return
        
        # Show confirmation
        await interaction.response.send_message("🔒 Closing ticket...", ephemeral=True)
        
        # Close the ticket
        await ticket_cog._close_ticket_internal(interaction.channel, interaction.user, "Closed via button")
    
    @discord.ui.button(label="Alert Staff", style=discord.ButtonStyle.secondary, emoji="🔔", custom_id="alert_staff")
    async def alert_staff_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Alert staff button"""
        # Create mention string for all support roles
        mentions = []
        for role_id in config.TICKET_CONFIG['support_roles']:
            role = interaction.guild.get_role(role_id)
            if role:
                mentions.append(role.mention)
        
        if mentions:
            mention_text = " ".join(mentions)
            await interaction.response.send_message(
                f"🔔 **Staff Alert!**\n{mention_text}\n\n"
                f"**{interaction.user.mention}** needs immediate assistance in this ticket!",
                ephemeral=False  # Everyone in ticket can see this
            )
        else:
            await interaction.response.send_message("❌ No staff roles configured!", ephemeral=True)

class TicketView(discord.ui.View):
    """View containing the ticket dropdown"""
    
    def __init__(self, bot):
        super().__init__(timeout=None)  # Persistent view
        self.add_item(TicketDropdown(bot))

class TicketSystem(commands.Cog):
    """Professional ticket system with dropdown interface"""
    
    def __init__(self, bot):
        self.bot = bot
        self.tickets_data_file = 'tickets_data.json'
        self.ticket_config_file = 'ticket_config.json'
        self.active_tickets = {}
        self.user_tickets = {}  # Track tickets per user
        self.ticket_log_channel = None  # Will be loaded from config
        
        # Load existing ticket data
        self.load_ticket_data()
        self.load_ticket_config()
        
        # Start auto-close task
        if config.FEATURES.get('ticket_system', True):
            self.auto_close_tickets.start()
    
    def cog_unload(self):
        """Clean up when cog is unloaded"""
        self.auto_close_tickets.cancel()
        self.save_ticket_data()
        self.save_ticket_config()
    
    def load_ticket_config(self):
        """Load ticket configuration from file"""
        try:
            if os.path.exists(self.ticket_config_file):
                with open(self.ticket_config_file, 'r') as f:
                    config_data = json.load(f)
                    self.ticket_log_channel = config_data.get('log_channel_id')
                logger.info("✅ Loaded ticket configuration")
        except Exception as e:
            logger.error(f"❌ Error loading ticket config: {e}")
            self.ticket_log_channel = None
    
    def save_ticket_config(self):
        """Save ticket configuration to file"""
        try:
            config_data = {
                'log_channel_id': self.ticket_log_channel
            }
            with open(self.ticket_config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
            logger.info("✅ Saved ticket configuration")
        except Exception as e:
            logger.error(f"❌ Error saving ticket config: {e}")
    
    def load_ticket_data(self):
        """Load ticket data from file"""
        try:
            if os.path.exists(self.tickets_data_file):
                with open(self.tickets_data_file, 'r') as f:
                    data = json.load(f)
                    self.active_tickets = data.get('active_tickets', {})
                    self.user_tickets = data.get('user_tickets', {})
                logger.info("✅ Loaded existing ticket data")
        except Exception as e:
            logger.error(f"❌ Error loading ticket data: {e}")
            self.active_tickets = {}
            self.user_tickets = {}
    
    def save_ticket_data(self):
        """Save ticket data to file"""
        try:
            data = {
                'active_tickets': self.active_tickets,
                'user_tickets': self.user_tickets
            }
            with open(self.tickets_data_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info("✅ Saved ticket data")
        except Exception as e:
            logger.error(f"❌ Error saving ticket data: {e}")
    
    def create_ticket_embed(self, title, description, color=None, guild=None):
        """Create a professional ticket embed with server branding"""
        embed = discord.Embed(
            title=f"🎫 {title}",
            description=description,
            color=color or config.TICKET_CONFIG['embed_color']
        )
        
        # Add server branding
        if guild:
            embed.set_author(
                name=f"{config.TICKET_CONFIG['server_name']} Support",
                icon_url=guild.icon.url if guild.icon else None
            )
            if guild.icon:
                embed.set_thumbnail(url=guild.icon.url)
        
        embed.set_footer(
            text=f"{config.TICKET_CONFIG['server_name']} • Support System",
            icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None
        )
        embed.timestamp = discord.utils.utcnow()
        
        return embed
    
    async def get_or_create_ticket_category(self, guild):
        """Get or create the ticket support category"""
        category_name = config.TICKET_CONFIG['category_name']
        
        # Look for existing category
        for category in guild.categories:
            if category.name == category_name:
                return category
        
        # Create new category with proper permissions
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_messages=True)
        }
        
        # Add permissions for support roles
        for role_id in config.TICKET_CONFIG['support_roles']:
            role = guild.get_role(role_id)
            if role:
                overwrites[role] = discord.PermissionOverwrite(
                    read_messages=True, 
                    send_messages=True, 
                    manage_messages=True
                )
        
        category = await guild.create_category(category_name, overwrites=overwrites)
        logger.info(f"✅ Created ticket category: {category_name}")
        return category
    
    @commands.group(name='setup', invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def setup_group(self, ctx):
        """Setup commands for ticket system"""
        if ctx.invoked_subcommand is None:
            embed = self.create_ticket_embed(
                "Ticket System Setup",
                (
                    "**Available Setup Commands:**\n"
                    f"`{ctx.prefix}setup ticketlog <#channel>` - Set ticket log channel\n"
                    f"`{ctx.prefix}setup ticketpanel` - Create ticket panel\n\n"
                    f"**Current Configuration:**\n"
                    f"📝 **Log Channel:** {f'<#{self.ticket_log_channel}>' if self.ticket_log_channel else 'Not set'}"
                ),
                guild=ctx.guild
            )
            await ctx.send(embed=embed)
    
    @setup_group.command(name='ticketlog')
    @commands.has_permissions(administrator=True)
    async def setup_ticket_log(self, ctx, channel: discord.TextChannel = None):
        """Set the ticket log channel where transcripts will be sent"""
        
        if channel is None:
            # Show current config and instructions
            current_channel = None
            if self.ticket_log_channel:
                current_channel = ctx.guild.get_channel(self.ticket_log_channel)
            
            embed = self.create_ticket_embed(
                "🔧 Ticket Log Configuration",
                f"**Current log channel:** {current_channel.mention if current_channel else 'Not configured'}\n\n"
                f"**Usage:** `!setup ticketlog #channel-name`\n"
                f"**Example:** `!setup ticketlog #ticket-logs`\n\n"
                f"**What will be logged:**\n"
                f"📜 Ticket transcripts\n"
                f"🔒 Ticket closure notifications\n"
                f"📊 Ticket statistics\n\n"
                f"*Note: Logs will ONLY go to this channel, not the ticket creation panel.*",
                color=0xFFAA00,
                guild=ctx.guild
            )
            await ctx.send(embed=embed)
            return
        
        # Save the log channel
        self.ticket_log_channel = channel.id
        self.save_ticket_config()
        
        embed = self.create_ticket_embed(
            "✅ Ticket Log Channel Set",
            f"Ticket logs and transcripts will now be sent to {channel.mention}\n\n"
            f"**What will be logged:**\n"
            f"📜 Ticket transcripts\n"
            f"🔒 Ticket closure notifications\n"
            f"📊 Ticket statistics",
            color=0x00FF00,
            guild=ctx.guild
        )
        
        await ctx.send(embed=embed)
        logger.info(f"✅ Set ticket log channel to {channel.name} ({channel.id})")
    
    @setup_group.command(name='ticketpanel')
    @commands.has_permissions(administrator=True)
    async def setup_ticket_panel(self, ctx):
        """Set up the ticket creation panel"""
        
        embed = self.create_ticket_embed(
            f"{config.COMPANY_NAME} Support System",
            (
                f"Welcome to the **{config.COMPANY_NAME}** support system.\n\n"
                "**How it works:**\n"
                "🔸 Select a ticket type from the dropdown below\n"
                "🔸 A private support channel will be created for you\n"
                "🔸 Our team will assist you promptly\n"
                "🔸 Your ticket will be handled professionally and privately\n\n"
                "**Need immediate help?** Create a ticket below."
            ),
            guild=ctx.guild
        )
        
        # Add useful information without cluttering
        embed.add_field(
            name="⚡ Quick Info",
            value=(
                f"📊 Max tickets per user: `{config.TICKET_CONFIG['max_tickets_per_user']}`\n"
                f"⏱️ Auto-close after: `{config.TICKET_CONFIG['auto_close_hours']} hours of inactivity`\n"
                f"🔒 All tickets are private and secure"
            ),
            inline=False
        )
        
        # Create the view with dropdown
        view = TicketView(self.bot)
        
        # Send the message with the dropdown
        message = await ctx.send(embed=embed, view=view)
        
        # Confirm to admin
        await ctx.send(f"✅ Ticket panel set up successfully! Users can now create tickets using the dropdown menu.", delete_after=10)
        
        # Delete the admin command
        try:
            await ctx.message.delete()
        except:
            pass
    
    @commands.group(name='ticket', aliases=['tickets'], invoke_without_command=True)
    async def ticket_group(self, ctx):
        """Ticket system - Admin commands"""
        if ctx.invoked_subcommand is None:
            # Only show this to admins, regular users shouldn't see all commands
            if not any(role.id in config.TICKET_CONFIG['support_roles'] for role in ctx.author.roles):
                await ctx.send("❌ You don't have permission to view ticket system commands. Use the ticket panel in the designated channel.", delete_after=10)
                return
            
            embed = self.create_ticket_embed(
                "Admin Ticket System Commands",
                "**Administrative Commands:**\n"
                f"`{ctx.prefix}ticket close` - Close current ticket\n"
                f"`{ctx.prefix}ticket add <user>` - Add user to ticket\n"
                f"`{ctx.prefix}ticket remove <user>` - Remove user from ticket\n"
                f"`{ctx.prefix}ticket list` - List all open tickets\n\n"
                "**Setup Commands:**\n"
                f"`{ctx.prefix}setup ticketpanel` - Create ticket panel\n"
                f"`{ctx.prefix}setup ticketlog <#channel>` - Set log channel",
                guild=ctx.guild
            )
            await ctx.send(embed=embed)
    
    # Remove the old create command - users now use dropdown
    
    async def _create_ticket_channel(self, guild, user, ticket_type, reason):
        """Internal method to create a ticket channel"""
        
        # Get or create category
        category = await self.get_or_create_ticket_category(guild)
        
        # Generate unique ticket ID
        ticket_id = len(self.active_tickets) + 1
        while f"ticket-{ticket_id:04d}" in [ticket['channel_name'] for ticket in self.active_tickets.values()]:
            ticket_id += 1
        
        channel_name = f"ticket-{ticket_id:04d}"
        
        # Set up channel permissions
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_messages=True)
        }
        
        # Add support role permissions
        for role_id in config.TICKET_CONFIG['support_roles']:
            role = guild.get_role(role_id)
            if role:
                overwrites[role] = discord.PermissionOverwrite(
                    read_messages=True, 
                    send_messages=True, 
                    manage_messages=True
                )
        
        # Create the ticket channel
        channel = await guild.create_text_channel(
            channel_name,
            category=category,
            overwrites=overwrites,
            topic=f"Support ticket for {user.display_name} | Type: {ticket_type} | Created: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        )
        
        # Store ticket data
        ticket_data = {
            'channel_id': channel.id,
            'channel_name': channel_name,
            'user_id': user.id,
            'ticket_type': ticket_type,
            'reason': reason,
            'created_at': datetime.now().isoformat(),
            'status': 'open'
        }
        
        self.active_tickets[str(channel.id)] = ticket_data
        
        # Track user tickets
        user_id = str(user.id)
        if user_id not in self.user_tickets:
            self.user_tickets[user_id] = []
        self.user_tickets[user_id].append(channel.id)
        
        self.save_ticket_data()
        
        # Send welcome message to ticket channel
        ticket_type_info = config.TICKET_CONFIG['ticket_types'].get(ticket_type, {'name': 'General', 'description': 'General support'})
        
        embed = self.create_ticket_embed(
            f"Support Ticket #{ticket_id:04d}",
            (
                f"Welcome {user.mention}!\n\n"
                f"**Ticket Type:** {ticket_type} {ticket_type_info['name']}\n"
                f"**Created by:** {user.display_name}\n\n"
                f"Please describe your issue and our team will assist you."
            ),
            guild=guild
        )
        
        # Create the action view with buttons
        action_view = TicketActionView()
        
        welcome_msg = await channel.send(
            f"🎫 **New Support Ticket**",
            embed=embed,
            view=action_view
        )
        
        # Pin the welcome message
        await welcome_msg.pin()
        
        logger.info(f"✅ Created ticket #{ticket_id:04d} for {user.name} ({user.id})")
        return channel
    
    @ticket_group.command(name='close')
    async def close_ticket(self, ctx, *, reason: str = "No reason provided"):
        """Close the current ticket"""
        
        channel_id = str(ctx.channel.id)
        if channel_id not in self.active_tickets:
            await ctx.send("❌ This command can only be used in ticket channels!")
            return
        
        # Use the internal close method
        await self._close_ticket_internal(ctx.channel, ctx.author, reason)
    
    async def _close_ticket_internal(self, channel, closed_by, reason):
        """Internal method to close a ticket (used by both command and button)"""
        channel_id = str(channel.id)
        if channel_id not in self.active_tickets:
            return
        
        ticket_data = self.active_tickets[channel_id]
        
        # Create closing embed
        embed = self.create_ticket_embed(
            f"🔒 Closing Ticket #{channel.name}",
            (
                f"This ticket is being closed by {closed_by.mention}\n\n"
                f"**Reason:** {reason}\n"
                f"**Duration:** {self._get_ticket_duration(ticket_data['created_at'])}\n\n"
                f"**This channel will be deleted in 10 seconds.**"
            ),
            color=0xFF6B6B,
            guild=channel.guild
        )
        
        await channel.send(embed=embed)
        
        # Generate transcript BEFORE deleting
        transcript_content = await self._generate_transcript(channel, closed_by, reason)
        
        # Send transcript to logs
        await self._send_transcript_to_logs(channel.guild, channel, closed_by, reason, transcript_content)
        
        # Update ticket data
        ticket_data['status'] = 'closed'
        ticket_data['closed_at'] = datetime.now().isoformat()
        ticket_data['closed_by'] = closed_by.id
        ticket_data['close_reason'] = reason
        
        # Remove from user tickets
        user_id = str(ticket_data['user_id'])
        if user_id in self.user_tickets and channel.id in self.user_tickets[user_id]:
            self.user_tickets[user_id].remove(channel.id)
        
        # Remove from active tickets
        del self.active_tickets[channel_id]
        self.save_ticket_data()
        
        # Delete channel after short delay
        await asyncio.sleep(10)
        try:
            await channel.delete(reason=f"Ticket closed by {closed_by}")
            logger.info(f"✅ Closed ticket {channel.name} by {closed_by.name}")
        except Exception as e:
            logger.error(f"❌ Error deleting ticket channel: {e}")
    
    async def _send_transcript_to_logs(self, guild, channel, closed_by, reason, transcript_content):
        """Send transcript to the designated tickets log channel"""
        try:
            # Check if log channel is configured
            if not self.ticket_log_channel:
                logger.warning("❌ No ticket log channel configured. Use !setup ticketlog to set one.")
                return
            
            # Send to configured log channel
            log_channel = self.bot.get_channel(self.ticket_log_channel)
            if not log_channel:
                logger.warning(f"❌ Configured ticket log channel {self.ticket_log_channel} not found")
                return
            
            # Get the ticket user
            channel_id = str(channel.id)
            ticket_data = self.active_tickets.get(channel_id)
            if not ticket_data:
                return
                
            user = guild.get_member(ticket_data['user_id'])
            
            embed = self.create_ticket_embed(
                f"📜 Ticket Closed - {channel.name}",
                (
                    f"**Ticket Information:**\n"
                    f"👤 **User:** {user.mention if user else 'Unknown User'} ({ticket_data['user_id']})\n"
                    f"🎯 **Type:** {ticket_data['ticket_type']}\n"
                    f"📅 **Created:** {ticket_data['created_at'][:19].replace('T', ' ')}\n"
                    f"⏱️ **Duration:** {self._get_ticket_duration(ticket_data['created_at'])}\n"
                    f"🔒 **Closed by:** {closed_by.mention}\n"
                    f"📝 **Reason:** {reason}"
                ),
                color=0x95A5A6,
                guild=guild
            )
            
            # Create transcript file
            import io
            file = discord.File(
                io.StringIO(transcript_content), 
                filename=f"transcript-{channel.name}-{datetime.now().strftime('%Y%m%d-%H%M%S')}.txt"
            )
            
            await log_channel.send(embed=embed, file=file)
            logger.info(f"✅ Sent transcript for {channel.name} to ticket log channel")
            
        except Exception as e:
            logger.error(f"❌ Error sending transcript to logs: {e}")
    
    async def _generate_transcript(self, channel, closed_by, reason):
        """Generate a transcript of the ticket and return the content"""
        try:
            messages = []
            async for message in channel.history(limit=None, oldest_first=True):
                # Skip bot messages except for important ones
                if message.author.bot and not message.pinned:
                    continue
                    
                timestamp = message.created_at.strftime("%Y-%m-%d %H:%M:%S UTC")
                content = message.content or "[Embed/Attachment content]"
                
                # Include attachment information
                if message.attachments:
                    content += f" [Attachments: {', '.join([att.filename for att in message.attachments])}]"
                
                messages.append(f"[{timestamp}] {message.author.display_name}: {content}")
            
            # Create transcript content
            transcript_content = f"""{config.COMPANY_NAME.upper()} SUPPORT TICKET TRANSCRIPT
=====================================
Ticket: {channel.name}
Closed by: {closed_by.display_name} ({closed_by.id})
Close reason: {reason}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
Total messages: {len(messages)}

CONVERSATION:
=============
""" + "\n".join(messages)
            
            return transcript_content
            
        except Exception as e:
            logger.error(f"❌ Error generating transcript: {e}")
            return f"Error generating transcript: {str(e)}"
    
    def _get_ticket_duration(self, created_at_str):
        """Calculate ticket duration"""
        try:
            created_at = datetime.fromisoformat(created_at_str)
            duration = datetime.now() - created_at
            hours = int(duration.total_seconds() // 3600)
            minutes = int((duration.total_seconds() % 3600) // 60)
            return f"{hours}h {minutes}m"
        except:
            return "Unknown"
    
    @ticket_group.command(name='add')
    @commands.has_any_role(*[role_id for role_id in config.TICKET_CONFIG['support_roles']])
    async def add_user_to_ticket(self, ctx, user: discord.Member):
        """Add a user to the current ticket (Staff only)"""
        
        channel_id = str(ctx.channel.id)
        if channel_id not in self.active_tickets:
            await ctx.send("❌ This command can only be used in ticket channels!")
            return
        
        # Add user to channel permissions
        await ctx.channel.set_permissions(user, read_messages=True, send_messages=True)
        
        embed = self.create_ticket_embed(
            "User Added to Ticket",
            f"✅ {user.mention} has been added to this ticket by {ctx.author.mention}",
            color=0x00FF00,
            guild=ctx.guild
        )
        
        await ctx.send(embed=embed)
        logger.info(f"✅ Added {user.name} to ticket {ctx.channel.name}")
    
    @ticket_group.command(name='remove')
    @commands.has_any_role(*[role_id for role_id in config.TICKET_CONFIG['support_roles']])
    async def remove_user_from_ticket(self, ctx, user: discord.Member):
        """Remove a user from the current ticket (Staff only)"""
        
        channel_id = str(ctx.channel.id)
        if channel_id not in self.active_tickets:
            await ctx.send("❌ This command can only be used in ticket channels!")
            return
        
        # Remove user from channel permissions
        await ctx.channel.set_permissions(user, overwrite=None)
        
        embed = self.create_ticket_embed(
            "User Removed from Ticket",
            f"🚫 {user.mention} has been removed from this ticket by {ctx.author.mention}",
            color=0xFF6B6B,
            guild=ctx.guild
        )
        
        await ctx.send(embed=embed)
        logger.info(f"✅ Removed {user.name} from ticket {ctx.channel.name}")
    
    @ticket_group.command(name='list')
    @commands.has_any_role(*[role_id for role_id in config.TICKET_CONFIG['support_roles']])
    async def list_tickets(self, ctx):
        """List all open tickets (Staff only)"""
        
        if not self.active_tickets:
            embed = self.create_ticket_embed(
                "No Active Tickets",
                "🎉 There are currently no open support tickets!",
                color=0x00FF00,
                guild=ctx.guild
            )
            await ctx.send(embed=embed)
            return
        
        embed = self.create_ticket_embed(
            f"Active Support Tickets ({len(self.active_tickets)})",
            "📊 Here are all currently open support tickets:",
            guild=ctx.guild
        )
        
        for ticket_data in list(self.active_tickets.values())[:10]:  # Limit to 10 for embed limits
            user = self.bot.get_user(ticket_data['user_id'])
            username = user.display_name if user else "Unknown User"
            
            duration = self._get_ticket_duration(ticket_data['created_at'])
            
            embed.add_field(
                name=f"🎫 {ticket_data['channel_name']}",
                value=(
                    f"👤 **User:** {username}\n"
                    f"🎯 **Type:** {ticket_data['ticket_type']}\n"
                    f"⏱️ **Age:** {duration}\n"
                    f"📝 **Reason:** {ticket_data['reason'][:50]}{'...' if len(ticket_data['reason']) > 50 else ''}"
                ),
                inline=True
            )
        
        if len(self.active_tickets) > 10:
            embed.add_field(
                name="📋 Note",
                value=f"Showing first 10 of {len(self.active_tickets)} total tickets",
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_ready(self):
        """Set up persistent views when bot starts"""
        # Add the persistent views so dropdowns and buttons work after bot restart
        self.bot.add_view(TicketView(self.bot))
        self.bot.add_view(TicketActionView())
    
    @tasks.loop(hours=1)
    async def auto_close_tickets(self):
        """Auto-close old inactive tickets"""
        current_time = datetime.now(timezone.utc)
        tickets_to_close = []
        
        for channel_id, ticket_data in self.active_tickets.items():
            try:
                created_at = datetime.fromisoformat(ticket_data['created_at'])
                # Make created_at timezone-aware if it isn't
                if created_at.tzinfo is None:
                    created_at = created_at.replace(tzinfo=timezone.utc)
                age_hours = (current_time - created_at).total_seconds() / 3600
                
                if age_hours >= config.TICKET_CONFIG['auto_close_hours']:
                    channel = self.bot.get_channel(int(channel_id))
                    if channel:
                        # Check for recent activity
                        has_recent_activity = False
                        async for message in channel.history(limit=50):
                            message_age = (current_time - message.created_at).total_seconds() / 3600
                            if message_age < 24 and not message.author.bot:  # 24 hours
                                has_recent_activity = True
                                break
                        
                        if not has_recent_activity:
                            tickets_to_close.append((channel, ticket_data))
            except Exception as e:
                logger.error(f"❌ Error checking ticket age: {e}")
        
        # Close old tickets
        for channel, ticket_data in tickets_to_close:
            try:
                embed = self.create_ticket_embed(
                    "Auto-Closing Inactive Ticket",
                    (
                        f"🔒 This ticket is being automatically closed due to inactivity.\n\n"
                        f"**Reason:** No activity for {config.TICKET_CONFIG['auto_close_hours']} hours\n"
                        f"📅 **Created:** {ticket_data['created_at']}\n"
                        f"💬 **Need help?** Create a new ticket anytime!\n\n"
                        f"This channel will be deleted in 5 minutes."
                    ),
                    color=0xFF6B6B,
                    guild=channel.guild
                )
                
                await channel.send(embed=embed)
                
                # Update ticket data
                ticket_data['status'] = 'auto_closed'
                ticket_data['closed_at'] = current_time.isoformat()
                ticket_data['close_reason'] = 'Auto-closed due to inactivity'
                
                # Generate transcript
                await self._generate_transcript(channel, self.bot.user, "Auto-closed due to inactivity")
                
                # Remove from tracking
                user_id = str(ticket_data['user_id'])
                if user_id in self.user_tickets and channel.id in self.user_tickets[user_id]:
                    self.user_tickets[user_id].remove(channel.id)
                
                del self.active_tickets[str(channel.id)]
                
                # Delete channel after delay
                await asyncio.sleep(300)  # 5 minutes
                await channel.delete(reason="Auto-closed due to inactivity")
                
                logger.info(f"✅ Auto-closed ticket {channel.name}")
                
            except Exception as e:
                logger.error(f"❌ Error auto-closing ticket: {e}")
        
        if tickets_to_close:
            self.save_ticket_data()
    
    @auto_close_tickets.before_loop
    async def before_auto_close(self):
        """Wait for bot to be ready before starting auto-close task"""
        await self.bot.wait_until_ready()

async def setup(bot):
    """Setup function for the cog"""
    await bot.add_cog(TicketSystem(bot))
    logger.info("✅ Ticket system cog loaded successfully")