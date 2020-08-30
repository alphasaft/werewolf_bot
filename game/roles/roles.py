# -*- coding=utf-8 -*-

from random import shuffle

from .were_wolf import WereWolf
from .witch import Witch
from .villager import Villager
from .seeker import Seeker
from .hunter import Hunter
from .lovemaker import LoveMaker
from .little_girl import LittleGirl

from .rolegroup import RoleGroup
from assets.exceptions import CommandPermissionError
import assets.messages as msgs


class Roles(dict):
    def __init__(self, dialogs, game_name, players: list = None, admin=None):
        dict.__init__(self)
        self.clear()  # Else this could store old players in case we restart a game

        self.game_name = game_name
        self.dialogs = dialogs

        self.admin = admin
        if players:
            self.build(players, admin)

    def __repr__(self):
        return "<Roles : %s>" % ", ".join(name + ' -> ' + user.role.title() for name, user in self.items())

    def build(self, players: list, admin, nicknames=None):
        shuffle(players)
        self.admin = admin
        self._set_roles(players, nicknames=nicknames)

    def _set_roles(self, players: list, nicknames=None):
        max_were_wolfs = (len(players) // 5) + 1
        nicknames = nicknames or {}

        def set_role(_player, role):
            if nicknames.get(_player.id):
                self[nicknames[_player.id]] = role(_player, self.dialogs)
            elif self.get(_player.name):
                self[_player.__str__()] = role(_player, self.dialogs)  # discord.User.__str__ returns name#discriminator
            else:
                self[_player.name] = role(_player, self.dialogs)

        for i, player in enumerate(players):
            if i < max_were_wolfs:
                set_role(player, WereWolf)
            elif i == max_were_wolfs:
                set_role(player, Seeker)
            elif i == max_were_wolfs + 1:
                set_role(player, Witch)
            elif i == max_were_wolfs + 2:
                set_role(player, LoveMaker)
            elif i == max_were_wolfs + 3:
                set_role(player, Hunter)
            else:
                set_role(player, Villager)

    def add_player(self, player):
        nicknames = {p.id: n for n, p in self.items()}  # We save the nicknames
        users = [r.user for r in self.players()] + [player]
        self.build(users, self.admin, nicknames=nicknames)

    def nicknames(self):
        return list(self.keys())

    def players(self):
        return list(self.values())

    def check_has_player(self, name: str, injured=False):
        """
        If not INJURED, checks if the player designed by PLAYER_MENTION belongs this game and is not wounded, and alive.
        If INJURED, checks if this players belongs this game and is wounded, but alive.
        If some of this two checks fails, raises a NameError.
        """

        player_role = self.get_role_by_name(name)
        if not player_role:
            raise NameError(msgs.NO_SUCH_PLAYER % name)
        elif not player_role.alive:
            raise NameError(msgs.DEAD_PLAYER % name)

        if injured:
            if player_role and not player_role.injured:
                raise NameError(msgs.ALIVE_PLAYER % name)
        else:
            if player_role and player_role.injured:
                raise NameError(msgs.WOUNDED_PLAYER % name)

    def check_is_admin(self, player):
        if not player.user == self.admin:
            raise CommandPermissionError(msgs.MISSING_PERMISSIONS % ('admin', self.game_name))

    def has_role(self, role):
        for player in self.players():
            if player.role == role:
                return True
        return False

    def get_role_by_name(self, name: str):
        return self.get(name)

    def get_role_by_id(self, user_id: int):
        for role in self.values():
            if role.user.id == user_id:
                return role

    def get_name_by_id(self, user_id: int):
        for name, role in self.items():
            if role.user.id == user_id:
                return name

    def get_name_by_role(self, user_role):
        for name, role in self.items():
            if role == user_role:
                return name

    def change_nickname(self, old: str, new: str):
        self[new] = self.pop(old)

    @property
    def everyone(self):
        """Returns a RoleGroup object containing all players of this game."""
        return RoleGroup(self.values())

    @property
    def alive_players(self):
        """Returns a RoleGroup object containing all alive and not injured players of this game."""
        return RoleGroup(p for p in self.values() if p.alive)

    @property
    def dead_players(self):
        """Returns a RoleGroup object containing all dead players of this game."""
        return RoleGroup(p for p in self.values() if not p.alive)

    @property
    def injured_players(self):
        """Returns a RoleGroup object containing all injured but alive players of this game."""
        return RoleGroup(p for p in self.values() if p.injured and p.alive)

    @property
    def villagers(self):
        """Returns a RoleGroup object containing all non-Werewolfs of this game."""
        return RoleGroup(w for w in self.players() if not isinstance(w, WereWolf))

    @property
    def were_wolfs(self):
        """Returns a RoleGroup object containing all Werewolfs of this game."""
        return RoleGroup(w for w in self.players() if isinstance(w, WereWolf))

    @property
    def hunter(self):
        """Returns the Hunter of this game."""
        for r in self.players():
            if isinstance(r, Hunter):
                return r

    @property
    def love_maker(self):
        """Returns the LoveMaker of this game"""
        for r in self.players():
            if isinstance(r, LoveMaker):
                return r

    @property
    def seeker(self):
        """Returns the Seeker of this game"""
        for r in self.players():
            if isinstance(r, Seeker):
                return r

    @property
    def witch(self):
        """Returns the Witch of this game"""
        for r in self.players():
            if isinstance(r, Witch):
                return r

    @property
    def little_girl(self):
        """Returns the LittleGirl of this game"""
        for r in self.players():
            if isinstance(r, LittleGirl):
                return r

    def wound(self, name):
        self[name].injured = True

    def heal(self, name):
        self[name].injured = False

    async def kill(self, name, from_lover=False):
        if self[name].alive:
            await self[name].kill(roles=self, dialogs=self.dialogs, from_lover=from_lover)

    async def tell_roles(self):
        for role in self.values():
            await role.tell_role()

    async def kill_injured_players(self):
        for player in self.alive_players.copy():
            if player.injured:
                await player.kill(roles=self, dialogs=self.dialogs)

    def quit_game(self, player_name):
        self.pop(player_name)

    def set_admin(self, player_name):
        role = self.get_role_by_name(player_name)
        self.admin = role.user
