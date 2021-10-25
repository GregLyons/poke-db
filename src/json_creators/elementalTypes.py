import csv
from utils import parseName, genSymbolToNumber, getDataPath, genSymbolToNumber, typeList

def makeTypeDict(fnamePrefix):
  typeDict = {}

  # add damage_to type matchups, i.e. typeDict["fire"]["damage_to"] is a dictionary consisting of the multipliers fire has as an attacking type against all the other types
  with open(fnamePrefix + '1.csv', 'r', encoding='utf-8') as gen1CSV, open(fnamePrefix + '2.csv', 'r', encoding='utf-8') as gen2CSV, open(fnamePrefix + '6.csv', 'r', encoding='utf-8') as gen6CSV:
    gens = [1, 2, 6]
    genCounter = 0
    for csvFile in [gen1CSV, gen2CSV, gen6CSV]:
      reader = csv.DictReader(csvFile)
      for row in reader:
        attackingType = row["Attacking Type"]

        if attackingType not in typeDict:
          typeDict[attackingType] = {
            "gen": gens[genCounter],
            # dictionaries keeping track of type matchups
            "damage_to": {},
            "damage_from": {},
          }

        del row["Attacking Type"]
        # remaining keys in the dict, row, are types
        for defendingType in row.keys():
          if defendingType not in typeDict:
            typeDict[defendingType] = {
              "gen": gens[genCounter],
              "damage_to": {},
              "damage_from": {},
            }

          # if defendingType isn't already in attackingType's damage_to dictionary, add it
          if defendingType not in typeDict[attackingType]["damage_to"]:
            typeDict[attackingType]["damage_to"][defendingType] = [[row[defendingType], gens[genCounter]]]
          # otherwise, see if the multiplier has changed
          else: 
            # if multiplier has changed, add the change
            if typeDict[attackingType]["damage_to"][defendingType][-1][0] != row[defendingType]:
              typeDict[attackingType]["damage_to"][defendingType].append([row[defendingType], gens[genCounter]])
            # otherwise, continue to next defendingType
          
          # similar process, but for "damage_from" relations
          if attackingType not in typeDict[defendingType]["damage_from"]:
            typeDict[defendingType]["damage_from"][attackingType] = [[row[defendingType], gens[genCounter]]]
          else:
            if typeDict[defendingType]["damage_from"][attackingType][-1][0] != row[defendingType]:
              typeDict[defendingType]["damage_from"][attackingType].append([row[defendingType], gens[genCounter]])

      genCounter += 1

  return typeDict

def main():
  dataPath = getDataPath() + 'types\\'
  fnamePrefix = dataPath + 'typeMatchupsGen'
  typeDict = makeTypeDict(fnamePrefix)

  return typeDict

if __name__ == '__main__':
  typeDict = main()

  print('Checking consistency of names...')

  for type in typeDict.keys():
    if type not in typeList():
      print('Inconsistent main key', type)
    for defendingType in typeDict[type]["damage_to"]:
      if defendingType not in typeList():
        print('Inconsistent defending type', defendingType, 'for main key', type)
    for attackingType in typeDict[type]["damage_from"]:
      if defendingType not in typeList():
        print('Inconsistent attacking type', attackingType, 'for main key', type)

  print('Finished.')