from assets.utils import unpack
import assets.messages as msgs


class BaseStep:
    """
    Represents a step of a were-wolf game. Defines start, react, send and end. Override them if what they currently do
    is not what you want to do.
    """
    def __init__(self, active_role_name):
        self.ended = False
        self.active_role = active_role_name

    async def start(self, roles, dialogs):
        """Starts the step. For example, sends all players who wakes up and what to do. Default is to pass."""
        pass

    async def react(self, cmd, args, author, roles, dialogs):
        """
        Reacts to a command, such as !kill or !vote. Default reaction is to check if the author is alive and if he is
        the current active role, (pass this step if this None) and then call self.<CMD>_cmd, or self.command_not_found
        if it cannot be called.
        """
        if not (author.alive or cmd in ['admin', 'players', 'private', 'public', 'quit'] or author.role_name == "chasseur"):
            await author.user.send(msgs.DEAD_USER_INVOKES_CMD)
            return

        if not (not self.active_role or author.role_name == self.active_role or cmd in ['admin', 'players', 'private', 'public', 'quit']):
            await author.user.send(msgs.WRONG_ROLE)
            return

        if hasattr(self, cmd+'_cmd'):
            await getattr(self, cmd+'_cmd')(args, author, roles, dialogs)
        else:
            await self.command_not_found(cmd, author)

    async def public_cmd(self, args, author, roles, dialogs):
        await roles.everyone.exclude(author.user.id).send(roles.get_name_by_id(author.user.id)+' : '+" ".join(args))

    async def private_cmd(self, args, author, roles, dialogs):
        await roles.get_role_by_name(args[0]).user.send(roles.get_name_by_id(author.user.id)+' : '+" ".join(args[1:]))

    async def players_cmd(self, args, author, roles, dialogs):
        await author.user.send(msgs.GET_NICKNAMES % ",\n- ".join([
            player.user.mention+' -> '+nickname for nickname, player in roles.roles.items()
        ]))

    async def quit_cmd(self, args, author, roles, dialogs):
        roles.quit_game(roles.get_name_by_id(author.user.id))
        await roles.everyone.send("%s a quitté la partie. Il/elle était %s" % (author.user.mention, author.role_name))

    async def admin_cmd(self, args, author, roles, dialogs):
        try:
            new_admin = unpack(args, '!admin <nouvel_admin>')
            assert author.user == roles.admin, msgs.MISSING_PERMISSIONS % ('admin', roles.game_name)
            assert roles.get_role_by_name(new_admin), msgs.NO_SUCH_PLAYER % new_admin
        except Exception as e:
            await author.user.send(e)
            return

        roles.change_admin(new_admin)
        await roles.everyone.send(msgs.ADMIN_SUCCESSFULLY_CHANGED % (roles.game_name, new_admin))

    async def command_not_found(self, cmd, author):
        await author.user.send(msgs.WRONG_COMMAND % cmd)

    async def send(self, msg, roles):
        """
        As messages are redirected from the dm_channel between the bot and the player,
        this sends the message to correct players ; for example, a message from a were-wolfs will only be redirected to
        other were-wolfs. Default redirection is everyone if not MSG.author is self.active_role, else warn the author,
        and doesn't redirect the message.
        """
        if self.active_role and roles.get_role_by_id(msg.author.id).role_name == self.active_role:
            await msg.author.send(
                "Attention ! Il ne faudrait pas que les autres te surprennent ! [CE MESSAGE N'A PAS ÉTÉ RELAYÉ ; "
                "UTILISE !public <msg> SI TU VEUX VRAIMENT L'ENVOYER À TOUS LES JOUEURS]"
            )
            return
        else:
            await roles.everyone.exclude(msg.author.id).send(roles.get_name_by_id(msg.author.id)+' : '+msg.content)

    async def end(self, roles, dialogs):
        """Ends the step. Default is to set self.ended to True"""
        self.ended = True
