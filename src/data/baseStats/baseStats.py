import csv

def makeBaseStatDict():
  with open('src\data\\baseStats\scraping\gen1.csv', encoding='utf-8') as gen1, open('src\data\\baseStats\scraping\gen5.csv', encoding='utf-8') as gen5, open('src\data\\baseStats\scraping\gen6.csv', encoding='utf-8') as gen6, open('src\data\\baseStats\scraping\gen7.csv', encoding='utf-8') as gen7, open('src\data\\baseStats\scraping\gen8.csv', encoding='utf-8') as gen8:
    gen1Reader, gen5Reader, gen6Reader, gen7Reader, gen8Reader = csv.DictReader(gen1), csv.DictReader(gen5), csv.DictReader(gen6), csv.DictReader(gen7), csv.DictReader(gen8)

    patchDict = {}

    readerList = [gen1Reader, gen5Reader, gen6Reader, gen7Reader, gen8Reader]
    gen = [1, 5, 6, 7, 8]

    i = 0

    for reader in readerList:
      print(gen[i])
      for row in reader:
        # If Pokemon is new, add it to patchDict
        if row["Pokemon"] not in patchDict.keys():
          patchDict[row["Pokemon"]] = {
            "Dex Number": row["Dex Number"],
            "HP": [[row["HP"], gen[i]]],
            "Attack": [[row["Attack"], gen[i]]],
            "Defense": [[row["Defense"], gen[i]]],
            "Sp. Attack": [[row["Sp. Attack"], gen[i]]],
            "Sp. Defense": [[row["Sp. Defense"], gen[i]]],
            "Speed": [[row["Speed"], gen[i]]]
          }
        # If Pokemon is old, check for changes in its stats
        else:
          for key, value in patchDict[row["Pokemon"]].items():
            # If change is found, add that to the patch log
            if key == "Dex Number":
              continue
            if value[-1][0] != row[key]:
              value.append([row[key], gen[i]])
              patchDict[row["Pokemon"]][key] = value
      i += 1

    print(patchDict["Butterfree"])
  return patchDict
    

makeBaseStatDict()