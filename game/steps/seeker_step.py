from .base_step import BaseStep
from assets.utils import unpack
from assets.constants import SEEKER


class SeekerStep(BaseStep):
    def __init__(self):
        BaseStep.__init__(
            self,
            active_role=SEEKER,
            helps=(
                "Choisissez qui vous voulez espionner avec `*see unJoueur`",
                "La voyante consulte sa boule de cristal"
            ))

    async def start(self, roles, dialogs):
        self.__init__()
        if not (roles.seeker and roles.seeker.alive):
            await BaseStep.end(self, roles, dialogs)
            return

        await roles.everyone.send(dialogs.seeker.wakes_up.tell())
        await roles.seeker.user.send(dialogs.seeker.turn.tell())

    async def on_player_quit(self, roles, dialogs):
        if not (roles.seeker and roles.seeker.alive):
            await BaseStep.end(self, roles, dialogs)

    async def see_cmd(self, args, author, roles, dialogs):
        """ `*see unJoueur` : Vous renvoie le role de ce joueur """
        try:
            target = unpack(args, "!see unJoueur")
            roles.check_has_player(target)
            assert target != roles.get_name_by_id(author.user.id), dialogs.seeker.try_to_see_herself.tell()
        except Exception as e:
            await self.error(to=author, msg=e)
            return

        target_role = roles.get_role_by_name(target)
        await author.send(dialogs.seeker.see_role.tell(
                target=target,
                role=target_role.role.upper()
        ))
        await self.end(roles, dialogs)

    async def end(self, roles, dialogs):
        await roles.seeker.user.send(dialogs.seeker.done.tell())
        await roles.everyone.exclude(roles.seeker.user.id).send(dialogs.seeker.go_to_sleep.tell())
        await BaseStep.end(self, roles, dialogs)
