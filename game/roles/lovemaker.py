from .villager import Villager
from assets.constants import LOVEMAKER


class LoveMaker(Villager):
    def __init__(self, user, dialogs):
        Villager.__init__(self, user, dialogs, LOVEMAKER)

    async def tell_role(self):
        await self.user.send(self.dialogs.lovemaker.tell_role.tell())
