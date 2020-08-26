"""Contains the event stuff of the bot"""

import discord
import datetime
import time
import re

from assets.constants import TIMEZONE
from assets.exceptions import *


# Functions
# - - - - - - - - -

def _named_regex_group(name, regex):
    """
    Returns a regex that will gather your regex result as a named group.
    e.g. re.search(_named_regex_group('myGroup', '[0-9]'), "hello 4 !").group("myGroup") returns "4"
    """
    return "(?P<%s>%s)" % (name, regex)


_DATETIME_REGEX = re.compile("(%s/%s,|today\+%s,)?%s:%s" % (
    _named_regex_group("day", "[0-3][0-9]"),
    _named_regex_group("month", "(0[1-9]|1[0-2])"),
    _named_regex_group("forward", "([1-9]|10)"),
    _named_regex_group("hour", "[0-2]?[0-9]"),
    _named_regex_group("minute", "[0-5][0-9]")
))


def now():
    """
    Returns a datetime.datetime object corresponding to the current date and time, for the given timezone
    (see assets/constants.py)
    """
    return datetime.datetime.utcfromtimestamp(time.time() + TIMEZONE)


def convert_to_datetime(s: str):
    """
    Converts S to a datetime.datetime object. S must be formatted like this :
        (<day>/<month>|today\+<forward>)?,<hour>:<minute>
    """

    match = _DATETIME_REGEX.match(s)
    if not match:
        raise SyntaxError("Invalid datetime format has been passed")

    def get(info):
        ret = match.group(info)
        if ret and ret.isnumeric():
            return int(ret)
        else:
            return ret

    _now = now()
    year = _now.year
    day = get('day')
    month = get('month')
    forward = get('forward')
    hour = get('hour')
    minute = get('minute')

    if forward:
        dt = datetime.datetime.utcfromtimestamp(
            time.time() + TIMEZONE + forward * 3600 * 24
        ).replace(hour=hour, minute=minute)

    elif day:
        if month < _now.month or (month == _now.month and day < _now.day):
            year += 1

        dt = datetime.datetime(
            year=year,
            month=month,
            day=day,
            hour=hour,
            minute=minute,
        )

    else:
        dt = _now.replace(hour=hour, minute=minute)

    return dt


def convert_to_str(dt: datetime.datetime):
    ret = "%02i/%02i,%02i:%02i" % (dt.day, dt.month, dt.hour, dt.minute)
    return ret


def is_over(when: str):
    """Returns True if the described date and time belong to the past else False"""
    return now() > convert_to_datetime(when)


def clean_str_dt(when):
    """Clean the datetime str format WHEN"""
    dt = convert_to_datetime(when)
    if (dt.year, dt.month, dt.day) == (now().year, now().month, now().day):
        return "%02i:%02i" % (dt.hour, dt.minute)
    else:
        return convert_to_str(convert_to_datetime(when)).replace(',', ', ')


# Core
# - - - - - - - - -

class _BaseEvent(object):
    """
    Represents a dated object, also the skeleton of a valid event. Warning, the datetime must have been built using
    datetime.datetime.utcfromstamp OR with the basic constructor (__init__), else its timestamp is invalid.
    """
    def __init__(self, dt: datetime.datetime, description):
        self.dt = dt

        self.year = dt.year
        self.month = dt.month
        self.day = dt.day
        self.hour = dt.hour
        self.minute = dt.minute

        self.raw_description = description

    @property
    def description(self):
        return self.raw_description

    def __eq__(self, other):
        return any((
            isinstance(other, _BaseEvent) and other.dt == self.dt,
            isinstance(other, datetime.datetime) and other == self.dt
        ))

    def timestamp(self):
        return self.dt.timestamp()

    def on_now(self):
        _now = now()
        return all((
            self.year == _now.year,
            self.month == _now.month,
            self.day == _now.day,
            self.hour == _now.hour,
            self.minute == _now.minute
        ))

    def over(self):
        if now() >= self.dt:
            return True
        return False


class Remainder(_BaseEvent):
    def __init__(self, event, dt: datetime.datetime, description):
        self._event = event
        _BaseEvent.__init__(self, dt, description)

    @property
    def description(self):
        date = self._event.dt
        _now = now()

        return self.raw_description.format(
            when="le %02i/%02i à %02i:%02i" % (date.day, date.month, date.hour, date.minute),
            now="le %02i/%02i à %02i:%02i" % (_now.day, _now.month, _now.hour, _now.minute),
            date="%02i/%02i" % (date.month, date.day),
            time="%02i:%02i" % (date.hour, date.minute),
            now_date="%02i/%02i" % (_now.month, _now.day),
            now_time="%02i:%02i" % (_now.hour, _now.minute)
        )

    @property
    def time_from_event(self):
        """Returns the time that separates the event from the remainder, in minutes"""
        return round((self.timestamp() - self._event.timestamp())/60)


