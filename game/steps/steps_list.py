import game.steps


class StepList:
    def __init__(self):
        self.steps = [  # Begin steps (lovemaker, robber etc)
            game.steps.nicknames_step.NicknamesStep(),
            game.steps.begin_step.BeginStep(),
            game.steps.lovemaker_step.LoveMakerStep(),
        ]
        self.turn = [  # A turn : vote, witch, were-wolfs...
            game.steps.seeker_step.SeekerStep(),
            game.steps.werewolfs_step.WereWolfsStep(),
            game.steps.witch_step.WitchStep(),
            game.steps.hunter_step.HunterStep(),
            game.steps.death_summary_step.DeathSummaryStep(),
            game.steps.vote_step.VoteStep(),
            game.steps.hunter_step.HunterStep(),
            game.steps.dusk_step.DuskStep()
        ]
        self.end_step = game.steps.end_step.EndStep()
        self._generate_turn()
        self._cur = 0

    async def next_step(self, roles, dialogs):
        """Go to next step when the previous one is over"""
        if not self._cur < len(self.steps) - 1:
            self._generate_turn()
        self._cur += 1
        await self.check_game_is_over(roles)
        await self.current_step.start(roles, dialogs)

    def _generate_turn(self):
        """Create a new turn : night + day"""
        k = self.turn or []
        self.steps.extend(k)

    async def check_game_is_over(self, roles):
        print('checking')
        if (len(roles.alive_players) == 2 and roles.alive_players[0].loving == roles.alive_players[1] or
            roles.alive_players == roles.villagers or
                roles.alive_players == roles.were_wolfs or
                not roles.alive_players):
            self.end_step.active = True
        print('ended')

    @property
    def current_step(self):
        """Returns a BaseStep-subclass instance, representing the actual step : vote, witch turn, etc..."""
        return self.end_step if self.end_step.active else self.steps[self._cur]

    @property
    def ended(self):
        return self.end_step.ended
