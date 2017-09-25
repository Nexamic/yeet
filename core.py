from discord.ext import commands
from collections import Counter
from datetime import datetime
import traceback
import aiohttp
import discord
import asyncio
import logging
import praw
import json
import sys

load = [	
	'ext.admin','ext.fixtures','ext.fun','ext.google','ext.images','ext.info',
	'ext.meta','ext.mod','ext.mtb','ext.nufc','ext.permissions','ext.quotes',
	'ext.radio','ext.reactions','ext.scores', 'ext.sidebar',
	'ext.teams','ext.twitter','ext.transfers',	'ext.wiki',
	'ext.tables'
]
					
# Enable Logging
log = logging.getLogger('discord')
log.setLevel(logging.INFO)
handler = logging.FileHandler(filename='Rewrite.log',
							  encoding='utf-8', mode='w')
log.addHandler(handler)

prefix = ['$','!','`','.','-','?']
description = "Football lookup bot by Painezor#8489"
help_attrs = dict(hidden=True)
bot = commands.Bot(command_prefix=prefix, description=description,
				   pm_help=None, help_attrs=help_attrs)

# Errors and invalid commands outputs
@bot.event
async def on_command_error(ctx, error):
	if isinstance(error, commands.NoPrivateMessage):
		await ctx.author.send('Command cannot be used in private messages.')
	elif isinstance(error, commands.DisabledCommand):
		await ctx.send('Sorry. This command is disabled and cannot be used.')
	elif isinstance(error, commands.CommandInvokeError):
		print('In {0.command.qualified_name}:'.format(ctx), file=sys.stderr)
		traceback.print_tb(error.original.__traceback__)
		print('{0.__class__.__name__}: {0}'.format(error.original),
			  file=sys.stderr)

# On Client Ready
@bot.event
async def on_ready():
	print(f'{bot.user.name}: {datetime.now()}\n---------------------')
	if not hasattr(bot, 'uptime'):
		bot.uptime = datetime.utcnow()
	# bot.reddit = praw.Reddit(**bot.credentials["Reddit"])
	bot.reddit = praw.Reddit(**bot.credentials["Reddit"])
	bot.session = aiohttp.ClientSession(loop=bot.loop)
	for c in load:
		try:
			bot.load_extension(c)
		except Exception as e:
			print(f'Failed to load cog {c}\n{type(e).__name__}: {e}')
	await asyncio.sleep(5)
	await bot.change_presence(game=discord.Game(name="Use !help",type=0))

# Define command handler
@bot.event
async def on_command(ctx):
	bot.commands_used[ctx.command.name] += 1
	destination = None 
	if isinstance(ctx.channel,discord.abc.PrivateChannel):
		destination = 'Private Message'
	else:
		destination = f'#{ctx.channel.name} ({ctx.guild.name})'
	log.info(f'{ctx.message.created_at}: {ctx.author.name} in'
			  '{destination}: {ctx.message.content}')

# Load bot and logging.
if __name__ == '__main__':
	with open('credentials.json') as f:
		bot.credentials = json.load(f)
	bot.clientid = bot.credentials['bot']['client_id']
	bot.commands_used = Counter()
	with open('ignored.json') as f:
		bot.ignored = json.load(f)
	with open('leagues.json') as f:
		bot.leagues = json.load(f)
	with open('config.json') as f:
		bot.config = json.load(f)
	with open('compsnew.json') as f:
		bot.comps = json.load(f)
	bot.configlock = asyncio.Lock()
	bot.run(bot.credentials['bot']['token'])
	
	# Cleanup.
	bot.twitask.cancel()
	bot.scorechecker.cancel()
	bot.ticker.cancel()
	bot.session.close() #Aiohttp ClientSession
	handlers = log.handlers[:]
	for hdlr in handlers:
		hdlr.close()
		log.removeHandler(hdlr)