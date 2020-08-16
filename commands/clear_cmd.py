from discord.ext.commands import has_permissions


BRIEF = """Supprime les n derniers messages."""

FULL = """
Supprime les n derniers messages, ou tous si n n'est pas donné, ou s'il est égal à "full"
Seul les administrateurs du serveur peuvent utiliser cette commande
"""


def __implement__(bot):
    """Implement the command 'clear' in the bot. Unable to use that command if not implemented"""

    @bot.command(name='clear', brief=BRIEF, help=FULL, category="administrator")
    @has_permissions(manage_messages=True)
    async def clear(ctx, n=None):
        if n == 'full' or n is None:
            n = len(await ctx.channel.history(limit=None).flatten())

        await ctx.channel.purge(limit=int(n)+1)
