from game.steps.base_step import BaseStep
from game.roles.roleslist import RolesList
from assets.utils import mention, unpack, signed_message, infos_format
import assets.messages as msgs


class WereWolfsStep(BaseStep):
    def __init__(self):
        self.targeted = None
        self.agree_players = []
        BaseStep.__init__(self, 'loup-garou')

    async def start(self, roles: RolesList, dialogs):
        self.__init__()
        await roles.everyone.send(dialogs.werewolf.wakes_up.tell())
        await roles.were_wolfs.send(dialogs.werewolf.turn.tell())

    async def send(self, msg, roles):
        if roles.get_role_by_id(msg.author.id).role_name == "loup-garou":
            await roles.were_wolfs.exclude(msg.author.id).send(signed_message(msg))
        else:
            await roles.everyone.exclude(msg.author.id).send(msg.author.mention+' : '+msg.content)

    async def kill_cmd(self, args, author, roles, dialogs):
        try:
            target = unpack(args, "!kill <joueur>")
            roles.check_has_player(target)
            assert roles.get_role_by_name(target) not in roles.were_wolfs, dialogs.werewolf.try_to_kill_werewolf.tell()
        except Exception as e:
            await author.user.send(e)
            return

        if not self.targeted or self.targeted == target:
            await author.user.send(infos_format(dialogs.werewolf.propose_target.tell(), target=target))

            await roles.were_wolfs.exclude(author.user.id).send(
                infos_format(dialogs.werewolf.get_target_proposition.tell(),
                             from_player=roles.get_name_by_id(author.user.id), target=target
                             ))
            self.agree_players.append(author)

        else:
            await author.user.send(infos_format(dialogs.werewolf.not_agree.tell(), old=self.targeted, new=target))

            await roles.were_wolfs.exclude(author.user.id).send(
                infos_format(dialogs.werewolf.someone_doesnt_agree.tell(),
                             from_player=roles.get_name_by_id(author.user.id), old=self.targeted, new=target
                             ))

            self.agree_players = [author]

        self.targeted = target
        if self.agree_players == roles.were_wolfs:
            await self.end(roles, dialogs)

    async def confirm_cmd(self, args, author, roles, dialogs):
        if not self.targeted:
            await author.user.send(dialogs.werewolf.no_target.tell())
            return

        self.agree_players.append(author)
        await author.user.send(infos_format(dialogs.werewolf.agree.tell(), target=self.targeted))
        await roles.were_wolfs.exclude(author.user.id).send(
            infos_format(dialogs.werewolf.someone_agree.tell(),
                         from_player=roles.get_name_by_id(author.user.id), target=self.targeted)
        )
        if self.agree_players == roles.were_wolfs:
            await self.end(roles, dialogs)

    async def end(self, roles, dialogs):
        roles.wound(self.targeted)
        await roles.were_wolfs.send(infos_format(dialogs.werewolf.done.tell(), target=self.targeted))
        await roles.everyone.send(dialogs.werewolf.go_to_sleep.tell())
        await BaseStep.end(self, roles, dialogs)
