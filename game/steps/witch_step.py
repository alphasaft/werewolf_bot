from .base_step import BaseStep
from assets.utils import unpack
from assets.constants import WITCH


class WitchStep(BaseStep):
    def __init__(self):
        BaseStep.__init__(
            self,
            active_role=WITCH,
            helps=(
                "Ressucitez quelqu'un avec `*resurrect (unJoueur)`, tuez-en un avec `*kill unJoueur` ou ne faites rien "
                "avec `*pass`", "La socière choisit que faire")
        )

    async def on_player_quit(self, roles, dialogs):
        if not (roles.witch and roles.witch.alive):
            await BaseStep.end(self, roles, dialogs)

    async def start(self, roles, dialogs):
        self.__init__()
        if not (roles.witch and roles.witch.alive):
            await BaseStep.end(self, roles, dialogs)
            return

        await roles.everyone.send(dialogs.witch.wakes_up.tell())
        if roles.witch.injured:
            await roles.witch.user.send(dialogs.witch.is_dying.tell(
                 killed_players=", ".join([name for name, player in roles.items() if player.injured and not player == roles.witch]) or "personne (sauf vous)",
                 death_potion=str(roles.witch.death_potion),
                 resurrect_potion=str(roles.witch.resurrect_potion)
            ))
        else:
            await roles.witch.user.send(dialogs.witch.turn.tell(
                 killed_players=", ".join(name for name, player in roles.items() if player.injured and not player == roles.witch and player.alive) or "personne",
                 death_potion=str(roles.witch.death_potion),
                 resurrect_potion=str(roles.witch.resurrect_potion)
            ))

    async def pass_cmd(self, args, author, roles, dialogs):
        """ `*pass` : Indique que vous ne voulez rien faire """
        await author.send(dialogs.witch.do_nothing.tell())
        await self.end(roles, dialogs)

    async def kill_cmd(self, args, author, roles, dialogs):
        """ `*kill unJoueur` : Utilise votre potion de mort pour tuer ce joueur """
        try:
            target = unpack(args, "!kill unJoueur")
            roles.check_has_player(target)
            assert roles.witch.death_potion, dialogs.witch.empty_death_potion.tell()
            assert target != roles.get_name_by_id(author.user.id), dialogs.witch.try_to_kill_herself.tell()
        except Exception as e:
            await self.error(to=author, msg=e)
            return

        author.use_death_potion()
        roles.wound(target)
        await roles.witch.user.send(dialogs.witch.kill.tell(target=target))
        await self.end(roles, dialogs)

    async def resurrect_cmd(self, args, author, roles, dialogs):
        """ `*resurrect (unJoueur)` : Ressucite  ce joueur, ou vous avec `$resurrect` """
        if not args:
            await self.resurrect_self(author, roles, dialogs)
            return

        try:
            target = unpack(args, "!resurrect unJoueur")
            assert not (target == roles.get_name_by_id(author.user.id) and not author.injured), dialogs.witch.try_to_resurrect_herself.tell()
            roles.check_has_player(target, injured=True)
            assert roles.witch.resurrect_potion, dialogs.witch.empty_resurrect_potion.tell()
        except Exception as e:
            await self.error(to=author, msg=e)
            return

        author.use_resurrect_potion()
        roles.heal(target)
        await roles.witch.user.send(dialogs.witch.resurrect.tell(target=target))
        await self.end(roles, dialogs)

    async def resurrect_self(self, author, roles, dialogs):
        """Resurrect the witch when she was injured"""
        try:
            assert author.injured, dialogs.witch.try_to_resurrect_herself.tell()
        except Exception as e:
            await author.send(e)
            return

        author.use_resurrect_potion()
        roles.heal(roles.get_name_by_id(author.user.id))
        await roles.witch.user.send(dialogs.witch.resurrect_herself.tell())
        await self.end(roles, dialogs)

    async def end(self, roles, dialogs):
        await roles.everyone.exclude(roles.witch.user.id).send(dialogs.witch.go_to_sleep.tell())
        await BaseStep.end(self, roles, dialogs)
