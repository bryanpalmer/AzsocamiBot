from os.path import dirname, join, os
from dotenv import load_dotenv
import json

dotenv_path = join(dirname(__file__), "../.env")
print("Env vars in:", dotenv_path)
load_dotenv(
    dotenv_path,
    verbose=True,
)

import wowapi
from operator import itemgetter


charData = wowapi.getCharacterAchievements("Aaryn", "silver-hand")
# data = json.dumps(charData, indent=4)

# with open("achieves.txt", "w") as outfile:
#     json.dump(charData, outfile)

highestCompleted = 0
completed = [(0, "None")]
for item in charData["achievements"]:
    if item["id"] in (14468, 14469, 14470, 14471, 14472, 14568, 14569, 14570):
        if item["id"] > highestCompleted:
            highestCompleted = item["id"]
            completed.append((item["id"], item["achievement"]["name"]))

# print(f"{item['id']} - {item['achievement']['name']}")

HighestFinished = max(completed, key=itemgetter(1))[1]
