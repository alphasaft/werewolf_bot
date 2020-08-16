from .villager import Villager
from assets.constants import SEEKER


class Seeker(Villager):
    def __init__(self, user, dialogs):
        Villager.__init__(self, user, dialogs, SEEKER)
        self.saw = {}

    def see_role(self, user_mention: str, role: str):
        self.saw[user_mention] = role

    def saw_as_str(self):
        """Returns something like

        - @AnUser: WereWolf,
        - @AnOtherUser: Villager,
        - @AThirdUser: Witch

        Depending of the roles the player have seen
        """
        return "- "+",\n- ".join([user+': '+role for user, role in self.saw.items()])

    async def tell_role(self):
        await self.user.send(self.dialogs.seeker.tell_role.tell())

