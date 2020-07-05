from game.steps.base_step import BaseStep


class BeginStep(BaseStep):
    def __init__(self):
        BaseStep.__init__(self, None)

    async def start(self, roles, dialogs):
        await roles.everyone.send(dialogs.everyone.game_begins.tell())
        await roles.everyone.send(dialogs.everyone.first_sleep.tell())
        await roles.tell_roles()
        await BaseStep.end(self, roles, dialogs)
