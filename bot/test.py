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
import umj

armors = wowapi.getLegendaryArmorsList()
umjConn = umj.create_connection()
for armorId in armors:
    curId = armors[armorId]["id"]
    print(f"Looking up armorId {armorId}")
    item = umj.getItemById(umjConn, curId)
    armors[armorId]["name"] = item.name
    armors[armorId]["classname"] = item.classname
    armors[armorId]["subclass"] = item.subclass
    # print(vars(item))
# print(armors)
umjConn.close()

print(armors)