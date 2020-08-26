from bot import GameMaster
from assets.constants import EVENTS_CHANNEL
import assets.messages as msgs


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

:exclamation: Attention :exclamation: 
La date ne doit comporter AUCUN espace !

Aides des commandes:

calendar add NomDeLaPartie Quand  ->  Programme une partie pour cette date
calendar subscribe NomDeLaPartie  ->  Vous ajoute à cette partie. Vous en recevrez donc les notifications
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
            bot.check_has_free_time(ctx.author.id, when)
            bot.check_name_is_available(name)
        except Exception as e:
            await ctx.channel.send(e)
            return

        bot.add_game_event(when, name, ctx.author, ctx.channel)
        # await bot.get_channel(EVENTS_CHANNEL).send(msgs.NEW_EVENT % (name, "jeu", ctx.author.mention, when))
        await ctx.channel.send(msgs.EVENT_SUCCESSFULLY_CREATED % name)

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
        await ctx.channel.send(msgs.EVENT_SUCCESSFULLY_SUBSCRIBED % name)

    @calendar.command()
    async def present(ctx, name=None):
        try:
            bot.check_parameter(name, "$calendar present NomDeLEvenement", "NomDeLEvenement")
            bot.check_event_exists(name)
            bot.confirm_presence(name, ctx.author.id)
        except Exception as e:
            await ctx.channel.send(e)
            return

        await ctx.channel.send(":white_check_mark: Votre présence a bien été confirmée pour l'événement %s !" % name)
