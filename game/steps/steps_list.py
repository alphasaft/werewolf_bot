import game.steps
import assets.logger as logger
from assets.utils import configure_logger
from assets.constants import WEREWOLF


# Logger configuration
configure_logger(logger)


class StepList:
    def __init__(self):
        self._steps = [  # Begin steps (lovemaker, nicknames etc)
            game.steps.nicknames_step.NicknamesStep(),
            game.steps.begin_step.BeginStep(),
            game.steps.lovemaker_step.LoveMakerStep(),
        ]
        self._turn = [  # A turn : vote, witch, were-wolfs...
            game.steps.seeker_step.SeekerStep(),
            game.steps.werewolfs_step.WereWolfsStep(),
            game.steps.witch_step.WitchStep(),
            game.steps.death_summary_step.DeathSummaryStep(),
            game.steps.hunter_step.HunterStep(),
            game.steps.vote_step.VoteStep(),
            game.steps.hunter_step.HunterStep(),
            game.steps.dusk_step.DuskStep()
        ]
        self._end_step = game.steps.end_step.EndStep()
        self._generate_turn()
        self._cur = 0
        self._end_step_enabled = False

    def _generate_turn(self):
        """Create a new turn : night + day"""
        logger.debug("A new game turn was generated")
        self._steps.extend(self._turn or [])

    def _check_game_is_over(self, roles):
        if any((
            (len(roles.alive_players) == 2 and list(roles.alive_players)[0].loving == list(roles.alive_players)[1] and
             (list(roles.alive_players)[0].role == WEREWOLF) ^ (list(roles.alive_players)[1].role == WEREWOLF)),
            roles.alive_players == roles.villagers.only_alive(),
            roles.alive_players == roles.were_wolfs.only_alive(),
            not roles.alive_players
        )):
            self._end_step_enabled = True

    async def next_step(self, roles, dialogs):
        """Go to next step when the previous one is over"""
        if not self._cur < len(self._steps) - 1:
            self._generate_turn()
        self._cur += 1
        self._check_game_is_over(roles)
        logger.debug(
            "Step %s has ended, starting step %s" % (self._steps[self._cur-1], self.current_step.__class__.__name__)
        )
        await self.current_step.start(roles, dialogs)

    @property
    def current_step(self):
        """Returns a BaseStep-subclass instance, representing the actual step : vote, witch turn, etc..."""
        return self._end_step if self._end_step_enabled else self._steps[self._cur]

    @property
    def ended(self):
        return self._end_step.ended
