import wowapi

import datetime
import pytz


lastReset = wowapi.getLastResetDateTime()

# fin1 = "2021-01-25T03:58:27.000Z"
# fin2 = "2021-01-25T03:58:27.000+00:00"

# print(parser.isoparse(fin1))
# print(datetime.datetime.fromisoformat(fin2))

keysRun = []
runsData = wowapi.api_raiderio_char_mplus_recent_runs("aaryn", "silver-hand")
for run in runsData["mythic_plus_recent_runs"]:
    keyLvl = run["mythic_level"]
    rt = datetime.datetime.fromisoformat(run["completed_at"].replace("Z", "+00:00"))
    if rt > lastReset:
        # print(f"{rt} comes after {lastReset}")
        keysRun.append(keyLvl)
#    else:
# print(f"{rt} comes before {lastReset}")

keysRun.sort(reverse=True)

for key in keysRun:
    print(key)

print("All done.")