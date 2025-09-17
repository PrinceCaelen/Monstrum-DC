"""
Game Information Cog for Monstrum Discord Bot
Posts formatted information about the Monstrum game

Features:
- Setup command for about-this-game channel
- Rich embeds with server branding
- Game information formatting
"""

import discord
from discord.ext import commands
import logging
import config

logger = logging.getLogger(__name__)

class AboutChannelSetup(commands.Cog):
    """Game information and setup commands"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='setupgameinfo', aliases=['setupabout'])
    @commands.has_permissions(administrator=True)
    async def setup_game_info(self, ctx):
        """Post the formatted game information in this channel"""
        
        embed = discord.Embed(
            title="📖 About Monstrum",
            description="🕯️ **Fear the dark. Trust the light.**",
            color=config.EMBED_COLORS['info']
        )
        
        # Add server icon as thumbnail
        if ctx.guild.icon:
            embed.set_thumbnail(url=ctx.guild.icon.url)
        
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
            "🌑 **Unique Environments** – From forsaken villages to haunted asylums.\n"
            "👹 **Different Monsters** – Every location has its own terrifying predator.\n"
            "⚙️ **Distinct Mechanics** – New challenges, puzzles, and rituals on every map.\n"
            "🕷️ **Stealth & Hiding** – Stay silent to avoid being detected… or become prey."
        )
        
        embed.add_field(
            name="🗺️ Each Map Tells a Different Story",
            value=map_info,
            inline=False
        )
        
        # Game features
        features = (
            "🤝 **1–4 Player Co-Op** – Survive together or die alone.\n"
            "🔦 **UV Flashlight Combat** – Burn lesser monsters, but save your power wisely.\n"
            "📜 **Rituals & Lore** – Discover the truth hidden in each cursed place.\n"
            "🗺️ **Multiple Maps** – Each with unique stories, enemies, and mechanics.\n"
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
        
        # Add server branding
        if ctx.guild.icon:
            embed.set_author(
                name=f"{ctx.guild.name} Community",
                icon_url=ctx.guild.icon.url
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
    
    @commands.command(name='aboutgame')
    @commands.cooldown(1, 300, commands.BucketType.guild)  # 5 minute cooldown
    async def about_game(self, ctx):
        """Display information about Monstrum (public command with cooldown)"""
        
        embed = discord.Embed(
            title="📖 About Monstrum",
            description="🕯️ **Fear the dark. Trust the light.**",
            color=config.EMBED_COLORS['info']
        )
        
        # Add server icon as thumbnail
        if ctx.guild.icon:
            embed.set_thumbnail(url=ctx.guild.icon.url)
        
        # Condensed version for public use
        game_description = (
            "**Monstrum** is a 1–4 player co-op horror experience for mobile.\n\n"
            "🔦 **UV Flashlight Combat** – Your only weapon against lesser creatures\n"
            "📜 **Ancient Rituals** – Banish greater monstrosities with cursed relics\n"
            "🕷️ **Stealth & Survival** – Sometimes hiding is your only option\n"
            "🗺️ **Multiple Maps** – Each with unique stories and terrors"
        )
        
        embed.add_field(
            name="🎮 Survive the Nightmare",
            value=game_description,
            inline=False
        )
        
        embed.add_field(
            name="🌑 Will you survive?",
            value="**Conquer the darkness… or hide until it swallows you whole.**",
            inline=False
        )
        
        embed.set_footer(text=config.BOT_FOOTER)
        embed.timestamp = discord.utils.utcnow()
        
        await ctx.send(embed=embed)

async def setup(bot):
    """Setup function for the cog"""
    await bot.add_cog(AboutChannelSetup(bot))
    logger.info("✅ About channel setup cog loaded successfully")