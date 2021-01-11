# wowclasses
import json


class Item:
    def __init__(self, itemRec):
        if itemRec != None:
            self.id = itemRec[0]
            self.name = itemRec[1]
            self.quality = itemRec[2]
            self.level = itemRec[3]
            self.classname = self.getClassName(itemRec[4])
            self.subclass = itemRec[5]
            self.icon = itemRec[6]
            self.stacksize = itemRec[7]
            self.buyfromvendor = itemRec[8]

    def getClassName(self, classId):
        item_classes = {
            0: "Consumable",
            1: "Container",
            2: "Weapon",
            3: "Gem",
            4: "Armor",
            5: "Reagent",
            6: "Projectile",
            7: "Tradeskill",
            8: "Item Enhancement",
            9: "Recipe",
            11: "Quiver",
            12: "Quest",
            13: "Key",
            15: "Miscellaneous",
            16: "Glyph",
            17: "Battle Pets",
            18: "WoW Token",
        }
        return item_classes[classId]


class Character:
    def __init__(self, charJson):
        # see character.json in devstuff
        self.wowid = charJson["id"]
        self.name = charJson["name"]
        self.gender = charJson["gender"]["name"]
        self.faction = charJson["faction"]["name"]
        self.race = charJson["race"]["name"]
        self.classname = charJson["character_class"]["name"]
        self.active_spec = charJson["active_spec"]["name"]
        self.realmname = charJson["realm"]["name"]
        self.realmslug = charJson["realm"]["slug"]
        self.realmid = charJson["realm"]["id"]
        self.guild = charJson["guild"]["name"]
        self.level = charJson["level"]
        self.ilvl = charJson["equipped_item_level"]
        self.covenant = charJson["covenant_progress"]["chosen_covenant"]["name"]
        # self.covenant_renown = charJson['covenant_progress']['renown_level']


class CharacterEquipment:
    def __init__(self, charJson):
        """Init Character class with wowapi JSON."""
        # print(json.dumps(charJson, indent=4))

        self.id = charJson["character"]["id"]
        self.name = charJson["character"]["name"]
        self.realm = {
            "name": charJson["character"]["realm"]["name"],
            "slug": charJson["character"]["realm"]["slug"],
            "id": charJson["character"]["realm"]["id"],
        }
        self.equipped_items = []
        for item in charJson["equipped_items"]:
            self.equipped_items.append(
                EquippedItem(
                    item["item"]["id"],
                    item["slot"]["name"],
                    item["name"],
                    item["level"]["value"],
                    "FakeId"
                    # item["transmog"]["item"]["id"],
                )
                # {
                #     "id": item["item"]["id"],
                #     "slot": item["slot"]["name"],
                #     "name": item["name"],
                #     "level": item["level"]["value"],
                #     "transmogid": item["transmog"]["item"]["id"],
                # }
            )


class EquippedItem:
    def __init__(self, itemId, slot, name, level, transmogid):
        self.id = itemId
        self.slot = slot
        self.name = name
        self.level = level
        self.transmogid = transmogid
