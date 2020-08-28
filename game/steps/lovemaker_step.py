from .base_step import BaseStep
from assets.utils import unpack
from assets.constants import LOVEMAKER, WEREWOLF


class LoveMakerStep(BaseStep):
    def __init__(self):
        BaseStep.__init__(
            self,
            active_roles=LOVEMAKER,
            helps=(
                "Choisissez deux personnes à faire s'aimer avec `*love joueur1 joueur2`",
                "Cupidon choisit les amoureux"
            ))

    async def start(self, roles, dialogs):
        self.__init__()
        self.ended = False
        if not (roles.love_maker and roles.love_maker.alive):
            await BaseStep.end(self, roles, dialogs)
            return

        await roles.everyone.send(dialogs.lovemaker.wakes_up.tell())
        await roles.love_maker.user.send(dialogs.lovemaker.turn.tell())

    async def on_player_quit(self, roles, dialogs):
        if not (roles.love_maker and roles.love_maker.alive):
            await BaseStep.end(self, roles, dialogs)

    async def love_cmd(self, args, author, roles, dialogs):
        """ `*love joueur1 joueur2` : Rends les joueurs j1 et j2 amoureux """
        try:
            target1, target2 = unpack(args, "!love joueur1 joueur2")
            roles.check_has_player(target1)
            roles.check_has_player(target2)
            assert roles.get_name_by_id(author.user.id) not in [target1, target2], dialogs.lovemaker.try_to_involve_himself.tell()
            assert not target1 == target2, dialogs.lovemaker.target1_is_target2.tell()
        except Exception as e:
            await self.error(to=author, msg=e)
            return

        target1_name = target1
        target2_name = target2
        target1 = roles.get_role_by_name(target1_name)
        target2 = roles.get_role_by_name(target2_name)

        target1.loving = target2
        target2.loving = target1
        await target1.user.send(dialogs.lovemaker.in_love.tell(lover=target2_name, role=target2.role.upper()))
        await target2.user.send(dialogs.lovemaker.in_love.tell(lover=target1_name, role=target1.role.upper()))
        if (target1.role == WEREWOLF) ^ (target2.role == WEREWOLF):
            await target1.user.send(dialogs.lovemaker.new_goal.tell(lover=target2_name))
            await target2.user.send(dialogs.lovemaker.new_goal.tell(lover=target1_name))

        await self.end(roles, dialogs)

    async def end(self, roles, dialogs):
        await roles.love_maker.user.send(dialogs.lovemaker.done.tell())
        await roles.everyone.exclude(roles.love_maker.user.id).send(dialogs.lovemaker.go_to_sleep.tell())
        await BaseStep.end(self, roles, dialogs)