class Event(_BaseEvent):
    """Represents an Event that has a date, a time and a description, and that owns several remainders"""

    def __init__(self,
                 when: str,
                 description: str,
                 admin: discord.User,
                 bef_remainder_desc=None,
                 aft_remainder_desc=None,
                 _remainders=None
                 ):

        _BaseEvent.__init__(self, convert_to_datetime(when), description)

        self.admin = admin
        self.members = {admin.id: admin}
        self.present_members = set()

        _remainders = _remainders or (-60, -30, -5, 5, 10, 15)
        self.bef_remainder_desc = bef_remainder_desc
        self.aft_remainder_desc = aft_remainder_desc
        self.bef_remainders = self._get_remainders(self.timestamp(), (r for r in _remainders if r < 0))
        self.aft_remainders = self._get_remainders(self.timestamp(), (r for r in _remainders if r > 0))

    def __repr__(self):
        return "<Event '%s' on %02i/%02i, %02i:%02i>" % (self.description, self.day, self.month, self.hour, self.minute)

    @property
    def remainders(self):
        """Returns self.bef_remainders + self.aft_remainders"""
        return self.bef_remainders + self.aft_remainders

    def _get_remainders(self, initial_stamp, _list):
        """Returns a list of COUNT Remainder object(s)"""
        remainders = []
        _now = now()
        for remainder in _list:
            date = datetime.datetime.utcfromtimestamp(initial_stamp + remainder*60)
            if remainder < 0:
                desc = self.bef_remainder_desc or "Rappel : %s" % self.description
            else:
                desc = self.aft_remainder_desc or "On t'attend : %s" % self.description
            remainders.append(Remainder(self, date, desc))

        return remainders

    def add_member(self, member):
        """Add a member to the event"""
        self.members[member.id] = member

    def remove_member(self, user_id):
        """Remove a member from the event"""
        self.members.pop(user_id)

    def has_member(self, user_id):
        """Returns True if the user belongs to this event, False otherwise"""
        return user_id in self.members

    def get_members(self):
        """Returns the list of the event members"""
        return list(self.members.values())

    def confirm_presence(self, user_id):
        """
        Confirm that the user is present for the event.
        It raises a BelongingError if the user doesn't belong to this event or an EventRelatedError in the case the
        event hasn't yet begin
        """
        if not self.has_member(user_id):
            raise BelongingError("Vous n'appartenez pas à cet événement !")

        if user_id in self.present_members:
            raise EventRelatedError("Vous avez déjà confirmé pour cette événement !")

        if now() < self.dt:
            raise EventRelatedError("L'événement n'a pas encore commencé !")

        self.present_members.add(user_id)

    async def check_and_activate(self, bot):
        """
        Checks if the event (or one of the remainders) corresponds to the current date and time and notify all members
        with its description if yes. In case it's the event that corresponds, it calls self.activate() too.
        """
        for remainder in self.bef_remainders:
            if remainder.on_now():
                await self.notify(remainder.description)

        for remainder in self.aft_remainders:
            if remainder.on_now():
                for _id, member in self.members.items():
                    if _id not in self.present_members:
                        await member.send(remainder.description)

        if self.on_now():
            await self.activate(bot=bot)
            await self.notify(self.description)

    async def activate(self, bot):
        pass

    async def notify(self, msg):
        """Sends MSG to all the event members"""
        for member in self.members.values():
            await member.send(msg)

    def over(self):
        """Return True if the event is over (the latest Remainder was done), False otherwise"""
        if not self.aft_remainders and now() >= self.dt:
            return True

        elif self.aft_remainders and now() >= self.aft_remainders[-1].dt:
            return True

        else:
            return False


# Specific events
# - - - - - - - - -

class GameEvent(Event):
    def __init__(self,
                 when,
                 name,
                 admin,
                 home_channel,
                 _remainders=None,
                 ):

        self.home_channel = home_channel
        smiley = ":stuck_out_tongue_closed_eyes:"
        desc = "La partie %s va commencer ! Viens vite !"
        bef_remainder_desc, aft_remainder_desc = (
            "Rappel : La partie %s est programmée pour {when}, et nous sommes {now}, ne l'oublie pas %s",
            "La partie %s a déjà commencé ! Viens vite, où ça va commencer sans toi %s"
        )

        Event.__init__(
            self,
            when,
            desc % name,
            admin=admin,
            _remainders=_remainders,
            bef_remainder_desc=bef_remainder_desc % (name, smiley),
            aft_remainder_desc=aft_remainder_desc % (name, smiley)
        )

    async def activate(self, bot):
        ...
