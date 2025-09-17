"""
Game Information Cog for Monstrum Discord Bot
Admin-controlled commands for posting game information and announcements

Features:
- Rich embeds for game information
- Monster information commands
- Update and patch note posting
- Admin-only controls
- Beautiful formatting with images and fields
"""

import discord
from discord.ext import commands
import logging
import random
from datetime import datetime
import config

logger = logging.getLogger(__name__)

class GameInfo(commands.Cog):
    """Game information and announcement system"""
    
    def __init__(self, bot):
        self.bot = bot
    
    def create_game_embed(self, title, description, color=None):
        """Create a standard game info embed"""
        embed = discord.Embed(
            title=title,
            description=description,
            color=color or config.EMBED_COLORS['game_info']
        )
        embed.set_footer(text=config.BOT_FOOTER)
        embed.timestamp = discord.utils.utcnow()
        return embed
    
    @commands.group(name='game', aliases=['gameinfo'], invoke_without_command=True)
    async def game_info_group(self, ctx):
        """Game information commands"""
        if ctx.invoked_subcommand is None:
            embed = self.create_game_embed(
                "🎮 Game Information Commands",
                (
                    "Use these commands to get information about Monstrum:\n\n"
                    f"`{ctx.prefix}game about` - General game information\n"
                    f"`{ctx.prefix}game monsters` - Information about all monsters\n"
                    f"`{ctx.prefix}game monster <name>` - Specific monster info\n"
                    f"`{ctx.prefix}game tips` - Survival tips\n"
                    f"`{ctx.prefix}game links` - Official links and resources\n\n"
                    "**Admin Commands:**\n"
                    f"`{ctx.prefix}game announce` - Post game announcements\n"
                    f"`{ctx.prefix}game update` - Post update information\n"
                    f"`{ctx.prefix}game news` - Post news updates"
                )
            )
            await ctx.send(embed=embed)
    
    @game_info_group.command(name='about')
    @commands.cooldown(1, 10, commands.BucketType.guild)
    async def game_about(self, ctx):
        """General information about Monstrum"""
        game = config.GAME_INFO
        
        embed = self.create_game_embed(
            f"🚢 {game['name']} - Game Information",
            game['description']
        )
        
        embed.add_field(
            name="🎯 Game Details",
            value=(
                f"**Developer:** {game['developer']}\n"
                f"**Genre:** {game['genre']}\n"
                f"**Release:** {game['release_date']}\n"
                f"**Platforms:** {', '.join(game['platforms'])}"
            ),
            inline=True
        )
        
        embed.add_field(
            name="🎮 Gameplay",
            value=(
                "• Survive terrifying encounters\n"
                "• Explore detailed mobile maps\n"
                "• Face unique monsters\n"
                "• Mobile-optimized controls\n"
                "• Intense horror atmosphere"
            ),
            inline=True
        )
        
        embed.add_field(
            name="� Download Links",
            value=(
                f"[📱 iOS App Store]({game.get('mobile_stores', {}).get('ios', '#')})\n"
                f"[🤖 Google Play Store]({game.get('mobile_stores', {}).get('android', '#')})\n"
                f"[� Official Website]({game['official_website']})"
            ),
            inline=False
        )
        
        embed.add_field(
            name="� Mobile Gaming",
            value="Optimized for mobile devices with touch controls and mobile-specific features!",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @game_info_group.command(name='monsters')
    @commands.cooldown(1, 10, commands.BucketType.guild) 
    async def game_monsters(self, ctx):
        """Information about all monsters in Monstrum"""
        embed = self.create_game_embed(
            "👹 Monstrum Entities",
            "Two deadly creatures roam different maps. Each requires different survival strategies."
        )
        
        for monster_key, monster in config.MONSTERS.items():
            abilities_text = "\n".join([f"• {ability}" for ability in monster['abilities']])
            
            embed.add_field(
                name=f"{monster['emoji']} {monster['name']}",
                value=(
                    f"**Map:** {monster['map']}\n"
                    f"**Description:** {monster['description']}\n"
                    f"**Abilities:**\n{abilities_text}\n"
                    f"**Weakness:** {monster['weakness']}"
                ),
                inline=False
            )
        
        embed.add_field(
            name="💡 Survival Tip",
            value="Learning each monster's behavior is key to survival. Listen for audio cues and adapt your strategy!",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @game_info_group.command(name='monster')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def game_monster(self, ctx, monster_name: str = None):
        """Detailed information about a specific monster"""
        if not monster_name:
            await ctx.send("Please specify a monster: `hutman` or `shaytan`")
            return
        
        monster_key = monster_name.lower()
        if monster_key not in config.MONSTERS:
            await ctx.send("Monster not found! Available: `hutman`, `shaytan`")
            return
        
        monster = config.MONSTERS[monster_key]
        
        embed = self.create_game_embed(
            f"{monster['emoji']} {monster['name']} - Entity Profile",
            monster['description']
        )
        
        # Add map information
        embed.add_field(
            name="🗺️ Location",
            value=f"📍 {monster['map']}",
            inline=True
        )
        
        # Abilities
        abilities_text = "\n".join([f"🔸 {ability}" for ability in monster['abilities']])
        embed.add_field(
            name="⚡ Abilities",
            value=abilities_text,
            inline=True
        )
        
        # Weakness
        embed.add_field(
            name="🎯 Weakness",
            value=f"🔸 {monster['weakness']}",
            inline=True
        )
        
        # Survival tips based on monster
        tips = {
            'hutman': [
                "Stay away from main streets - he knows the town layout",
                "Use buildings for cover from his revolver",
                "His madness makes him unpredictable - don't assume patterns",
                "Quick movements and silence are your allies"
            ],
            'shaytan': [
                "Avoid dark corners where demons can spawn",
                "Keep moving - her demons will track you if you stay still",
                "Look for holy symbols or blessed items if available",
                "Her supernatural presence distorts reality - trust your instincts"
            ]
        }
        
        embed.add_field(
            name="💡 Survival Tips",
            value="\n".join([f"• {tip}" for tip in tips[monster_key]]),
            inline=False
        )
        
        # Threat rating
        threat_levels = {
            'hutman': "� EXTREME - Armed and unstable sheriff",
            'shaytan': "👹 MAXIMUM - Demonic entity with summoning powers"
        }
        
        embed.add_field(
            name="⚠️ Threat Assessment",
            value=threat_levels[monster_key],
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @game_info_group.command(name='tips')
    @commands.cooldown(1, 15, commands.BucketType.guild)
    async def game_tips(self, ctx):
        """General survival tips for Monstrum"""
        tips = [
            "🔦 **Manage your flashlight battery** - Darkness is deadly, but light can attract attention",
            "🚪 **Close doors behind you** - It slows down pursuing monsters",
            "👂 **Listen carefully** - Each monster has distinct audio cues",
            "🗺️ **Learn the ship layout** - Knowing escape routes is crucial",
            "📦 **Search systematically** - Items spawn in specific locations",
            "⚙️ **Check your escape method** - Helicopter, submarine, or raft each need different items",
            "🏃 **Know when to run** - Sometimes stealth isn't an option",
            "💡 **Use distractions** - Throw items to create noise and mislead monsters",
            "🔧 **Prioritize key items** - Focus on items needed for your escape method",
            "🎯 **Stay calm** - Panic leads to mistakes, and mistakes lead to death"
        ]
        
        embed = self.create_game_embed(
            "💡 Survival Guide - Monstrum Tips",
            "Essential knowledge for surviving aboard the cursed vessel"
        )
        
        # Split tips into two fields for better formatting
        half = len(tips) // 2
        embed.add_field(
            name="🎯 Core Survival Tips",
            value="\n\n".join(tips[:half]),
            inline=False
        )
        
        embed.add_field(
            name="⚡ Advanced Strategies", 
            value="\n\n".join(tips[half:]),
            inline=False
        )
        
        embed.add_field(
            name="🆘 Emergency Protocol",
            value="If you're being chased: **BREAK LINE OF SIGHT** → **CHANGE DIRECTION** → **FIND HIDING SPOT**",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @game_info_group.command(name='links')
    @commands.cooldown(1, 20, commands.BucketType.guild)
    async def game_links(self, ctx):
        """Official game links and resources"""
        game = config.GAME_INFO
        
        embed = self.create_game_embed(
            "🔗 Official Monstrum Links & Resources",
            "Connect with the community and stay updated on the latest news"
        )
        
        embed.add_field(
            name="📱 Mobile Download",
            value=(
                f"[📱 iOS App Store]({game.get('mobile_stores', {}).get('ios', '#')})\n"
                f"[🤖 Google Play Store]({game.get('mobile_stores', {}).get('android', '#')})\n"
                f"[🌐 Official Website]({game['official_website']})\n"
                f"[🎮 Steam (Future PC Release)]({game['steam_url']})"
            ),
            inline=True
        )
        
        embed.add_field(
            name="📚 Community Resources",
            value=(
                "[📖 Game Guides](https://example.com/guides)\n"
                "[💬 Discord Community](https://discord.gg/monstrum)\n"
                "[🎥 Gameplay Videos](https://www.youtube.com/results?search_query=monstrum+mobile)\n"
                "[📝 Tips & Tricks](https://example.com/tips)"
            ),
            inline=True
        )
        
        embed.add_field(
            name="� Where to Download",
            value=(
                f"[📱 iOS App Store]({game.get('mobile_stores', {}).get('ios', '#')})\n"
                f"[🤖 Google Play Store]({game.get('mobile_stores', {}).get('android', '#')})\n"
                "🖥️ **PC Version:** Coming Soon!\n"
                "🎮 **Console Versions:** Under Consideration"
            ),
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='setupaboutchannel')
    @commands.has_permissions(administrator=True)
    async def setup_about_channel(self, ctx):
        """Post the formatted game information about Monstrum in this channel"""
        
        embed = discord.Embed(
            title="📖 About Monstrum",
            description="🕯️ **Fear the dark. Trust the light.**",
            color=config.EMBED_COLORS['info']
        )
        
        # Add server icon as thumbnail and author
        if ctx.guild.icon:
            embed.set_thumbnail(url=ctx.guild.icon.url)
            embed.set_author(
                name=f"{ctx.guild.name} Community",
                icon_url=ctx.guild.icon.url
            )
        
        # Main game description
        game_description = (
            "**Monstrum** is a 1–4 player co-op horror experience built for mobile, where survival depends on teamwork, courage, and silence.\n\n"
            "Every player carries a UV flashlight – your only weapon against the lesser creatures that lurk in the dark. But the greater monstrosities cannot be stopped by light alone. To banish them, you must uncover cursed relics and perform ancient rituals before the nightmare consumes you.\n\n"
            "But light comes at a cost: the enemy hears you, hunts you, and adapts. Sometimes the only way to survive is to hide in the shadows, holding your breath while the horror passes by."
        )
        
        embed.add_field(
            name="🎮 Game Overview",
            value=game_description,
            inline=False
        )
        
        # Map features
        map_info = (
            "🌑 **Unique Environments** – From forsaken villages to haunted asylums.\n\n"
            "👹 **Different Monsters** – Every location has its own terrifying predator.\n\n"
            "⚙️ **Distinct Mechanics** – New challenges, puzzles, and rituals on every map.\n\n"
            "🕷️ **Stealth & Hiding** – Stay silent to avoid being detected… or become prey."
        )
        
        embed.add_field(
            name="🗺️ Each Map Tells a Different Story",
            value=map_info,
            inline=False
        )
        
        # Game features
        features = (
            "🤝 **1–4 Player Co-Op** – Survive together or die alone.\n\n"
            "🔦 **UV Flashlight Combat** – Burn lesser monsters, but save your power wisely.\n\n"
            "📜 **Rituals & Lore** – Discover the truth hidden in each cursed place.\n\n"
            "🗺️ **Multiple Maps** – Each with unique stories, enemies, and mechanics.\n\n"
            "📱 **Stylized Horror for Mobile** – Terrifying atmosphere, anytime, anywhere."
        )
        
        embed.add_field(
            name="✨ Features",
            value=features,
            inline=False
        )
        
        # Final question
        embed.add_field(
            name="🌑 The Question Remains...",
            value="**Will you conquer the darkness…\nOr hide until it swallows you whole?**",
            inline=False
        )
        
        embed.set_footer(
            text=f"Welcome to {ctx.guild.name} • {config.BOT_FOOTER}",
            icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None
        )
        embed.timestamp = discord.utils.utcnow()
        
        # Send the embed
        await ctx.send(embed=embed)
        
        # Send a simple confirmation reaction instead of DM
        await ctx.message.add_reaction("✅")
        
        logger.info(f"✅ Game info posted in {ctx.channel.name} by {ctx.author.name}")
    
    # Admin-only commands for posting announcements
    @game_info_group.command(name='announce', hidden=True)
    @commands.has_permissions(administrator=True)
    async def post_announcement(self, ctx, *, content: str):
        """Post a game announcement (Admin only)"""
        channel = self.bot.get_channel(config.ANNOUNCEMENTS_CHANNEL_ID)
        if not channel:
            await ctx.send("❌ Announcements channel not configured!")
            return
        
        embed = self.create_game_embed(
            "📢 Monstrum Community Announcement",
            content,
            config.EMBED_COLORS['info']
        )
        
        embed.set_author(
            name=f"Announced by {ctx.author.display_name}",
            icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url
        )
        
        await channel.send("@everyone", embed=embed)
        await ctx.send("✅ Announcement posted!")
        logger.info(f"Announcement posted by {ctx.author.name}: {content[:50]}...")
    
    @game_info_group.command(name='update', hidden=True)
    @commands.has_permissions(administrator=True)
    async def post_update(self, ctx, version: str, *, changes: str):
        """Post a game update (Admin only)"""
        channel = self.bot.get_channel(config.ANNOUNCEMENTS_CHANNEL_ID)
        if not channel:
            await ctx.send("❌ Announcements channel not configured!")
            return
        
        embed = self.create_game_embed(
            f"🔄 Monstrum Update {version}",
            "A new update has been released for Monstrum!",
            config.EMBED_COLORS['success']
        )
        
        embed.add_field(
            name="📋 Changelog",
            value=changes,
            inline=False
        )
        
        embed.add_field(
            name="💡 How to Update",
            value=(
                "• **Steam**: Updates automatically\n"
                "• **Console**: Check your platform's store\n"
                "• **Epic Games**: Use the Epic Games Launcher"
            ),
            inline=False
        )
        
        embed.set_author(
            name=f"Update posted by {ctx.author.display_name}",
            icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url
        )
        
        await channel.send("🎮 @everyone New update available!", embed=embed)
        await ctx.send("✅ Update information posted!")
        logger.info(f"Update {version} posted by {ctx.author.name}")
    
    @game_info_group.command(name='news', hidden=True)
    @commands.has_permissions(administrator=True)
    async def post_news(self, ctx, title: str, *, content: str):
        """Post game news (Admin only)"""
        channel = self.bot.get_channel(config.ANNOUNCEMENTS_CHANNEL_ID)
        if not channel:
            await ctx.send("❌ Announcements channel not configured!")
            return
        
        embed = self.create_game_embed(
            f"📰 {title}",
            content,
            config.EMBED_COLORS['game_info']
        )
        
        embed.set_author(
            name="Monstrum News",
            icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None
        )
        
        embed.add_field(
            name="📅 Posted",
            value=discord.utils.format_dt(datetime.now(), style='F'),
            inline=True
        )
        
        embed.add_field(
            name="👤 Author",
            value=ctx.author.display_name,
            inline=True
        )
        
        await channel.send(embed=embed)
        await ctx.send("✅ News posted!")
        logger.info(f"News '{title}' posted by {ctx.author.name}")
    
    # Slash command example (currently commented out due to simplicity)
    # @discord.slash_command(name="gameinfo", description="Get information about Monstrum")
    async def slash_game_info(self, ctx, info_type: str = "about"):
        """Slash command for game information"""
        if info_type == "about":
            await self.game_about(ctx)
        elif info_type == "monsters":
            await self.game_monsters(ctx)
        elif info_type == "tips":
            await self.game_tips(ctx)
        elif info_type == "links":
            await self.game_links(ctx)
        else:
            # Default to about
            await self.game_about(ctx)

async def setup(bot):
    """Setup function for the cog"""
    await bot.add_cog(GameInfo(bot))
    logger.info("✅ Game info cog loaded successfully")