import discord
from time import sleep
from game.roles import Roles
from game.steps.steps_list import StepList
from assets.constants import PREFIX
from assets.utils import make_mention
import assets.messages as msgs


class Session:
    def __init__(self, name, admin, home_channel, dialogs):
        self.name = name
        self.active = False

        self.dialogs = dialogs
        self.steps = StepList()
        self.roles = Roles(game_name=name, dialogs=self.dialogs)

        self.players = {}
        self.admin = admin
        self.home_channel = home_channel
        self.add_player(admin)

    def force_build(self, players):
        self.players = {}
        for player in players:
            self.add_player(player)

    def add_player(self, new_player: discord.User):
        self.players[new_player.id] = new_player

    def remove_player(self, player_id: int):
        self.players.pop(player_id)
        if self.active:
            self.roles.quit_game(self.roles.get_name_by_id(player_id))

    def set_admin(self, player_id: int):
        if not self.players.get(player_id):
            raise NameError(msgs.FAILED_ADMIN_CHANGE % (make_mention(player_id), self.name))

        self.admin = self.players[player_id]
        if self.active:
            self.roles.set_admin(self.roles.get_name_by_id(player_id))

    def has_player(self, player_id: str):
        return player_id in self.players.keys()

    def get_players(self):
        return list(self.players.values())

    @property
    def ended(self):
        """Returns self.steps.ended"""
        return self.steps.ended

    async def launch(self):
        self.active = True
        self.steps.__init__()
        self.roles.__init__(self.dialogs, self.name, list(self.players.values()), self.admin)
        await self.steps.current_step.start(self.roles, self.dialogs)
        await self.check_step_continues()

    async def react(self, msg):
        if self.active and self.has_player(msg.author.id):
            if msg.content.startswith(PREFIX):
                cmd = msg.content.split()[0][len(PREFIX):]
                args = msg.content.split()[1:]
                author = self.roles.get_role_by_id(msg.author.id)
                await self.steps.current_step.react(cmd, args, author, self.roles, self.dialogs, session=self)
            else:
                await self.steps.current_step.send(msg, self.roles)
            await self.check_step_continues()

    async def check_step_continues(self):
        if self.ended:
            return

        while self.steps.current_step.ended:
            sleep(1)
            await self.steps.next_step(self.roles, self.dialogs)
