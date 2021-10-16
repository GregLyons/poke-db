import csv

def makeBaseStatDict():
  with open('src\data\\baseStatsGen1.csv', encoding='utf-8') as gen1, open('src\data\\baseStatsGen5.csv', encoding='utf-8') as gen5, open('src\data\\baseStatsGen6.csv', encoding='utf-8') as gen6, open('src\data\\baseStatsGen7.csv', encoding='utf-8') as gen7, open('src\data\\baseStatsGen8.csv', encoding='utf-8') as gen8:
    gen1Reader, gen5Reader, gen6Reader, gen7Reader, gen8Reader = csv.DictReader(gen1), csv.DictReader(gen5), csv.DictReader(gen6), csv.DictReader(gen7), csv.DictReader(gen8)

    baseStatDict = {}

    readerList = [gen1Reader, gen5Reader, gen6Reader, gen7Reader, gen8Reader]

    # i keeps track of the generation in the array gen
    # note that there are no base stat changes between gen 2 and gen 5
    gen = [1, 5, 6, 7, 8]
    i = 0

    for reader in readerList:
      for row in reader:
        # If Pokemon is new, add it to patchDict
        if row["Pokemon"] not in baseStatDict.keys():
          baseStatDict[row["Pokemon"]] = {
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
          for key, value in baseStatDict[row["Pokemon"]].items():
            # If change is found, add that to the patch log
            if key == "Dex Number":
              continue
            if value[-1][0] != row[key]:
              value.append([row[key], gen[i]])
              baseStatDict[row["Pokemon"]][key] = value
      i += 1

    print(baseStatDict["Butterfree"])
  return baseStatDict
    
makeBaseStatDict()