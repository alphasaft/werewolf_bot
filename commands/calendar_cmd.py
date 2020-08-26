from bot import GameMaster
from assets.constants import EVENTS_CHANNEL
from assets.utils import configure_logger
import assets.logger as logger
import assets.messages as msgs
from game.events import convert_to_str, clean_str_dt


configure_logger(logger)


BRIEF = """Organise vos parties de jeu"""

FULL = """
Organise vos parties de jeu.
Vous devrez tout de même les créer et les rejoindre manuellement avec $game ... (autrement le moindre retard causerait \
votre exclusion de la partie, ou, au contraire, une longue attente des membres qui ne viendront peut être même pas, \
mais cette commande vous permet de programmer des parties pour une certaine date, et de vous le rappeler le moment \
venu, ainsi qu'à vos amis

Tous les "Quand" ci-dessous doivent être remplacés par une date, comme ceci :
    (jour/mois,)heure:minutes OU "today+"jours,heure:minutes
    
Ce qui donne par exemple:
    26/08,16:15    -->  Le 26 Août, 16h15
    18:00          -->  Aujourd'hui, 18h00
    today+3,19:30  -->  Dans 3 jours, à 19h30

! Attention ! 
La date ne doit comporter AUCUN espace !

Aides des commandes:
-------------------

calendar add Type Nom Quand  ->  Programme un événement de ce type avec ce nom pour cette date. Un seul type \
                                        ("game") est pour l'instant disponible

calendar subscribe NomDeLEvenement  ->  Vous ajoute à cette partie. Vous en recevrez donc les notifications

calendar quit NomDeLEvenement  ->  Quitte cet événement, ou le détruit si vous en êtes l'admin

calendar present NomDeLEvenement  ->  Confirme votre présence à l'événement après que celui-ci ait commencé

calendar when NomDeLEvenement  ->  Retourne la date de cet événement

calendar list  ->  Liste les événements disponibles sur le serveur

calendar me  ->  Affiche les événements auquels vous êtes inscrits

calendar notify NomDeLEvenement message -> Envoie le message à tous les participants de l'événément  
"""


