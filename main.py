# -*- coding: utf-8 -*-


import discord
from discord.utils import get
import asyncio

from bot import GameMaster
from assets.utils import assure_assertions
import assets.token as token
import assets.messages as msgs
import assets.constants as consts
import commands

# Checking that assertion will work.
assure_assertions()

bot = GameMaster(command_prefix=consts.PREFIX, description=consts.DESCRIPTION, case_insensitive=True)
commands.game_cmd.__implement__(bot)
commands.clear_cmd.__implement__(bot)
commands.kick_cmd.__implement__(bot)
commands.embed_cmd.__implement__(bot)
commands.tests_cmd.__implement__(bot)


@bot.event
async def on_ready():
    print(bot.user.name, 'is ready !')
    print('Id :', bot.user.id)
    print('------')


@bot.event
async def on_message(msg):
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
        await bot.react(msg)
    else:
        await bot.process_commands(msg)


@bot.event
async def on_member_join(member):
    channel = bot.get_channel(consts.WELCOME_CHANNEL)
    await channel.send(msgs.WELCOME % member.mention)
    if consts.BASE_ROLE:
        roles = bot.get_guild(consts.GUILD).roles
        await member.add_roles(discord.utils.get(roles, name=consts.BASE_ROLE), reason="Role de base du village")


@bot.event
async def on_disconnect():
    print('Disconnected')


if __name__ == '__main__':
    try:
        # Launch the bot
        bot.run(token.TOKEN)
    finally:
        # Recording the dialogs
        bot.dialogs.save(consts.DIALOGS_PATH)
