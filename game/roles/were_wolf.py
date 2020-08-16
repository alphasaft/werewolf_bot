from .villager import Villager
from assets.constants import WEREWOLF


class WereWolf(Villager):
    def __init__(self, user, dialogs):
        Villager.__init__(self, user, dialogs, WEREWOLF)

    async def tell_role(self):
        await self.user.send(self.dialogs.werewolf.tell_role.tell())
