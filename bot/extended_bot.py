from discord.ext.commands import Bot
from assets.exceptions import MissingParameterError
from assets.constants import PREFIX
from .devtools import DevTool, DevCommandNotFound, TransformationError, __implement_dev_commands__
import assets.messages as msgs


class ExtendedBot(Bot):
    """
    Adds some new features to the discord.ext.commands.Bot class, such as a dev-tool and confirmations
    """

    def __init__(self, *args, **kwargs):
        self._waiting_for_confirmations = {}
        self.devtool = DevTool()
        self.devmode = False

        Bot.__init__(self, *args, **kwargs)

        @self.command(help="Confirme une commande")
        async def confirm(ctx): pass
        @self.command(help="Annule une commande")
        async def cancel(ctx): pass

        __implement_dev_commands__(self)

    async def process_commands(self, message):
        """
        Process the command(s) contained in message.
        If the devmode is off, we just process normally the commands with Bot.process_commands().
        Else we try to handle this command using the DevTool.
        """
        if not message.content.strip().startswith(PREFIX):
            return

        if not self.devmode:
            return await Bot.process_commands(self, message)

        try: return await self.devtool.process_commands(message)
        except DevCommandNotFound: pass

        try:
            command = self.all_commands[message.content.split()[0][1:]]
            ctx = await self.get_context(message)

            checks = []

            # We apply the checks using the right context
            for check in command.checks.copy():
                try:
                    check(ctx)
                except Exception as e:
                    await ctx.channel.send(str(e))

                command.checks.remove(check)  # We remove it temporary...
                checks.append(check)  # And we store it to restore the command's old state when the work is done

            # Then we transform the context
            ctx = self.devtool.transform_ctx(ctx)

            # Finally we invoke the commands, with removed checks.
            ret = await command.invoke(ctx)
            command.checks = checks
            return ret

        except KeyError:
            await message.channel.send("Erreur : la commande %s n'existe pas." % message.content.split()[0][1:])

        except TransformationError as e:
            await message.channel.send(str(e))

        except Exception as e:
            await message.channel.send(str(e))

    async def confirm(self, user, command, confirm='$confirm', cancel='$cancel'):
        """
        Waits for a confirmation or a cancellation message from the discord User USER for the command COMMAND.
        Raises a RuntimeError if self was already waiting for a confirmation for that user.

        Returns

        True -- the user confirmed
        False -- the user canceled

        Raises

        RuntimeError -- Already waiting for a confirmation
        """

        self.check_can_confirm(user)

        self._waiting_for_confirmations[user] = command
        confirmation = await self.wait_for('message', check=lambda m: m.content.strip() in [confirm, cancel])
        del self._waiting_for_confirmations[user]

        return True if confirmation.content == confirm else False

    def check_can_confirm(self, user):
        """Checks that self isn't waiting for a confirmation from USER, else raises a RuntimeError"""
        already_waiting = self._waiting_for_confirmations.get(user)
        if already_waiting:
            raise RuntimeError(msgs.ALREADY_WAITING % already_waiting)

    @staticmethod
    def check_parameter(parameter, syntax, parameter_name):
        """Checks that parameter is not None, else raises MissingParameterError(ERR_MSG)"""
        if parameter is None:
            raise MissingParameterError(msgs.MISSING_PARAMETER % (syntax, parameter_name))

    @staticmethod
    def check_not_too_much_parameters(too_much, expected_syntax):
        """Checks that too_much is empty or None, else raises a ValueError."""
        if too_much:
            raise ValueError(msgs.TOO_MUCH_PARAMETERS % expected_syntax, "', '".join(too_much))
