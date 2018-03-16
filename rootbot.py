import discord, logging, json
from discord.ext import commands
from profanity import profanity
from tinydb import TinyDB, Query
from tinydb.operations import delete,increment
# Requirements: discord.py, tinydb, profanity

# Define all variables to be used around the script
description = '''Test Bot'''
bot = commands.Bot(command_prefix='r!', description=description)
db = TinyDB('data.json')
Users = Query()

# Print the starting text
print('---------------')
print('Test Bot')
print('---------------')
print('Starting Bot...')

# Setup basic logging for the bot
logging.basicConfig(level=logging.WARNING)

@bot.event
async def on_ready():
    print('Ready Boss')

@bot.listen()
async def on_message_edit(before, after):
	message = after
	if profanity.contains_profanity(message.content):
		await bot.delete_message(message)
		if db.contains(Users.id == message.author.id):
			if db.contains((Users.id == message.author.id) & (Users.swears == 2)):
				await bot.kick(message.author)
				db.update({'swears': 0}, Users.id == message.author.id)
			else:
				db.update(increment('swears'), Users.id == message.author.id)
		else:
			db.insert({'id': message.author.id, 'swears': 0})
		await bot.send_message(message.author,"Don't curse, bitch. You have 2 more chances.")

@bot.listen()
async def on_message(message):
	if profanity.contains_profanity(message.content):
		await bot.delete_message(message)
		if db.contains(Users.id == message.author.id):
			if db.contains((Users.id == message.author.id) & (Users.swears == 2)):
				await bot.kick(message.author)
				db.update({'swears': 0}, Users.id == message.author.id)
			else:
				db.update(increment('swears'), Users.id == message.author.id)
		else:
			db.insert({'id': message.author.id, 'swears': 0})
		await bot.send_message(message.author,"You have recived a strike if you recive three strikes you will be kicked")

@bot.listen()
async def on_member_join(member):
	is_verified = False
	for role in member.roles:
		if role.name == "Verified":
			is_verified = True
			break
	if is_verified == False:
		await bot.send_message(member,"Message the bot with the command | Verify for normal permissions")

@bot.command(pass_context=True, hidden=True)
async def strike(context):
	usr = context.message.mentions[0]
	if db.contains(Users.id ==usr.id):
			if db.contains((Users.id == usr.id) & (Users.swears == 2)):
				await bot.kick(usr)
				db.update({'swears': 0}, Users.id ==usr.id)
			else:
				db.update(increment('swears'), Users.id == usr.id)
	else:
		db.insert({'id': usr.id, 'swears': 0})
	await bot.send_message(usr,"You have recived a strike if you recive three strikes you will be kicked")

@bot.command(pass_context=True)
async def purge(context, number : int):
	"""Clear a specified number of messages in the chat"""
	deleted = await bot.purge_from(context.message.channel, limit=number)
	await bot.send_message(context.message.channel, 'Deleted {} message(s)'.format(len(deleted)))

@bot.command(pass_context=True,hidden=True)
async def punish(context, number : int, text : str):
	"""Ooooh you're badddd"""
	for role in context.message.author.roles:
		if role.name == "Founder":
			for i in range(number):
				await bot.send_message(context.message.mentions[0],text)
			break

@bot.command(pass_context=True)
async def verify(context):
	"""Basic command to give user basic permissions"""
	for server in bot.servers:
		roles = server.roles
		members = server.members
		member = None
		for mem in members:
			if mem.id == context.message.author.id:
				member = mem
				break
		for role in roles:
			if role.name == "Verified":
				await bot.add_roles(member, role)
				break

@bot.command(pass_context=True)
async def roles(context):
	"""Displays all of the roles with their ids"""
	roles = context.message.server.roles
	result = "The roles are "
	for role in roles:
		result += role.name + ": " + role.id + ", "
	await bot.say(result)

@bot.command(pass_context=True)
async def invite(context):
	"""Generates a invite code to the server for the user to share"""
	invite = await bot.create_invite(context.message.server,max_uses=1,xkcd=True)
	await bot.send_message(context.message.author,"Your invite URL is ()".format(invite.url))

@bot.command()
async def ping(ctx):
    return await ctx.send('Pong! {0}'.format(round(bot.latency, 1))
