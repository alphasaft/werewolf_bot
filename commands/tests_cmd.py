from assets.constants import EXPEDITIONS_CATEGORY
from assets.utils import get_id
from discord.ext.commands import has_permissions
from discord.utils import get


PURGE_EXP_HELP = """Supprime tous les channels EXPEDITIONS"""
ERASE_TEST_HELP = """Supprime les traces du dernier test"""
DISCONNECT_HELP = """Déconnecte le bot"""
ID_HELP = """Renvoie l'id correspondant à la mention"""


def __implement__(bot):
    """Implement some tests commands in the bot. Unable to use those commands if not implemented"""

    @bot.command(name='purgeexpeditions', help=PURGE_EXP_HELP)
    @has_permissions(administrator=True)
    async def purge_expeditions(ctx):
        category = get(ctx.guild.categories, name=EXPEDITIONS_CATEGORY)
        for channel in category.channels:
            await channel.delete()

        await ctx.channel.send("Expeditions voice channels deleted !")

    @bot.command(name='erasetest', help=ERASE_TEST_HELP)
    @has_permissions(administrator=True)
    async def erase_test(ctx):
        async for message in ctx.channel.history(limit=None):
            if (message.author.name.strip()) not in ['Alphasaft', 'Clyde the Storyteller']:
                break
            else:
                await message.delete()

    @bot.command(name='disconnect', help=DISCONNECT_HELP)
    @has_permissions(administrator=True)
    async def disconnect(ctx):
        await ctx.channel.send("Disconnecting...")
        exit(0)

    @bot.command(name='id', help=ID_HELP)
    @has_permissions(administrator=True)
    async def _id(ctx, mention):
        await ctx.channel.send(get_id(mention))
