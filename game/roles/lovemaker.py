from game.roles.villager import Villager


class LoveMaker(Villager):
    def __init__(self, user, dialogs):
        Villager.__init__(self, user, dialogs, 'cupidon')

    async def tell_role(self):
        await self.user.send(self.dialogs.lovemaker.tell_role.tell())
