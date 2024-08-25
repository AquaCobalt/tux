import discord
from discord.ext import commands
from loguru import logger

from prisma.enums import CaseType
from tux.utils import checks
from tux.utils.flags import KickFlags, generate_usage

from . import ModerationCogBase


class Kick(ModerationCogBase):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__(bot)
        self.kick.usage = generate_usage(self.kick, KickFlags)

    @commands.hybrid_command(
        name="kick",
        aliases=["k"],
    )
    @commands.guild_only()
    @checks.has_pl(2)
    async def kick(
        self,
        ctx: commands.Context[commands.Bot],
        target: discord.Member,
        *,
        flags: KickFlags,
    ) -> None:
        """
        Kick a user from the server.

        Parameters
        ----------
        ctx : commands.Context[commands.Bot]
            The context in which the command is being invoked.
        target : discord.Member
            The member to kick.
        flags : KickFlags
            The flags for the command. (reason: str, silent: bool)

        Raises
        ------
        discord.Forbidden
            If the bot is unable to kick the user.
        discord.HTTPException
            If an error occurs while kicking the user.
        """

        if ctx.guild is None:
            logger.warning("Kick command used outside of a guild context.")
            return

        moderator = ctx.author

        if not await self.check_conditions(ctx, target, moderator, "kick"):
            return

        try:
            await self.send_dm(ctx, flags.silent, target, flags.reason, "kicked")
            await ctx.guild.kick(target, reason=flags.reason)

        except (discord.Forbidden, discord.HTTPException) as e:
            logger.error(f"Failed to kick {target}. {e}")
            await ctx.send(f"Failed to kick {target}. {e}", delete_after=30, ephemeral=True)
            return

        case = await self.db.case.insert_case(
            case_target_id=target.id,
            case_moderator_id=ctx.author.id,
            case_type=CaseType.KICK,
            case_reason=flags.reason,
            guild_id=ctx.guild.id,
        )

        await self.handle_case_response(ctx, CaseType.KICK, case.case_id, flags.reason, target)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Kick(bot))
