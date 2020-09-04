import random
import enum

from .base_step import BaseStep
from assets.utils import unpack
from assets.constants import WEREWOLF, LITTLE_GIRL
from assets.exceptions import ProtectedPlayer
import assets.messages as msgs


class _LittleGirlResults(enum.Enum):
    CAUGHT_RED_HANDED = 0
    NOTHING_HAPPENS = 1
    WEREWOLF_SEEN = 2


class _LittleGirlProbabilities(object):

    # Base probabilities
    CAUGHT_RED_HANDED = range(0, 2)
    NOTHING_HAPPENS = range(2, 80)
    WEREWOLF_SEEN = range(80, 100)

    EVOLUTION = (2, 5, 10, 20, 50)

    def __init__(self):
        self.caught_red_handed = self.CAUGHT_RED_HANDED
        self.nothing_happens = self.NOTHING_HAPPENS
        self.werewolf_seen = self.WEREWOLF_SEEN

    def spy(self):
        result = random.randint(0, 100)

        if result in self.caught_red_handed:
            ret = _LittleGirlResults.CAUGHT_RED_HANDED
        elif result in self.nothing_happens:
            ret = _LittleGirlResults.NOTHING_HAPPENS
        elif result in self.werewolf_seen:
            ret = _LittleGirlResults.WEREWOLF_SEEN
        else:
            ret = None

        if self.caught_red_handed.stop < 50:
            new = self.EVOLUTION[self.EVOLUTION.index(self.caught_red_handed.stop)+1]
            self.caught_red_handed = range(0, new)
            self.nothing_happens = range(new, 80)

        return ret


