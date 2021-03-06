from discord.utils import get

from bot.game_master import GameMaster
from assets.utils import get_id, make_mention
from assets.constants import EXPEDITIONS_CATEGORY
import assets.messages as msgs
import assets.logger as logger


BRIEF = """Crée, supprime et gère vos parties."""

FULL = """
Crée, supprime et gère vos parties.

game new nomDeLaPartie -> crée une partie ; vous êtes son admin
game join unePartie -> Rejoint cette partie
game quit -> Quitte la partie, ou la détruit si vous êtes son admin
game list -> Affiche la liste des parties joignables
game members unePartie -> Affiche les membres de cette partie

Ces commandes nécessitent d'être l'admin de votre partie.
[admin] game admin unJoueur -> Change l'admin de votre partie pour ce joueur
[admin] game kick unJoueur -> Kick ce joueur de votre partie
"""


def __implement__(bot: GameMaster):
    """Implement the command 'game' in the bot. Unable to use that command if not implemented"""
    
    @bot.group(brief=BRIEF, help=FULL)
    async def game(ctx):
        if not ctx.invoked_subcommand:
            await ctx.channel.send("Sub-commande invalide %s" % ctx.message.content.strip().split()[1])

    # Create a new game session
    @game.command()
    async def new(ctx, game_name=None, *too):
        try:
            bot.check_parameter(game_name, "game new nomDeLaPartie", "nomDeLaPartie")
            bot.check_name_is_available(game_name)
            bot.check_is_alone(ctx.author.id)
            bot.check_not_too_much_parameters(too, "game new nomDeLaPartie")
        except Exception as e:
            await ctx.channel.send(e)
            return

        bot.add_game(game_name, ctx.author, home_channel=ctx.channel)
        logger.debug("%s created a game named %s" % (ctx.author.name, game_name))
        await ctx.channel.send(msgs.SUCCESSFULLY_CREATED % (game_name, game_name))

    # Join a game session
    @game.command()
    async def join(ctx, game_name=None):
        try:
            bot.check_parameter(game_name, "game join unePartie", "unePartie")
            bot.check_game_exists(game_name)
            bot.check_is_alone(ctx.author.id)
            bot.check_game_is_available(game_name)
        except Exception as e:
            await ctx.channel.send(e)
            return

        await bot.join_game(game_name, ctx.author)

        logger.debug("%s joined the game named %s " % (ctx.author.name, game_name))
        await ctx.channel.send(msgs.SUCCESSFULLY_JOINED % game_name)

    # Change the admin of a game session
    @game.command()
    async def admin(ctx, new_admin=None):
        new_admin = get_id(new_admin)
        try:
            bot.check_parameter(new_admin, "game admin unJoueur", "unJoueur")
            bot.check_has_joined_game(ctx.author.id)
            bot.check_has_joined_game(new_admin, bot.which_game(ctx.author.id))
            bot.check_is_game_admin(ctx.author.id)
        except Exception as e:
            await ctx.channel.send(e)
            return

        game_name = bot.which_game(ctx.author.id)
        bot.set_admin(game_name, new_admin)
        await ctx.channel.send(msgs.ADMIN_SUCCESSFULLY_CHANGED % (game_name, make_mention(new_admin)))

    # Quit the game
    @game.command(name='quit')
    async def _quit(ctx):
        try:
            bot.check_has_joined_game(ctx.author.id)
            bot.check_can_confirm(ctx.author)
            assert not bot.is_active(bot.which_game(ctx.author.id)), msgs.CANNOT_QUIT_IN_GAME
        except Exception as e:
            await ctx.channel.send(e)
            return

        game_name = bot.which_game(ctx.author.id)

        if bot.get_admin(game_name) == ctx.author:
            await ctx.channel.send(msgs.CONFIRM_FOR_GAME_DESTRUCTION % game_name)
            confirm = await bot.confirm(ctx.author, "game quit (admin)")

            if confirm is None:
                return

            elif confirm:
                bot.delete_game(game_name)
                logger.debug("Game %s was deleted by its owner %s" % (game_name, ctx.author.name))
                await ctx.channel.send(msgs.GAME_SUCCESSFULLY_DELETED % game_name)

        else:
            bot.quit_game(ctx.author.id)
            logger.debug("%s quited the game %s" % (ctx.author.name, bot.which_game(ctx.author.id)))
            await ctx.channel.send(msgs.GAME_SUCCESSFULLY_QUITED % game_name)

    # Kick a player from your game
    @game.command()
    async def kick(ctx, player: str = None):
        player = get_id(player)
        try:
            bot.check_parameter(player, "!game kick unJoueur", "unJoueur")
            bot.check_has_joined_game(ctx.author.id)
            bot.check_has_joined_game(player, bot.which_game(ctx.author.id))
            bot.check_is_game_admin(ctx.author.id)
            if player == ctx.author.id:
                raise NameError(msgs.CANNOT_KICK_YOURSELF)
        except Exception as e:
            await ctx.channel.send(e)
            return

        _game = bot.which_game(player)
        bot.quit_game(player)
        logger.debug("%s was kicked of the game %s" % (ctx.author.name, bot.which_game(ctx.author.id)))
        await ctx.channel.send(msgs.SUCCESSFULLY_KICKED_FROM_GAME % (make_mention(player), _game))

    # Get the list of the available games
    @game.command(name='list')
    async def _list(ctx):
        games = bot.get_opened_games()
        if games:
            await ctx.channel.send(embed=msgs.OPENED_GAMES_LIST.build(games="\n- ".join(games)))
        else:
            await ctx.channel.send(embed=msgs.NO_OPENED_GAME.build())
            
        logger.debug("Error")

    # Get the members of a game
    @game.command(name='members')
    async def _members(ctx, game_name=None, *too):
        try:
            bot.check_parameter(game_name, "!game members unePartie", "unePartie")
            bot.check_not_too_much_parameters(too, "!game members unePartie")
            bot.check_game_exists(game_name)
        except Exception as e:
            await ctx.channel.send(e)
            return

        members = [member.mention for member in bot.get_game_members(game_name)]
        await ctx.channel.send(embed=msgs.GAME_MEMBERS_LIST.build(
            members="\n- ".join(members),
            name=game_name,
            how_much=len(members)
        ))

    # Start a game
    @game.command()
    async def start(ctx, *too):
        try:
            bot.check_not_too_much_parameters(too, "!game start")
            bot.check_has_joined_game(ctx.author.id)
            bot.check_is_game_admin(ctx.author.id)
            bot.check_can_launch(bot.which_game(ctx.author.id))
        except Exception as e:
            await ctx.channel.send(e)
            return

        async with ctx.channel.typing():
            game_name = bot.which_game(ctx.author.id)
            category = get(ctx.guild.categories, name=EXPEDITIONS_CATEGORY)
            bot.voice_channels[game_name] = await ctx.guild.create_voice_channel(
                game_name,
                category=category,
                reason="Heberge les débats"
            )
            members = [member.mention for member in bot.get_game_members(game_name)]
            await bot.launch_game(game_name)
            logger.debug("Game %s was started by its owner %s" % (game_name, ctx.author.name))
            await ctx.channel.send(embed=msgs.GAME_START.build(members="\n- ".join(members)))




