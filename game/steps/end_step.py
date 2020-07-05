from game.steps.base_step import BaseStep
from game.roles.roleslist import RolesList
from assets.utils import infos_format
import assets.messages as msgs


class EndStep(BaseStep):
    def __init__(self):
        BaseStep.__init__(self, None)
        self.active = False
        self.confirmed = []

    async def start(self, roles: RolesList, dialogs):
        roles_summary = "- "+",\n- ".join([name+': '+role.role_name for name, role in roles.roles.items()])

        if len(roles.alive_players) == 2 and roles.alive_players[0].loving == roles.alive_players[1]:
            await roles.everyone.send(infos_format(
                dialogs.everyone.lovers_won.tell(),
                lover1=roles.alive_players[0],
                lover2=roles.alive_players[1],
                roles=roles_summary
            ))

        elif roles.alive_players == roles.villagers:
            await roles.everyone.send(infos_format(dialogs.everyone.villagers_won.tell(), roles=roles_summary))

        elif roles.alive_players == roles.were_wolfs:
            await roles.everyone.send(infos_format(dialogs.everyone.werewolfs_won.tell(), roles=roles_summary))

        elif not roles.alive_players:
            await self.end(roles, dialogs)
            return

        await roles.everyone.send(dialogs.everyone.game_ended.tell())

    async def quit_cmd(self, args, author, roles, dialogs):
        if args:
            await author.user.send(msgs.TOO_MUCH_PARAMETERS % ("!quit", "' ,'".join(args)))

        self.confirmed.append(author)
        if self.confirmed == roles.everyone or author.user == roles.admin:
            await self.end(roles, dialogs)

    async def end(self, roles, dialogs):
        self.active = False
        await BaseStep.end(self, roles, dialogs)
