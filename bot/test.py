from os.path import join, dirname, os
from dotenv import load_dotenv
import os

dotenv_path = join(dirname(__file__), "../.env")
print(join(dirname(__file__)))
load_dotenv(
    dotenv_path,
    verbose=True,
)

import wowapi
import wowclasses

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")
DB_PORT = 3306
BNET_CLIENTID = os.getenv("BATTLENET_CLIENT_ID")
BNET_SECRET = os.getenv("BATTLENET_CLIENT_SECRET")

# print(wowapi.getAllTableRows("config"))
# print(wowapi.getTableStructure("config"))

wowapi.initDTCacheTable()

print(wowapi.getAllTableRows("dtcache"))
