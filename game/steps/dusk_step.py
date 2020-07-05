from game.steps.base_step import BaseStep


class DuskStep(BaseStep):
    def __init__(self):
        BaseStep.__init__(self, None)

    async def start(self, roles, dialogs):
        await roles.everyone.send(dialogs.everyone.sleep.tell())
        await BaseStep.end(self, roles, dialogs)
