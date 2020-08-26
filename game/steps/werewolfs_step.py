from .base_step import BaseStep
from assets.utils import unpack
from assets.constants import WEREWOLF
import assets.messages as msgs


class WereWolfsStep(BaseStep):
    def __init__(self):
        self.targeted = None
        self.agree_players = set()
        BaseStep.__init__(
            self,
            active_role=WEREWOLF,
            helps=(
                "Proposez une cible avec `*kill uneCible`, ou montrez votre approbation avec `*confirm`",
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
        if not self.targeted:
            await self.error(to=author, msg=dialogs.werewolf.no_target.tell())
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
            agree=", ".join(roles.get_role_by_id(w.id) for w in self.agree_players) if self.agree_players else "encore personne"
        ))

    async def external_quit_cmd(self, args, author, roles, dialogs, session):
        """ `*quit` : Quitte définitivement la partie """
        if author in self.agree_players:
            self.agree_players.remove(author)
        await BaseStep.external_quit_cmd(self, args, author, roles, dialogs, session)

    async def end(self, roles, dialogs):
        roles.wound(self.targeted)
        await roles.were_wolfs.send(dialogs.werewolf.done.tell(target=self.targeted))
        await roles.everyone.send(dialogs.werewolf.go_to_sleep.tell())
        await BaseStep.end(self, roles, dialogs)
