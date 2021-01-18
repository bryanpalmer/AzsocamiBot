from os.path import join, dirname, os
from dotenv import load_dotenv
import os
import json


dotenv_path = join(dirname(__file__), "../.env")
print("Env vars in:", dotenv_path)
load_dotenv(
    dotenv_path,
    verbose=True,
)

import wowapi


ahdata = wowapi.getAuctionHouseData()

with open("ahdata.json", "w") as outfile:
    json.dump(ahdata, outfile)
