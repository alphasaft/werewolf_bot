from game.steps.base_step import BaseStep
from game.roles import Roles
from assets.utils import unpack
from assets.constants import WHITE_VOTE
import assets.messages as msgs


class VoteStep(BaseStep):
    def __init__(self):
        self.votes = {}
        self.forced_targets = []
        self.vote_turn = 1

        BaseStep.__init__(
            self,
            active_roles=None,
            helps=(
                "Votez contre un joueur dangereux avec `*vote unJoueur`, ou votez blanc avec `*pass`",
                "Les villageois votent..."
            )
        )

    def _new_turn(self):
        self.vote_turn += 1
        self.votes = {}

    async def start(self, roles: Roles, dialogs):
        self.__init__()
        await roles.everyone.send(dialogs.everyone.vote_begins.tell())

    async def on_player_quit(self, roles, dialogs):
        if not roles.alive_players:
            await BaseStep.end(self, roles, dialogs)
        elif set(roles.get_name_by_id(player.user.id) for player in roles.alive_players) == set(self.votes.keys()):
            await self.end(roles, dialogs)

    async def vote_cmd(self, args, author, roles, dialogs):
        """ `*vote unJoueur` : Dépose un vote contre ce joueur """
        try:
            target = unpack(args, "!vote unJoueur")
            roles.check_has_player(target)
            assert not self.votes.get(roles.get_name_by_id(author.user.id)), dialogs.everyone.has_already_voted.tell()
            assert not self.forced_targets or target in self.forced_targets, dialogs.everyone.invalid_vote_target.tell(
                authorized_targets=", ".join(self.forced_targets[:-1]) + " ou " + self.forced_targets[-1]
            )
        except Exception as e:
            await self.error(to=author, msg=e)
            return

        self.votes[roles.get_name_by_id(author.user.id)] = target
        await self.info(
            to=roles.everyone,
            msg=dialogs.everyone.has_voted.tell(player=roles.get_name_by_id(author.user.id), target=target)
        )

        if set(roles.get_name_by_id(player.user.id) for player in roles.alive_players) == set(self.votes.keys()):
            await self.end(roles, dialogs)

    async def pass_cmd(self, args, author, roles, dialogs):
        """ `*pass` : Dépose un vote blanc """
        try:
            assert not self.votes.get(roles.get_name_by_id(author.user.id)), dialogs.everyone.has_already_voted.tell()
            assert not args, msgs.TOO_MUCH_PARAMETERS % ('!pass', "' ,'".join(args))
        except Exception as e:
            await self.error(to=author, msg=e)
            return

        await self.info(
            to=roles.everyone,
            msg=dialogs.everyone.white_vote.tell(player=roles.get_name_by_id(author.user.id))
        )
        self.votes[roles.get_name_by_id(author.user.id)] = WHITE_VOTE

        if set(roles.get_name_by_id(player.user.id) for player in roles.alive_players) == set(self.votes.keys()):
            await self.end(roles, dialogs)

    async def external_quit_cmd(self, args, author, roles, dialogs, session):
        """ `*quit` : Quitte définitivement la partie, en annulant votre vote """
        if self.votes.get(roles.get_name_by_id(author.user.id)):
            self.votes.pop(roles.get_name_by_id(author.user.id))
        await BaseStep.external_quit_cmd(self, args, author, roles, dialogs, session)

    async def votes_cmd(self, args, author, roles, dialogs):
        """ `*votes` : Affiche les votes de chacun """
        default = {player: "?" if status.alive else "définitivement mort" for player, status in roles.items()}

        await author.send(embed=msgs.GET_VOTES.build(votes=",\n- ".join((
            player + " -> " + target for player, target in {**default, **self.votes}.items()
        ))))

    async def voteforall_cmd(self, args, author, roles, dialogs):
        """ `*voteforall unJoueur : Force tous les joueurs à votre contre ce joueur"""
        try:
            target = unpack(args, "!voteforall unJoueur")
            roles.check_has_player(target)
            roles.check_is_game_admin(author)
        except Exception as e:
            await self.error(to=author, msg=e)
            return

        for user in roles.alive_players.players():
            self.votes[roles.get_name_by_id(user.id)] = target

        await self.end(roles, dialogs)

    async def end(self, roles, dialogs):
        if all(target == WHITE_VOTE for target in self.votes.values()):
            await roles.everyone.send(dialogs.everyone.canceled_vote_by_white_votes.tell())
            await BaseStep.end(self, roles, dialogs)
            return

        # Counting the votes for each players
        votes_count = {}
        for target in self.votes.values():
            if votes_count.get(target):
                votes_count[target] += 1
            else:
                votes_count[target] = 1
        if votes_count.get(WHITE_VOTE):
            votes_count.pop(WHITE_VOTE)

        # Getting the most voted players$conf
        max_votes = max(votes_count.values())
        final_targets = []
        for target, votes in votes_count.items():
            if votes == max_votes:
                final_targets.append(target)

        if len(final_targets) > 1:  # There is one or more equalities
            if self.vote_turn < 3:  # We organize a new vote turn
                self.forced_targets = final_targets
                self._new_turn()
                await roles.everyone.send(dialogs.everyone.equality.tell(
                    players=" ,".join(final_targets[:-1])+" et "+final_targets[-1], turn=str(self.vote_turn)
                ))

            else:  # We cancel the vote
                await roles.everyone.send(dialogs.everyone.canceled_vote_by_equality.tell(
                    players=" ,".join(final_targets[:-1])+" et "+final_targets[-1]
                ))
                await BaseStep.end(self, roles, dialogs)

        else:  # A player will be killed
            await roles.everyone.send(dialogs.everyone.player_was_killed_by_vote.tell(
                player=final_targets[0],
                role=roles.get_role_by_name(final_targets[0]).role
            ))
            await roles.kill(final_targets[0])
            await BaseStep.end(self, roles, dialogs)
