import discord
from discord.ext import commands, tasks
import os, sys, inspect
import asyncio

current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
import botlib

DEVMODE = os.getenv("DEVMODE") == "TRUE"  # Boolean flag for devmode
ENVVERSION = os.getenv("ENV_VERSION")  # Local .env or server vars
COMMAND_PREFIX = os.getenv("COMMAND_PREFIX")  # Bot command prefix


class Dnd(commands.Cog):
    """
    Dnd bot discord functions
    """

    def __init__(self, client):
        self.client = client

    ## On_Ready event for cog
    @commands.Cog.listener()
    async def on_ready(self):
        print("Dnd is initialized.")

    ###################################################################
    ###################################################################
    ##                                                               ##
    ##                    DND COMMANDS                               ##
    ##                                                               ##
    ###################################################################
    ###################################################################

    @commands.command()
    async def roll(self, ctx, *args):
        """ Roll command """
        fullmsg = ""

        for arg in args:
            diceStr = arg.lower()

            dIndex = diceStr.find('d')
            if dIndex == -1:
                raise Exception('Missing the "d" character.')

            numberOfDice = diceStr[:dIndex]
            if not numberOfDice.isdecimal():
                raise Exception('Missing number of dice')
            numberOfDice = int(numberOfDice)

            modIndex = diceStr.find('+')
            if modIndex == -1:
                modIndex = diceStr.find('-')

            if 

            if 'D' in uarg:
                targ = uarg.split("D", 1)
            msg += f"{arg} "

        await ctx.send(msg)

    ###################################################################
    ###################################################################
    ##                                                               ##
    ##             NOT IMPLEMENTED YET                               ##
    ##                                                               ##
    ###################################################################
    ###################################################################


## Initialize cog
def setup(client):
    client.add_cog(Dnd(client))
