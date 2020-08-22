import discord
import assets.messages as msgs
import assets.logger as logger


class _DiscordFormatter:
    """Class that implement class methods, useful to use discord markdown"""

    @classmethod
    def bold(cls, msg):
        lines = msg.splitlines()
        done = ""
        for line in lines:
            if line:
                done += '**'+line.strip()+'**' + '\n'
        return done[:-1]

    @classmethod
    def italic(cls, msg):
        lines = msg.splitlines()
        done = ""
        for line in lines:
            done += '*'+line.strip()+'*' + '\n'
        return done[:-1]

    @classmethod
    def block(cls, msg):
        return "```%s```" % msg

    @classmethod
    def indented(cls, msg):
        lines = msg.splitlines()
        done = ""
        for line in lines:
            done += '> '+line.strip()+'\n'
        return done[:-1]

    @classmethod
    def underlined(cls, msg):
        return "__%s__" % msg

    @classmethod
    def suppress_markdown(cls, msg):
        if msg.startswith('> '):
            msg = msg[2:]

        return suppress(
            msg,
            "__",
            "\n> ",
            "```",
            "*",
        )

    @classmethod
    def make_embed(cls, **kwargs):
        """Returns a discord.Embed object out of the kwargs"""

        _NOTHING = discord.Embed.Empty
        _AVAILABLE_OPTIONS = {"title", "content", "color", "footer"}

        invalid = set(kwargs) - _AVAILABLE_OPTIONS
        if invalid:
            raise ValueError("Invalid option(s) for an Embed : %s" % ", ".join(invalid))

        payload = {
            "title": kwargs.pop("title", _NOTHING),
            "description": kwargs.pop("content", _NOTHING),
        }

        if kwargs.get('color'):
            if isinstance(kwargs['color'], str):
                payload['color'] = getattr(discord.colour.Color, kwargs['color'])()
            elif isinstance(kwargs['color'], tuple) and len(kwargs['color']) == 3:
                payload['color'] = discord.colour.Color.from_rgb(*kwargs['color'])
            else:
                raise ValueError('Invalid colour format for Embed')
        else:
            payload['color'] = _NOTHING

        embed = discord.Embed(**payload)

        if kwargs.get('footer'):
            embed.set_footer(text=kwargs['footer'])

        return embed


# Exporting
bold = _DiscordFormatter.bold
italic = _DiscordFormatter.italic
block = _DiscordFormatter.block
indented = _DiscordFormatter.indented
underlined = _DiscordFormatter.underlined
suppress_markdown = _DiscordFormatter.suppress_markdown
make_embed = _DiscordFormatter.make_embed


def assure_assertions():
    """Checks that __debug__ isn't False, because else the assertions won't work."""
    if not __debug__:
        raise EnvironmentError("This couldn't be run with option -O, because assertions are needed.")


def configure_logger(_logger, level=None, fmt=None, file=None, filemode=None, tee=True):
    """
    Prepare the logger config. _LOGGER can either be a logger.Logger object, or the logger.py file itself.
    Default configuration is

    LEVEL: logger.Level.INFO,
    FMT : logger.DATED_FMT,
    FILE: ".log",
    FILEMODE: "a",
    TEE: True
    """

    try:
        _logger.set_level(level or logger.Level.INFO)
    except NameError:
        pass

    _logger.set_format(fmt or logger.DATED_FMT)
    _logger.set_output(file=file or '.log', filemode=filemode or 'a')

    if tee:
        _logger.enable_tee()
    else:
        _logger.disable_tee()



def on_channel(channel_name: str, contains: bool = False, warn: bool = False):
    """Decorator. Call the decorated command only if it was invoked on channel CHANNEL_NAME"""
    def decorator(f):
        async def wrapper(ctx, *args, **kwargs):
            if not isinstance(ctx.channel, discord.DMChannel) and \
                    (ctx.channel.name == channel_name or (contains and channel_name in ctx.channel.name)):
                return await f(ctx, *args, **kwargs)
            elif warn:
                await ctx.channel.send("Cette commande ne peut être invoquée que sur le salon #%s" % channel_name)
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator


def replaces(string, *replacements):
    """Does multiple replacements on string, and return it"""
    if len(replacements) % 2 != 0:
        raise ValueError("Uneven replacements")

    i = 0
    while i < len(replacements):
        string = string.replace(replacements[i], replacements[i+1])
        i += 2
    return string


def suppress(string, *substrings):
    """Suppress substrings from string."""
    for substring in substrings:
        string = string.replace(substring, "")
    return string


def unpack(args, expected_syntax):
    expected_syntax = expected_syntax.split(' ')
    if len(args) < len(expected_syntax)-1:
        raise SyntaxError(msgs.MISSING_PARAMETER % " ".join(expected_syntax), expected_syntax[len(args)+1][1:-1])

    elif len(args) > len(expected_syntax)-1:
        raise SyntaxError(
            msgs.TOO_MUCH_PARAMETERS % " ".join(expected_syntax), ", ".join(args[len(expected_syntax)-1:])
        )
    return args if len(args) > 1 else args[0]


def get_id(m: str):
    """Get an user id from his mention"""
    return int(m.replace('!', '')[2:-1]) if isinstance(m, str) else m


def make_mention(u_id: int):
    """Make a discord mention with an user id"""
    return "<@"+str(u_id)+">"
