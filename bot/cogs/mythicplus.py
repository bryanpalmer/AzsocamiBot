import discord
from discord.ext import commands, tasks
import os, sys, inspect
import datetime

current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
import botlib
import wowapi

DEVMODE = os.getenv("DEVMODE") == "TRUE"  # Boolean flag for devmode
COMMAND_PREFIX = os.getenv("COMMAND_PREFIX")  # Bot command prefix
# TIMEZONE = "US/Central"  # Timezone for bot responses
# TIMEFORMAT = "%Y-%m-%d %H:%M:%S %Z"

# Global dungeon shortnames
dungeon_count = 8
mplusdungeons = []
mplusdungeons.append("GD")
mplusdungeons.append("ID")
mplusdungeons.append("YARD")
mplusdungeons.append("WORK")
mplusdungeons.append("LOWR")
mplusdungeons.append("UPPR")
mplusdungeons.append("GMBT")
mplusdungeons.append("STRT")


class MythicPlus(commands.Cog):
    """
    Commands related to Mythic Plus results and tracking
    """

    def __init__(self, client):
        self.client = client

    ## EVENTS
    @commands.Cog.listener()
    async def on_ready(self):
        print("MythicPlus is initialized.")
        if DEVMODE == False:
            self.updateMythicPlusDataBG.start()

    ## NON-COMMAND FUNCTIONS
    async def announceUpdate(self, rec):
        if DEVMODE == False:
            ## Guild bot channel
            botChannel = self.client.get_channel(742388489038987374)
        if DEVMODE == True:
            ## Test server bot-testing channel
            botChannel = self.client.get_channel(790667200197296138)
        await botChannel.send(
            f"{rec['name']}'s score has increased from {rec['prev']} to {rec['high']}!"
        )

    async def hiddenAnnouncedScoreUpdate(self, playerName):
        if DEVMODE == False:
            botChannel = self.client.get_channel(742388489038987374)
        if DEVMODE == True:
            botChannel = self.client.get_channel(790667200197296138)

        # botChannel = bot.get_channel(742388489038987374)
        playerRow = wowapi.getMythicPlusByName(playerName)
        if playerRow != "":
            realm = playerRow[2]
            player = playerRow[1]
            rioScore = wowapi.api_raiderio_char_mplus_score(player, realm)
            rioRecent = wowapi.api_raiderio_char_mplus_recent_runs(player, realm)
            rioRank = wowapi.api_raiderio_char_mplus_rank(player, realm)
            serverRealm = rioRank["realm"]
            playerFaction = rioRank["faction"]
            playerClass = rioRank["class"]
            classIcon = wowapi.getClassIconUrl(playerClass)
            playerThumb = rioRank["thumbnail_url"]
            playerSpec = rioScore["active_spec_name"]
            lastCrawled = rioScore["last_crawled_at"]
            profileUrl = rioScore["profile_url"]
            playerScoreAll = rioScore["mythic_plus_scores_by_season"][0]["scores"][
                "all"
            ]
            playerScoreTank = 0
            if "tank" in rioScore["mythic_plus_scores_by_season"][0]["scores"]:
                playerScoreTank = rioScore["mythic_plus_scores_by_season"][0]["scores"][
                    "tank"
                ]

            playerScoreDps = 0
            if "dps" in rioScore["mythic_plus_scores_by_season"][0]["scores"]:
                playerScoreDps = rioScore["mythic_plus_scores_by_season"][0]["scores"][
                    "dps"
                ]

            playerScoreHeals = 0
            if "healer" in rioScore["mythic_plus_scores_by_season"][0]["scores"]:
                playerScoreHeals = rioScore["mythic_plus_scores_by_season"][0][
                    "scores"
                ]["healer"]

            playerRankOverall = rioRank["mythic_plus_ranks"]["overall"]["realm"]
            playerRankClass = rioRank["mythic_plus_ranks"]["class"]["realm"]

            response = discord.Embed(
                title=f"{int(playerScoreAll)} Mythic+ Score",
                description=f"**Tank Score:** {int(playerScoreTank)}\n**Healer Score:** {int(playerScoreHeals)}\n**DPS Score:** {int(playerScoreDps)}\n",
                color=0x990000,
            )
            classIconUrl = classIcon
            response.set_author(
                name=f"{player}, {playerSpec} {playerClass}",
                icon_url=classIconUrl,
            )
            response.set_thumbnail(url=playerThumb)
            ranksValue = ""
            if "faction_tank" in rioRank["mythic_plus_ranks"]:
                ranksValue += f"**Tank Rank:** #{rioRank['mythic_plus_ranks']['faction_tank']['realm']} "
                ranksValue += f"(#{rioRank['mythic_plus_ranks']['faction_class_tank']['realm']} {playerClass})\n"

            if "faction_dps" in rioRank["mythic_plus_ranks"]:
                ranksValue += f"**DPS Rank:** #{rioRank['mythic_plus_ranks']['faction_dps']['realm']} "
                ranksValue += f"(#{rioRank['mythic_plus_ranks']['faction_class_dps']['realm']} {playerClass})\n"

            if "faction_healer" in rioRank["mythic_plus_ranks"]:
                ranksValue += f"**Healer Rank:** #{rioRank['mythic_plus_ranks']['faction_healer']['realm']} "
                ranksValue += f"(#{rioRank['mythic_plus_ranks']['faction_class_healer']['realm']} {playerClass})\n"

            ranksValue += f"[Character Info]({profileUrl})\n*All ranks are {serverRealm} {playerFaction}.*"

            response.add_field(
                name=f"#{playerRankOverall} on {serverRealm} (#{playerRankClass} {playerClass})",
                value=ranksValue,
                inline=False,
            )

            if (
                not "mythic_plus_recent_runs" in rioRecent
                or len(rioRecent["mythic_plus_recent_runs"]) == 0
            ):
                recentDungeon = "None"
                recentLevel = 0
                recentResult = 0
                recentScore = 0
                recentUrl = "#"
            else:
                recentDungeon = rioRecent["mythic_plus_recent_runs"][0]["dungeon"]
                recentLevel = rioRecent["mythic_plus_recent_runs"][0]["mythic_level"]
                recentResult = rioRecent["mythic_plus_recent_runs"][0][
                    "num_keystone_upgrades"
                ]
                recentScore = rioRecent["mythic_plus_recent_runs"][0]["score"]
                recentUrl = rioRecent["mythic_plus_recent_runs"][0]["url"]

            lrMsg = f"**Dungeon:** {recentDungeon}\n"
            lrMsg += f"**Level:** +{recentLevel}\n"
            lrMsg += f"**Result:** +{recentResult}\n"
            lrMsg += f"**Points:** {recentScore}\n"
            lrMsg += f"[Group Info]({recentUrl})"
            response.add_field(name="Last Run", value=lrMsg, inline=False)

            response.set_footer(
                text=f"AzsocamiBot w/ Raider.IO Data | Last crawled at {lastCrawled}",
            )
            await botChannel.send(embed=response)

        else:
            botChannel.send("Player not found.")

    ## COMMANDS
    # follow
    @commands.command()
    async def follow(self, ctx, playerName, realmName="zuljin"):
        """ Adds <playerName> <realmName> to the Mythic Plus tracking system """
        print(f"Adding {playerName} {realmName} to mythic plus tracking")
        msg = wowapi.addPlayerToMythicPlus(playerName, realmName)
        await ctx.send(msg)

    # unfollow
    @commands.command()
    async def unfollow(self, ctx, playerName):
        """ Removes <playerName> from the Mythic Plus tracking system """
        print(f"Removing {playerName} from mythic plus tracking")
        msg = wowapi.removePlayerFromMythicPlus(playerName)
        await ctx.send(msg)

    # update
    @commands.command(name="update")
    async def update_scores(self, ctx):
        """ Updates MythicPlus scores database from Raider.IO """
        msgId = await ctx.send("Running update.")
        updates = wowapi.updateMythicPlusScores()
        if len(updates) > 0:
            for rec in updates:
                # print(rec)
                await self.announceUpdate(rec)
                await self.hiddenAnnouncedScoreUpdate(rec["name"])
        await ctx.send("Mythic+ scores updated.")
        await msgId.delete()

    @commands.command(aliases=["gv"])
    async def gvault(self, ctx):
        ## id, name, realmslug, role, expires FROM members ORDER BY name
        teamList = wowapi.getMembersList()
        gvList = []
        lastReset = wowapi.getLastResetDateTime()
        print(lastReset)
        for member in teamList:
            keysRun = []
            runsData = wowapi.api_raiderio_char_mplus_recent_runs(member[1], member[2])
            for run in runsData["mythic_plus_recent_runs"]:
                keyLvl = run["mythic_level"]
                rt = datetime.datetime.fromisoformat(
                    run["completed_at"].replace("Z", "+00:00")
                )
                print(rt, lastReset)
                if rt > lastReset:
                    keysRun.append(keyLvl)
            keysRun.sort(reverse=True)
            gvList.append((member[1].title(), keysRun))
        msg = "```| Name            | M+ Vault |   Count    |\n"
        msg += "|-----------------+----------+------------|\n"
        for member in gvList:
            # print(member)
            m1 = 0
            m4 = 0
            m10 = 0
            if len(member[1]) > 0:
                m1 = member[1][0]
            if len(member[1]) > 3:
                m4 = member[1][3]
            if len(member[1]) > 9:
                m10 = member[1][9]
            msg += f"| {member[0].ljust(15,' ')} | {(str(m1) + '/' + str(m4) + '/' + str(m10)).rjust(8,' ') } |  {str(len(member[1])).rjust(2,' ')} {'run ' if len(member[1])==1 else 'runs'}   |\n"
        msg += "```"
        print(f"Msg length: {len(msg)}")
        await ctx.send(msg)

    # scores
    @commands.command()
    async def scores(self, ctx):
        """ Lists scores of all followed Mythic Plus members """
        scores = wowapi.getMythicPlusScores()
        scoreNames = ""
        scoreValues = ""
        currentRow = 0
        curSet = 0
        sNames = []
        sValues = []
        for row in scores:
            curSet += 1
            if curSet > 10:
                ## Exceeded 10 rows, time to reset
                sNames.append(scoreNames)
                sValues.append(scoreValues)
                scoreNames = ""
                scoreValues = ""
                curSet = 1
            ## Set values for the strings
            currentRow += 1
            scoreNames += f"{currentRow}) [{ row[1] }](https://raider.io/characters/us/{row[2].lower()}/{row[1]})\n"
            scoreValues += f"{row[3]}\n"
        ## all rows processed, add strings to the lists
        sNames.append(scoreNames)
        sValues.append(scoreValues)

        response = discord.Embed(
            title="Followed Characters for Azsocami",
            description="Sorted by Score",
            color=0x990000
            # discord.Color.blue(),
        )

        j = len(sNames)
        i = 0
        for nam, scor in zip(sNames, sValues):
            fieldName = f"Character{'' if i==0 else ' cont.'}"
            response.add_field(name=fieldName, value=nam, inline=True)
            response.add_field(name="Score", value=scor, inline=True)
            ## this is an ugly fix to keep inline fields from appearing 3 wide
            i += 1
            if i < j:
                response.add_field(name=".", value=".", inline=False)

        # response.add_field(name="Character", value=scoreNames, inline=True)
        # response.add_field(name="Score", value=scoreValues, inline=True)

        response.set_footer(
            text=f"AzsocamiBot w/ Raider.IO Data | Last crawled at {botlib.localNow()}",
        )

        await ctx.send(embed=response)

    # score <playername>
    @commands.command()
    async def score(self, ctx, playerName):
        """ Reports current Mythic Plus dungeon scores and rankings """

        # dng1 = "GD"
        # dng2 = "ID"
        # dng3 = "YARD"
        # dng4 = "WORK"
        # dng5 = "LOWR"
        # dng6 = "UPPR"
        # dng7 = "GMBT"
        # dng8 = "STRT"

        playerRow = wowapi.getMythicPlusByName(playerName)
        # print(playerRow)
        if playerRow != None:
            realm = playerRow[2]
            player = playerRow[1]
            dbplayerScore = playerRow[3]
            dbplayerPrev = playerRow[4]
            dbplayerId = playerRow[0]

            rioScore = wowapi.api_raiderio_char_mplus_score(player, realm)
            rioPrev = wowapi.api_raiderio_char_mplus_previous(player, realm)
            rioBest = wowapi.api_raiderio_char_mplus_best_runs(player, realm)
            rioAlts = wowapi.api_raiderio_char_mplus_alternate_runs(player, realm)
            rioRecent = wowapi.api_raiderio_char_mplus_recent_runs(player, realm)
            rioRank = wowapi.api_raiderio_char_mplus_rank(player, realm)
            serverRealm = rioRank["realm"]
            playerFaction = rioRank["faction"]
            playerClass = rioBest["class"]
            classIcon = wowapi.getClassIconUrl(playerClass)
            playerThumb = rioBest["thumbnail_url"]
            playerSpec = rioScore["active_spec_name"]
            lastCrawled = rioScore["last_crawled_at"]
            profileUrl = rioScore["profile_url"]
            playerScoreAll = rioScore["mythic_plus_scores_by_season"][0]["scores"][
                "all"
            ]
            playerScorePrev = rioPrev["mythic_plus_scores_by_season"][0]["scores"][
                "all"
            ]
            ## Major values all collected, let's sort out highest/previous scores
            ## and update our database.
            ## New high score incoming
            if dbplayerScore < playerScoreAll:
                prevScore = dbplayerScore
                highScore = playerScoreAll
            else:
                prevScore = dbplayerPrev
                highScore = playerScoreAll

            wowapi.updateMythicPlusScoreById(dbplayerId, highScore, prevScore)
            ## Done with updating db

            playerScoreTank = 0
            if "tank" in rioScore["mythic_plus_scores_by_season"][0]["scores"]:
                playerScoreTank = rioScore["mythic_plus_scores_by_season"][0]["scores"][
                    "tank"
                ]

            playerScoreDps = 0
            if "dps" in rioScore["mythic_plus_scores_by_season"][0]["scores"]:
                playerScoreDps = rioScore["mythic_plus_scores_by_season"][0]["scores"][
                    "dps"
                ]

            playerScoreHeals = 0
            if "healer" in rioScore["mythic_plus_scores_by_season"][0]["scores"]:
                playerScoreHeals = rioScore["mythic_plus_scores_by_season"][0][
                    "scores"
                ]["healer"]
            playerRankOverall = rioRank["mythic_plus_ranks"]["overall"]["realm"]
            playerRankClass = rioRank["mythic_plus_ranks"]["class"]["realm"]

            ## best = fortified, alt = tyrannical

            dDict = {}
            for i in range(len(mplusdungeons)):
                # print(f"{i} - {mplusdungeons[i]}")
                dDict[mplusdungeons[i]] = {
                    "shortname": mplusdungeons[i],
                    "best_level": 0,
                    "best_result": 0,
                    "best_score": 0,
                    "alt_level": 0,
                    "alt_result": 0,
                    "alt_score": 0,
                }

            for run in rioBest["mythic_plus_best_runs"]:
                # print(run)
                affix = run["affixes"][0]["name"]
                dung = run["short_name"]
                mlvl = run["mythic_level"]
                result = run["num_keystone_upgrades"]
                score = run["score"]

                if affix == "Fortified" and dDict[dung]["best_score"] == 0:
                    dDict[dung]["best_score"] = score
                    dDict[dung]["best_level"] = mlvl
                    dDict[dung]["best_result"] = result
                elif affix == "Tyrannical" and dDict[dung]["alt_score"] == 0:
                    dDict[dung]["alt_score"] = score
                    dDict[dung]["alt_level"] = mlvl
                    dDict[dung]["alt_result"] = result

            for run in rioAlts["mythic_plus_alternate_runs"]:
                affix = run["affixes"][0]["name"]
                dung = run["short_name"]
                mlvl = run["mythic_level"]
                result = run["num_keystone_upgrades"]
                score = run["score"]
                if affix == "Fortified" and dDict[dung]["best_score"] == 0:
                    dDict[dung]["best_score"] = score
                    dDict[dung]["best_level"] = mlvl
                    dDict[dung]["best_result"] = result
                elif affix == "Tyrannical" and dDict[dung]["alt_score"] == 0:
                    ## Only recording alternate run scores here
                    dDict[dung]["alt_score"] = score
                    dDict[dung]["alt_level"] = mlvl
                    dDict[dung]["alt_result"] = result

            response = discord.Embed(
                title=f"{playerScoreAll} Mythic+ Score",
                description=f"**Tank Score:** {int(playerScoreTank)}\n**Healer Score:** {int(playerScoreHeals)}\n**DPS Score:** {int(playerScoreDps)}\n**Last Season Score:** {int(playerScorePrev)}",
                color=0x990000,
            )
            classIconUrl = classIcon
            response.set_author(
                name=f"{player}, {playerSpec} {playerClass}",
                icon_url=classIconUrl,
            )
            response.set_thumbnail(url=playerThumb)

            ## Rankings
            ranksValue = ""
            if "faction_tank" in rioRank["mythic_plus_ranks"]:
                ranksValue += f"**Tank Rank:** #{rioRank['mythic_plus_ranks']['faction_tank']['realm']} "
                ranksValue += f"(#{rioRank['mythic_plus_ranks']['faction_class_tank']['realm']} {playerClass})\n"

            if "faction_dps" in rioRank["mythic_plus_ranks"]:
                ranksValue += f"**DPS Rank:** #{rioRank['mythic_plus_ranks']['faction_dps']['realm']} "
                ranksValue += f"(#{rioRank['mythic_plus_ranks']['faction_class_dps']['realm']} {playerClass})\n"

            if "faction_healer" in rioRank["mythic_plus_ranks"]:
                ranksValue += f"**Healer Rank:** #{rioRank['mythic_plus_ranks']['faction_healer']['realm']} "
                ranksValue += f"(#{rioRank['mythic_plus_ranks']['faction_class_healer']['realm']} {playerClass})\n"

            ranksValue += f"[Character Info]({profileUrl})\n*All ranks are {serverRealm} {playerFaction}.*"

            response.add_field(
                name=f"#{playerRankOverall} on {serverRealm} (#{playerRankClass} {playerClass})",
                value=ranksValue,
                inline=False,
            )

            ## Dungeons
            dMsg = ""
            sMsg = ""
            aMsg = ""
            for dungeon in dDict:
                fortBest = dDict[dungeon]["best_score"] > dDict[dungeon]["alt_score"]
                tyrBest = dDict[dungeon]["alt_score"] > dDict[dungeon]["best_score"]
                # print(dungeon)
                dName = dDict[dungeon]["shortname"]
                bestLvl = dDict[dungeon]["best_level"]
                bestScore = dDict[dungeon]["best_score"] * (1.5 if fortBest else 0.5)
                bestResult = dDict[dungeon]["best_result"]
                altLvl = dDict[dungeon]["alt_level"]
                altScore = dDict[dungeon]["alt_score"] * (1.5 if tyrBest else 0.5)
                altResult = dDict[dungeon]["alt_result"]

                baffix = (
                    "\*\*\*"
                    if bestResult == 3
                    else "\*\*"
                    if bestResult == 2
                    else "\*"
                    if bestResult == 1
                    else ""
                )

                aaffix = (
                    "\*\*\*"
                    if altResult == 3
                    else "\*\*"
                    if altResult == 2
                    else "\*"
                    if altResult == 1
                    else ""
                )

                dMsg += f"{dName.upper()}\n"
                sMsg += f"{'**' if fortBest else ''}{'--' if bestLvl==0 else '+'+str(bestLvl)}{baffix} ({int(bestScore)}){'**' if fortBest else ''}\n"
                aMsg += f"*{'**' if tyrBest else ''}{'--' if altLvl==0 else '+'+str(altLvl)}{aaffix} ({int(altScore)})*{'**' if tyrBest else ''}\n"
            # dMsg += "Highest This Week: --"

            response.add_field(name="Dungeon", value=dMsg, inline=True)
            response.add_field(name="Fortified", value=sMsg, inline=True)
            response.add_field(name="Tyrannical", value=aMsg, inline=True)

            if (
                not "mythic_plus_recent_runs" in rioRecent
                or len(rioRecent["mythic_plus_recent_runs"]) == 0
            ):
                recentDungeon = "None"
                recentLevel = 0
                recentResult = 0
                recentScore = 0
                recentUrl = "#"
            else:
                recentDungeon = rioRecent["mythic_plus_recent_runs"][0]["dungeon"]
                recentLevel = rioRecent["mythic_plus_recent_runs"][0]["mythic_level"]
                recentResult = rioRecent["mythic_plus_recent_runs"][0][
                    "num_keystone_upgrades"
                ]
                recentScore = rioRecent["mythic_plus_recent_runs"][0]["score"]
                recentUrl = rioRecent["mythic_plus_recent_runs"][0]["url"]

            lrMsg = f"**Dungeon:** {recentDungeon}\n"
            lrMsg += f"**Level:** +{recentLevel}\n"
            lrMsg += f"**Result:** +{recentResult}\n"
            lrMsg += f"**Points:** {recentScore}\n"
            lrMsg += f"[Group Info]({recentUrl})"
            response.add_field(name="Last Run", value=lrMsg, inline=False)

            response.set_footer(
                text=f"AzsocamiBot w/ Raider.IO Data | Last crawled at {lastCrawled}",
            )
            await ctx.send(embed=response)

        else:
            await ctx.send(
                f"{playerName.title()} not being followed.  Type **{COMMAND_PREFIX}follow {playerName}** to add to the tracking list."
            )

    ## Compare <playername> and <playername>
    @commands.command()
    async def compare(self, ctx, player1, player2):
        pass

    @commands.command(aliases=["br"])
    async def bestruns(self, ctx):
        """ Reports current Mythic Plus dungeon scores and rankings """

        playersList = wowapi.getMythicPlusPlayers()
        results = []
        for playerRow in playersList:
            realm = playerRow[2]
            player = playerRow[1].title()
            # print(f"Retrieving {player} {realm}")
            rioBest = wowapi.api_raiderio_char_mplus_best_runs(player, realm)
            rioAlts = wowapi.api_raiderio_char_mplus_alternate_runs(player, realm)

            dDict = {}
            for i in range(len(mplusdungeons)):
                # print(f"{i} - {mplusdungeons[i]}")
                dDict[mplusdungeons[i]] = {
                    "shortname": mplusdungeons[i],
                    "best_level": 0,
                    "best_result": 0,
                    "best_score": 0,
                    "alt_level": 0,
                    "alt_result": 0,
                    "alt_score": 0,
                }

            for run in rioBest["mythic_plus_best_runs"]:
                affix = run["affixes"][0]["name"]
                dung = run["short_name"]
                mlvl = run["mythic_level"]
                result = run["num_keystone_upgrades"]
                score = run["score"]

                if affix == "Fortified" and dDict[dung]["best_score"] == 0:
                    dDict[dung]["best_score"] = score
                    dDict[dung]["best_level"] = mlvl
                    dDict[dung]["best_result"] = result
                elif affix == "Tyrannical" and dDict[dung]["alt_score"] == 0:
                    dDict[dung]["alt_score"] = score
                    dDict[dung]["alt_level"] = mlvl
                    dDict[dung]["alt_result"] = result

            for run in rioAlts["mythic_plus_alternate_runs"]:
                affix = run["affixes"][0]["name"]
                dung = run["short_name"]
                mlvl = run["mythic_level"]
                result = run["num_keystone_upgrades"]
                score = run["score"]
                if affix == "Fortified" and dDict[dung]["best_score"] == 0:
                    dDict[dung]["best_score"] = score
                    dDict[dung]["best_level"] = mlvl
                    dDict[dung]["best_result"] = result
                elif affix == "Tyrannical" and dDict[dung]["alt_score"] == 0:
                    ## Only recording alternate run scores here
                    dDict[dung]["alt_score"] = score
                    dDict[dung]["alt_level"] = mlvl
                    dDict[dung]["alt_result"] = result

            results.append((player, dDict))

        # print(results)

        # Build header string
        msg = f"```{'Player'.ljust(13)}"
        for i in range(len(mplusdungeons)):
            msg += f" {mplusdungeons[i].ljust(7)}"
        msg += "\n"

        for player in results:
            playerName = player[0]
            dDict = player[1]
            # print(player[0])

            msg += f"{playerName.ljust(13)}"
            for i in range(len(mplusdungeons)):
                fortResult = (
                    dDict[mplusdungeons[i]]["best_level"]
                    if dDict[mplusdungeons[i]]["best_score"] > 0
                    else 0
                )
                tyrResult = (
                    dDict[mplusdungeons[i]]["alt_level"]
                    if dDict[mplusdungeons[i]]["alt_score"] > 0
                    else 0
                )
                msg += f" {fortResult:>2} {tyrResult:>2} |"
            msg += "\n"

        msg += "```\n"
        msg += "*All dungeons shown are Fortified Tyrannical, and only show positive values if the score>0 for the run.*"

        await ctx.send(msg)

    @commands.command(aliases=["brf"])
    async def bestrunsf(self, ctx):
        """ Reports current Mythic Plus dungeon scores and rankings """

        msgId = await ctx.send("Gathering BRF data, please wait...")
        playersList = wowapi.getMythicPlusPlayers()
        results = []
        for playerRow in playersList:
            realm = playerRow[2]
            player = playerRow[1].title()
            print(f"Retrieving {player} {realm}")
            rioBest = wowapi.api_raiderio_char_mplus_best_runs(player, realm)
            rioAlts = wowapi.api_raiderio_char_mplus_alternate_runs(player, realm)
            dDict = {}
            for i in range(len(mplusdungeons)):
                # print(f"{i} - {mplusdungeons[i]}")
                dDict[mplusdungeons[i]] = {
                    "shortname": mplusdungeons[i],
                    "best_level": 0,
                    "best_result": 0,
                    "best_score": 0,
                    "alt_level": 0,
                    "alt_result": 0,
                    "alt_score": 0,
                }

            for run in rioBest["mythic_plus_best_runs"]:
                # print(run)
                affix = run["affixes"][0]["name"]
                dung = run["short_name"]
                mlvl = run["mythic_level"]
                result = run["num_keystone_upgrades"]
                score = run["score"]

                if affix == "Fortified" and dDict[dung]["best_score"] == 0:
                    dDict[dung]["best_score"] = score
                    dDict[dung]["best_level"] = mlvl
                    dDict[dung]["best_result"] = result
                elif affix == "Tyrannical" and dDict[dung]["alt_score"] == 0:
                    dDict[dung]["alt_score"] = score
                    dDict[dung]["alt_level"] = mlvl
                    dDict[dung]["alt_result"] = result

            for run in rioAlts["mythic_plus_alternate_runs"]:
                affix = run["affixes"][0]["name"]
                dung = run["short_name"]
                mlvl = run["mythic_level"]
                result = run["num_keystone_upgrades"]
                score = run["score"]
                if affix == "Fortified" and dDict[dung]["best_score"] == 0:
                    dDict[dung]["best_score"] = score
                    dDict[dung]["best_level"] = mlvl
                    dDict[dung]["best_result"] = result
                elif affix == "Tyrannical" and dDict[dung]["alt_score"] == 0:
                    ## Only recording alternate run scores here
                    dDict[dung]["alt_score"] = score
                    dDict[dung]["alt_level"] = mlvl
                    dDict[dung]["alt_result"] = result

            results.append((player, dDict))

        # print(results)

        msg = "**Best FORTIFIED Runs**\n"
        # Modified header for 9.2
        msg += f"```{'Player'.ljust(13)}"
        for i in range(len(mplusdungeons)):
            msg += f" {mplusdungeons[i][:4].ljust(4)}"
        msg += "\n"

        for player in results:
            playerName = player[0]
            dDict = player[1]
            # print(player[0])

            msg += f"{playerName.ljust(13)}"

            for i in range(len(mplusdungeons)):
                fortResult = (
                    dDict[mplusdungeons[i]]["best_level"]
                    if dDict[mplusdungeons[i]]["best_score"] > 0
                    else 0
                )
                tyrResult = (
                    dDict[mplusdungeons[i]]["alt_level"]
                    if dDict[mplusdungeons[i]]["alt_score"] > 0
                    else 0
                )
                affix = (
                    ";"
                    if dDict[mplusdungeons[i]]["best_result"] == 3
                    else ":"
                    if dDict[mplusdungeons[i]]["best_result"] == 2
                    else "."
                    if dDict[mplusdungeons[i]]["best_result"] == 1
                    else " "
                )

                msg += f" {fortResult:>2}{affix}|"
            msg += "\n"

        msg += "```\n"
        msg += "*All dungeons shown are Fortified, and only show positive values if the score>0 for the run. (Results ;=3 key  :=2 key  .=1 key)*"

        await ctx.send(msg)
        await msgId.delete()

    @commands.command(aliases=["brt"])
    async def bestrunst(self, ctx):
        """ Reports current Mythic Plus dungeon scores and rankings """

        msgId = await ctx.send("Gathering BRT data, please wait...")
        playersList = wowapi.getMythicPlusPlayers()
        results = []
        for playerRow in playersList:
            realm = playerRow[2]
            player = playerRow[1].title()
            # print(f"Retrieving {player} {realm}")
            rioBest = wowapi.api_raiderio_char_mplus_best_runs(player, realm)
            rioAlts = wowapi.api_raiderio_char_mplus_alternate_runs(player, realm)
            dDict = {}
            for i in range(len(mplusdungeons)):
                # print(f"{i} - {mplusdungeons[i]}")
                dDict[mplusdungeons[i]] = {
                    "shortname": mplusdungeons[i],
                    "best_level": 0,
                    "best_result": 0,
                    "best_score": 0,
                    "alt_level": 0,
                    "alt_result": 0,
                    "alt_score": 0,
                }

            for run in rioBest["mythic_plus_best_runs"]:
                affix = run["affixes"][0]["name"]
                dung = run["short_name"]
                mlvl = run["mythic_level"]
                result = run["num_keystone_upgrades"]
                score = run["score"]

                if affix == "Fortified" and dDict[dung]["best_score"] == 0:
                    dDict[dung]["best_score"] = score
                    dDict[dung]["best_level"] = mlvl
                    dDict[dung]["best_result"] = result
                elif affix == "Tyrannical" and dDict[dung]["alt_score"] == 0:
                    dDict[dung]["alt_score"] = score
                    dDict[dung]["alt_level"] = mlvl
                    dDict[dung]["alt_result"] = result

            for run in rioAlts["mythic_plus_alternate_runs"]:
                affix = run["affixes"][0]["name"]
                dung = run["short_name"]
                mlvl = run["mythic_level"]
                result = run["num_keystone_upgrades"]
                score = run["score"]
                if affix == "Fortified" and dDict[dung]["best_score"] == 0:
                    dDict[dung]["best_score"] = score
                    dDict[dung]["best_level"] = mlvl
                    dDict[dung]["best_result"] = result
                elif affix == "Tyrannical" and dDict[dung]["alt_score"] == 0:
                    ## Only recording alternate run scores here
                    dDict[dung]["alt_score"] = score
                    dDict[dung]["alt_level"] = mlvl
                    dDict[dung]["alt_result"] = result

            results.append((player, dDict))

        # print(results)

        msg = "**Best TYRANNICAL Runs**\n"

        msg += f"```{'Player'.ljust(13)}"
        for i in range(len(mplusdungeons)):
            msg += f" {mplusdungeons[i][:4].ljust(4)}"
        msg += "\n"

        for player in results:
            playerName = player[0]
            dDict = player[1]
            # print(player[0])

            msg += f"{playerName.ljust(13)}"

            for i in range(len(mplusdungeons)):
                fortResult = (
                    dDict[mplusdungeons[i]]["best_level"]
                    if dDict[mplusdungeons[i]]["best_score"] > 0
                    else 0
                )
                tyrResult = (
                    dDict[mplusdungeons[i]]["alt_level"]
                    if dDict[mplusdungeons[i]]["alt_score"] > 0
                    else 0
                )
                affix = (
                    ";"
                    if dDict[mplusdungeons[i]]["best_result"] == 3
                    else ":"
                    if dDict[mplusdungeons[i]]["best_result"] == 2
                    else "."
                    if dDict[mplusdungeons[i]]["best_result"] == 1
                    else " "
                )

                msg += f" {tyrResult:>2}{affix}|"
            msg += "\n"

        msg += "```\n"
        msg += "*All dungeons shown are Tyrannical, and only show positive values if the score>0 for the run. (Results ;=3 key  :=2 key  .=1 key)*"

        await ctx.send(msg)
        await msgId.delete()

    ###################################################################
    ###################################################################
    ##                                                               ##
    ##                       BACKGROUND TASKS                        ##
    ##                                                               ##
    ###################################################################
    ###################################################################

    @tasks.loop(hours=1)
    async def updateMythicPlusDataBG(self):
        print("MythicPlus:updateMythicPlusDataBG process")
        if DEVMODE == False:
            # bot-logs channel 799290844862480445
            botLogs = self.client.get_channel(799290844862480445)
        if DEVMODE == True:
            botLogs = self.client.get_channel(790667200197296138)
        await botLogs.send(f"UpdateMythicPlusDataBG: {botlib.localNow()}")
        updates = wowapi.updateMythicPlusScores()
        if len(updates) > 0:
            for rec in updates:
                await self.announceUpdate(rec)
                await self.hiddenAnnouncedScoreUpdate(rec["name"])


def setup(client):
    client.add_cog(MythicPlus(client))
