class Villager:
    def __init__(self, user, dialogs, role_name='villageois'):
        self.loving = None
        self.alive = True
        self.injured = False

        self.user = user
        self.dialogs = dialogs
        self.role_name = role_name

    def __str__(self):
        return '< %s : %s >' % (self.user.mention, type(self).__name__)

    def __eq__(self, other):
        return isinstance(other, Villager) and other.user == self.user

    def __ne__(self, other):
        return not self.__eq__(other)

    async def tell_role(self):
        await self.user.send(self.dialogs.villager.tell_role.tell())

    async def kill(self, roles, dialogs, from_lover=False):
        self.alive = False
        if from_lover:
            await roles.everyone.send(dialogs.lovemaker.death_by_love.tell(
                lover=roles.get_name_by_role(self.loving), player=roles.get_name_by_role(self)
            ))

        if self.loving and not self.loving.injured and not from_lover:
            await roles.kill(roles.get_name_by_role(self.loving), from_lover=True)
