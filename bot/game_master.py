import discord
from lxml import etree
import datetime

from .extended_bot import ExtendedBot
from game import Session, StoryBook, GameEvent, convert_to_datetime, convert_to_str, is_over
from assets.exceptions import *
from assets.utils import make_mention, configure_logger, StateOwner
import assets.messages as msgs
import assets.constants as consts
import assets.logger as logger


configure_logger(logger)


class _XmlEventsIO(object):
    def __init__(self, events):
        self.events = events

    @staticmethod
    def _dump_date(node, dated_object):
        set = node.set
        set("year", str(dated_object.year))
        set("month", str(dated_object.month))
        set("day", str(dated_object.day))
        set("hour", str(dated_object.hour))
        set("minute", str(dated_object.minute))

    @staticmethod
    def _load_date(node):
        def get(s):
            return int(node.get(s))

        return datetime.datetime(
            year=get('year'),
            month=get('month'),
            day=get('day'),
            hour=get('hour'),
            minute=get('minute')
        )

    def dump(self, file: str):
        """Dumps the events into the provided xml FILE"""
        root = etree.Element("events")

        for name, event in self.events.items():
            # Event root node
            event_node = etree.SubElement(root, "event")

            if isinstance(event, GameEvent):
                event_node.set('type', 'game')

                # Raw event data (name, date, ...)
                etree.SubElement(event_node, "name").text = name
                etree.SubElement(event_node, "home_channel").text = str(event.home_channel.id)
                date = etree.SubElement(event_node, "date")
                self._dump_date(node=date, dated_object=event)

            else:
                raise ValueError("One of the event isn't a valid event type")

            # Saving the event members
            members = etree.SubElement(event_node, "members")
            for member in event.members.values():
                member_node = etree.SubElement(members, "member")
                member_node.set('id', str(member.id))
                if member == event.admin:
                    member_node.set('admin', "True")

            # Remainders
            remainders = etree.SubElement(event_node, "remainders")
            for remainder in event.remainders:
                etree.SubElement(remainders, "elem").text = str(remainder.time_from_event)

        with open(file, 'w') as f:
            f.write(etree.tostring(root, pretty_print=True).decode("utf-8"))

    @classmethod
    def load(cls, file: str, bot):
        """
        Loads the event of the passed xml FILE. BOT should be connected to discord, otherwise we can't use bot.get_user
        """
        events = {}
        root = etree.parse(file)

        for event in root.findall("event"):
            members = []
            admin = None
            members_node = event.find("members")

            for member_node in members_node.findall("member"):
                user = bot.get_user(int(member_node.get('id')))
                members.append(user)
                if member_node.get("admin", False):
                    admin = user

            remainders = []
            remainders_node = event.find("remainders")
            for elem in remainders_node.findall("elem"):
                remainders.append(int(elem.text))

            if event.get("type") == "game":
                date = cls._load_date(event.find("date"))
                name = event.find("name").text
                events[name] = GameEvent(
                    convert_to_str(date),
                    event.find("name").text,
                    admin,
                    bot.get_channel(int(event.find('home_channel').text)),
                    remainders
                )

                for member in members:
                    events[name].add_member(member)

        return cls(events)


class _XmlExperienceIO(object):
    def __init__(self, xp_counts):
        self.xp_counts = xp_counts

    def dump(self, file: str):
        root = etree.Element("xp_counts")

        for user_id, xp in self.xp_counts.items():
            print(user_id)
            user_xp = etree.SubElement(root, "user_xp")
            user_xp.set("id", str(user_id))
            user_xp.set("xp", str(xp))

        with open(file, 'w') as f:
            f.write(etree.tostring(root, pretty_print=True).decode("utf-8"))

    @classmethod
    def load(cls, file: str, bot):
        xp_counts = {}
        root = etree.parse(file)

        for user_xp in root.findall("user_xp"):
            xp_counts[int(user_xp.get("id"))] = int(user_xp.get("xp"))

        return cls(xp_counts)


