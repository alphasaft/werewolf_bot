import discord
from discord.ext.commands import has_permissions
import asyncio
import datetime
import time
import re
import random

from assets.constants import PREFIX


# Exceptions
class DevCommandNotFound(discord.DiscordException):
    def __init__(self, command):
        self._msg = "The dev command %s couldn't be found" % command

    def __str__(self):
        return self._msg


class TransformationError(discord.DiscordException):
    pass


# Assets
class _AsyncIterator:
    """Asynchronous iterator on an iterable"""
    def __init__(self, iterable):
        self._iterable = iterable
        self._i = 0

    def __aiter__(self):
        return self

    def __iter__(self):
        return self

    async def __anext__(self):
        try:
            result = next(self)
        except StopIteration:
            raise StopAsyncIteration() from None
        else:
            return result

    def __next__(self):
        if self._i >= len(self._iterable):
            raise StopIteration()

        result = self._iterable[self._i]
        self._i += 1
        return result

    def flatten(self):
        return list(self._iterable)


# core
class _MockedUser(discord.User):
    """
    Mocks a discord user, allowing the DevTool class instances to fool discord.

    If a method doc starts with, or contains, "Mocked.", this means that this method won't do what it should initially
    do, but just _inform() the mocked user's owner, or something very similar to it. Read its whole doc for further
    info.

    If a method doc starts with, or contains, "Delegated.", this means that this method will call self.parent.theMethod
    with the given args, and return the result. Read its whole doc for further info.

    Notice that discord's commands checks such as has_permissions are applied on self.parent.
    """

    __slots__ = (
        'id', 'name', 'discriminator', 'avatar', 'bot', 'system', 'parent', '_created_at', '_history', '_relationship'
    )

    def __init__(self, _id: int, name: str, parent: discord.User):
        """
        We copy the data of the discord.User PARENT, except for the name and the id : they are manually chosen.
        Warning, even if a _MockedUser is created by a bot, its attribute self.bot is always False.
        We initialize a few private attributes too, needed for mocking.
        """

        self.id = _id
        self.name = name
        self.bot = False

        # Copying
        self.parent = parent  # We keep the parent too
        self.discriminator = parent.discriminator
        self.avatar = parent.avatar
        self.system = parent.system

        # Mocking-needed attributes
        self._created_at = datetime.datetime.utcfromtimestamp(time.time())
        self._relationship = None
        self._history = []

    @property
    def default_avatar(self):
        """Delegated. Returns self.parent.default_avatar"""
        return self.parent.default_avatar

    @property
    def default_avatar_url(self):
        """Delegated. Returns self.parent.default_avatar_url"""
        return self.parent.default_avatar_url

    @property
    def display_name(self):
        """Returns self.name"""
        return self.name

    @property
    def mention(self):
        """Returns @{self.name}. This isn't a legal discord mention, but it looks like one of them."""
        return "@%s" % self.name

    @property
    def dm_channel(self):
        """
        Delegated. As _MockedUsers doesn't own their own dm_channel, we just return the parent's dm_channel.
        Notice that it is better to do myMockedUser.send(...) that myMockedUser.dm_channel.send(...), because the first
        solution informs self.parent that the message was originally destined to his mocked user.
        """
        return self.parent.dm_channel

    @property
    def color(self):
        """
        Delegated. Because the mocked users have the same permissions as their owner, they should have the same color
        too. We also returns self.parent.color
        """
        return self.parent.color

    @property
    def colour(self):
        """Alias for self.color"""
        return self.color

    @property
    def relationship(self):
        """
        Returns the current state of the relationships between this user and the bot.

        None -> No relationship
        1 -> friend
        2 -> blocked
        3 -> incoming_request
        4 -> outgoing_request

        If you just want to know if this mocked user is blocked / friend with you, use self.is_blocked() or
        self.is_friend()
        Practically, this could never return 1 or 4, because mocked user cannot accept or send friend requests.
        """
        return self._relationship

    @property
    def created_at(self):
        """Returns a datetime.datetime object corresponding at the initialization with __init__() of self"""
        return self._created_at

    async def _inform(self, message: str):
        """Calls self.parent.send(message % self.name)"""
        await self.parent.send(message % self.name)

    def _push_history(self, message):
        """Deleted the header of the message's content (ex. "<To aUser>") and append the mesage to the history."""
        message.content = re.sub(r"<To .+> +", "", message.content)
        self._history.append(message)

    async def send(self, content=None, *, tts=False, embed=None, file=None, files=None, delete_after=None, nonce=None):
        """
        Mocked. Sends a message. This actually sends <To {self.name}> {content} to self.parent if content is provided,
        else just calls self.parent.send() with the given args.
        """

        if content:
            content = "<To %s> %s" % (self.name, content)
        elif embed:
            title = embed.title
            embed.title = "<To %s> %s" % (self.name, title)
        else:
            raise ValueError("One of CONTENT or EMBED should be provided")

        request = dict(
            content=content,
            tts=tts,
            embed=embed,
            file=file,
            files=files,
            delete_after=delete_after,
            nonce=nonce
        )

        ret = await self.parent.send(**request)
        self._push_history(ret)
        if embed:
            embed.title = title
        return ret

    def avatar_url_as(self, *, format=None, static_format='webp', size=1024):
        """Delegated. Returns self.parent.avatar_url_as(...) with the given args"""
        return self.parent.avatar_url_as(
            format=format,
            static_format=static_format,
            size=size
        )

    def is_avatar_animated(self):
        """Delegated. Returns self.parent.is_avatar_animated"""
        return self.parent.is_avatar_animated()

    async def send_friend_request(self):
        """
        Warns the user self.parent that someone tried to send a friend request to his mocked user, and set
        self.relationship to 3
        """
        self._relationship = 3
        await self._inform("Someone tried to send a friend request to your mocked user %s")

    async def remove_friend(self):
        """
        Warns the user that someone removed from his friends his mocked user. It only removes friend invitations if some
        were sent, because a mocked user cannot accept friends invitation.
        """
        if self.relationship == 3:
            self._relationship = None

        await self._inform("Someone removed your mocked user %s from his friends.")

    async def block(self):
        """
        Warns self.parent that someone blocked his mocked user.
        In fact, self can always send messages, blocked or not. However, it sets self.relationship to 2
        """
        self._relationship = 2
        await self._inform("Someone blocked you mocked user %s")

    def is_blocked(self):
        """Returns True if self was blocked using self.block(), False otherwise."""
        return self.relationship == 2

    def is_friend(self):
        """Returns True if self is friend with the client, False otherwise. This also always returns False."""
        return self.relationship == 1

    def typing(self):
        """Delegated. Given self is not a real user and doesn't own a DMChannel, returns self.parent.typing instead."""
        return self.parent.typing()

    async def trigger_typing(self):
        """
        Delegated. Given self is not a real user and doesn't own a DMChannel, this triggers self.parent's typing
        instead.
        """
        await self.parent.trigger_typing()

    async def create_dm(self):
        """Delegated. This create a DM channel with self.parent if it doesn't already exist, and returns it."""
        if not self.parent.dm_channel:
            return self.parent.create_dm()
        else:
            return self.parent.dm_channel

    async def fetch_message(self, id):
        """Search a message sent through self.send that have the corresponding id."""
        for message in self._history:
            if message.id == id:
                return message

        raise ValueError("No message with id %i was sent to this user." % id)

    def mentioned_in(self, message):
        """
        Returns True if self was mentioned in message. Discord won't recognize mentions of self (because self.id
        isn't an official id), so we just return True if self.mention is in message.content, False otherwise.
        """
        return self.mention in message.content

    def history(self, *, limit=100, before=None, after=None, around=None, oldest_first=None):
        """
        Returns an AsyncIterator object that contains the LIMIT last messages sent trough self.send.
        Because tests using the DevTool and so _MockedUsers shouldn't take long, I haven't implemented the BEFORE, AFTER
        and AROUND features. It won't raise anything if you try to use them, but it won't work.
        """

        if oldest_first:
            return _AsyncIterator(self._history[:limit])
        else:
            return _AsyncIterator(self._history[-limit:])

    async def pins(self):
        """
        Returns a list of messages that are both pinned on the DMChannel of self.parent and contained in self.history
        (so that were sent trough self.send())
        """
        return [message for message in await self.parent.pins() if message in self._history]

    def permissions_in(self, channel):
        """
        Delegated. Returns self.parent.permissions_in(channel), and is basically equivalent to
        channel.permissions_for(self.parent)
        """
        return self.parent.permissions_in(channel)

    async def profile(self):
        """Delegated. Gets the profile of self.parent (so his flags etc), changes its user for self and returns it."""
        profile = await self.parent.profile()
        profile.user = self
        return profile


