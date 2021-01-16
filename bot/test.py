from os.path import join, dirname, os
from dotenv import load_dotenv
import os

dotenv_path = join(dirname(__file__), "../.env")
print(join(dirname(__file__)))
load_dotenv(
    dotenv_path,
    verbose=True,
)

# import wowapi
import umj

# import wowclasses

# DB_HOST = os.getenv("DB_HOST")
# DB_USER = os.getenv("DB_USER")
# DB_PASS = os.getenv("DB_PASS")
# DB_NAME = os.getenv("DB_NAME")
# DB_PORT = 3306
# BNET_CLIENTID = os.getenv("BATTLENET_CLIENT_ID")
# BNET_SECRET = os.getenv("BATTLENET_CLIENT_SECRET")

# print(wowapi.getAllTableRows("config"))
# print(wowapi.getTableStructure("config"))

matList = [
    (169701, "Death Blossom"),
    (168583, "Widowbloom"),
    (168586, "Rising Glory"),
    (168589, "Marrowroot"),
    (170554, "Vigil's Torch"),
    (171315, "Nightshade"),
    (180457, "Shadestone"),
    (171841, "Shaded Stone"),
    (173204, "Lightless Silk"),
    (172089, "Desolate Leather"),
    (172094, "Callous Hide"),
    (172096, "Heavy Desolate Leather"),
    (172097, "Heavy Callous Hide"),
    (172053, "Tenebrous Ribs"),
    (172055, "Phantasmal Haunch"),
    (173034, "Silvergill Pike"),
    (173036, "Spinefin Piranha"),
    (173037, "Elysian Thade"),
    (171267, "Spiritual Healing Potion"),
    (171270, "Potion of Spectral Agility"),
    (171273, "Potion of Spectral Intellect"),
    (171275, "Potion of Spectral Strength"),
    (171276, "Spectral Flask of Power"),
    (171284, "Eternal Cauldron"),
    (172043, "Feast of Gluttonous Hedonism"),
    (172347, "Heavy Desolate Armor Kit"),
    (171437, "Shaded Sharpening Stone"),
    (171439, "Shaded Weightstone"),
    (181468, "Veiled Augment Rune"),
]

items = umj.getItemsListById(matList)

for item in items:
    print(vars(item))
