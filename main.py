# -*- coding: utf-8 -*-
import discord
import discord.ext.tasks as tasks
import traceback

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

bot = GameMaster(command_prefix=consts.PREFIX, description=consts.DESCRIPTION, case_insensitive=True)


commands.game_cmd.__implement__(bot)
commands.calendar_cmd.__implement__(bot)
commands.clear_cmd.__implement__(bot)
commands.kick_cmd.__implement__(bot)
commands.embed_cmd.__implement__(bot)
commands.tests_cmd.__implement__(bot)
commands.level_cmd.__implement__(bot)


# Implementing events
@bot.event
async def on_ready():
    logger.info("Ready as %s with id %s" % (bot.user.name, bot.user.id))
    try:
        bot.load(consts.EVENTS_PATH, consts.XP_COUNTS_PATH)
        logger.info("Loaded %i event(s) and %s user(s) xp account(s)" % (len(bot.events), len(bot.xp_counts)))
    except (SyntaxError, FileNotFoundError):
        logger.warn("Data loading failed")


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
            except BaseException:
                msg = bot.devtool.transform_msg(msg)
                logger.debug("Message author was truncated for %s" % msg.author.name)
            else:
                return

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


@tasks.loop(minutes=1.0)
async def bot_updating():
    if not bot.is_ready():
        return

    try:
        # await bot.activate_events()
        top_xps = sorted({xp for _id, xp in bot.xp_counts.items() if bot.get_level_info(_id)['level'] >= 3})[-5:]
        guild = bot.get_guild(consts.GUILD)
        roles = guild.roles
        role = discord.utils.get(roles, name=consts.TOP_PLAYER_ROLE)
        for _id, xp in bot.xp_counts.items():
            member = discord.utils.get(guild.members, id=_id)
            if xp in top_xps:
                await member.add_roles(role)
            elif role in member.roles:
                await member.remove_roles(role)

    except BaseException as e:
        logger.error("%s %s : %s" % ("".join(traceback.format_tb(e.__traceback__)), e.__class__.__name__, str(e)))
        bot_updating.close()


if __name__ == '__main__':
    try:
        logger.info("Process started")

        # Launch the bot
        bot_updating.start()
        bot.run(token.TOKEN)
    except BaseException as e:
        logger.critical("Killed by %s : %s" % (e.__class__.__name__, e))
    finally:
        bot.dialogs.save(consts.DIALOGS_PATH)
        bot.dump(consts.EVENTS_PATH, consts.XP_COUNTS_PATH)

        logger.info("Process ended")
