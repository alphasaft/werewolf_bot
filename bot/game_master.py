import discord
from bot.extended_bot import ExtendedBot
from game.game_manager import GameManager
from game.dialogs.story_book import StoryBook
from assets.exceptions import *
import assets.messages as msgs
import assets.constants as consts


class GameMaster(ExtendedBot):
    def __init__(self, *args, **kwargs):
        self._games = {}
        self.dialogs = StoryBook(consts.DIALOGS_PATH)
        self.vote_channels = {}
        ExtendedBot.__init__(self, *args, **kwargs)

    def which_game(self, user_mention: str):
        for name, game in self._games.items():
            if game.has_player(user_mention):
                return name

    def check_game_exists(self, name: str, err_msg: str = None):
        if not self._games.get(name):
            raise NameError(err_msg or (msgs.WRONG_GAME_NAME % name))

    def check_game_doesnt_exist(self, name: str, err_msg: str = None):
        if self._games.get(name):
            raise NameError(err_msg or (msgs.FAILED_GAME_CREATION % (name, 'cette partie existe déjà')))

    def check_is_admin(self, user_mention: str, err_msg: str = None):
        if not self._games[self.which_game(user_mention)].admin.mention == user_mention:
            raise NotAnAdminError(err_msg or (msgs.MISSING_PERMISSIONS % ('admin', self.which_game(user_mention))))

    def check_is_alone(self, user_mention: str, err_msg: str = None):
        belong_to = self.which_game(user_mention)
        if belong_to:
            raise GameJoinError(err_msg or (msgs.FAILED_JOIN % belong_to))

    def check_has_joined(self, user_mention: str, name: str = None, err_msg: str = None):
        if name is None:
            if not self.which_game(user_mention):
                raise GameJoinError(err_msg or (msgs.NO_GAME_JOINED % (user_mention, 'de partie')))
        else:
            if not self._games[name].has_player(user_mention):
                raise GameJoinError(err_msg or (msgs.NO_GAME_JOINED % (user_mention, 'la partie '+name)))

    def check_can_launch(self, name: str):
        players = len(self._games[name].get_players())
        if players < consts.MINIMUM_PLAYERS:
            raise ValueError(msgs.MISSING_PLAYERS % (name, players))

    def check_can_join(self, name: str):
        if self._games[name].active:
            raise GameJoinError(msgs.NOT_JOIGNABLE % name)

    def add_game(self, name, admin):
        if self._games.get(name):
            raise NameError(msgs.FAILED_GAME_CREATION % (name, "cette partie existe déjà."))

        self._games[name] = GameManager(name, admin, self.dialogs)

    def delete_game(self, name: str):
        del self._games[name]

    def join_game(self, name: str, user: discord.User):
        self._games[name].add_player(user)

    def quit_game(self, user_mention: str):
        self._games[self.which_game(user_mention)].remove_player(user_mention)

    async def launch_game(self, name: str):
        await self._games[name].launch()
        if self._games[name].ended:  # Means the game has ended
            await self.vote_channels[name].delete()
            self.vote_channels.pop(name)
            self._games.pop(name)

    async def react(self, msg):
        for name, game in self._games.items():
            if game.has_player(msg.author.mention) and game.active:
                await game.react(msg)
                if game.ended:
                    await self.vote_channels[name].delete()
                    self.vote_channels.pop(name)
                    self._games.pop(name)

    def get_admin(self, name: str):
        return self._games[name].admin

    def get_games(self):
        return list(self._games.keys())

    def get_opened_games(self):
        return [name for name, g in self._games.items() if not g.active]

    def get_game_members(self, name: str):
        return self._games[name].get_players()

    def set_admin(self, name: str, user_mention: str):
        self._games[name].set_admin(user_mention)



