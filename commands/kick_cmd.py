from discord.ext.commands import has_permissions
from discord.utils import get
from assets import messages as msgs
from assets.utils import get_id
from bot.game_master import GameMaster


BRIEF = """Kick un joueur du serveur."""

FULL = """
Kick un joueur du serveur.
Seul les administrateurs du serveur peuvent utiliser cette commande
"""


def __implement__(bot: GameMaster):
    """Implement the command 'kick' in the bot. Unable to use that command if not implemented"""

    @bot.command(name='kick', brief=BRIEF, help=FULL)
    @has_permissions(administrator=True)
    async def kick(ctx, player_mention=None, *reason):
        try:
            bot.check_parameter(player_mention, '!kick unJoueur', 'unJoueur')
            player = get(ctx.guild.members, id=get_id(player_mention))
            if not player:
                raise NameError(msgs.MISSING_USER % player_mention)
        except Exception as e:
            await ctx.channel.send(e)
            return

        await ctx.guild.kick(player, reason=" ".join(reason))
