# Cannot speak correctly english, so maybe "seeker" is not "voyante"
from game.roles.villager import Villager


class Seeker(Villager):
    def __init__(self, user, dialogs):
        Villager.__init__(self, user, dialogs, 'voyante')
        self.saw = {}

    def see_role(self, user_mention: str, role_name: str):
        self.saw[user_mention] = role_name

    def saw_as_str(self):
        """Returns something like

        - @AnUser: WereWolf,
        - @AnOtherUser: Villager,
        - @AThirdUser: Witch

        Depending of the roles the player have seen
        """
        return "- "+",\n- ".join([user+': '+role_name for user, role_name in self.saw.items()])

    async def tell_role(self):
        await self.user.send(self.dialogs.seeker.tell_role.tell())

