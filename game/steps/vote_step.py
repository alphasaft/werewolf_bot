from game.steps.base_step import BaseStep
from game.roles.roleslist import RolesList
from assets.utils import unpack
import assets.messages as msgs


class VoteStep(BaseStep):
    def __init__(self):
        self.vote_targets = {}
        self.white_votes = 0
        self.forced_targets = []
        self.vote_turn = 1
        self.have_voted = []
        BaseStep.__init__(self, None)

    def _new_turn(self):
        self.vote_turn += 1
        self.vote_targets = {}
        self.white_votes = 0
        self.have_voted = []

    async def start(self, roles: RolesList, dialogs):
        self.__init__()
        await roles.everyone.send(dialogs.everyone.vote_begins.tell())

    async def vote_cmd(self, args, author, roles, dialogs):
        try:
            target = unpack(args, "!vote <joueur>")
            roles.check_has_player(target)
            assert author not in self.have_voted, dialogs.everyone.has_already_voted.tell()
            assert not self.forced_targets or target in self.forced_targets, dialogs.everyone.invalid_vote_target.tell(
                authorized_targets=" ,".join(self.forced_targets)
            )
        except Exception as e:
            await author.user.send(e)
            return

        if self.vote_targets.get(target):
            self.vote_targets[target] += 1
        else:
            self.vote_targets[target] = 1

        self.have_voted.append(author)

        await roles.everyone.send(
            dialogs.everyone.has_voted.tell(player=roles.get_name_by_id(author.user.id), target=target)
        )

        if self.have_voted == roles.alive_players:
            await self.end(roles, dialogs)

    async def voteforall_cmd(self, args, author, roles, dialogs):
        try:
            target = unpack(args, "!voteforall <joueur>")
            roles.check_has_player(target)
            roles.check_is_admin(author)
        except Exception as e:
            await author.user.send(e)
            return

        self.vote_targets = {target: len(roles.everyone)}
        await self.end(roles, dialogs)

    async def pass_cmd(self, args, author, roles, dialogs):
        if args:
            await author.user.send(msgs.TOO_MUCH_PARAMETERS % ('!pass', "' ,'".join(args)))

        await roles.everyone.send(dialogs.everyone.white_vote.tell(player=roles.get_name_by_id(author.user.id)))
        self.white_votes += 1

    async def end(self, roles, dialogs):
        if not self.vote_targets:
            await roles.everyone.send(dialogs.everyone.canceled_vote_by_white_votes.tell())
            await BaseStep.end(self, roles, dialogs)
            return

        final_targets = []
        max_votes = 0
        for target, votes in self.vote_targets.items():
            if votes >= max_votes:
                final_targets.append(target)
                max_votes = votes

        if len(final_targets) > 1:
            if self.vote_turn < 3:  # New vote turn
                self.forced_targets = final_targets
                self._new_turn()
                await roles.everyone.send(dialogs.everyone.equality.tell(
                    players=" ,".join(final_targets[:-1])+" et "+final_targets[-1], turn=str(self.vote_turn)
                ))
            else:
                await roles.everyone.send(dialogs.everyone.canceled_vote_by_equality.tell(
                    players=" ,".join(final_targets[:-1])+" et "+final_targets[-1]
                ))
                await BaseStep.end(self, roles, dialogs)
        else:
            await roles.everyone.send(dialogs.everyone.player_was_killed_by_vote.tell(
                player=final_targets[0],
                role=roles.get_role_by_name(final_targets[0]).role_name
            ))
            await roles.kill(final_targets[0])
            await BaseStep.end(self, roles, dialogs)
