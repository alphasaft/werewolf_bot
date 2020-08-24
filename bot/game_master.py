import discord
import pickle
import datetime

from .extended_bot import ExtendedBot
from game import Session, StoryBook, GameEvent, convert_to_datetime
from assets.exceptions import *
from assets.utils import make_mention
import assets.messages as msgs
import assets.constants as consts


class _BotState(object):
    def __init__(self, bot):
        self.games, self.events = bot.games, bot.events


class GameMaster(ExtendedBot):
    def __init__(self, games=None, events=None, *args, **kwargs):
        self.games = games or {}
        self.events = events or {}

        self.dialogs = StoryBook(consts.DIALOGS_PATH)
        self.voice_channels = {}
        ExtendedBot.__init__(self, *args, **kwargs)

    @classmethod
    def from_binary_file(cls, file, *args, **kwargs):
        """Returns a new GameMaster object, loaded with pickle from the file"""

        """with open(file, 'rb') as f:
            ret = pickle.load(f)
            if isinstance(ret, _BotState):
                return cls(games=ret.games, events=ret.events, *args, **kwargs)
            else:
                raise ValueError("The file returned a %s object" % ret.__class__.__name__)
        """

        raise ValueError()

    def dump(self, file):
        """Dumps self into the binary file using pickle.dump"""
        with open(file, 'wb') as f:
            pickle.dump(_BotState(self), f)

    # - - - Checks - - -
    def check_game_exists(self, name: str, err_msg: str = None):
        if not self.games.get(name):
            raise GameRelatedError(err_msg or (msgs.WRONG_GAME_NAME % name))

    def check_event_exists(self, name: str, err_msg: str = None):
        if not self.events.get(name):
            raise GameRelatedError(err_msg or "L'événement %s n'existe pas !" % name)

    def check_name_is_available(self, name: str, err_msg: str = None):
        if self.games.get(name) or self.events.get(name):
            raise GameRelatedError(err_msg or (msgs.NAME_ALREADY_TAKEN % name))

    def check_is_admin(self, user_id: str, err_msg: str = None):
        if not self.games[self.which_game(user_id)].admin.id == user_id:
            raise CommandPermissionError(err_msg or (msgs.MISSING_PERMISSIONS % ('admin', self.which_game(user_id))))

    def check_is_alone(self, user_id: str, err_msg: str = None):
        belong_to = self.which_game(user_id)
        if belong_to:
            raise AvailabilityError(err_msg or (msgs.HAS_ALREADY_JOINED % belong_to))

    def check_has_joined(self, user_id, game_name=None):
        if game_name is None:
            if not self.which_game(user_id):
                raise BelongingError(msgs.NO_GAME_JOINED % (make_mention(user_id), 'de partie'))
        else:
            if not self.games[game_name].has_player(user_id):
                raise BelongingError(msgs.NO_GAME_JOINED % (make_mention(user_id), 'la partie '+game_name))

    def check_can_launch(self, name: str):
        players = len(self.games[name].get_players())
        if players < consts.MINIMUM_PLAYERS:
            raise GameRelatedError(msgs.MISSING_PLAYERS % (name, players))

    def check_is_available(self, name: str):
        if self.games[name].active:
            raise GameRelatedError(msgs.GAME_NOT_AVAILABLE % name)

    def check_has_free_time(self, user_id, when):
        _when = when if isinstance(when, datetime.datetime) else convert_to_datetime(when)
        for name, event in {name: e for name, e in self.events.items() if _when == e}.items():
            if user_id in event.members.keys():
                raise AvailabilityError(msgs.NO_FREE_TIME % name)
        return True

    # - - - Info - - -
    def is_active(self, game):
        if self.games[game].active:
            return True
        else:
            return False

    def which_game(self, user_id: str):
        for name, game in self.games.items():
            if game.has_player(user_id):
                return name

    def get_admin(self, name: str):
        return self.games[name].admin

    def get_games(self):
        return list(self.games.keys())

    def get_opened_games(self):
        return [name for name, g in self.games.items() if not g.active]

    def get_game_members(self, name: str):
        return self.games[name].get_players()

    # - - - Game - - -
    def add_game(self, name, admin, home_channel):
        self.check_name_is_available(name)
        self.games[name] = Session(name, admin, home_channel, self.dialogs)

    def delete_game(self, name: str):
        del self.games[name]

    def join_game(self, name: str, user: discord.User):
        self.games[name].add_player(user)

    def quit_game(self, user_id: str):
        self.games[self.which_game(user_id)].remove_player(user_id)

    def set_admin(self, name: str, user_id: str):
        self.games[name].set_admin(user_id)

    async def launch_game(self, name: str):
        await self.games[name].launch()
        if self.games[name].ended:  # Means the game has ended
            await self.voice_channels.pop(name).delete()
            self.games.pop(name)

    async def react(self, msg):
        for name, game in self.games.copy().items():
            if game.has_player(msg.author.id) and game.active:
                await game.react(msg)

                if game.ended:
                    await self.voice_channels.pop(name).delete()
                    self.games.pop(name)
                    await game.home_channel.send(msgs.GAME_HAS_ENDED % name)

    # - - - Events - - -
    def add_game_event(self, when, name, admin, home_channel):
        self.events[name] = GameEvent(when, name, admin=admin, home_channel=home_channel)

    def add_event_member(self, name, member):
        self.events[name].add_member(member)

    def confirm_presence(self, name, user_id):
        self.events[name].confirm_presence(user_id)

    async def activate_events(self):
        for name, event in self.events.copy().items():
            await event.check_and_activate(bot=self)
            if event.over():
                self.events.pop(name)



