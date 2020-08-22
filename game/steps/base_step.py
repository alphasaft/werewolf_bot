from assets.utils import italic, bold, indented, suppress_markdown, suppress, unpack, configure_logger
from assets.constants import ALLTIMES_CMDS, PREFIX
import assets.logger as logger
import assets.messages as msgs


# Logger configuration
configure_logger(logger)


class BaseStep:
    """
    Represents a step of a were-wolf game. Defines start, react, send and end, and a few commands.
    Override them if what they currently do is not what you want to do.
    """

    def __init__(self, active_role=None, helps=()):
        """
        Initialize self.

        Active_role describe the current active player, everyone (None) by default.
        Helps is a maximum-two-sized tuple, that contains first a help for the active role, and second for the others
        (this is not necessary provided when active_role is None)
        """
        self.ended = False
        self.active_role = active_role

        self.active_help = (helps[0] if len(helps) > 0 else "Pas d'aide disponible").replace('*', PREFIX)
        self.external_help = (helps[1] if len(helps) > 1 else "En attente d'un autre joueur").replace('*', PREFIX)

    @staticmethod
    async def error(to, msg):
        await to.send(bold(suppress_markdown(str(msg).strip())))

    @staticmethod
    async def redirect(from_, to, msg):
        await to.send(italic(suppress_markdown(from_ + ' : ' + str(msg).strip())))

    @staticmethod
    async def info(to, msg):
        await to.send(indented(suppress_markdown(str(msg).strip())))

    def is_current_role(self, user):
        return not self.active_role or user.role == self.active_role

    async def start(self, roles, dialogs):
        """
        Starts the step. For example, sends all players who wakes up and what to do. Default comportment is to
        reinitialize self using self.__init__(...).
        """
        self.__init__(self.active_role, (self.active_help, self.external_help))

    async def on_player_quit(self, roles, dialogs):
        """
        Should be called every time a player quits the game.
        This ends this step using BaseStep.end() if the player was needed for it.
        Default reaction is to end the step if there's no player anymore
        """
        if not roles:  # Nobody in here
            await self.end(roles, dialogs)

    async def send(self, msg, roles):
        """
        As messages are redirected from the dm_channel between the bot and the player,
        this sends the message to correct players ; for example, a message from a were-wolf will only be redirected to
        other were-wolfs.

        If MSG looks like a command where "$" where omitted, warn the user and doesn't redirect the message.
        Default redirection is everyone.
        """
        try:
            if (self.active_role and
                roles.get_role_by_id(msg.author.id).role == self.active_role and
                (hasattr(self, msg.content.strip().split()[0]+'_cmd'))
            ):
                await self.error(
                    to=msg.author,
                    msg="Attention ! Ce message ressemble fortement à une commande, et il ne faudrait pas que les "
                        "autres te surprennent ! [CE MESSAGE N'A PAS ÉTÉ RELAYÉ ; UTILISE $public monMessage SI TU "
                        "VEUX VRAIMENT L'ENVOYER À TOUS LES JOUEURS]"
                )
            else:
                await self.redirect(
                    from_=roles.get_name_by_id(msg.author.id),
                    to=roles.everyone.exclude(msg.author.id),
                    msg=msg.content
                )

        except Exception as e:
            logger.error(
                "The redirection of the message '%s' raised a(n) %s : %s" % (msg.content, e.__class__.__name, e)
            )
            await self.error(to=msg.author, msg=msgs.MESSAGE_HAS_RAISED % msg.content)

    async def react(self, cmd, args, author, roles, dialogs, session, disable_checks=False):
        """Reacts to a command, such as $kill or $vote."""

        if not disable_checks:
            if not (author.alive or cmd in ALLTIMES_CMDS):
                await self.error(to=author, msg=msgs.DEAD_USER_INVOKES_CMD)
                return

            if not (self.is_current_role(author) or cmd in ALLTIMES_CMDS):
                await author.send(msgs.WRONG_ROLE)
                return

        try:
            if hasattr(self, cmd + '_cmd'):
                await getattr(self, cmd + '_cmd')(args, author, roles, dialogs)
            elif hasattr(self, 'external_' + cmd + '_cmd'):
                await getattr(self, 'external_' + cmd + '_cmd')(args, author, roles, dialogs, session)
            else:
                await self.command_not_found(cmd, author)

        except Exception as e:
            fmt = "'%s %s' command invocation raised a(n) %s : %s" % (
                cmd, " ".join(args), e.__class__.__name__, str(e) or "[no further info]"
            )
            logger.error(fmt)
            await self.error(to=author, msg=msgs.COMMAND_HAS_RAISED % cmd)

        else:
            logger.debug("La commande de jeu '%s' vient d'être invoquée avec succès par %s" % (cmd, author.user.name))

    async def skip_cmd(self, args, author, roles, dialogs):
        """ `*skip` : Passe cette étape du jeu. À n'utiliser qu'en cas de problèmes."""
        try:
            assert not args, msgs.TOO_MUCH_PARAMETERS % (", ".join(args), "$skip")
            roles.check_is_admin(author)
        except Exception as e:
            await self.error(to=author, msg=e)

        await BaseStep.end(self, roles, dialogs)

    async def public_cmd(self, args, author, roles, dialogs):
        """ `*public monMessage` : Force l'envoi de ce message à tous les joueurs """
        await self.redirect(
            from_=roles.get_name_by_id(author.user.id),
            to=roles.everyone.exclude(author.user.id),
            msg=" ".join(args)
        )

    async def private_cmd(self, args, author, roles, dialogs):
        """ `*private unJoueur monMessage` : Envoi le message uniquement à ce joueur """
        try:
            roles.check_has_player(args[0])
        except Exception as e:
            await self.error(to=author, msg=e)
            return

        await self.redirect(
            from_=roles.get_name_by_id(author.user.id),
            to=roles.get_role_by_name(args[0]).user,
            msg=" ".join(args[1:])
        )

    async def players_cmd(self, args, author, roles, dialogs):
        """ `*players` : Renvoie la liste des joueurs ainsi que leur état """
        await author.send(embed=msgs.GET_NICKNAMES.build(nicknames=",\n- ".join(
                "%s -> %s (%s)" %
                (
                    player.user.mention,
                    nickname,
                    (
                        "vivant(e)" if not player.injured and player.alive else
                        "mort(e)" if player.injured and player.alive else
                        player.role
                     )
                )
                for nickname, player in roles.items()
        )))

    async def commands_cmd(self, args, author, roles, dialogs):
        """ `*commands` : Renvoie la liste des commandes utilisables """
        docs = ['- - - - - - - - - - - - - - - ']
        for attr in dir(self):
            if "cmd" in attr and (suppress(attr, "_cmd", "external_") in ALLTIMES_CMDS or self.is_current_role(author)):
                doc = getattr(self, attr).__doc__ or '`' + PREFIX + suppress(attr, "_cmd", "external_") + " [args...]`"
                if hasattr(BaseStep, attr):  # Basic command
                    docs.insert(0, doc)
                else:
                    docs.append(doc)

        await author.send(
            embed=msgs.GET_COMMANDS.build(commands=",\n- ".join(doc.strip().replace('*', PREFIX) for doc in docs))
        )

    async def external_quit_cmd(self, args, author, roles, dialogs, session):
        """ `*quit` : Quitte définitivement la partie """

        if author.user == roles.admin and not len(roles) == 1:
            candidates = list(roles.values())
            if candidates[0] == author:
                roles.admin = candidates[1].user
            else:
                roles.admin = candidates[0].user

            await self.info(to=author, msg="Votre role d'admin vient d'être transféré à %s" % roles.admin.name)

        await self.info(
            to=roles.everyone,
            msg="%s a quitté la partie. Il/elle était %s" % (roles.get_name_by_id(author.user.id), author.role)
        )

        await roles.kill(roles.get_name_by_id(author.id))
        session.remove_player(author.user.id)
        await self.on_player_quit(roles, dialogs)

    async def external_kick_cmd(self, args, author, roles, dialogs, session):
        """ `*kick unJoueur` : Kick ce joueur de la partie """
        try:
            kicked = unpack(args, '!kick unJoueur')
            roles.check_is_admin(author)
            assert roles.get_role_by_name(kicked), msgs.NO_SUCH_PLAYER % kicked
        except Exception as e:
            await self.error(author.user, str(e))
            return

        await self.info(
            to=roles.everyone,
            msg="%s a été kické(e) de la partie. Il/elle était %s" % (roles.get_name_by_id(author.user.id), author.role)
        )

        await roles.kill(roles.get_name_by_id(author.id))
        session.remove_player(author.user.id)
        await self.on_player_quit(roles, dialogs)

    async def external_admin_cmd(self, args, author, roles, dialogs, session):
        """ `*admin unJoueur` : Change l'administrateur de la partie pour unJoueur """
        try:
            new_admin = unpack(args, '!admin unJoueur')
            roles.check_is_admin(author)
            assert roles.get_role_by_name(new_admin), msgs.NO_SUCH_PLAYER % new_admin
        except Exception as e:
            await self.error(author.user, str(e))
            return

        session.set_admin(roles.get_role_by_name(new_admin).user.id)
        await roles.everyone.send(msgs.ADMIN_SUCCESSFULLY_CHANGED % (roles.game_name, new_admin))

    async def role_cmd(self, args, author, roles, dialogs):
        """ `*role` : Affiche votre role si vous l'avez oublié """
        await self.info(to=author, msg=msgs.GET_ROLE % author.role)

    async def help_cmd(self, args, author, roles, dialogs):
        """
        `*help (full)` : Vous indique ce que vous devez faire ; tapez $help full pour un tutoriel complet du jeu
        """
        if tuple(args) == ('full',):
            await author.send(embed=msgs.GAME_PRINCIPE.build())
            await author.send(embed=msgs.BASE_COMMANDS.build())
            return

        if self.is_current_role(author) and author.alive:
            await self.info(to=author, msg=self.active_help)
        else:
            await self.info(to=author, msg=self.external_help)

    async def command_not_found(self, cmd, author):
        await self.error(to=author, msg=msgs.WRONG_COMMAND % cmd)

    async def end(self, roles, dialogs):
        """Ends the step. Default is to set self.ended to True"""
        self.ended = True
