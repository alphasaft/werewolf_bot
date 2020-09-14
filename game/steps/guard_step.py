from .base_step import BaseStep
from assets.utils import unpack
from assets.constants import GUARD
import assets.messages as msgs


class GuardStep(BaseStep):
    def __init__(self):
        BaseStep.__init__(
            self,
            active_roles=GUARD,
            helps=(
                "Utilisez `*protect` pour protéger la personne de votre choix",
                "Le garde se dirige vers la maison qu'il souhaite protéger"
            )
        )

    async def start(self, roles, dialogs):
        self.__init__()
        if not (roles.guard and roles.guard.alive):
            await BaseStep.end(self, roles, dialogs)

        await roles.everyone.send(dialogs.guard.wakes_up.tell())
        await roles.guard.send(dialogs.guard.turn.tell())

    async def on_player_quit(self, roles, dialogs):
        if not (roles.guard and roles.guard.alive):
            await BaseStep.end(self, roles, dialogs)

    async def protect_cmd(self, args, author, roles, dialogs):
        """ `*protect unJoueur` : protège ce joueur """
        try:
            target = unpack(args, "$protect unJoueur")
            roles.check_has_player(target)
            assert roles.get_role_by_name(target) != author, dialogs.guard.try_to_protect_himself.tell()
            assert author.protected_player != target, dialogs.guard.same_target.tell(target=target)
        except Exception as e:
            await self.error(to=author, msg=str(e))
            return

        roles.protect(target)
        author.protected_player = target
        await author.send(dialogs.guard.done.tell(target=target))
        await self.end(roles, dialogs)

    async def pass_cmd(self, args, author, roles, dialogs):
        """ `*pass` : passez votre tour et ne protégez personne """
        author.protected_player = None
        await author.send(dialogs.guard.do_nothing.tell())
        await BaseStep.end(self, roles, dialogs)

    async def end(self, roles, dialogs):
        await roles.everyone.send(dialogs.guard.go_to_sleep.tell())
        await BaseStep.end(self, roles, dialogs)
