import asyncio
from traceback import extract_stack

from game.session import Session
from game.dialogs import StoryBook
from random import randint
import assets.constants as consts


class OfflineMessage:
    def __init__(self, content, author):
        self.content = content
        self.author = author

    async def delete(self):
        pass


class OfflineUser:
    def __init__(self, name):
        self.name = name
        self.id = randint(0, 1000000)

    def __str__(self):
        return self.mention

    @property
    def mention(self):
        return '@'+self.name

    async def send(self, content):
        print("<To %s> %s" % (self.mention, content))


class OfflineBot:
    async def react(self, msg):
        pass


class OfflineBotDmChannels:
    def __init__(self, name, users,  default_user=None, bot=None):
        self.name = name
        self.running = False

        self.default_user = default_user or users[0]
        self.users = {u.mention: u for u in users}
        self.logged_user = self.default_user

        self.bot = bot

    async def start(self):
        """
        Start the channel and blocks the program. Waits for messages, and, if self.bot is not None, calls
        self.bot.react(OfflineMessage(msg, self.logged_user)) for each message.
        """
        print("[system] Starting simulated channel %s" % self.name)
        self.logged_user = self.default_user
        self.running = True

        msg = ...
        while msg and self.running:
            msg = input('> ')
            if msg.startswith("."):
                self.process_command(msg.strip())
            else:
                if self.bot:
                    await self.bot.react(OfflineMessage(msg, self.logged_user))

    def send(self, msg):
        """Sends the message MSG only if MSG.author == self.logged_user"""
        if msg.author == self.logged_user:
            print("<To %s> %s" % msg.author, msg.content)

    def process_command(self, msg):
        """
        Process the command MSG. MSG should begin with '.'

        Current command list :
        .as <user> : log you in as user
        .exit : close the channel
        """
        if msg.startswith('.as'):
            self.change_logged_user(new_logged=msg.split(' ')[1])

        elif msg.startswith('.exit'):
            self.exit()

        else:
            print("Wrong command %s" % msg)

    def change_logged_user(self, new_logged):
        new_logged = new_logged if new_logged[0] == "@" else "@"+new_logged

        if self.users.get(new_logged):
            self.logged_user = self.users[new_logged]
        else:
            print("Wrong user %s" % new_logged)
            return

        print("- - - - - - - - - - - - - -\n[system] Logged user changed for %s\n- - - - - - - - - - - - - -" % new_logged)

    def exit(self):
        self.running = False


class GameBot(OfflineBot):
    def __init__(self, session):
        OfflineBot.__init__(self)
        self.session = session

    async def react(self, msg):
        await self.session.react(msg)


if __name__ == "__main__":
    async def main():
        players = [OfflineUser("Alphasaft"), OfflineUser("Blueberry"), OfflineUser("Ecta"), OfflineUser("Lucifer"), OfflineUser("Dridri"), OfflineUser("Wera"), OfflineUser('Hello')]
        session = Session("offline", players[0], None, StoryBook(consts.DIALOGS_PATH))
        bot = GameBot(session)
        game_dm_channels = OfflineBotDmChannels("test", players, bot=bot)

        session.force_build(players)

        # launch_future = async_error_pusher(session.launch)
        # channel_start_future = async_error_pusher(game_dm_channels.start)
        await asyncio.gather(
            asyncio.ensure_future(session.launch()),
            asyncio.ensure_future(game_dm_channels.start())
        )

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
