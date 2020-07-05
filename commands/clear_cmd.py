from assets import messages as msgs
from discord.ext.commands import has_permissions
from discord.utils import get


BRIEF = """Supprime les n derniers messages."""

FULL = """
Supprime les n derniers messages.
Seul les administrateurs du serveur peuvent utiliser cette commande
Utiliser !clear full revient à supprimer tous les messages du channel sauf ceux de bienvenue.
"""


def __implement__(bot):
    """Implement the command 'clear' in the bot. Unable to use that command if not implemented"""

    @bot.command(name='clear', brief=BRIEF, help=FULL, category="administrator")
    @has_permissions(manage_messages=True)
    async def clear(ctx, n=None):
        history_length = len(await ctx.channel.history().flatten())
        if n == 'full' or n is None:
            n = history_length

        await ctx.channel.purge(limit=int(n)+1)
