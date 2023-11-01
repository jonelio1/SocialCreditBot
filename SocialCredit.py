import os
import discord
from discord.ext import commands, tasks
import json
import datetime
# from dotenv import load_dotenv

# load_dotenv()
# creditStoreFilePath = 'data.json'
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

botConfig['SuperMult'] = 1
try:
    with open(creditStoreFilePath, 'r') as f:
        CreditStore = json.load(f)
except:
    print("No cache found")

utc = datetime.timezone.utc
time = datetime.time(hour=20, tzinfo=utc)
botConfig['DailyTime'] = time
try:
    with open(botConfigFilePath, 'r') as f:
        botConfig = json.load(f)
except:
    print("No settings found, using defaults")


def InitUser(user):
    CreditStore[user] = 0
    print(f'Initialised user with ID {user}')


def AddCredit(user, score):
    CreditStore[user] += score


def RemoveCredit(user, score):
    CreditStore[user] -= score


def BuildCreditEmbed():
    message = ""
    sortlist = []
    userlist = bot.users
    for user in userlist:
        id = str(user.id)
        if id in CreditStore:
            sortlist.append((user.mention, CreditStore[id]))
            sortlist.sort(key=lambda x: x[1], reverse=True)
    for user in sortlist:
        message = message + \
            f"{user[0]} has {user[1]} credits \n"
    text = discord.Embed(colour=None, title='Credits', type='rich',
                         url=None, description=message, timestamp=None)
    return text


# @bot.command(name='setsupermult')
# async def setSuperMult(ctx, arg):
#     if ctx.author.id == SUPERUSER_ID:
#         try:
#             botConfig['SuperMult'] == arg
#             print(f"Setting Super multiplier to {arg}")
#             await ctx.send(f"Super Multiplier set to {arg}")
#             with open(botConfigFilePath, 'w') as f:
#               json.dump(botConfig, f)
#         except:
#             await ctx.send("Invalid command dumbass")
#     else:
#         await ctx.send("who the fuck are you")

# @bot.command(name='supermult')
# async def getSuperMult(ctx):
#     await ctx.send(f"Super Multiplier is currently {botConfig['SuperMult']}")


@tasks.loop(time=botConfig['DailyTime'])
async def dailyCredits(self):
    text = BuildCreditEmbed()
    channel = botConfig['TargetChannel']
    await channel.send(embed=text)


@bot.command(name='setchannel')
async def setChannel(ctx):
    if ctx.author.id == SUPERUSER_ID:
        dailyCredits.cancel()
        botConfig['TargetChannel'] = ctx.channel
        channel = botConfig['TargetChannel']
        await channel.send("Using this channel")
        with open(botConfigFilePath, 'w') as f:
            json.dump(botConfig, f)
        dailyCredits.start()
    else:
        await ctx.send("i'm sorry who the fuck are you")


@bot.command(name='settime')
async def setTime(ctx, arg):
    if ctx.author.id == SUPERUSER_ID:
        dailyCredits.cancel()
        time = datetime.time(hour=arg, tzinfo=utc)
        botConfig['DailyTime'] = time
        await ctx.send(f"Daily Credits run at {arg} UTC")
        with open(botConfigFilePath, 'w') as f:
            json.dump(botConfig, f)
        dailyCredits.start()
    else:
        await ctx.send("i'm sorry who the fuck are you")


@bot.command(name='where')
async def shoutChannel(ctx):
    channel = botConfig['TargetChannel']
    await channel.send("Here!")


@bot.command(name='credits')
async def listCredits(ctx):
    try:
        text = BuildCreditEmbed()
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
        # if reaction.burst:
        # score = 1*botConfig['SuperMult']
        # else:
        score = 1
        if user not in CreditStore:
            InitUser(user)
        if reaction.emoji.name == PositiveEmote:
            AddCredit(user, score)
        if reaction.emoji.name == NegativeEmote:
            RemoveCredit(user, score)
        print(reaction.emoji.name)
        with open(creditStoreFilePath, 'w') as f:
            json.dump(CreditStore, f)


@bot.event
async def on_raw_reaction_remove(reaction):
    channel = bot.get_channel(reaction.channel_id)
    message = await channel.fetch_message(reaction.message_id)
    author = message.author
    user = str(author.id)
    # if reaction.burst:
    # score = 1*botConfig['SuperMult']
    # else:
    score = 1
    if user not in CreditStore:
        InitUser(user)
    if reaction.emoji.name == PositiveEmote:
        RemoveCredit(user, score)
    if reaction.emoji.name == NegativeEmote:
        AddCredit(user, score)
    print(reaction.emoji.name)
    with open(creditStoreFilePath, 'w') as f:
        json.dump(CreditStore, f)


@bot.event
async def on_ready():
    print(discord.__version__)
bot.run(TOKEN)
