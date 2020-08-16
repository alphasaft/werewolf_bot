import discord
from bot.extended_bot import ExtendedBot
from game.session import Session
from game.dialogs import StoryBook
from assets.exceptions import *
from assets.utils import make_mention
import assets.messages as msgs
import assets.constants as consts


class GameMaster(ExtendedBot):
    def __init__(self, *args, **kwargs):
        self._games = {}
        self.dialogs = StoryBook(consts.DIALOGS_PATH)
        self.voice_channels = {}
        ExtendedBot.__init__(self, *args, **kwargs)

    def check_game_exists(self, name: str, err_msg: str = None):
        if not self._games.get(name):
            raise NameError(err_msg or (msgs.WRONG_GAME_NAME % name))

    def check_game_doesnt_exist(self, name: str, err_msg: str = None):
        if self._games.get(name):
            raise NameError(err_msg or (msgs.FAILED_GAME_CREATION % (name, 'cette partie existe déjà')))

    def check_is_admin(self, user_id: str, err_msg: str = None):
        if not self._games[self.which_game(user_id)].admin.id == user_id:
            raise NotAnAdminError(err_msg or (msgs.MISSING_PERMISSIONS % ('admin', self.which_game(user_id))))

    def check_is_alone(self, user_id: str, err_msg: str = None):
        belong_to = self.which_game(user_id)
        if belong_to:
            raise GameJoinError(err_msg or (msgs.FAILED_JOIN % belong_to))

    def check_has_joined(self, user_id, game_name=None):
        if game_name is None:
            if not self.which_game(user_id):
                raise GameJoinError(msgs.NO_GAME_JOINED % (make_mention(user_id), 'de partie'))
        else:
            if not self._games[game_name].has_player(user_id):
                raise GameJoinError(msgs.NO_GAME_JOINED % (make_mention(user_id), 'la partie '+game_name))

    def check_can_launch(self, name: str):
        players = len(self._games[name].get_players())
        if players < consts.MINIMUM_PLAYERS:
            raise ValueError(msgs.MISSING_PLAYERS % (name, players))

    def check_can_join(self, name: str):
        if self._games[name].active:
            raise GameJoinError(msgs.NOT_JOIGNABLE % name)

    def add_game(self, name, admin, home_channel):
        if self._games.get(name):
            raise NameError(msgs.FAILED_GAME_CREATION % (name, "cette partie existe déjà."))

        self._games[name] = Session(name, admin, home_channel, self.dialogs)

    def delete_game(self, name: str):
        del self._games[name]

    def join_game(self, name: str, user: discord.User):
        self._games[name].add_player(user)

    def quit_game(self, user_id: str):
        self._games[self.which_game(user_id)].remove_player(user_id)

    async def launch_game(self, name: str):
        await self._games[name].launch()
        if self._games[name].ended:  # Means the game has ended
            await self.voice_channels.pop(name).delete()
            self._games.pop(name)

    async def react(self, msg):
        for name, game in self._games.copy().items():
            if game.has_player(msg.author.id) and game.active:
                await game.react(msg)

                if game.ended:
                    await self.voice_channels.pop(name).delete()
                    self._games.pop(name)
                    await game.home_channel.send(msgs.GAME_HAS_ENDED % name)

    def is_active(self, game):
        if self._games[game].active:
            return True
        else:
            return False

    def which_game(self, user_id: str):
        for name, game in self._games.items():
            if game.has_player(user_id):
                return name

    def get_admin(self, name: str):
        return self._games[name].admin

    def get_games(self):
        return list(self._games.keys())

    def get_opened_games(self):
        return [name for name, g in self._games.items() if not g.active]

    def get_game_members(self, name: str):
        return self._games[name].get_players()

    def set_admin(self, name: str, user_id: str):
        self._games[name].set_admin(user_id)



