from time import sleep
from game.roles.roleslist import RolesList
from game.steps.steps_list import StepList
import assets.constants as consts


class Session:
    def __init__(self, name, dialogs):
        self.name = name
        self.admin = None
        self.launched = False

        self.dialogs = dialogs
        self.steps = StepList()
        self.roles = RolesList(game_name=name, dialogs=self.dialogs, admin=self.admin)

    @property
    def ended(self):
        """Returns self.steps.ended"""
        return self.steps.ended

    async def start(self, players, admin):
        self.launched = True
        self.roles.build(players, admin)
        await self.steps.current_step.start(self.roles, self.dialogs)
        await self.check_step_continues()

    async def react(self, msg):
        if msg.content.startswith(consts.PREFIX):
            cmd = msg.content.split(' ')[0][1:]
            args = msg.content.strip().split(' ')[1:]
            author = self.roles.get_role_by_id(msg.author.id)
            await self.steps.current_step.react(cmd, args, author, self.roles, self.dialogs)
        else:
            await self.steps.current_step.send(msg, self.roles)
        await self.check_step_continues()

    async def check_step_continues(self):
        if self.ended:
            return

        while self.steps.current_step.ended:
            sleep(1)
            await self.steps.next_step(self.roles, self.dialogs)
