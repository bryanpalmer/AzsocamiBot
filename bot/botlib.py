#  botlib
import discord

# from discord.ext import commands
from discord.errors import Forbidden

# Generic functions for the discord bot
import datetime
from pytz import timezone

# import time
TIMEZONE = "US/Central"  # Timezone for bot responses
TIMEFORMAT = "%Y-%m-%d %H:%M:%S %Z"


async def send_embed(ctx, embed):
    """
    Function that handles the sending of embeds
    -> Takes context and embed to send
    - tries to send embed in channel
    - tries to send normal message when that fails
    - tries to send embed private with information abot missing permissions
    If this all fails: https://youtu.be/dQw4w9WgXcQ
    """
    try:
        await ctx.send(embed=embed)
    except Forbidden:
        try:
            await ctx.send(
                "Hey, seems like I can't send embeds. Please check my permissions :)"
            )
        except Forbidden:
            await ctx.author.send(
                f"Hey, seems like I can't send any message in {ctx.channel.name} on {ctx.guild.name}\n"
                f"May you inform the server team about this issue? :slight_smile: ",
                embed=embed,
            )


def str2embedarray(origString, maxlen=1024):
    if len(origString) < maxlen:
        return [origString]
    aLines = origString.splitlines(True)
    retArray = []
    tempStr = ""
    for line in aLines:
        if len(tempStr + line) < maxlen:
            tempStr += line
        else:
            retArray.append(tempStr)
            tempStr = line
    retArray.append(tempStr)
    return retArray


def localTimeStr(utcTime):
    return utcTime.astimezone(timezone(TIMEZONE)).strftime(TIMEFORMAT)


def localTimeFromUTC(utcTime):
    return utcTime.astimezone(timezone(TIMEZONE))


def localNow():
    return localTimeStr(datetime.datetime.now())
