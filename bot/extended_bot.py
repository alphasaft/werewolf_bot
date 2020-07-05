from discord.ext.commands import Bot
from assets.exceptions import MissingParameterError
from assets.utils import on_channel
import assets.messages as msgs


class ExtendedBot(Bot):
    """
    Adds some new features to the discord.ext.commands.Bot class, such as super-commands
    """

    def __init__(self, *args, **kwargs):
        self.sub_commands = {}
        self.waiting_for_confirmations = {}

        Bot.__init__(self, *args, **kwargs)

        @self.command()
        async def confirm(ctx): pass
        @self.command()
        async def cancel(ctx): pass

    def super_command(self, name, subcommands, *cmd_args, channel=None, contains=False, false_channel_warn=False,
                      **cmd_kwargs):
        """
        Create a super-command, that can call sub-commands.

        NAME -> str
        SUBCOMMANDS -> list | tuple

        Usage :

        bot.super_command('super', ['sub1', ...])

        @bot.sub_command
        def super_sub1(ctx, *args):
            pass

        Actually calls super_sub1 when someone types super sub1 [args...]
        """

        if channel:
            @self.command(name=name, *cmd_args, **cmd_kwargs)
            @on_channel(channel, contains, false_channel_warn)
            async def game(ctx, sub=None, *args):
                if not sub or sub not in subcommands:
                    if len(subcommands) > 1:
                        await ctx.channel.send("Error : %s command's first parameter should be %s"
                                     % (name, ", ".join(subcommands[:-1]) + ' or ' + subcommands[-1]))
                    else:
                        await ctx.channel.send("Error : %s command's first parameter should be %s"
                                     % (name, subcommands[0]))

                    return

                await self._invoke_subcommand(name + '_' + sub, ctx, *args)
        else:
            @self.command(name=name, *cmd_args, **cmd_kwargs)
            async def game(ctx, sub=None, *args):
                if not sub or sub not in subcommands:
                    if len(subcommands) > 1:
                        await ctx.channel.send("Error : %s command's first parameter should be %s"
                                     % (name, ", ".join(subcommands[:-1]) + ' or ' + subcommands[-1]))
                    else:
                        await ctx.channel.send("Error : %s command's first parameter should be %s"
                                     % (name, subcommands[0]))

                    return

                await self._invoke_subcommand(name + '_' + sub, ctx, *args)

    def sub_command(self, funct):
        """
        Create a sub-command, that would be called by a super-command.

        FUNCT -> function, no lambda

        USAGE :

        bot.super_command('super', ['sub1', ...])

        @bot.sub_command
        def super_sub1(ctx, *args):
            pass

        Actually calls super_sub1 when someone types super sub1 [args...]
        """
        self.sub_commands[funct.__name__] = funct
        return funct

    async def _invoke_subcommand(self, name, *args, **kwargs):
        await self.sub_commands[name](*args, **kwargs)

    async def confirm(self, user, command, confirm='!confirm', cancel='!cancel'):
        self.waiting_for_confirmations[user] = command
        confirmation = await self.wait_for('message', check=lambda m: m.content in [confirm, cancel])
        del self.waiting_for_confirmations[user]
        return True if confirmation.content == confirm else False

    def check_can_confirm(self, user):
        already_waiting = self.waiting_for_confirmations.get(user)
        if already_waiting:
            raise RuntimeError(msgs.ALREADY_WAITING %
                               already_waiting)

    @staticmethod
    def check_parameter(parameter, err_msg):
        """Check if parameter is not None, else raises MissingParameterError(ERR_MSG)"""
        if parameter is None:
            raise MissingParameterError(err_msg)

    @staticmethod
    def check_not_too_much_parameters(too_much, expected_syntax):
        if too_much:
            raise ValueError(msgs.TOO_MUCH_PARAMETERS % (expected_syntax, "', '".join(too_much)))
