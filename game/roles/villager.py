from assets.constants import VILLAGER


class Villager:
    def __init__(self, user, dialogs, role=VILLAGER):
        self.loving = None
        self.alive = True
        self.injured = False
        self.protected = False

        self.user = user
        self.dialogs = dialogs
        self.role = role

    def __repr__(self):
        return '< %s : %s >' % (self.user.mention, type(self).__name__)

    def __eq__(self, other):
        return isinstance(other, Villager) and other.user == self.user

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return 0

    @property
    def id(self):
        """Shortcut for self.user.id"""
        return self.user.id

    async def send(self, content=None, **kwargs):
        """Shortcut for self.user.send()"""
        await self.user.send(content=content, **kwargs)

    async def tell_role(self):
        await self.user.send(self.dialogs.villager.tell_role.tell())

    async def kill(self, roles, dialogs, from_lover=False):
        self.injured = True
        self.alive = False

        if from_lover:
            await roles.everyone.send(dialogs.lovemaker.killed_by_love.tell(
                lover=roles.get_name_by_role(self.loving), player=roles.get_name_by_role(self), role=self.role
            ))
            await self.send(dialogs.everyone.you_are_dead.tell())

        if self.loving and not self.loving.injured and not from_lover:
            await roles.kill(roles.get_name_by_role(self.loving), from_lover=True)
