from assets.utils import mention


class RoleGroup(list):
    def __init__(self, roles):
        list.__init__(self, roles)

    def __eq__(self, other):
        if not isinstance(other, (list, RoleGroup)):
            raise TypeError("Invalid type %s for RoleGroup.__eq__(self, other)" % other.__class__.__name__)

        for item in other:
            if item not in self:
                return False
        for item in self:
            if item not in other:
                return False

        return True

    def exclude(self, player_id: str):
        for i, role in enumerate(self):
            if role.user.id == player_id:
                self.pop(i)
        return self

    def contains_player(self, player_mention):
        return player_mention in self.players()

    def players(self):
        return [role.user for role in self]

    async def send(self, msg):
        for role in self:
            await role.user.send(msg)

    def __getitem__(self, item):
        return RoleGroup(list.__getitem__(self, item))
