from game.steps.base_step import BaseStep
from game.roles.roleslist import RolesList
from assets.utils import unpack, infos_format


class SeekerStep(BaseStep):
    def __init__(self):
        BaseStep.__init__(self, 'voyante')

    async def start(self, roles: RolesList, dialogs):
        self.ended = False
        if not roles.seeker:
            await BaseStep.end(self, roles, dialogs)
            return

        await roles.everyone.send(dialogs.seeker.wakes_up.tell())
        await roles.seeker.user.send(dialogs.seeker.turn.tell())

    async def see_cmd(self, args, author, roles, dialogs):
        try:
            target = unpack(args, "!see <joueur>")
            roles.check_has_player(target)
            assert target != roles.get_name_by_id(author.user.id), dialogs.seeker.try_to_see_herself.tell()
        except Exception as e:
            await author.user.send(e)
            return

        target_role = roles.get_role_by_name(target)
        await author.user.send(infos_format(dialogs.seeker.see_role.tell(),
                                            target=target,
                                            role=target_role.role_name.upper()))
        await self.end(roles, dialogs)

    async def end(self, roles, dialogs):
        await roles.seeker.user.send(dialogs.seeker.done.tell())
        await roles.everyone.exclude(roles.seeker.user.mention).send(dialogs.seeker.go_to_sleep.tell())
        await BaseStep.end(self, roles, dialogs)