class WereWolfsStep(BaseStep):
    def __init__(self):
        # Werewolfs
        self.targeted = None
        self.agree_players = set()

        # Little girl
        self.probabilities = _LittleGirlProbabilities()
        self.werewolf_seen = None
        self.caught_red_handed = False

        BaseStep.__init__(
            self,
            active_roles={WEREWOLF, LITTLE_GIRL},
            helps=(
                "Si vous êtes un loup-garou, proposez une cible avec `*kill uneCible`, ou montrez votre approbation "
                "avec `*confirm`.\n"
                "Si vous êtes la petite fille, espionnez-les avec `$spy`. Attention, plus vous espionnerez, plus vous "
                "aurez de chance de vous faire attraper !",
                "Les loup-garous choisissent leur prochaine victime..."
            )
        )

    async def start(self, roles, dialogs):
        self.__init__()

        werewolfs = list(roles.were_wolfs.only_alive())
        if len(werewolfs) >= 2:
            fmt = ", ".join(roles.get_name_by_id(w.id) for w in werewolfs[:-1]) + " et " + roles.get_name_by_id(werewolfs[-1].id)
        else:
            fmt = roles.get_name_by_id(werewolfs[0])

        await roles.everyone.send(dialogs.werewolf.wakes_up.tell())
        await roles.were_wolfs.only_alive().send(dialogs.werewolf.turn.tell(werewolfs=fmt))
        if roles.little_girl and roles.little_girl.alive:
            await roles.little_girl.send(dialogs.little_girl.turn.tell())

    async def on_player_quit(self, roles, dialogs):
        if not roles.were_wolfs.only_alive():
            await BaseStep.end(self, roles, dialogs)
        elif self.agree_players == roles.were_wolfs.only_alive():
            await self.end(roles, dialogs)

    async def send(self, msg, roles):
        if roles.get_role_by_id(msg.author.id).role == WEREWOLF:
            to = roles.were_wolfs.exclude(msg.author.id)
        else:
            to = roles.everyone.exclude(msg.author.id)

        await self.redirect(
            from_=roles.get_name_by_id(msg.author.id),
            to=to,
            msg=msg.content
        )

    async def kill_cmd(self, args, author, roles, dialogs):
        """ `*kill uneCible` : Propose de tuer ce joueur. Si tous les loups sont d'accord, il/elle sera tué(e)"""
        try:
            target = unpack(args, "!kill uneCible")
            assert author in roles.were_wolfs, "Vous n'êtes pas un loup-garou !"
            roles.check_has_player(target)
            assert roles.get_role_by_name(target) not in roles.were_wolfs, dialogs.werewolf.try_to_kill_werewolf.tell()
        except Exception as e:
            await self.error(to=author, msg=e)
            return

        if not self.targeted or self.targeted == target:
            self.agree_players.add(author)
            await self.info(to=author, msg=dialogs.werewolf.propose_target.tell(target=target))
            await self.info(
                to=roles.were_wolfs.exclude(author.user.id),
                msg=dialogs.werewolf.get_target_proposition.tell(
                    from_player=roles.get_name_by_id(author.user.id),
                    target=target
                ))

        else:
            await self.info(to=author, msg=dialogs.werewolf.not_agree.tell(old=self.targeted, new=target))
            await self.info(to=roles.were_wolfs.exclude(author.user.id),
                            msg=dialogs.werewolf.someone_doesnt_agree.tell(
                                from_player=roles.get_name_by_id(author.user.id),
                                old=self.targeted, new=target
                            ))

            self.agree_players = {author}

        self.targeted = target
        if self.agree_players == roles.were_wolfs.only_alive():
            await self.end(roles, dialogs)

    async def confirm_cmd(self, args, author, roles, dialogs):
        """ `*confirm` : Confirme que vous êtes d'accord """
        try:
            assert author in roles.were_wolfs, "Vous n'êtes pas un loup-garou !"
            assert self.targeted, dialogs.werewolf.no_target.tell()
        except Exception as e:
            await self.error(to=author, msg=str(e))
            return

        self.agree_players.add(author)
        await self.info(to=author, msg=dialogs.werewolf.agree.tell(target=self.targeted))
        await self.info(to=roles.were_wolfs.exclude(author.user.id),
                        msg=dialogs.werewolf.someone_agree.tell(
                            from_player=roles.get_name_by_id(author.user.id),
                            target=self.targeted
                        ))

        if self.agree_players == roles.were_wolfs.only_alive():
            await self.end(roles, dialogs)

    async def werewolfs_cmd(self, args, author, roles, dialogs):
        """ `*werewolfs` : Affiche la liste des loup-garous ainsi que leur cible actuelle"""
        try:
            assert author in roles.were_wolfs, "Vous n'êtes pas un loup-garou !"
            assert not args, msgs.TOO_MUCH_PARAMETERS % ("!werewolfs", "', '".join(args))
        except Exception as e:
            await self.error(to=author, msg=e)

        await author.send(embed=msgs.GET_WEREWOLFS.build(
            werewolfs=",\n- ".join(roles.get_name_by_id(w.id) for w in roles.were_wolfs.only_alive()),
            target=self.targeted or "encore personne",

            agree=", ".join(roles.get_name_by_id(w.id) for w in self.agree_players) if self.agree_players else "encore personne"
        ))

    async def spy_cmd(self, args, author, roles, dialogs):
        """ `*spy` : Espionne les loup-garous. Attention à ne pas vous faire attraper !"""

        try:
            assert roles.little_girl and author == roles.little_girl, "Vous n'êtes pas la petite fille !"
            assert not self.werewolf_seen, dialogs.little_girl.werewolf_already_seen.tell(werewolf=self.werewolf_seen)
            assert not self.caught_red_handed, dialogs.little_girl.already_caught.tell()
        except Exception as e:
            await self.error(to=author, msg=str(e))
            return
        
        result = self.probabilities.spy()

        if result == _LittleGirlResults.WEREWOLF_SEEN:
            self.werewolf_seen = roles.were_wolfs.only_alive().random()
            await author.send(dialogs.little_girl.werewolf_seen.tell(werewolf=self.werewolf_seen.user.name))
        elif result == _LittleGirlResults.NOTHING_HAPPENS:
            await author.send(dialogs.little_girl.nothing_happens.tell())
        elif result == _LittleGirlResults.CAUGHT_RED_HANDED:
            self.caught_red_handed = True
            await author.send(dialogs.little_girl.caught_red_handed.tell())
            await roles.were_wolfs.send(dialogs.little_girl.little_girl_caught.tell(little_girl=author.user.name))

    async def external_quit_cmd(self, args, author, roles, dialogs, session):
        """ `*quit` : Quitte définitivement la partie """
        if author in self.agree_players:
            self.agree_players.remove(author)
        await BaseStep.external_quit_cmd(self, args, author, roles, dialogs, session)

    async def end(self, roles, dialogs):
        try:
            roles.wound(self.targeted)
            await roles.were_wolfs.send(dialogs.werewolf.done.tell(target=self.targeted))
        except ProtectedPlayer:
            await roles.were_wolfs.send(dialogs.werewolf.target_protected.tell(target=self.targeted))
        await roles.everyone.send(dialogs.werewolf.go_to_sleep.tell())
        await BaseStep.end(self, roles, dialogs)