def __implement__(bot: GameMaster):
    """Implement the command 'calender' in the bot. Unable to use that command if not implemented"""

    @bot.group(brief=BRIEF, help=FULL)
    async def calendar(ctx):
        if ctx.invoked_subcommand is None:
            sub = ctx.message.content.strip().split()[1:2]
            if sub:
                await ctx.channel.send("Sous-commande invalide %s (tapez $help calendar pour plus d'informations)" % sub)
            else:
                await ctx.channel.send("Sous-commande manquante (tapez $help calendar pour plus d'informations)")

    @calendar.group()
    async def add(ctx):
        if ctx.invoked_subcommand is None:
            await ctx.channel.send(msgs.BAD_EVENT_TYPE % (ctx.message.content.strip().split()[2:3] or "[pas de type]"))

    @add.command()
    async def game(ctx, name=None, when=None):
        try:
            bot.check_parameter(name, "$calendar add game NomDuJeu Quand", "NomDuJeu")
            bot.check_parameter(when, "$calendar add game NomDuJeu Quand", "Quand")
            bot.check_datetime_format(when)
            bot.check_is_not_over(when)
            bot.check_has_free_time(ctx.author.id, when)
            bot.check_name_is_available(name)
        except Exception as e:
            await ctx.channel.send(e)
            return

        bot.add_game_event(when, name, ctx.author, ctx.channel)
        await ctx.channel.send(msgs.EVENT_SUCCESSFULLY_CREATED % name)
        await bot.get_channel(EVENTS_CHANNEL).send(
            msgs.NEW_EVENT % (name, "jeu", ctx.author.mention, clean_str_dt(when), name)
        )

    @calendar.command()
    async def subscribe(ctx, name=None):
        try:
            bot.check_parameter(name, "$calendar subscribe NomDeLEvenement", "NomDeLEvenement")
            bot.check_event_exists(name)
            bot.check_has_free_time(ctx.author.id, bot.events[name].dt)
        except Exception as e:
            await ctx.channel.send(e)
            return

        bot.add_event_member(name, ctx.author)
        await bot.get_admin(name).send(msgs.SOMEONE_JOINED_YOUR_EVENT % (ctx.author.mention, name))
        await ctx.channel.send(msgs.EVENT_SUCCESSFULLY_SUBSCRIBED % name)

    @calendar.command(name='quit')
    async def _quit(ctx, name=None):
        try:
            bot.check_parameter(name, "$calendar quit NomDeLEvenement", "NomDeLEvenement")
            bot.check_event_exists(name)
            bot.check_has_joined_event(ctx.author.id, name)
            bot.check_can_confirm(ctx.author)
        except Exception as e:
            await ctx.channel.send(e)
            return

        if bot.get_admin(name) == ctx.author:
            await ctx.channel.send(msgs.CONFIRM_FOR_EVENT_DESTRUCTION % name)
            confirm = await bot.confirm(ctx.author, "$calendar quit (admin)")

            if confirm is None:
                return

            elif confirm:
                bot.delete_event(name)
                logger.info("Event %s was deleted by its owner %s" % (name, ctx.author.name))
                await ctx.channel.send(msgs.EVENT_SUCCESSFULLY_DELETED % name)

        else:
            bot.quit_event(ctx.author.id, name)
            logger.info("%s quited the event %s" % (ctx.author.name, bot.which_game(ctx.author.id)))
            await bot.get_admin(name).send(msgs.SOMEONE_JOINED_YOUR_EVENT % (ctx.author.mention, name))
            await ctx.channel.send(msgs.EVENT_SUCCESSFULLY_QUITED % name)

    @calendar.command(name="list")
    async def _list(ctx):
        events = ["%s (%s)" % (name, clean_str_dt(convert_to_str(dt))) for name, dt in bot.get_opened_events()]
        if events:
            await ctx.channel.send(embed=msgs.OPENED_EVENTS_LIST.build(events="\n- ".join(events)))
        else:
            await ctx.channel.send(embed=msgs.NO_OPENED_EVENT.build())

    @calendar.command()
    async def present(ctx, name=None):
        try:
            bot.check_parameter(name, "$calendar present NomDeLEvenement", "NomDeLEvenement")
            bot.check_event_exists(name)
            bot.confirm_presence(name, ctx.author.id)
        except Exception as e:
            await ctx.channel.send(e)
            return

        await ctx.channel.send(msgs.PRESENCE_CONFIRMED % name)
        await bot.get_admin(name).send(msgs.SOMEONE_CONFIRMED_HIS_PRESENCE % (ctx.author.display_name, name))

    @calendar.command()
    async def when(ctx, name=None):
        try:
            bot.check_parameter(name, "$calendar when NomDeLEvenement", "NomDeLEvenement")
            bot.check_event_exists(name)
        except Exception as e:
            await ctx.channel.send(e)

        await ctx.channel.send(msgs.GET_EVENT_DATE % (name, clean_str_dt(convert_to_str(bot.events[name].dt))))

    @calendar.command()
    async def me(ctx):
        events = [
            "%s (%s)" % (name, clean_str_dt(convert_to_str(dt))) for name, dt in bot.get_joined_events(ctx.author.id)
        ]
        if events:
            await ctx.channel.send(embed=msgs.GET_JOINED_EVENTS.build(events="\n- ".join(events)))
        else:
            await ctx.channel.send(embed=msgs.NO_JOINED_EVENTS.build())

    @calendar.command()
    async def notify(ctx, name, *msg):
        try:
            bot.check_event_exists(name)
            bot.check_has_joined_event(ctx.author.id, name)
        except Exception as e:
            await ctx.channel.send(e)
            return

        await bot.events[name].notify(" ".join(msg))