class GameMaster(ExtendedBot):
    def __init__(self, games=None, events=None, xp_counts=None, *args, **kwargs):
        self.games = games or {}
        self.events = events or {}
        self.xp_counts = xp_counts or {}

        self.dialogs = StoryBook(consts.DIALOGS_PATH)
        self.voice_channels = {}
        ExtendedBot.__init__(self, *args, **kwargs)

    def load(self, events_file, xp_counts_file):
        def _load_events():
            self.events = {**_XmlEventsIO.load(events_file, bot=self).events, **self.events}

        def _load_xps():
            self.xp_counts = {**_XmlExperienceIO.load(xp_counts_file, bot=self).xp_counts, **self.xp_counts}

        failed = False
        for data_load in (_load_events, _load_xps):
            try:
                data_load()
            except (SyntaxError, FileNotFoundError) as exc:
                failed = exc
        if failed:
            raise SyntaxError from failed

    def dump(self, events_file, xp_counts_file):
        _XmlEventsIO(self.events).dump(events_file)
        _XmlExperienceIO(self.xp_counts).dump(xp_counts_file)

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

    def check_is_game_admin(self, user_id: str, err_msg: str = None):
        if not self.games[self.which_game(user_id)].admin.id == user_id:
            raise CommandPermissionError(err_msg or (msgs.MISSING_PERMISSIONS % ('admin', self.which_game(user_id))))

    def check_is_alone(self, user_id: str, err_msg: str = None):
        belong_to = self.which_game(user_id)
        if belong_to:
            raise AvailabilityError(err_msg or (msgs.HAS_ALREADY_JOINED % belong_to))

    def check_has_joined_game(self, user_id, game_name=None):
        if game_name is None:
            if not self.which_game(user_id):
                raise BelongingError(msgs.NO_GAME_JOINED % (make_mention(user_id), 'de partie'))
        else:
            if not self.games[game_name].has_player(user_id):
                raise BelongingError(msgs.NO_GAME_JOINED % (make_mention(user_id), 'la partie '+game_name))

    def check_has_joined_event(self, user_id, event_name):
        if not self.events[event_name].has_member(user_id):
            raise BelongingError(msgs.EVENT_NOT_JOINED % (make_mention(user_id), event_name))

    def check_can_launch(self, name: str):
        players = len(self.games[name].get_players())
        if players < consts.MINIMUM_PLAYERS:
            raise GameRelatedError(msgs.MISSING_PLAYERS % (name, players))

    def check_game_is_available(self, name: str):
        if not (self.games[name].off() or self.games[name].active_but_reachable()):
            raise GameRelatedError(msgs.GAME_NOT_AVAILABLE % name)

    def check_has_free_time(self, user_id, when):
        _when = when if isinstance(when, datetime.datetime) else convert_to_datetime(when)
        for name, event in {name: e for name, e in self.events.items() if _when == e.dt}.items():
            if user_id in event.members.keys():
                raise AvailabilityError(msgs.NO_FREE_TIME % name)
        return True

    @staticmethod
    def check_datetime_format(when):
        try:
            convert_to_datetime(when)
        except SyntaxError:
            raise CommandSyntaxError("Le format de date est invalide !")

    @staticmethod
    def check_is_not_over(when):
        if is_over(when):
            raise EventRelatedError("Cette date est déjà passée !")

    # - - - Info - - -
    def is_active(self, game):
        if self.games[game].active():
            return True
        else:
            return False

    def which_game(self, user_id: str):
        for name, game in self.games.items():
            if game.has_player(user_id):
                return name

    def get_admin(self, name: str):
        if self.games.get(name):
            return self.games[name].admin
        elif self.events.get(name):
            return self.events[name].admin

    def get_games(self):
        return list(self.games.keys())

    def get_game(self, name):
        return self.games[name]

    def get_event(self, name):
        return self.events[name]

    def get_opened_games(self):
        return [name for name in self.games.keys() if self.is_active(name)]

    def get_opened_events(self):
        return [(name, event.dt) for name, event in self.events.items()]

    def get_joined_events(self, user_id):
        return [(name, event.dt) for name, event in self.events.items() if event.has_member(user_id)]

    def get_game_members(self, name: str):
        return self.games[name].get_players()

    def get_event_members(self, name: str):
        return self.events[name].get_members()

    # - - - Game - - -
    def add_game(self, name, admin, home_channel):
        self.games[name] = Session(name, admin, home_channel, self.dialogs)

    def delete_game(self, name: str):
        del self.games[name]

    def quit_game(self, user_id: str):
        self.games[self.which_game(user_id)].remove_player(user_id)

    def set_admin(self, name: str, user_id: str):
        self.games[name].set_admin(user_id)

    async def join_game(self, name: str, user: discord.User):
        await self.games[name].add_player(user)

    async def launch_game(self, name: str):
        await self.games[name].launch()
        if self.games[name].ended():
            await self.voice_channels.pop(name).delete()
            self.games.pop(name)

    async def react(self, msg):
        for name, game in self.games.copy().items():
            if game.has_player(msg.author.id) and game.active():
                await game.react(msg)

                if game.ended():
                    await self.finish_game(name)

    async def finish_game(self, name):
        for user in self.games[name].roles.everyone:
            if not self.xp_counts.get(user.id):
                self.create_xp_account(user.id)
            self.xp_counts[user.id] += user.xp

        await self.voice_channels.pop(name).delete()
        await self.games[name].home_channel.send(msgs.GAME_HAS_ENDED % name)
        self.games.pop(name)

    # - - - Events - - -
    def add_game_event(self, when, name, admin, home_channel):
        self.events[name] = GameEvent(when, name, admin=admin, home_channel=home_channel)

    def delete_event(self, name):
        self.events.pop(name)

    def quit_event(self, user_id, name):
        self.events[name].remove_member(user_id)

    def add_event_member(self, name, member):
        self.events[name].add_member(member)

    async def confirm_presence(self, name, where, user_id):
        await self.events[name].confirm_presence(user_id, where=where, bot=self)

    async def activate_events(self):
        for name, event in self.events.copy().items():
            await event.check_and_activate(bot=self)
            if event.over():
                self.events.pop(name)

    # - - - Experience points - - -
    def create_xp_account(self, user_id):
        self.xp_counts[user_id] = 0

    def get_level_info(self, user_id):
        xp = self.xp_counts[user_id]
        level = 1

        def _level_total_xp():
            return (level + 1) * 50

        while _level_total_xp() <= xp:
            xp -= _level_total_xp()
            level += 1

        level_name = consts.LEVELS[level]
        total_xp = _level_total_xp()
        needed_xp = total_xp - xp
        xp_bar = "■"*(int(xp/total_xp*10)) + "□"*(int(needed_xp/total_xp*10))

        return {
            "level": level,
            "level_name": level_name,
            "total_xp": total_xp,
            "xp": xp,
            "needed_xp": needed_xp,
            "xp_bar": xp_bar
        }
