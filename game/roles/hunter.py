from .villager import Villager
from assets.constants import HUNTER


class Hunter(Villager):
    def __init__(self, user, dialogs):
        Villager.__init__(self, user, dialogs, role=HUNTER)

    async def tell_role(self):
        await self.user.send(self.dialogs.hunter.tell_role.tell())
