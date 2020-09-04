from .villager import Villager
from assets.constants import GUARD


class Guard(Villager):
    def __init__(self, user, dialogs):
        Villager.__init__(self, user, dialogs, GUARD)
        self.protected_player = None

    async def tell_role(self):
        await self.user.send(self.dialogs.guard.tell_role.tell())
