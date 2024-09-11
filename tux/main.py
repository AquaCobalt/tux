import asyncio

import discord
import sentry_sdk
from discord.ext import commands
from loguru import logger
from sentry_sdk.integrations.asyncio import AsyncioIntegration
from sentry_sdk.integrations.loguru import LoguruIntegration

from tux.bot import Tux
from tux.database.controllers.guild_config import GuildConfigController
from tux.help import TuxHelp
from tux.utils.config import CONFIG

# from tux.utils.console import Console


async def get_prefix(bot: Tux, message: discord.Message) -> list[str]:
    prefix: str | None = None

    if message.guild:
        prefix = await GuildConfigController().get_guild_prefix(message.guild.id)

    return commands.when_mentioned_or(prefix or CONFIG.DEFAULT_PREFIX)(bot, message)


async def main() -> None:
    if not CONFIG.TUX_TOKEN:
        logger.critical("No token provided, exiting.")
        return

    logger.info("Setting up Sentry...")

    sentry_sdk.init(
        dsn=CONFIG.SENTRY_URL,
        environment="dev" if CONFIG.TUX_ENV == "dev" else "prod",
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
        enable_tracing=True,
        integrations=[AsyncioIntegration(), LoguruIntegration()],
    )

    logger.info(f"Sentry setup intitalized: {sentry_sdk.is_initialized()}")

    bot = Tux(
        command_prefix=get_prefix,
        strip_after_prefix=True,
        case_insensitive=True,
        intents=discord.Intents.all(),
        owner_ids=[*CONFIG.SYSADMIN_IDS, CONFIG.BOT_OWNER_ID],
        allowed_mentions=discord.AllowedMentions(everyone=False),
        help_command=TuxHelp(),
    )

    # Initialize the console and console task
    # console = None
    # console_task = None
    try:
        # console = Console(bot)
        # console_task = asyncio.create_task(console.run_console())

        await bot.start(token=CONFIG.TUX_TOKEN, reconnect=True)

    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt received, shutting down.")

    finally:
        logger.info("Closing resources...")
        await bot.shutdown()

        # Cancel the console task if it's still running
        # if console_task is not None and not console_task.done():
        # console_task.cancel()
        # Suppress the CancelledError exception
        # with contextlib.suppress(asyncio.CancelledError):
        # await console_task

    logger.info("Bot shutdown complete.")


if __name__ == "__main__":
    try:
        # Run the bot using asyncio
        asyncio.run(main())

    except KeyboardInterrupt:
        # Handle KeyboardInterrupt gracefully
        logger.info("Exiting gracefully.")
