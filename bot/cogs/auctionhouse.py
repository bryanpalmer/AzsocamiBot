import discord
from discord.ext import commands
import os, sys, inspect
import asyncio
from datetime import datetime

current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
import botlib
import wowapi
import umj

DEVMODE = os.getenv("DEVMODE") == "TRUE"  # Boolean flag for devmode


class AuctionHouse(commands.Cog):
    """
    Commands relating to Auction House data
    """

    def __init__(self, client):
        self.client = client

    ## On_Ready event for cog
    @commands.Cog.listener()
    async def on_ready(self):
        print("AuctionHouse is initialized.")

    @commands.command()
    @commands.has_any_role("RAID LEAD", "ADMIN", "MEMBER")
    async def add_item(self, ctx, itemId):
        """ Add <ItemID> to the RaidMats table """
        msgId = await ctx.send(f"Are you sure?  **Y**es or **N**o.")
        # This will make sure that the response will only be registered if the following
        # conditions are met:
        def check(msg):
            return (
                msg.author == ctx.author
                and msg.channel == ctx.channel
                and msg.content.lower() in ["y", "n"]
            )

        try:
            msg = await self.client.wait_for(
                "message", check=check, timeout=20
            )  # 20 seconds to reply
            if msg.content.lower() == "y":
                await ctx.send(wowapi.addItemIdToDB(itemId))
            await msg.delete()
            await msgId.delete()
        except asyncio.TimeoutError:
            await ctx.send("You didn't reply in time!  Cancelling item add.")
            await msgId.delete()

    @commands.command()
    @commands.has_any_role("RAID LEAD", "ADMIN", "MEMBER")
    async def remove_item(ctx, itemId):
        """ Remove ItemId from the RaidMats table """
        msgId = await ctx.send(f"Are you sure?  **Y**es or **N**o.")
        # This will make sure that the response will only be registered if the following
        # conditions are met:
        def check(msg):
            return (
                msg.author == ctx.author
                and msg.channel == ctx.channel
                and msg.content.lower() in ["y", "n"]
            )

        try:
            msg = await self.client.wait_for(
                "message", check=check, timeout=20
            )  # 20 seconds to reply
            if msg.content.lower() == "y":
                await ctx.send(wowapi.deleteItemFromDB(itemId))
            await msg.delete()
            await msgId.delete()
        except asyncio.TimeoutError:
            await ctx.send("You didn't reply in time!  Cancelling item delete.")
            await msgId.delete()

    @commands.command(name="lpc", aliases=["legendaries"])
    async def lpc(self, ctx, armortype="All"):
        """ Lookup legendary base items price and availability in Auction House """
        msgId = await ctx.send("Gathering data, please wait...")

        if armortype.lower() not in (
            "all",
            "cloth",
            "leather",
            "mail",
            "plate",
            "misc",
        ):
            # bad argument passed, defaulting to 'All'
            armorType = "ALL"
        else:
            armorType = armortype.upper()

        armors = wowapi.getLegendaryArmorsList()
        ahData = wowapi.getAuctionHouseData()
        for auction in ahData["auctions"]:
            # check auction data for legendaries
            if auction["item"]["id"] in armors:
                curID = auction["item"]["id"]
                context = auction["item"]["context"]
                # print(curID, context)
                if context == 63:
                    armors[curID]["lvl1qty"] += auction["quantity"]
                    if (
                        armors[curID]["lvl1cost"] == 0
                        or auction["buyout"] / 10000 < armors[curID]["lvl1cost"]
                    ):
                        armors[curID]["lvl1cost"] = auction["buyout"] / 10000
                if context == 64:
                    armors[curID]["lvl2qty"] += auction["quantity"]
                    if (
                        armors[curID]["lvl2cost"] == 0
                        or auction["buyout"] / 10000 < armors[curID]["lvl2cost"]
                    ):
                        armors[curID]["lvl2cost"] = auction["buyout"] / 10000
                if context == 65:
                    armors[curID]["lvl3qty"] += auction["quantity"]
                    if (
                        armors[curID]["lvl3cost"] == 0
                        or auction["buyout"] / 10000 < armors[curID]["lvl3cost"]
                    ):
                        armors[curID]["lvl3cost"] = auction["buyout"] / 10000
                if context == 66:
                    armors[curID]["lvl4qty"] += auction["quantity"]
                    if (
                        armors[curID]["lvl4cost"] == 0
                        or auction["buyout"] / 10000 < armors[curID]["lvl4cost"]
                    ):
                        armors[curID]["lvl4cost"] = auction["buyout"] / 10000

                if context == 67:
                    armors[curID]["lvl5qty"] += auction["quantity"]
                    if (
                        armors[curID]["lvl5cost"] == 0
                        or auction["buyout"] / 10000 < armors[curID]["lvl5cost"]
                    ):
                        armors[curID]["lvl5cost"] = auction["buyout"] / 10000

                if context == 68:
                    armors[curID]["lvl6qty"] += auction["quantity"]
                    if (
                        armors[curID]["lvl6cost"] == 0
                        or auction["buyout"] / 10000 < armors[curID]["lvl6cost"]
                    ):
                        armors[curID]["lvl6cost"] = auction["buyout"] / 10000

        heading = f"{'Name'.ljust(25,' ')}\t{'iLvl 225'.rjust(10,' ')}\t{'iLvl 235'.rjust(10,' ')}\t{'iLvl 249'.rjust(10,' ')}\t{'iLvl 262'.rjust(10,' ')}\n"
        cloth = heading
        leather = heading
        mail = heading
        plate = heading
        misc = heading
        for armorId in armors:
            msgLine = f"{armors[armorId]['name'].ljust(25,' ')}\t{armors[armorId]['lvl3cost']:>10,.2f}\t{armors[armorId]['lvl4cost']:>10,.2f}\t{armors[armorId]['lvl5cost']:>10,.2f}\t{armors[armorId]['lvl6cost']:>10,.2f}\n"
            if (
                armors[armorId]["subclass"] == "Cloth"
                and "Cape" not in armors[armorId]["name"]
            ):
                cloth += msgLine
            elif armors[armorId]["subclass"] == "Leather":
                leather += msgLine
            elif armors[armorId]["subclass"] == "Mail":
                mail += msgLine
            elif armors[armorId]["subclass"] == "Plate":
                plate += msgLine
            elif (
                armors[armorId]["subclass"] == "Miscellaneous"
                or "Cape" in armors[armorId]["name"]
            ):
                misc += msgLine

        msg1 = f"**Legendary Armors**\n"
        if armorType in ("ALL", "CLOTH"):
            msg1 += f"**Cloth Armors**\n```{cloth}```\n"
        if armorType in ("ALL", "LEATHER"):
            msg1 += f"**Leather Armors**\n```{leather}```"
        msg2 = f"**Legendary Armors**\n"
        if armorType in ("ALL", "MAIL"):
            msg2 += f"**Mail Armor**\n```{mail}```\n"
        if armorType in ("ALL", "PLATE"):
            msg2 += f"**Plate Armor**\n```{plate}```"
        msg3 = f"**Legendary Armors**\n"
        if armorType in ("ALL", "MISC"):
            msg3 += f"**Miscellaneous**\n```{misc}```"

        if armorType in ("ALL", "CLOTH", "LEATHER"):
            await ctx.send(msg1)
        if armorType in ("ALL", "MAIL", "PLATE"):
            await ctx.send(msg2)
        if armorType in ("ALL", "MISC"):
            await ctx.send(msg3)
        await msgId.delete()

    @commands.command(name="mats", aliases=["raidmats"])
    async def mats(self, ctx):
        """ Lookup common raid mats prices and availability in Auction House """
        # resp = wowapi.cmdRaidMats()
        # await botlib.send_embed(ctx, resp)

        raidMats = wowapi.getRaidMats()
        ahData = wowapi.getAuctionHouseData()
        umjConn = umj.create_connection()

        for mat in raidMats:
            # fill out class/subclass info from items db
            curId = raidMats[mat]["id"]
            item = umj.getItemById(umjConn, curId)
            raidMats[mat]["classname"] = item.classname
            raidMats[mat]["subclass"] = item.subclass

        for auction in ahData["auctions"]:
            # check auction data for raw mats
            if auction["item"]["id"] in raidMats:
                curID = auction["item"]["id"]
                raidMats[curID]["quantity"] += auction["quantity"]
                if (
                    raidMats[curID]["unitcost"] == 0
                    or auction["unit_price"] / 10000 < raidMats[curID]["unitcost"]
                ):
                    raidMats[curID]["unitcost"] = auction["unit_price"] / 10000

        umjConn.close()
        wowapi.setLastRun("AUCTION_HOUSE")
        lastRun = datetime.now()

        foodTxt = ""
        alchTxt = ""
        lwTxt = ""
        oreTxt = ""
        goodsTxt = ""
        miscTxt = ""

        for key in raidMats:
            name = raidMats[key]["name"]
            qty = raidMats[key]["quantity"]
            ttlcost = raidMats[key]["unitcost"]
            mattype = raidMats[key]["subclass"]
            matclass = raidMats[key]["classname"]
            # assign each mat to a specific embed field
            if matclass == "Tradeskill" and (mattype == "Herb" or mattype == "Other"):
                if qty > 0:
                    alchTxt += f"{ name }: {qty} - *{round(ttlcost,0)}g*\n"
                else:
                    alchTxt += f"{ name }: None Available\n"

            elif matclass == "Tradeskill" and mattype == "Cooking":
                if qty > 0:
                    foodTxt += f"{ name }: {qty} - *{round(ttlcost,0)}g*\n"
                else:
                    foodTxt += f"{ name }: None Available\n"

            elif matclass == "Tradeskill" and mattype == "Metal & Stone":
                if qty > 0:
                    oreTxt += f"{ name }: {qty} - *{round(ttlcost,0)}g*\n"
                else:
                    oreTxt += f"{ name }: None Available\n"

            elif matclass == "Tradeskill" and (
                mattype == "Leather" or mattype == "Cloth"
            ):
                if qty > 0:
                    lwTxt += f"{ name }: {qty} - *{round(ttlcost,0)}g*\n"
                else:
                    lwTxt += f"{ name }: None Available\n"

            elif (
                matclass == "Consumable"
                and (
                    mattype == "Potion"
                    or mattype == "Flask"
                    or mattype == "Other"
                    or mattype == "Food & Drink"
                    or mattype == "Vantus Runes"
                )
            ) or (matclass == "Item Enhancement" and mattype == "Misc"):
                if qty > 0:
                    goodsTxt += f"[{ name }](https://www.wowhead.com/item={key}): {qty} - *{round(ttlcost,0)}g*\n"
                else:
                    goodsTxt += f"[{ name }](https://www.wowhead.com/item={key}): None Available\n"

            else:
                if qty > 0:
                    miscTxt += f"{ name }: {qty} - *{round(ttlcost,0)}g*\n"
                else:
                    miscTxt += f"{ name }: None Available\n"
                print(f"{key} - {name} missing category:  {matclass} | {mattype}")

        response = discord.Embed(
            title="Raid Mats",
            url="https://www.wowhead.com/",
            description="Current auction house prices for common raid mats on our server.",
            color=discord.Color.blue(),
        )
        aLines = botlib.str2embedarray(alchTxt)
        for i, line in enumerate(aLines):
            if len(line) > 0:
                fieldName = f"Alchemy Mats{'' if i==0 else ' cont.'}"
                response.add_field(name="Alchemy Mats", value=line, inline=False)

        aLines = botlib.str2embedarray(foodTxt)
        for i, line in enumerate(aLines):
            if len(line) > 0:
                fieldName = f"Cooking Mats{'' if i==0 else ' cont.'}"
                response.add_field(name=fieldName, value=line, inline=False)

        # response.add_field(name="\u200b", value="\u200b", inline=False)

        aLines = botlib.str2embedarray(lwTxt)
        for i, line in enumerate(aLines):
            if len(line) > 0:
                fieldName = f"LW / Cloth Mats{'' if i==0 else ' cont.'}"
                response.add_field(name=fieldName, value=line, inline=False)

        aLines = botlib.str2embedarray(oreTxt)
        for i, line in enumerate(aLines):
            if len(line) > 0:
                fieldName = f"Smithing Mats{'' if i==0 else ' cont.'}"
                response.add_field(name=fieldName, value=line, inline=False)

        aLines = botlib.str2embedarray(goodsTxt)
        for i, line in enumerate(aLines):
            if len(line) > 0:
                fieldName = f"Finished Goods{'' if i==0 else ' cont.'}"
                response.add_field(name=fieldName, value=line, inline=False)

        aLines = botlib.str2embedarray(miscTxt)
        for i, line in enumerate(aLines):
            if len(line) > 0:
                fieldName = f"Uncategorized Items{'' if i==0 else ' cont.'}"
                response.add_field(name=fieldName, value=line, inline=False)

        response.set_footer(
            text=f"Auction house data last collected at {botlib.localTimeStr(lastRun)}"
        )

        await botlib.send_embed(ctx, response)
        # # await ctx.send(embed=response)

    @commands.command(aliases=["mats2"], hidden=True)
    async def raidmats2(self, ctx):
        raidMats = wowapi.getRaidMats()
        ahData = wowapi.getAuctionHouseData()
        for auction in ahData["auctions"]:
            # check auction data for raw mats
            if auction["item"]["id"] in raidMats:
                curID = auction["item"]["id"]
                raidMats[curID]["quantity"] += auction["quantity"]
                if (
                    raidMats[curID]["unitcost"] == 0
                    or auction["unit_price"] / 10000 < raidMats[curID]["unitcost"]
                ):
                    raidMats[curID]["unitcost"] = auction["unit_price"] / 10000
        wowapi.setLastRun("AUCTION_HOUSE")
        lastRun = datetime.now()

        ingNightShade = raidMats[171315]["unitcost"]  # 3
        ingRisingGlory = raidMats[168586]["unitcost"]  # 4
        ingMarrowRoot = raidMats[168589]["unitcost"]  # 4
        ingWidowBloom = raidMats[168583]["unitcost"]  # 4
        ingVigilsTorch = raidMats[170554]["unitcost"]  # 4
        ingFlask = raidMats[171276]["unitcost"]
        flaskCost = (
            (ingNightShade * 3)
            + (ingRisingGlory * 4)
            + (ingMarrowRoot * 4)
            + (ingWidowBloom * 4)
            + (ingVigilsTorch * 4)
        )

        msg = f"{raidMats[171276]['name']} AH Price - {ingFlask}\n"
        msg += f"{raidMats[171276]['name']} Crafted Cost - {flaskCost}\n"
        msg += f"{'Cheaper to craft your own,' if flaskCost<ingFlask else 'Cheaper to buy on AH,'} {round(ingFlask-flaskCost,2) if flaskCost<ingFlask else round(flaskCost-ingFlask,2)} savings."

        await ctx.send(msg)

    @commands.command(aliases=["wowtoken"])
    async def token(self, ctx):
        tokenData = wowapi.getTokenInfo()
        goldValue = tokenData["price"] / 10000
        dts = int(tokenData["last_updated_timestamp"] / 1000)
        msg = f"WoW Token Price:  {int(goldValue)}g as of {botlib.localTimeFromUTC(datetime.fromtimestamp(dts))}"
        await ctx.send(msg)


## Initialize cog
def setup(client):
    client.add_cog(AuctionHouse(client))