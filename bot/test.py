import botlib

longStr = """Eternal Cauldron: None Available
Feast of Gluttonous Hedonism: 55 - 4875.0g
Heavy Desolate Armor Kit: 121 - 379.82g
Potion of Spectral Agility: 388 - 169.0g
Potion of Spectral Intellect: 622 - 200.0g
Potion of Spectral Strength: 79 - 210.75g
Potion of the Hidden Spirit: 183 - 260.88g
Spectral Flask of Power: 394 - 787.87g
Spiritual Healing Potion: 1379 - 30.99g
Vantus Rune: Castle Nathria: 24 - 3757.96g
Veiled Augment Rune: 674 - 600.0g"""

res = botlib.str2embedarray(longStr, maxlen=1024)

for line in res:
    print(len(line), line)
