from game.roles.villager import Villager


class WereWolf(Villager):
    def __init__(self, user, dialogs):
        Villager.__init__(self, user, dialogs, 'loup-garou')

    async def tell_role(self):
        await self.user.send(self.dialogs.werewolf.tell_role.tell())
