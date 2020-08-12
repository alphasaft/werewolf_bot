import discord
from random import shuffle
import game.roles as roles
from game.roles.rolegroup import RoleGroup
from assets.exceptions import NotAnAdminError
import assets.messages as msgs


class RolesList:
    def __init__(self, dialogs, game_name, players: list = None, admin=None):
        self.roles = {}
        self._alive_players = {}
        self.admin = None
        self.game_name = game_name
        self.dialogs = dialogs
        if players:
            self.build(players, admin)

    def build(self, players: list, admin):
        shuffle(players)
        self.admin = admin
        self.roles = self._set_roles(players)
        self._alive_players = self.roles.copy()

    def _set_roles(self, players: list):
        max_were_wolfs = (len(players) // 4)
        roles_dict = {}

        def set_role(_roles, _player, role, dialogs):
            if _roles.get(_player.name):
                _roles[_player.__str__()] = role(_player, dialogs)  # discord.User.__str__ returns name#discriminator
            else:
                _roles[_player.name] = role(_player, dialogs)

        for i, player in enumerate(players):
            if i <= max_were_wolfs:
                set_role(roles_dict, player, roles.were_wolf.WereWolf, self.dialogs)
            elif i == max_were_wolfs + 1:
                set_role(roles_dict, player, roles.seeker.Seeker, self.dialogs)
            elif i == max_were_wolfs + 2:
                set_role(roles_dict, player, roles.witch.Witch, self.dialogs)
            elif i == max_were_wolfs + 3:
                set_role(roles_dict, player, roles.lovemaker.LoveMaker, self.dialogs)
            elif i == max_were_wolfs + 4:
                set_role(roles_dict, player, roles.hunter.Hunter, self.dialogs)
            else:
                set_role(roles_dict, player, roles.villager.Villager, self.dialogs)

        return roles_dict

    def check_has_player(self, name: str, injured=False):
        """
        If not WOUNDED, checks if the player designed by PLAYER_MENTION belongs this game and is not wounded, and alive.
        If WOUNDED, checks if this players belongs this game and is wounded, but alive.
        If some of this two checks fails, raises a NameError.
        """
        
        player_role = self.get_role_by_name(name)
        if not player_role:
            raise NameError(msgs.NO_SUCH_PLAYER % name)
        elif player_role and not player_role.alive:
            raise NameError(msgs.DEAD_PLAYER % name)

        if injured:
            if player_role and not player_role.injured:
                raise NameError(msgs.ALIVE_PLAYER % name)
        else:
            if player_role and player_role.injured:
                raise NameError(msgs.WOUNDED_PLAYER % name)

    def check_is_admin(self, player):
        if not player.user == self.admin:
            raise NotAnAdminError(msgs.MISSING_PERMISSIONS % ('admin', self.game_name))

    def get_role_by_name(self, name: str):
        return self.roles.get(name)

    def get_role_by_id(self, user_id: int):
        for role in self.roles.values():
            if role.user.id == user_id:
                return role

    def get_name_by_id(self, user_id: int):
        for name, role in self.roles.items():
            if role.user.id == user_id:
                return name

    def get_name_by_role(self, user_role):
        for name, role in self.roles.items():
            if role == user_role:
                return name

    def change_nickname(self, old: str, new: str):
        self.roles[new] = self.roles.pop(old)
        if old in self._alive_players:
            self._alive_players[new] = self._alive_players.pop(old)

    @property
    def everyone(self):
        return RoleGroup(self.roles.values())

    @property
    def alive_players(self):
        return RoleGroup(self._alive_players.values())

    @property
    def injured_players(self):
        return RoleGroup([r for r in self.alive_players if r.injured])

    @property
    def villagers(self):
        return RoleGroup([w for w in self.alive_players if not isinstance(w, roles.were_wolf.WereWolf)])

    @property
    def were_wolfs(self):
        return RoleGroup([w for w in self.alive_players if isinstance(w, roles.were_wolf.WereWolf)])

    @property
    def hunter(self):
        for r in self.alive_players:
            if isinstance(r, roles.hunter.Hunter):
                return r

    @property
    def love_maker(self):
        for r in self.alive_players:
            if isinstance(r, roles.lovemaker.LoveMaker):
                return r

    @property
    def seeker(self):
        for r in self.alive_players:
            if isinstance(r, roles.seeker.Seeker):
                return r

    @property
    def witch(self):
        for r in self.alive_players:
            if isinstance(r, roles.witch.Witch):
                return r

    def wound(self, name):
        self._alive_players[name].injured = True

    def heal(self, name):
        self._alive_players[name].injured = False

    async def kill(self, name, from_lover=False):
        self._alive_players[name].injured = True
        await self._alive_players[name].kill(roles=self, dialogs=self.dialogs, from_lover=from_lover)
        self._alive_players.pop(name)

    async def tell_roles(self):
        for role in self.roles.values():
            await role.tell_role()

    async def kill_injured_players(self):
        for name, player in self._alive_players.copy().items():
            if player.injured:
                await self._alive_players[name].kill(roles=self, dialogs=self.dialogs)
                self._alive_players.pop(name)

    def quit_game(self, player_name):
        self.roles.pop(player_name)
        if self._alive_players.get(player_name):
            self._alive_players.pop(player_name)

    def set_admin(self, player_name):
        role = self.get_role_by_name(player_name)
        self.admin = role.user
