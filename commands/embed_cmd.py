import discord
import discord.ext.commands

from assets.utils import indented, make_embed


def __implement__(bot):
    """Implement the command 'embed' in the bot. Unable to use that command if not implemented"""

    @bot.command(name='embed', help="Crée un nouvel Embed")
    @discord.ext.commands.has_permissions(manage_messages=True)
    async def create_embed(ctx, *options):

        _AVAILABLE_OPTIONS = {'title', 'content', 'color'}

        if options == ():
            options = _AVAILABLE_OPTIONS

        # Command processing
        invalid = set(options) - set(_AVAILABLE_OPTIONS)
        if invalid:
            await ctx.channel.send("Invalid option(s) %s" % ", ".join(options))
            return

        values = {}
        for option in options:
            await ctx.channel.send(indented(option.title() + ' ?'))
            values[option] = (await bot.wait_for('message', check=lambda m: m.author == ctx.author)).content

        await ctx.channel.purge(limit=len(options)*2+1)
        await ctx.channel.send(embed=make_embed(**values))
