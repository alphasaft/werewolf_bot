from .base_step import BaseStep
from assets.utils import unpack
from assets.constants import HUNTER


class HunterStep(BaseStep):

    _done = False

    def __init__(self):
        BaseStep.__init__(
            self,
            active_roles=HUNTER,
            helps=("Utilisez `*kill unJoueur` pour tuer quelqu'un avant votre mort", "Le chasseur décide de sa cible")
        )

    async def start(self, roles, dialogs):
        self.__init__()
        if not roles.hunter or roles.hunter.alive or self._done:
            await BaseStep.end(self, roles, dialogs)
            return

        await roles.everyone.send(
            dialogs.hunter.injured.tell(hunter=roles.get_name_by_id(roles.hunter.user.id))
        )
        await roles.hunter.user.send(dialogs.hunter.turn.tell())

    async def on_player_quit(self, roles, dialogs):
        if not roles.hunter or roles.hunter.alive or self._done:
            await BaseStep.end(self, roles, dialogs)

    async def react(self, cmd, args, author, roles, dialogs, session, disable_checks=False):
        """
        React to a command, either kill or an alltimes cmd. Notice that the author doesn't need to be alive to use
        the kill command if he is the hunter
        """
        if author.role == HUNTER:
            await BaseStep.react(self, cmd, args, author, roles, dialogs, session, True)
        else:
            await BaseStep.react(self, cmd, args, author, roles, dialogs, session, False)

    async def kill_cmd(self, args, author, roles, dialogs):
        """ `*kill unJoueur>` : Tue ce joueur. Vous mourrez après."""
        try:
            target = unpack(args, "!kill unJoueur>")
            assert target != roles.get_name_by_id(author.user.id), dialogs.hunter.try_to_kill_himself()
            roles.check_has_player(target)
        except Exception as e:
            await self.error(to=author, msg=e)
            return

        await roles.kill(target)
        await roles.hunter.user.send(dialogs.hunter.kill.tell(
            target=target,
            role=roles.get_role_by_name(target).role)
        )
        await roles.everyone.exclude(roles.hunter.user.id).send(dialogs.hunter.die.tell(
            hunter=roles.get_name_by_id(roles.hunter.user.id),
            target=target,
            role=roles.get_role_by_name(target).role
        ))
        await self.end(roles, dialogs)

    async def help_cmd(self, args, author, roles, dialogs):
        """ `*help (full)` : Vous indique ce que vous devez faire ; tapez $help full pour un guide complet"""
        # We redefine help because its default comportment is to send the external help if the author is dead
        if author.role == HUNTER:
            await self.info(to=author, msg=self.active_help)
        else:
            await self.info(to=author, msg=self.external_help)

    async def end(self, roles, dialogs):
        self.__class__._done = True  # The hunter can't die twice so this step is definitively over
        await BaseStep.end(self, roles, dialogs)
