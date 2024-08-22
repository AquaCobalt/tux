import discord
from discord import app_commands
from discord.ext import commands

from tux.utils.embeds import EmbedCreator


class Info(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    info = app_commands.Group(name="info", description="Information commands.")

    @info.command(name="server")
    async def server(self, interaction: discord.Interaction) -> None:
        """
        Show information about the server.

        Parameters
        ----------
        interaction : discord.Interaction
            The discord interaction object.
        """
        if not interaction.guild:
            return

        guild = interaction.guild
        owner = str(guild.owner) if guild.owner else "Unknown"

        embed = EmbedCreator.create_info_embed(
            title=guild.name,
            description="Here is some information about the server.",
            interaction=interaction,
        )

        embed.add_field(name="Members", value=str(guild.member_count))
        bots = sum(member.bot for member in guild.members if member.bot)
        embed.add_field(name="Bots", value=str(bots))
        embed.add_field(name="Boosts", value=str(guild.premium_subscription_count))
        embed.add_field(name="Vanity URL", value=str(guild.vanity_url_code or "None"))
        embed.add_field(name="Owner", value=owner)
        embed.add_field(name="Created", value=guild.created_at.strftime("%d/%m/%Y"))
        embed.add_field(name="ID", value=str(guild.id))

        embed.set_thumbnail(url=guild.icon)

        await interaction.response.send_message(embed=embed)

    @info.command(name="tux", description="Shows information about Tux.")
    async def tux(self, interaction: discord.Interaction) -> None:
        """
        Show information about Tux.

        Parameters
        ----------
        interaction : discord.Interaction
            The discord interaction object.
        """

        embed = EmbedCreator.create_info_embed(
            title="Tux",
            description="Tux is a Discord bot written in Python using discord.py.",
            interaction=interaction,
        )
        embed.add_field(
            name="GitHub",
            value="[View the source code](https://github.com/allthingslinux/tux)",
        )

        await interaction.response.send_message(embed=embed)

    @info.command(name="member", description="Shows information about a member.")
    async def member(self, interaction: discord.Interaction, member: discord.Member) -> None:
        """
        Show information about a member.

        Parameters
        ----------
        interaction : discord.Interaction
            The discord interaction object.
        member : discord.Member
            The member to get information about.
        """

        bot_status = "✅" if member.bot else "❌"
        joined = discord.utils.format_dt(member.joined_at, "R") if member.joined_at else "Unknown"
        created = discord.utils.format_dt(member.created_at, "R") if member.created_at else "Unknown"
        roles = ", ".join(role.mention for role in member.roles[1:]) if member.roles[1:] else "No roles"

        fetched_member = await self.bot.fetch_user(member.id)

        embed = EmbedCreator.create_info_embed(
            title=member.display_name,
            description="Here is some information about the member.",
            interaction=interaction,
        )

        embed.add_field(name="Bot?", value=bot_status, inline=False)
        embed.add_field(name="Username", value=member.name, inline=False)
        embed.add_field(name="ID", value=str(member.id), inline=False)
        embed.add_field(name="Joined", value=joined, inline=False)
        embed.add_field(name="Registered", value=created, inline=False)
        embed.add_field(name="Roles", value=roles, inline=False)

        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_image(url=fetched_member.banner)

        await interaction.response.send_message(embed=embed)

    @info.command(name="roles", description="Lists all roles in the server.")
    async def roles(self, interaction: discord.Interaction) -> None:
        """
        List all roles in the server.

        Parameters
        ----------
        interaction : discord.Interaction
            The discord interaction object.
        """
        if not interaction.guild:
            return

        guild = interaction.guild
        roles = [role.mention for role in guild.roles]

        embed = EmbedCreator.create_info_embed(
            title="Server Roles",
            description=f"Role list for {guild.name}",
            interaction=interaction,
        )

        embed.add_field(name="Roles", value=", ".join(roles), inline=False)

        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Info(bot))
