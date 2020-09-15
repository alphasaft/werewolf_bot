import discord
from collections import OrderedDict
from assets import messages as msgs
from bot.game_master import GameMaster
from assets.utils import make_mention


LEVEL_HELP = """Affiche votre expérience et votre niveau"""
RANK_HELP = "Affiche votre place parmi les autres membres du serveur"


def __implement__(bot: GameMaster):
    """Implement some levels and ranking commands in the bot. Unable to use these command if not implemented"""

    @bot.command(name='level', help=LEVEL_HELP)
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

    @bot.command(name='rank', help=RANK_HELP)
    async def get_rank(ctx):
        if not bot.xp_counts.get(ctx.author.id):
            bot.create_xp_account(ctx.author.id)

        xps = OrderedDict(sorted(bot.xp_counts.items(), key=lambda t: t[1]))
        around = ()
        _FORMAT = "%i - %s, %s xp"

        if len(xps) > 10:
            top = [(k, v) for k, v in xps[-3:].items()]
            for i, _id in enumerate(xps.keys()):
                if _id == ctx.author.id:
                    if i < 3:
                        around = [(k, v) for k, v in xps[-3:].items()]
                    else:
                        around = [(k, v) for k, v in xps[i-1:i+2].items()]
                    break

            ranks = [
                _FORMAT % (1, make_mention(top[0][0]), top[0][1]),
                _FORMAT % (2, make_mention(top[1][0]), top[1][1]),
                _FORMAT % (3, make_mention(top[2][0]), top[2][1]),
            ] + ['...'] + [
                _FORMAT % (i, make_mention(around[0][0]), around[0][1]),
                _FORMAT % (i+1, make_mention(around[1][0]), around[1][1]),
                _FORMAT % (i+2, make_mention(around[2][0]), around[2][1]),
            ]

        else:
            ranks = [
                _FORMAT % (i+1, make_mention(info[0]), info[1]) for i, info in enumerate(reversed(xps.items()))
            ]

        await ctx.channel.send(embed=msgs.GET_RANKS.build(ranks="\n".join(ranks)))


