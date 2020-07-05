from game.steps.base_step import BaseStep
from game.roles.roleslist import RolesList
from assets.utils import unpack
import assets.messages as msgs


class NicknamesStep(BaseStep):
    def __init__(self):
        BaseStep.__init__(self, None)
        self.waiting_for_nicknames = []
        self.confirmed = []

    async def start(self, roles: RolesList, dialogs):
        self.ended = False
        for name, role in roles.roles.items():
            if not (name.isalnum() and len(name) <= 10 and " " not in name):
                await role.user.send(msgs.BAD_NAME % name)
                self.waiting_for_nicknames.append(role)
            else:
                await role.user.send(msgs.CHOOSE_NICKNAME % name)

    async def send(self, msg, roles):
        await msg.author.send(msgs.PLEASE_FIRST_CHOOSE_NICKNAME)

    async def nickname_cmd(self, args, author, roles: RolesList, dialogs):
        try:
            new_nickname = unpack(args, "!nickname <pseudonyme>")
            assert new_nickname.isalnum() and len(new_nickname) <= 10, msgs.INVALID_NICKNAME % new_nickname
            assert author not in self.confirmed, msgs.NICKNAME_ALREADY_CONFIRMED % roles.get_name_by_id(author.user.id)
        except Exception as e:
            await author.user.send(e)
            return

        if author in self.waiting_for_nicknames:
            self.waiting_for_nicknames.remove(author)

        roles.change_nickname(roles.get_name_by_id(author.user.id), new_nickname)
        await author.user.send(msgs.CHANGED_NICKNAME % new_nickname)

    async def confirm_cmd(self, args, author, roles, dialogs):
        try:
            assert not args, msgs.TOO_MUCH_PARAMETERS % " ,".join(args)
            assert author not in self.confirmed, msgs.NICKNAME_ALREADY_CONFIRMED % roles.get_name_by_id(author.user.id)
            assert author not in self.waiting_for_nicknames, msgs.PLEASE_FIRST_CHOOSE_NICKNAME
        except Exception as e:
            await author.user.send(e)
            return

        await roles.everyone.send(msgs.CONFIRMED_NICKNAME % (author.user.mention, roles.get_name_by_id(author.user.id)))
        self.confirmed.append(author)
        if self.confirmed == roles.everyone:
            await self.end(roles, dialogs)

    async def confirmall_cmd(self, args, author, roles, dialogs):
        if roles.admin == author.user:
            await self.end(roles, dialogs)
        else:
            await author.user.send(msgs.MISSING_PERMISSIONS % ("admin", roles.game_name))

    async def end(self, roles, dialogs):
        await roles.everyone.send(msgs.GET_NICKNAMES % " ,\n- ".join([
            player.user.mention+' -> '+nickname for nickname, player in roles.roles.items()
        ]))
        await BaseStep.end(self, roles, dialogs)
