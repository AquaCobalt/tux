import discord
from discord.ext import commands
from loguru import logger

from tux.utils import checks


class Dev(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.hybrid_group(
        name="dev",
        aliases=["d"],
        usage="dev <subcommand>",
    )
    @commands.guild_only()
    @checks.has_pl(8)
    async def dev(self, ctx: commands.Context[commands.Bot]) -> None:
        """
        Dev related commands.

        Parameters
        ----------
        ctx : commands.Context[commands.Bot]
            The context object for the command.

        Raises
        ------
        commands.MissingPermissions
            If the user does not have the required permissions
        commands.CommandInvokeError
            If the subcommand is not found.
        """
        if ctx.invoked_subcommand is None:
            await ctx.send_help("dev")

    @dev.command(
        name="sync_tree",
        aliases=["st", "sync", "s"],
        usage="dev sync_tree [guild]",
    )
    @commands.guild_only()
    @checks.has_pl(8)
    async def sync_tree(self, ctx: commands.Context[commands.Bot], guild: discord.Guild) -> None:
        """
        Syncs the app command tree.

        Parameters
        ----------
        ctx : commands.Context
            The context in which the command is being invoked.
        guild : discord.Guild
            The guild to sync application commands to.

        Raises
        ------
        commands.MissingRequiredArgument
            If a guild is not specified.
        """

        if ctx.guild is None:
            await ctx.send("This command can only be used in a server.", ephemeral=True, delete_after=30)
            return

        # Copy the global tree to the guild
        self.bot.tree.copy_global_to(guild=ctx.guild)
        # Sync the guild tree
        await self.bot.tree.sync(guild=ctx.guild)
        await ctx.send("Application command tree synced.")

    @dev.command(
        name="clear_tree",
        aliases=["ct", "clear", "c"],
        usage="dev clear_tree",
    )
    @commands.guild_only()
    @checks.has_pl(8)
    async def clear_tree(self, ctx: commands.Context[commands.Bot]) -> None:
        """
        Clears the app command tree.

        Parameters
        ----------
        ctx : commands.Context
            The context in which the command is being invoked.

        Raises
        ------
        commands.MissingPermissions
            If the user does not have the required permissions.
        """

        if ctx.guild is None:
            await ctx.send("This command can only be used in a guild.", ephemeral=True, delete_after=30)
            return

        # Clear the slash command tree for the guild.
        self.bot.tree.clear_commands(guild=ctx.guild)
        # Copy the global slash commands to the guild.
        self.bot.tree.copy_global_to(guild=ctx.guild)
        # Sync the slash command tree for the guild.
        await self.bot.tree.sync(guild=ctx.guild)

        await ctx.send("Slash command tree cleared.")

    @dev.command(
        name="load_cog",
        aliases=["lc", "load", "l"],
        usage="dev load_cog [cog]",
    )
    @commands.guild_only()
    @checks.has_pl(8)
    async def load_cog(self, ctx: commands.Context[commands.Bot], *, cog: str) -> None:
        """
        Loads a cog into the bot.

        Parameters
        ----------
        ctx : commands.Context
            The context in which the command is being invoked.
        cog : str
            The name of the cog to load.

        Raises
        ------
        commands.MissingRequiredArgument
            If an cog is not specified.
        commands.ExtensionAlreadyLoaded
            If the specified cog is already loaded.
        commands.ExtensionNotFound
            If the specified cog is not found.
        commands.ExtensionFailed
            If the cog failed to load.
        commands.NoEntryPointError
            If the specified cog does not have a setup function.
        """

        try:
            await self.bot.load_extension(cog)
        except Exception as error:
            await ctx.send(f"Failed to load cog {cog}: {error}")
            logger.error(f"Failed to load cog {cog}: {error}")
        else:
            await ctx.send(f"Cog {cog} loaded.")
            logger.info(f"Cog {cog} loaded.")

    @dev.command(
        name="unload_cog",
        aliases=["uc", "unload", "u"],
        usage="dev unload_cog [cog]",
    )
    @commands.guild_only()
    @checks.has_pl(8)
    async def unload_cog(self, ctx: commands.Context[commands.Bot], *, cog: str) -> None:
        """
        Unloads a cog from the bot.

        Parameters
        ----------
        ctx : commands.Context
            The context in which the command is being invoked.
        cog : str
            The name of the cog to unload.

        Raises
        ------
        commands.MissingRequiredArgument
            If an extension name is not specified.
        commands.ExtensionNotLoaded
            If the specified extension is not loaded or doesn't exist.
        """

        try:
            await self.bot.unload_extension(cog)
        except Exception as error:
            logger.error(f"Failed to unload cog {cog}: {error}")
            await ctx.send(f"Failed to unload cog {cog}: {error}", ephemeral=True, delete_after=30)
        else:
            logger.info(f"Cog {cog} unloaded.")
            await ctx.send(f"Cog {cog} unloaded.", ephemeral=True, delete_after=30)

    @dev.command(
        name="reload_cog",
        aliases=["rc", "reload", "r"],
        usage="dev reload_cog [cog]",
    )
    @commands.guild_only()
    @checks.has_pl(8)
    async def reload_cog(self, ctx: commands.Context[commands.Bot], *, cog: str) -> None:
        """
        Reloads a cog in the bot.

        Parameters
        ----------
        ctx : commands.Context
            The context in which the command is being invoked.
        cog : str
            The name of the cog to reload.

        Raises
        ------
        commands.MissingRequiredArgument
            If an extension is not specified.
        commands.ExtensionNotLoaded
            If the specified extension is not loaded or doesn't exist.
        """

        try:
            await self.bot.unload_extension(cog)
            await self.bot.load_extension(cog)
        except Exception as error:
            await ctx.send(f"Failed to reload cog {cog}: {error}", ephemeral=True, delete_after=30)
            logger.error(f"Failed to reload cog {cog}: {error}")
        else:
            await ctx.send(f"Cog {cog} reloaded.", ephemeral=True, delete_after=30)
            logger.info(f"Cog {cog} reloaded.")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Dev(bot))
