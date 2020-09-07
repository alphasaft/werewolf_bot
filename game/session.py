import discord

import assets.messages as msgs
from assets.constants import PREFIX
from assets.utils import make_mention, indented, StateOwner
from assets.exceptions import GameRelatedError
from time import sleep
from game.roles import Roles
from game.steps import StepList, NicknamesStep


class Session(StateOwner):
    def __init__(self, name, admin, home_channel, dialogs):
        StateOwner.__init__(self)
        self.name = name

        self.dialogs = dialogs
        self.steps = StepList()
        self.roles = Roles(game_name=name, dialogs=self.dialogs)

        self.players = {admin.id: admin}
        self.admin = admin
        self.home_channel = home_channel

    def active_but_reachable(self):
        """Returns True if self is active and if the current step defines a "on_player_join" method"""
        return self.active() and hasattr(self.steps.current_step, "on_player_join")

    def force_build(self, players):
        self.players = {player.id: player for player in players}

    def remove_player(self, player_id: int):
        self.players.pop(player_id)
        if self.active():
            self.roles.quit_game(self.roles.get_name_by_id(player_id))

    def set_admin(self, player_id: int):
        if not self.players.get(player_id):
            raise NameError(msgs.FAILED_ADMIN_CHANGE % (make_mention(player_id), self.name))

        self.admin = self.players[player_id]
        if self.active():
            self.roles.set_admin(self.roles.get_name_by_id(player_id))

    def has_player(self, player_id: str):
        return player_id in self.players.keys()

    def get_players(self):
        return list(self.players.values())

    async def add_player(self, new_player: discord.User):
        self.players[new_player.id] = new_player
        if self.active_but_reachable():
            self.roles.add_player(new_player)
            await self.steps.current_step.on_player_join(new_player, self.roles, self.dialogs)

    async def notify(self, message):
        await self.roles.everyone.send(indented(message))

    async def launch(self):
        self.set_state("ACTIVE")
        self.steps.__init__()
        self.roles.__init__(self.dialogs, self.name, list(self.players.values()), self.admin)
        await self.steps.current_step.start(self.roles, self.dialogs)
        await self.check_step_continues()

    async def react(self, msg):
        if self.active() and self.has_player(msg.author.id):
            if msg.content.startswith(PREFIX):
                cmd = msg.content.split()[0][len(PREFIX):]
                args = msg.content.split()[1:]
                author = self.roles.get_role_by_id(msg.author.id)
                await self.steps.current_step.react(cmd, args, author, self.roles, self.dialogs, session=self)
            else:
                await self.steps.current_step.send(msg, self.roles)
            await self.check_step_continues()

    async def check_step_continues(self):
        if self.ended():
            return

        while self.steps.current_step.ended and not self.steps.ended:
            sleep(1)
            await self.steps.next_step(self.roles, self.dialogs)

        if self.steps.ended:
            self.set_state("ENDED")