class DevTool:

    USERS_CREATED = """<SYSTEM> The users %s were successfully created."""
    LOGGED_AS = """<SYSTEM> Logged in as %s"""
    INFO = """<SYSTEM> Users : %s | Logged in as : %s"""

    def __init__(self, master=None):
        self.master = master
        self.users = {}
        self.logged_in = None

    def reset(self):
        """Calls self.__init__()"""
        self.__init__()

    def set_master(self, master):
        self.master = master

    def create_users(self, users, master=None):
        """
        Create a _MockedUser for each user in USERS.
        Their parent is either MASTER if provided or self.master, and their id are randomly chosen between 10**20 and
        10**30. Notice that even if there's few chances that it happens, it can pick already existing ids.
        """
        if not (master or self.master):
            raise NameError("Got no master")

        if len(users) == 1 and users[0].isnumeric() and int(users[0]) <= 26:
            user_count = int(users[0])
            users = []

            for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"[:user_count]:
                users.append(letter)

        for user in users:
            _id = random.randint(10**20, 10**30)
            name = user
            parent = master or self.master
            self.users[user] = _MockedUser(_id, name, parent)

        if not self.logged_in:
            self.log(users[0])

        return users

    def log(self, user):
        """Log the discord user self.master in as USER."""
        if user not in self.users:
            raise NameError("User %s doesn't exist." % user)

        self.logged_in = self.users[user]

    async def process_commands(self, msg):
        """
        Try to execute the command contained in the discord.Message msg.
        It could raise exceptions, either from commands, or DevCommandNotFound if the command wasn't found
        """
        msg.content = msg.content.strip()

        def _is_command(cmd):
            return msg.content.startswith(PREFIX + cmd)

        if _is_command("create"):
            users = msg.content.split()[1:]
            users = self.create_users(users)
            await msg.channel.send(self.USERS_CREATED % ", ".join(users))

        elif _is_command("log"):
            user = msg.content.split()[1]
            self.log(user)
            await msg.channel.send(self.LOGGED_AS % user)

        elif _is_command("info"):
            await msg.channel.send(self.INFO % (", ".join(self.users), self.logged_in or "Nobody"))

        else:
            raise DevCommandNotFound(msg.content.split()[0])

    def transform_ctx(self, ctx):
        """Transform the discord Context CTX so that for discord, its author is self._logged_in, and returns it"""
        ctx.message = self.transform_msg(ctx.message)
        return ctx

    def transform_msg(self, msg):
        """Transform the discord Message MSG so that for discord, its author is self._logged_in, and returns it"""
        if not self.logged_in:
            raise TransformationError("No user was logged in")

        msg.author = self.logged_in
        return msg


