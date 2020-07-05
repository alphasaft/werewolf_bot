from game.steps.base_step import BaseStep
from game.roles.roleslist import RolesList
from assets.utils import mention, unpack, infos_format
import assets.messages as msgs


class HunterStep(BaseStep):
    def __init__(self):
        BaseStep.__init__(self, 'chasseur')
        self.targeted = None

    async def start(self, roles: RolesList, dialogs):
        self.__init__()
        if not (roles.hunter and roles.hunter.injured):
            await BaseStep.end(self, roles, dialogs)
            return

        await roles.everyone.send(infos_format(dialogs.hunter.injured.tell(),
                                               hunter=roles.get_name_by_id(roles.hunter.user.id)
                                               ))
        await roles.hunter.user.send(dialogs.hunter.turn.tell())

    async def kill_cmd(self, args, author, roles, dialogs):
        try:
            target = unpack(args, "!kill <joueur>")
            assert target != roles.get_name_by_id(author.user.id), dialogs.hunter.try_to_kill_himself()
            roles.check_has_player(target)
        except Exception as e:
            await author.user.send(e)
            return

        roles.wound(target)
        self.targeted = target
        await roles.hunter.user.send(infos_format(dialogs.hunter.kill.tell(), target=target))
        await self.end(roles, dialogs)

    async def end(self, roles, dialogs):
        await roles.everyone.exclude(roles.hunter.user.id).send(infos_format(
            dialogs.hunter.die.tell(),
            hunter=roles.get_name_by_id(roles.hunter.user.id),
            target=self.targeted
        ))
        await BaseStep.end(self, roles, dialogs)

