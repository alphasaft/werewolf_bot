# -*- coding: utf-8 -*-

from bot.game_master import GameMaster
from discord.utils import get
import discord
import commands
import assets
import assets.messages as msgs
import assets.constants as consts

DESCRIPTION = '''I'm the game master of this Werewolf server ; type !help and I will explain you.'''


bot = GameMaster(command_prefix=consts.PREFIX, description=DESCRIPTION, case_insensitive=True)

commands.game_cmd.__implement__(bot)
commands.clear_cmd.__implement__(bot)
commands.kick_cmd.__implement__(bot)


@bot.event
async def on_ready():
    print(bot.user.name, 'is ready !')
    print('Id :', bot.user.id)
    print('------')


@bot.event
async def on_message(msg):
    await msg.channel.send('_'+msg.content+'_')
    if type(msg.channel) is discord.DMChannel:
        await bot.react(msg)
    else:
        await bot.process_commands(msg)


@bot.event
async def on_member_join(member):
    channel = bot.get_channel(726114430093623308)
    roles = bot.get_guild(724226339443572770).roles
    await channel.send(msgs.WELCOME % member.mention)
    await member.add_roles(get(roles, name='Manant'), reason="Role de base du village")


@bot.event
async def on_disconnect():
    print('Disconnected')


# Launch the bot
bot.run(assets.token.TOKEN)
