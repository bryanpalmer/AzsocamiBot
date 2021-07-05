# AzsocamiBot
Custom Discord bot for Azsocami guild on Silver Hand.  Bot maintains list of current guild team mains for raid, as well as alts and/or non-raiding members.  Primary functions are to easily grab current AH pricing for common mats, as well as track seasonal mythic+ progression for members wanting to complete achievement requirements.

## Current Commands

**Command** | **Description**
----------- | ---------------
.mats | Gather current auction house data for commonly used mats
.br | Best mythic run for current season for all non-alt team members
.br4 \<playername> | Best timed and untimed runs of all dungeons for \<playername>
.team | Gather current wow info for all team members
.lpc [_plate \| mail \| leather \| cloth_] | Gets current pricing and availability for rank 1-4 of legendary base items.
.tc | Current twisting corridors achievement for team
.clean | Cleans up AzsocamiBot commands and messages from channel
.cleanbot | Same as .clean, but also works on several other bots in channel
.status | Gives current version and status info, as well as github link for source
.add_member \<playername> [\<realm>] | Adds player (default SilverHand realm) to team roster
.change_member_role \<playername> | Change member role to **T**ank, **H**ealer, **M**elee DPS, **R**anged DPS, or **A**lt
.add_item \<itemID> | Add \<itemID> to list of mats to check AH pricing on for **_mats_** command.
.remove_item \<itemID> | Removes \<itemID> from list of items to check for in AH during **_mats_** command.


