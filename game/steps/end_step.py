from .base_step import BaseStep
from game.roles import Roles
from game.session import Session
from assets.utils import block
import assets.messages as msgs
import assets.constants as consts



class EndStep(BaseStep):
    def __init__(self):
        BaseStep.__init__(
            self,
            active_role=None,
            helps=(
                "Utilisez `$quit` pour quitter la partie, ou discutez avec vos amis",
                "Utilisez `$quit` pour quitter la partie, ou discutez avec vos amis"  # help for the dead players
            ))

    async def start(self, roles: Roles, dialogs):
        roles_summary = "- "+",\n- ".join([name+': '+role.role for name, role in roles.items()])

        if len(roles.alive_players) == 2 and list(roles.alive_players)[0].loving == list(roles.alive_players)[1]:
            await roles.everyone.send(dialogs.everyone.lovers_won.tell(
                lover1=roles.get_name_by_id(list(roles.alive_players)[0].id),
                lover2=roles.get_name_by_id(list(roles.alive_players)[0].id),
                roles=roles_summary
            ))

        elif not roles.alive_players:
            await self.end(roles, dialogs)
            return

        elif roles.alive_players == roles.villagers.only_alive():
            await roles.everyone.send(dialogs.everyone.villagers_won.tell(roles=roles_summary))

        elif roles.alive_players == roles.were_wolfs.only_alive():
            await roles.everyone.send(dialogs.everyone.werewolfs_won.tell(roles=roles_summary))

        await roles.everyone.send(dialogs.everyone.game_ended.tell())

    async def external_again_cmd(self, args, author, roles, dialogs, session: Session):
        """ `*again` : Démarre une nouvelle partie """
        try:
            assert not args, msgs.TOO_MUCH_PARAMETERS % ("again", ", ".join(args))
            roles.check_is_admin(author)
            assert len(session.players) >= consts.MINIMUM_PLAYERS, "Pas assez de joueurs !"
        except Exception as e:
            await self.error(to=author, msg=e)
            return

        await roles.everyone.send(block(msgs.GAME_RESTARTED))
        await session.launch()

    async def end(self, roles, dialogs):
        await BaseStep.end(self, roles, dialogs)
