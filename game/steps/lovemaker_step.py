from game.steps.base_step import BaseStep
from game.roles.roleslist import RolesList
from assets.utils import mention, unpack, infos_format
import assets.messages as msgs


class LoveMakerStep(BaseStep):
    def __init__(self):
        BaseStep.__init__(self, 'cupidon')

    async def start(self, roles: RolesList, dialogs):
        self.ended = False
        if not roles.love_maker:
            await BaseStep.end(self, roles, dialogs)
            return

        await roles.everyone.send(dialogs.lovemaker.wakes_up.tell())
        await roles.love_maker.user.send(dialogs.lovemaker.turn.tell())

    async def love_cmd(self, args, author, roles, dialogs):
        try:
            target1, target2 = unpack(args, "!love <j1> <j2>")
            roles.check_has_player(target1)
            roles.check_has_player(target2)
            assert not target1 == target2, dialogs.lovemaker.target1_is_target2.tell()
            assert roles.get_name_by_id(author.user.id) not in [target1, target2], dialogs.lovemaker.try_to_involve_himself.tell()
        except Exception as e:
            await author.user.send(e)
            return

        target1_name = target1
        target2_name = target2
        target1 = roles.get_role_by_name(target1_name)
        target2 = roles.get_role_by_name(target2_name)

        target1.loving = target2
        target2.loving = target1
        await target1.user.send(infos_format(dialogs.lovemaker.in_love.tell(), lover=target2_name))
        await target2.user.send(infos_format(dialogs.lovemaker.in_love.tell(), lover=target1_name))
        await self.end(roles, dialogs)

    async def end(self, roles, dialogs):
        await roles.love_maker.user.send(dialogs.lovemaker.done.tell())
        await roles.everyone.exclude(roles.love_maker.user.id).send(dialogs.lovemaker.go_to_sleep.tell())
        await BaseStep.end(self, roles, dialogs)

