from game.roles.villager import Villager


class Hunter(Villager):
    def __init__(self, user, dialogs):
        Villager.__init__(self, user, dialogs, 'chasseur')

    async def tell_role(self):
        await self.user.send(self.dialogs.hunter.tell_role.tell())
