import discord
import assets.messages as msgs
from game.session import Session


class GameManager(Session):
    def __init__(self, name: str, admin: discord.User, dialogs):
        self.players = {}
        self.admin = admin
        self.add_player(admin)
        self.active = False

        Session.__init__(self, name, dialogs)

    def add_player(self, new_player: discord.User):
        self.players[new_player.mention] = new_player

    def remove_player(self, player: str):
        self.players.pop(player)

    def set_admin(self, player: str):
        if not self.players.get(player):
            raise NameError(msgs.FAILED_ADMIN_CHANGE % (player, self.name))

        self.admin = self.players[player]

    def has_player(self, player: str):
        return player in self.players.keys()

    def get_players(self):
        return list(self.players.keys
                    ())

    async def launch(self):
        self.active = True
        await self.start(list(self.players.values()), self.admin)

    async def react(self, msg):
        if self.launched and self.has_player(msg.author.mention):
            await Session.react(self, msg)
