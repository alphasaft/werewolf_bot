from assets.constants import EXPEDITIONS_CATEGORY, GUILD
from discord.ext.commands import has_permissions
from discord.utils import get


HELP = """Supprime tous les channels vocaux des expeditions du serveur."""


def __implement__(bot):
    """Implement the command 'purgevote' in the bot. Unable to use that command if not implemented"""

    @bot.command(name='purgeexpeditions', help=HELP)
    @has_permissions(manage_server=True)
    async def purge_expeditions(ctx):
        category = get(ctx.guild.categories, name=EXPEDITIONS_CATEGORY)
        for channel in category.channels:
            await channel.delete()

        await ctx.channel.send("Expeditions voice channels deleted !")
