# -*- coding: utf-8 -*-
import asyncio
import discord

from bot import GameMaster
from assets.utils import assure_assertions, configure_logger
import assets.logger as logger
import assets.token as token
import assets.messages as msgs
import assets.constants as consts
import commands

# Checking that assertion will work.
assure_assertions()

# Preparation for the logger
configure_logger(logger)

# Implementing commands
kwargs = {'command_prefix': consts.PREFIX, 'description': consts.DESCRIPTION, 'case_insensitive': True}
try:
    bot = GameMaster.from_binary_file(consts.BOT_STATE_PATH, **kwargs)
except (FileNotFoundError, ValueError, EOFError):
    bot = GameMaster(**kwargs)


commands.game_cmd.__implement__(bot)
commands.calendar_cmd.__implement__(bot)
commands.clear_cmd.__implement__(bot)
commands.kick_cmd.__implement__(bot)
commands.embed_cmd.__implement__(bot)
commands.tests_cmd.__implement__(bot)


# Implementing events
@bot.event
async def on_ready():
    logger.info("Ready as %s with id %s" % (bot.user.name, bot.user.id))
    while True:
        try:
            await asyncio.sleep(1*60)
            await bot.activate_events()
        except Exception as e:
            logger.error("%s : %s" % (e.__class__.__name__, e))
            if isinstance(e, (asyncio.CancelledError, KeyboardInterrupt)):
                exit(137)


@bot.event
async def on_connect():
    logger.info("(Re)connected")


@bot.event
async def on_disconnect():
    logger.warn("Disconnected")


@bot.event
async def on_message(msg):
    if not msg.author.bot:
        logger.debug("'%s' was sended by %s" % (msg.content, msg.author.display_name))

    if msg.author == bot.user:
        return  # We don't want the bot to reply to itself !

    if type(msg.channel) is discord.DMChannel:
        if bot.devmode:
            try:
                await bot.devtool.process_commands(msg)
            except Exception:
                pass
            else:
                return

            msg = bot.devtool.transform_msg(msg)
            logger.debug("Message author was truncated for %s" % msg.author.name)

        logger.debug("Reacting to the message...")
        await bot.react(msg)
    elif msg.content.strip().startswith(consts.PREFIX):
        logger.debug("Processing the message as a command...")
        await bot.process_commands(msg)


@bot.event
async def on_member_join(member):
    channel = bot.get_channel(consts.WELCOME_CHANNEL)
    await channel.send(msgs.WELCOME % member.mention)
    if consts.BASE_ROLE:
        roles = bot.get_guild(consts.GUILD).roles
        await member.add_roles(discord.utils.get(roles, name=consts.BASE_ROLE), reason="Role de base du village")


def finish_process(n):
    """Ends the process with exit code N"""
    # Recording the project state
    bot.dialogs.save(consts.DIALOGS_PATH)
    bot.dump(consts.BOT_STATE_PATH)

    logger.info("Process ended")
    exit(n)


if __name__ == '__main__':
    try:
        logger.info("Process started")

        # Launch the bot
        bot.run(token.TOKEN)
    except BaseException as e:
        logger.critical("Killed by %s : %s" % (e.__class__.__name__, e))
        finish_process(1)
    else:
        finish_process(0)
