from os.path import dirname, join, os
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), "../.env")
print("Env vars in:", dotenv_path)
load_dotenv(
    dotenv_path,
    verbose=True,
)

import wowapi

import datetime
import pytz


lastReset = wowapi.getLastResetDateTime()

# fin1 = "2021-01-25T03:58:27.000Z"
# fin2 = "2021-01-25T03:58:27.000+00:00"

# print(parser.isoparse(fin1))
# print(datetime.datetime.fromisoformat(fin2))

keysRun = []
runsData = wowapi.getCharacterSeasonDetails("aaryn", "silver-hand", 5)
for run in runsData["best_runs"]:
    if run["is_completed_within_time"] == True:
        print(f"{run['dungeon']['name']} - {run['keystone_level']} - ")


# for run in runsData["mythic_plus_recent_runs"]:
#     keyLvl = run["mythic_level"]
#     rt = datetime.datetime.fromisoformat(run["completed_at"].replace("Z", "+00:00"))
#     if rt > lastReset:
#         # print(f"{rt} comes after {lastReset}")
#         keysRun.append(keyLvl)
# #    else:
# # print(f"{rt} comes before {lastReset}")

# keysRun.sort(reverse=True)

# for key in keysRun:
#     print(key)

print("All done.")