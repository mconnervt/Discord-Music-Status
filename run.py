import asyncio
import configparser
import inspect
import sys
import time
import os

import discord
from discord.ext import commands
from logbook import Logger, StreamHandler, FileHandler

logger = Logger("Discord Xbox")
logger.handlers.append(StreamHandler(sys.stdout, bubble=True))
logger.handlers.append(FileHandler("last-run.log", bubble=True, mode="w"))

logger.debug("Loading config files")

default_config = "[Config]\ntoken = \napiKey = \nxboxID = "

config = configparser.ConfigParser()

token = ""
apiKey = ""
xboxID = ""

if os.path.exists("config.ini"):
    config.read("config.ini")

    try:
        token = config['Config']['token']
    except KeyError:
        logger.critical("No token found in config, please ensure that the config formatting is correct")
        time.sleep(5)
        exit(1)

    if token == "":
        logger.critical("No token set! Exiting")
        time.sleep(5)
        exit(1)

    try:
        apiKey = config['Config']['apiKey']
    except KeyError:
        logger.critical("No Xbox API key found in config, please ensure that the config formatting is correct")
        time.sleep(5)
        exit(1)

    if apiKey == "":
        logger.critical("No Xbox API key set! Exiting")
        time.sleep(5)
        exit(1)

    try:
        xboxID = config['Config']['xboxID']
    except KeyError:
        logger.critical("No Xbox ID found in config, please ensure that the config formatting is correct")
        time.sleep(5)
        exit(1)

    if xboxID == "":
        logger.critical("No Xbox API key set! Exiting")
        time.sleep(5)
        exit(1)

else:
    logger.error("No config file, creating one now")
    with open("config.ini", 'w') as f:
        f.write(default_config)
    logger.info("Config created, please set config!")
    time.sleep(3)
    exit(0)

logger.info("Config loaded")

bot = commands.Bot(command_prefix=['m.'], self_bot=True)
bot.remove_command('help')


@bot.event
async def on_ready():
    logger.info(f"Logged in as {bot.user.name} with ID {bot.user.id}")
    logger.info("Ready to start")


@bot.command(name="quit")
async def _quit():
    await bot.say("Logging out...")
    await bot.change_presence(afk=True, status=discord.Status.invisible, game=None)
    logger.info("Logging out")
    await bot.logout()


async def xbox_loop():
    await bot.wait_until_ready()
    await asyncio.sleep(1)
    last_game = ""
    while not bot.is_closed:
        xboxGame = pull_game()
        if xboxGame != last_game:
            last_game = xboxGame
            if xboxGame == "":
                await bot.change_presence(afk=True, status=discord.Status.invisible, game=None)
                logger.info("Cleared Discord Status because no game is active") #TODO how does API handle offline?
            else:
                await bot.change_presence(
                    afk=True,
                    status=discord.Status.invisible,
                    game=discord.Game(name=xboxGame, type=2) #TODO figure out what type means
                    )
                #logger.info(f"Set Discord status to {xboxGame.encode('ascii', 'ignore').decode()}") #TODO is the encode/decode needed?
                logger.info(f"Set Discord status to {xboxGame}") #TODO is the encode/decode needed?
        await asyncio.sleep(8)


def pull_game():
    print("Inside pull game")



try:
    logger.info("Logging in")
    bot.loop.create_task(xbox_loop())
    bot.run(token, bot=False)
except discord.errors.LoginFailure:
    logger.critical("Log in failed, check token!")
    time.sleep(5)
    exit(1)
