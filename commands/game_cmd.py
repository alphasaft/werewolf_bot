from discord.utils import get
from assets import messages as msgs
from bot.game_master import GameMaster
from assets.utils import mention


BRIEF = """Crée, supprime et gère vos parties."""

FULL = """
Crée, supprime et gère vos parties.
Pas d'autorisations nécessaires pour utiliser cette commande.

game new <NOM> -> crée la partie NOM ; vous êtes son admin
game join <NOM> -> Rejoint la partie NOM
game quit -> Quitte la partie, ou la détruit si vous êtes son admin
game list -> Affiche la liste des parties joignables
game members <PARTIE> -> Affiche les membres de la partie PARTIE

Ces commandes nécessitent d'être l'admin de votre partie.
[admin] game admin <JOUEUR> -> Change l'admin pour JOUEUR
[admin] game kick <JOUEUR> -> Kick le joueur JOUEUR de votre partie
"""


def __implement__(bot: GameMaster):
    """Implement the command 'game' in the bot. Unable to use that command if not implemented"""

    bot.super_command("game", ['new', 'join', 'admin', 'quit', 'kick', 'list', 'members', 'start'],
                      brief=BRIEF, help=FULL, channel="taverne", contains=True, false_channel_warn=True)

    # Create a new game session
    @bot.sub_command
    async def game_new(ctx, game_name=None, *too):
        try:
            bot.check_parameter(game_name, msgs.MISSING_PARAMETER % ("game new <NOM DE LA PARTIE>", "NOM DE LA PARTIE"))
            bot.check_game_doesnt_exist(game_name)
            bot.check_is_alone(ctx.author.mention)
            bot.check_not_too_much_parameters(too, "game new <NOM DE LA PARTIE>")
        except Exception as e:
            await ctx.channel.send(e)
            return

        bot.add_game(game_name, ctx.author)
        await ctx.channel.send(msgs.SUCCESSFULLY_CREATED % (game_name, game_name))

    # Join a game session
    @bot.sub_command
    async def game_join(ctx, game_name=None):
        try:
            bot.check_parameter(game_name, msgs.MISSING_PARAMETER % ("game join <NOM DE LA PARTIE>", "NOM DE LA PARTIE"))
            bot.check_is_alone(ctx.author.mention)
            bot.check_game_exists(game_name)
        except Exception as e:
            await ctx.channel.send(e)
            return

        bot.join_game(game_name, ctx.author)
        await ctx.channel.send(msgs.SUCCESSFULLY_JOINED % game_name)

    # Change the admin of a game session
    @bot.sub_command
    async def game_admin(ctx, new_admin=None):
        new_admin = mention(new_admin)  # Removing this <@>>!<<[id]>
        try:
            bot.check_parameter(new_admin, msgs.MISSING_PARAMETER % ("game admin <ADMIN>", "ADMIN"))
            bot.check_has_joined(ctx.author.mention)
            bot.check_has_joined(new_admin, bot.which_game(ctx.author.mention))
            bot.check_is_admin(ctx.author.mention)
        except Exception as e:
            await ctx.channel.send(e)
            return

        game_name = bot.which_game(ctx.author.mention)
        bot.set_admin(game_name, new_admin)
        await ctx.channel.send(msgs.ADMIN_SUCCESSFULLY_CHANGED % (game_name, new_admin))

    # Quit the game
    @bot.sub_command
    async def game_quit(ctx):
        try:
            bot.check_has_joined(ctx.author.mention)
            bot.check_can_confirm(ctx.author)
        except Exception as e:
            await ctx.channel.send(e)
            return

        game_name = bot.which_game(ctx.author.mention)
        if bot.get_admin(game_name) == ctx.author:
            await ctx.channel.send(msgs.CONFIRM_FOR_GAME_DESTRUCTION % game_name)
            confirm = await bot.confirm(ctx.author, "game quit (admin)")

            if confirm:
                bot.delete_game(game_name)
                await ctx.channel.send(msgs.SUCCESSFULLY_DELETED % game_name)

        else:
            bot.quit_game(ctx.author.mention)
            await ctx.channel.send(msgs.SUCCESSFULLY_QUITED % game_name)

    # Kick a player from your game
    @bot.sub_command
    async def game_kick(ctx, player: str = None):
        player = mention(player)
        try:
            bot.check_parameter(player, msgs.MISSING_PARAMETER % ("!game kick <JOUEUR>", "JOUEUR"))
            bot.check_has_joined(ctx.author.mention)
            bot.check_has_joined(player, bot.which_game(ctx.author.mention))
            bot.check_is_admin(ctx.author.mention)
            if player == ctx.author.mention:
                raise NameError(msgs.CANNOT_KICK_YOURSELF)
        except Exception as e:
            await ctx.channel.send(e)
            return

        game = bot.which_game(player)
        bot.quit_game(player)
        await ctx.channel.send(msgs.SUCCESSFULLY_KICKED % (player, game))

    # Get the list of the available games
    @bot.sub_command
    async def game_list(ctx):
        games = bot.get_opened_games()
        if games:
            await ctx.channel.send(msgs.OPENED_GAMES_LIST % "\n- ".join(games))
        else:
            await ctx.channel.send(msgs.NO_OPENED_GAME)

    # Get the members of a game
    @bot.sub_command
    async def game_members(ctx, game_name=None, *too):
        try:
            bot.check_parameter(game_name, msgs.MISSING_PARAMETER % ("!game members <NOM DE LA PARTIE>", "NOM DE LA PARTIE"))
            bot.check_not_too_much_parameters(too, "!game members <NOM DE LA PARTIE>")
            bot.check_game_exists(game_name)
        except Exception as e:
            await ctx.channel.send(e)
            return

        members = bot.get_game_members(game_name)
        await ctx.channel.send(msgs.GAME_MEMBERS_LIST % (game_name, "\n- ".join(members), len(members)))

    # Start a game
    @bot.sub_command
    async def game_start(ctx, *too):
        try:
            bot.check_not_too_much_parameters(too, "!game start")
            bot.check_has_joined(ctx.author.mention)
            bot.check_can_launch(bot.which_game(ctx.author.mention))
        except Exception as e:
            await ctx.channel.send(e)
            return

        game_name = bot.which_game(ctx.author.mention)
        #category = get(ctx.guild.categories, name='votes')
        #bot.vote_channels[game_name] = await ctx.guild.create_voice_channel(game_name, category=category, reason="Heberge les débats")
        await bot.launch_game(game_name)
        await ctx.channel.send(msgs.GAME_START % "\n- ".join(bot.get_game_members(game_name)))




