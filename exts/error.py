import logging
import discord
from collections import namedtuple

from discord.ext import commands
from lifesaver import Cog

from discord.ext.commands.errors import (
    CommandInvokeError,
    BadArgument,
    CommandOnCooldown,
    MissingRequiredArgument,
    NoPrivateMessage,
    UserInputError,
    MissingPermissions,
    BotMissingPermissions,
    CheckFailure,
)


log = logging.getLogger(__name__)

DMChan = namedtuple("DM", "id")


def _checks(ctx) -> list:
    return [c.__qualname__.split(".")[0] for c in ctx.command.checks]


def read_help(ctx) -> str:
    """Generate a reading help recommendation."""
    cog_name = ctx.cog.__class__.__name__
    cmd_name = ctx.command.name

    help_cog = f"`{ctx.prefix}help {cog_name}`"
    help_cmd = f"`{ctx.prefix}help {ctx.command.full_parent_name} {cmd_name}`"

    return (
        f"Read the documentation for the cog at {help_cog}\n"
        f"And for the command in {help_cmd}"
    )


class ErrorHandling(Cog):
    """Main error handling."""

    async def _handle_invoke_err(self, ctx, error):
        orig = error.original
        content = ctx.message.content

        # if isinstance(orig, self.SayException):
        #    arg0 = orig.args[0]

        #    if ctx.guild is None:
        #        ctx.guild = DMChan(ctx.author.id)

        #    log.warning(
        #        "SayException: %s[%d] %s %r => %r",
        #        ctx.guild,
        #        ctx.guild.id,
        #        ctx.author,
        #        content,
        #        arg0,
        #    )

        #    return await ctx.send(arg0)

        # if isinstance(orig, tuple(self.bot.simple_exc)):
        #     log.error("errored at %r from %s\n%r", content, ctx.author, orig)
        #     return await ctx.send(f"Error: `{error.original!r}` \n" f"{read_help(ctx)}")

        log.exception("errored at %r from %s", content, ctx.author, exc_info=orig)

        # if isinstance(orig, self.bot.cogs["Coins"].TransferError):
        #     return await ctx.send(f"JoséCoin error: `{orig!r}`")

        return await ctx.send(
            "An error happened during command execution:"
            f"```py\n{error.original!r}```"
        )

    async def _err(self, ctx, msg: str):
        await ctx.send(f"{msg}\n" f"{read_help(ctx)}")

    async def _handle_bad_arg(self, ctx, error):
        await self._err(ctx, "bad argument —  " f"{error!s}")

    async def _handle_dummy(self, _ctx, _error):
        pass

    async def _handle_missing_arg(self, ctx, error):
        await self._err(ctx, f"missing argument — `{error.param}`")

    async def _handle_no_dm(self, ctx, _error):
        await self._err(ctx, "Command is unusable in a DM")

    async def _handle_user_input(self, ctx, _error):
        await self._err(ctx, "User input error")

    async def _handle_check_fail(self, ctx, _error):
        checks = _checks(ctx)
        await self._err(ctx, f'check error — checks: `{", ".join(checks)}`')

    async def _handle_missing_perms(self, ctx, error):
        join = ", ".join(error.missing_perms)
        await self._err(ctx, f"you are missing permissions — `{join}`")

    async def _handle_bot_missing_perms(self, ctx, error):
        join = ", ".join(error.missing_perms)
        await self._err(ctx, f"bot is missing permissions — `{join}`")

    @Cog.listener()
    async def on_command_error(self, ctx, error):
        """Log and signal errors to the user"""

        handler = {
            CommandInvokeError: self._handle_invoke_err,
            BadArgument: self._handle_bad_arg,
            CommandOnCooldown: self._handle_dummy,
            MissingRequiredArgument: self._handle_missing_arg,
            NoPrivateMessage: self._handle_no_dm,
            UserInputError: self._handle_user_input,
            MissingPermissions: self._handle_missing_perms,
            BotMissingPermissions: self._handle_bot_missing_perms,
            CheckFailure: self._handle_check_fail,
        }.get(error.__class__)

        if handler is None:
            return

        try:
            await handler(ctx, error)
        except Exception:
            log.exception("error while handling error")
            await ctx.error("An error happened while handling the error.")

    @Cog.listener()
    async def on_error(self, event_method, *args, **kwargs):
        """handle any error while doing an event"""
        # TODO: analyze current exception
        # and simplify the logging to WARN
        # if it is on self.simple_exc

        log.exception("evt error (%s) args=%r kwargs=%r", event_method, args, kwargs)

    @Cog.listener()
    async def on_command(self, ctx):
        """Log command usage"""
        # thanks dogbot ur a good
        content = ctx.message.content

        author = ctx.message.author
        guild = ctx.guild
        checks = _checks(ctx)
        location = (
            "[DM]"
            if isinstance(ctx.channel, discord.DMChannel)
            else f"[Guild {guild.name} {guild.id}]"
        )

        checks = ",".join(checks) or "()"
        log.info(
            '[c] %s %s %d "%s" chk=%s', location, author, author.id, content, checks
        )


def setup(bot):
    bot.add_cog(ErrorHandling(bot))
