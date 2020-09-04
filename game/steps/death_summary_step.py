from game.steps.base_step import BaseStep
from game.roles import WereWolf


class DeathSummaryStep(BaseStep):
    def __init__(self):
        BaseStep.__init__(self, None)

    async def start(self, roles, dialogs):
        self.__init__()
        await roles.villagers.send(dialogs.everyone.villagers_dead_summary.tell())
        await roles.were_wolfs.send(dialogs.everyone.werewolfs_dead_summary.tell())

        if not roles.injured_players:
            await roles.everyone.send(dialogs.everyone.nobody_is_dead.tell())

        else:
            for role in roles.injured_players:
                player_name = roles.get_name_by_id(role.user.id)
                await role.user.send(dialogs.everyone.killed_by_night.tell())

                if isinstance(role, WereWolf):
                    await roles.villagers.send(
                        dialogs.everyone.werewolf_death_seen_by_villager.tell(player=player_name)
                    )
                    await roles.were_wolfs.exclude(role.user.id).send(
                        dialogs.everyone.werewolf_death_seen_by_werewolf.tell(player=player_name)
                    )

                else:
                    await roles.villagers.exclude(role.user.id).send(
                        dialogs.everyone.villager_death_seen_by_villager.tell(player=player_name, role=role.role)
                    )

                    await roles.were_wolfs.send(
                        dialogs.everyone.villager_death_seen_by_werewolf.tell(player=player_name, role=role.role)
                    )

        for role in roles.everyone:
            role.protected = False

        await roles.kill_injured_players()
        await self.end(roles, dialogs)
