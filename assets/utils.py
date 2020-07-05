import discord
import assets.messages as msgs


def mention(m: str):
    """Get an valid mention by removing the additional '!'"""
    return m.replace('!', '') if isinstance(m, str) else m


def on_channel(channel_name: str, contains: bool = False, warn: bool = False):
    """Decorator. Call the decorated command only if it was invoked on channel CHANNEL_NAME"""
    def decorator(f):
        async def wrapper(ctx, *args, **kwargs):
            if not isinstance(ctx.channel, discord.DMChannel) and \
                    (ctx.channel.name == channel_name or (contains and channel_name in ctx.channel.name)):
                return await f(ctx, *args, **kwargs)
            elif warn:
                await ctx.channel.send("Cette commande ne peut être invoquée que sur le salon #%s" % channel_name)
        return wrapper
    return decorator


def signed_message(msg):
    return msg.author.mention + ' : ' + msg.content


def unpack(args, expected_syntax):
    expected_syntax = expected_syntax.split(' ')
    if len(args) < len(expected_syntax)-1:
        raise SyntaxError(msgs.MISSING_PARAMETER % (" ".join(expected_syntax), expected_syntax[len(args)+1][1:-1]))
    elif len(args) > len(expected_syntax)-1:
        raise SyntaxError(msgs.TOO_MUCH_PARAMETERS % (" ".join(expected_syntax), ", ".join(args[len(expected_syntax)-1:])))
    return args if len(args) > 1 else args[0]


def infos_format(message, **infos):
    for name, info in infos.items():
        if '<'+name+'>' not in message:
            raise NameError("Incorrect info name %s : cannot format the message" % name)
        message = message.replace('<'+name+'>', info)
    return message
