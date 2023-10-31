import os
import discord
from discord.ext import commands, tasks
import json
##from dotenv import load_dotenv

##load_dotenv()
##creditStoreFilePath = 'data.json'
creditStoreFilePath = '/etc/socialcredit/data/creditstore.json'
botConfigFilePath = '/etc/socialcredit/data/config.json'

TOKEN = os.getenv('DISCORD_TOKEN')
SUPERUSER_ID = int(os.getenv('SUPERUSER_ID'))

intents = discord.Intents().all()
bot = commands.Bot(command_prefix='!', intents=intents)

PositiveEmote = 'positivesocialcredit'
NegativeEmote = 'negativesocialcredit'

CreditStore = {}
botConfig = {}

try:
    with open(creditStoreFilePath, 'r') as f:
        CreditStore = json.load(f)
except:
    print("No cache found")
try:
    with open(botConfigFilePath,'r') as f:
        botConfig = json.load(f)
except:
    print("No settings found, setting defaults")



def InitUser(user):
    CreditStore[user] = 0
    print(f'Initialised user with ID {user}')


def AddCredit(user):
    CreditStore[user] += 1


def RemoveCredit(user):
    CreditStore[user] -= 1


@bot.command(name='credits')
async def listCredits(ctx):
    try:
        message = ""
        sortlist = []
        userlist = bot.users
        for user in userlist:
            id = str(user.id)
            if id in CreditStore:
                sortlist.append((user.mention,CreditStore[id]))
                sortlist.sort(key = lambda x:x[1], reverse=True)
        for user in sortlist:
            message = message + \
                f"{user[0]} has {user[1]} credits \n"
        text = discord.Embed(colour=None, title='Credits', type='rich',
                             url=None, description=message, timestamp=None)
        await ctx.send(embed=text)
    except:
        await ctx.send("There's nothing here :(")
    return


@bot.command(name='clearcredits')
async def destructCredits(ctx):
    if ctx.author.id == SUPERUSER_ID:
        global CreditStore
        CreditStore = {}
        with open(creditStoreFilePath, 'w') as f:
            json.dump(CreditStore, f)
        await ctx.send("we wipin")


@bot.event
async def on_raw_reaction_add(reaction):
    channel = bot.get_channel(reaction.channel_id)
    message = await channel.fetch_message(reaction.message_id)
    author = message.author
    if reaction.member.id != author.id:
        user = str(author.id)
        if user not in CreditStore:
            InitUser(user)
        if reaction.emoji.name == PositiveEmote:
            AddCredit(user)
        if reaction.emoji.name == NegativeEmote:
            RemoveCredit(user)
        print(reaction.emoji.name)
        with open(creditStoreFilePath, 'w') as f:
            json.dump(CreditStore, f)


@bot.event
async def on_raw_reaction_remove(reaction):
    channel = bot.get_channel(reaction.channel_id)
    message = await channel.fetch_message(reaction.message_id)
    author = message.author
    user = str(author.id)
    if user not in CreditStore:
        InitUser(user)
    if reaction.emoji.name == PositiveEmote:
        RemoveCredit(user)
    if reaction.emoji.name == NegativeEmote:
        AddCredit(user)
    print(reaction.emoji.name)
    with open(creditStoreFilePath, 'w') as f:
        json.dump(CreditStore, f)

bot.run(TOKEN)
