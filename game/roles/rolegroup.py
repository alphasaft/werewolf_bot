import random


class RoleGroup(set):
    def __init__(self, roles):
        set.__init__(self, roles)

    def __eq__(self, other):
        if not isinstance(other, (set, RoleGroup)):
            try:
                other = set(other)
            except Exception as e:
                raise TypeError("Invalid type %s for RoleGroup.__eq__(self, other)" % other.__class__.__name__) from e

        return set.__eq__(self, other)

    def contains_player(self, player_id):
        try:
            self.get_player(player_id)
            return True
        except KeyError:
            return False

    def get_player(self, player_id):
        for role in self.copy():
            if role.user.id == player_id:
                return role
        raise KeyError("Cannot find a player with id %i" % player_id)

    def exclude(self, *player_ids):
        for _id in player_ids:
            self.remove(self.get_player(_id))
        return self

    def players(self):
        return [role.user for role in self]

    def only_alive(self):
        for player in self.copy():
            if not player.alive:
                self.exclude(player.id)
        return self

    def random(self):
        return random.choice(list(self))

    async def send(self, content=None, **kwargs):
        for role in self:
            await role.user.send(content=content, **kwargs)
