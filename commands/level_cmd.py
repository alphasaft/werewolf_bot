from discord.ext.commands import has_permissions
from discord.utils import get
from assets import messages as msgs
from assets.utils import get_id
from bot.game_master import GameMaster


HELP = """Affiche votre expérience et votre niveau"""


def __implement__(bot: GameMaster):
    """Implement the command 'level' in the bot. Unable to use that command if not implemented"""

    @bot.command(name='level', help=HELP)
    async def display_level(ctx):
        if not bot.xp_counts.get(ctx.author.id):
            bot.create_xp_account(ctx.author.id)

        level_info = bot.get_level_info(ctx.author.id)

        level = level_info['level']
        level_name = level_info['level_name']
        xp = level_info['xp']
        total_xp = level_info['total_xp']
        needed_xp = level_info['needed_xp']
        xp_bar = level_info['xp_bar']

        await ctx.channel.send(embed=msgs.GET_LEVEL.build(
            level=level,
            level_name=level_name,
            gained_xp=xp,
            total_xp=total_xp,
            needed_xp=needed_xp,
            xp_bar=xp_bar
        ))
