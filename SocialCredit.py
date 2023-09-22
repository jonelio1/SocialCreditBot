import os
import discord
from discord.ext import commands, tasks
import json

TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents().all()
bot = commands.Bot(command_prefix='!', intents=intents)

PositiveEmote = 'positivesocialcredit'
NegativeEmote = 'negativesocialcredit'

CreditStore = {}

try:
    with open('/data/creditstore.json', 'r') as f:
        CreditStore = json.load(f)
except:
    print("No cache found")


class User:
    def __init__(self, ID, Name):
        self.ID = ID
        self.Name = Name


def CheckUserExists(user):
    if user.ID in CreditStore:
        UserUpdate(user)
        return True
    else:
        return False


def InitUser(user):
    CreditStore[user.ID] = [user.Name, 0]
    print(f'Initialised user {user.Name} with ID {user.ID}')


def UserUpdate(user):
    z = CreditStore[user.ID]
    if z[0] != user.Name:
        z[0] = user.Name


def AddCredit(user):
    x = CreditStore[user.ID]
    x[1] += 1


def RemoveCredit(user):
    x = CreditStore[user.ID]
    x[1] -= 1


@bot.command(name='credits')
async def listCredits(ctx):
    for user in CreditStore:
        z = CreditStore[user]
        await ctx.send(f"{z[0]} has {z[1]} credits ")
    return


@bot.event
async def on_raw_reaction_add(reaction):
    channel = bot.get_channel(reaction.channel_id)
    message = await channel.fetch_message(reaction.message_id)
    author = message.author
    if reaction.member.id != author.id:
        if author.nick == None:
            username = author.name
        else:
            username = author.nick
        user = User(author.id, username)
        if CheckUserExists(user) != True:
            InitUser(user)
        if reaction.emoji.name == PositiveEmote:
            AddCredit(user)
        if reaction.emoji.name == NegativeEmote:
            RemoveCredit(user)
        print(reaction.emoji.name)
        with open('/data/creditstore.json', 'w') as f:
            json.dump(CreditStore, f)


@bot.event
async def on_raw_reaction_remove(reaction):
    channel = bot.get_channel(reaction.channel_id)
    message = await channel.fetch_message(reaction.message_id)
    author = message.author
    if author.nick == None:
        username = author.name
    else:
        username = author.nick
    user = User(author.id, username)
    if CheckUserExists(user) != True:
        InitUser(user)
    if reaction.emoji.name == PositiveEmote:
        RemoveCredit(user)
    if reaction.emoji.name == NegativeEmote:
        AddCredit(user)
    print(reaction.emoji.name)
    with open('/data/creditstore.json', 'w') as f:
        json.dump(CreditStore, f)

bot.run(TOKEN)
