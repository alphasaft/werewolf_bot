from game.steps.base_step import BaseStep
from game.roles.roleslist import RolesList
from assets.utils import unpack, infos_format


class WitchStep(BaseStep):
    def __init__(self):
        BaseStep.__init__(self, 'sorcière')

    async def start(self, roles: RolesList, dialogs):
        self.ended = False
        if not roles.witch:
            await BaseStep.end(self, roles, dialogs)
            return

        await roles.everyone.send(dialogs.witch.wakes_up.tell())
        if roles.witch.injured:
            await roles.witch.user.send(
                infos_format(dialogs.witch.is_dying.tell(),
                             killed_players=", ".join([name for name, player in roles.roles.items() if player.injured and not player == roles.witch]) or "personne (sauf vous)",
                             death_potion=str(roles.witch.death_potion),
                             resurrect_potion=str(roles.witch.resurrect_potion)
            ))
        else:
            await roles.witch.user.send(
                infos_format(dialogs.witch.turn.tell(),
                             killed_players=", ".join([name for name, player in roles.roles.items() if player.injured and not player == roles.witch]) or "personne",
                             death_potion=str(roles.witch.death_potion),
                             resurrect_potion=str(roles.witch.resurrect_potion)
            ))

    async def pass_cmd(self, args, author, roles, dialogs):
        await author.user.send(dialogs.witch.do_nothing.tell())
        await self.end(roles, dialogs)

    async def kill_cmd(self, args, author, roles, dialogs):
        try:
            target = unpack(args, "!kill <joueur>")
            roles.check_has_player(target)
            assert roles.witch.death_potion, dialogs.witch.empty_death_potion.tell()
            assert target != roles.get_name_by_id(author.user.id), dialogs.witch.try_to_kill_herself.tell()
        except Exception as e:
            await author.user.send(e)
            return

        roles.witch.use_death_potion()
        roles.wound(target)
        await roles.witch.user.send(infos_format(dialogs.witch.kill.tell(), target=target))
        await self.end(roles, dialogs)

    async def resurrect_cmd(self, args, author, roles, dialogs):
        if not args:
            await self.resurrect_self(author, roles, dialogs)
            return

        try:
            target = unpack(args, "!resurrect <joueur>")
            assert not (target == roles.get_name_by_id(author.user.id) and not author.injured), dialogs.witch.try_to_resurrect_herself.tell()
            roles.check_has_player(target, injured=True)
            assert roles.witch.resurrect_potion, dialogs.witch.empty_resurrect_potion.tell()
        except Exception as e:
            await author.user.send(e)
            return

        author.use_resurrect_potion()
        roles.heal(target)
        await roles.witch.user.send(infos_format(dialogs.witch.resurrect.tell(), target=target))
        await self.end(roles, dialogs)

    async def resurrect_self(self, author, roles, dialogs):
        try:
            assert author.injured, dialogs.witch.try_to_resurrect_herself.tell()
        except Exception as e:
            await author.user.send(e)
            return

        author.use_resurrect_potion()
        roles.heal(roles.get_name_by_id(author.user.id))
        await roles.witch.user.send(dialogs.witch.resurrect_herself.tell())
        await self.end(roles, dialogs)

    async def end(self, roles, dialogs):
        await roles.everyone.exclude(roles.witch.user.id).send(dialogs.witch.go_to_sleep.tell())
        await BaseStep.end(self, roles, dialogs)
