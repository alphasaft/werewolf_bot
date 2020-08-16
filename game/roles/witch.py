from .villager import Villager
from assets.constants import WITCH


class Witch(Villager):
    def __init__(self, user, dialogs):
        Villager.__init__(self, user, dialogs, WITCH)
        self.resurrect_potion = 1
        self.death_potion = 1

    def use_death_potion(self):
        self.death_potion -= 1

    def use_resurrect_potion(self):
        self.resurrect_potion -= 1

    async def tell_role(self):
        await self.user.send(self.dialogs.witch.tell_role.tell())