def __implement_dev_commands__(bot):
    """
    Implements additional development commands, such as !devmode or !forall.
    You must have the permission to manage the server to use them.
    These commands are auto-implemented in the ExtendedBot class.
    """

    @bot.command(help="[dev] Active le mode developpeur.")
    @has_permissions(administrator=True)
    async def devmode(ctx):
        bot.devmode = not bot.devmode
        await ctx.channel.send("Devmode set to %s" % str(bot.devmode).lower())
        if bot.devmode:
            bot.devtool.set_master(ctx.author)
        else:
            bot.devtool.reset()

    @bot.command(help="[dev] Execute la commande qui suit pour tous les utilisateurs simulés")
    @has_permissions(administrator=True)
    async def forall(ctx, *cmd):
        if not bot.devmode:
            await ctx.channel.send("Error : The devmode isn't on.")
            return

        # Author was truncated
        ctx.message.author = ctx.message.author.parent
        ctx.message.content = " ".join(cmd)

        old_logged = bot.devtool.logged_in
        for user in bot.devtool.users.values():
            bot.devtool.log(user.name)
            await bot.process_commands(ctx.message)
        bot.devtool.log(old_logged.name)

    @bot.command(name='as', help="[dev] Execute une commande en tant qu'utilisateur simulé")
    @has_permissions(administrator=True)
    async def _as(ctx, user, *cmd):
        if not bot.devmode:
            await ctx.channel.send("Error : The devmode isn't on.")
            return

        # Author was truncated
        ctx.message.author = ctx.message.author.parent
        ctx.message.content = " ".join(cmd)

        old_logged = bot.devtool.logged_in
        bot.devtool.log(user)
        await bot.process_commands(ctx.message)
        bot.devtool.log(old_logged.name)

