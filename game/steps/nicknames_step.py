from game.steps.base_step import BaseStep
from game.roles import Roles
from assets.utils import unpack, block
import assets.messages as msgs


class NicknamesStep(BaseStep):
    def __init__(self):
        BaseStep.__init__(
            self,
            active_role=None,
            helps=("Choisissez votre pseudo avec `$nickname monPseudo`, puis blockez le avec `*confirm`",)
        )
        self.waiting_for_nicknames = []
        self.confirmed = set()

    async def start(self, roles: Roles, dialogs):
        self.__init__()
        for name, role in roles.items():
            if not (name.isalnum() and len(name) <= 10 and " " not in name):
                await role.send(block(msgs.BAD_NAME % name))
                self.waiting_for_nicknames.append(role)
            else:
                await role.send(block(msgs.CHOOSE_NICKNAME % name))

    async def on_player_quit(self, roles, dialogs):
        if self.confirmed == roles.everyone or not roles:
            await BaseStep.end(self, roles, dialogs)

    async def nickname_cmd(self, args, author, roles: Roles, dialogs):
        """ `*nickname unPseudo` : Change votre pseudo pour unPseudo """

        try:
            new_nickname = unpack(args, "!nickname unPseudo")
            assert new_nickname.isalnum() and len(new_nickname) <= 10, msgs.INVALID_NICKNAME % new_nickname
            assert author not in self.confirmed, msgs.NICKNAME_ALREADY_CONFIRMED % roles.get_name_by_id(author.user.id)
            assert not roles.get_role_by_name(new_nickname), \
                msgs.NICKNAME_ALREADY_TAKEN % (new_nickname, roles.get_role_by_name(new_nickname).user.mention)
        except Exception as e:
            await self.error(to=author, msg=e)
            return

        if author in self.waiting_for_nicknames:
            self.waiting_for_nicknames.remove(author)

        roles.change_nickname(roles.get_name_by_id(author.user.id), new_nickname)
        await self.info(to=author, msg=msgs.CHANGED_NICKNAME % new_nickname)

    async def confirm_cmd(self, args, author, roles, dialogs):
        """ `*confirm` : Bloque votre pseudo pour celui actuel """
        try:
            assert not args, msgs.TOO_MUCH_PARAMETERS % " ,".join(args)
            assert author not in self.confirmed, msgs.NICKNAME_ALREADY_CONFIRMED % roles.get_name_by_id(author.user.id)
            assert author not in self.waiting_for_nicknames, msgs.PLEASE_FIRST_CHOOSE_NICKNAME
        except Exception as e:
            await self.error(to=author, msg=e)
            return

        self.confirmed.add(author)
        await self.info(
            to=roles.everyone,
            msg=msgs.CONFIRMED_NICKNAME % (author.user.mention, roles.get_name_by_id(author.user.id))
        )
        if self.confirmed == roles.everyone:
            await self.end(roles, dialogs)

    async def confirmall_cmd(self, args, author, roles, dialogs):
        if roles.admin == author.user:
            await self.end(roles, dialogs)
        else:
            await author.send(msgs.MISSING_PERMISSIONS % ("admin", roles.game_name))

    async def end(self, roles, dialogs):
        await roles.everyone.send(embed=msgs.GET_NICKNAMES.build(nicknames=" ,\n- ".join(
                player.user.mention + ' -> ' + nickname for nickname, player in roles.items()
        )))
        await BaseStep.end(self, roles, dialogs)

