from .villager import Villager
from assets.constants import LITTLE_GIRL


class LittleGirl(Villager):
    def __init__(self, user, dialogs):
        Villager.__init__(self, user, dialogs, LITTLE_GIRL)

    async def tell_role(self):
        await self.user.send(self.dialogs.little_girl.tell_role.tell())

