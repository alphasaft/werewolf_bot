from .villager import Villager
from assets.constants import IDIOT


class Idiot(Villager):
    def __init__(self, user, dialogs):
        Villager.__init__(self, user, dialogs, IDIOT)
        self.revealed = False

    async def tell_role(self):
        await self.user.send(self.dialogs.idiot.tell_role.tell())
