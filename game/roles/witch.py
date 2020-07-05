from game.roles.villager import Villager


class Witch(Villager):
    def __init__(self, user, dialogs):
        Villager.__init__(self, user, dialogs, 'sorcière')
        self.resurrect_potion = 1
        self.death_potion = 1

    def use_death_potion(self):
        self.death_potion -= 1

    def use_resurrect_potion(self):
        self.resurrect_potion -= 1

    async def tell_role(self):
        await self.user.send(self.dialogs.witch.tell_role.tell())
