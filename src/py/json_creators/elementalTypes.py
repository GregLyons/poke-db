import csv
from utils import getCSVDataPath, checkConsistency, fieldStateList

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
            typeDict[attackingType]["damage_to"][defendingType] = [[float(row[defendingType]), gens[genCounter]]]
          # otherwise, see if the multiplier has changed
          else: 
            # if multiplier has changed, add the change
            if typeDict[attackingType]["damage_to"][defendingType][-1][0] != float(row[defendingType]):
              typeDict[attackingType]["damage_to"][defendingType].append([float(row[defendingType]), gens[genCounter]])
            # otherwise, continue to next defendingType
          
          # similar process, but for "damage_from" relations
          if attackingType not in typeDict[defendingType]["damage_from"]:
            typeDict[defendingType]["damage_from"][attackingType] = [[float(row[defendingType]), gens[genCounter]]]
          else:
            if typeDict[defendingType]["damage_from"][attackingType][-1][0] != float(row[defendingType]):
              typeDict[defendingType]["damage_from"][attackingType].append([float(row[defendingType]), gens[genCounter]])

      genCounter += 1

  return typeDict

def addFormattedName(typeDict):
  for typeName in typeDict.keys():
    typeDict[typeName]['formatted_name'] = typeName.title()

  return

def addFieldStateData(typeDict):
  for typeName in typeDict:
    typeDict[typeName]["resists_field_state"] = {}
    typeDict[typeName]["removes_field_state"] = {}
    typeDict[typeName]["ignores_field_state"] = {}

  # G-Max 
  typeDict["grass"]["resists_field_state"]["vine_lash"] = [[True, 8]]
  typeDict["fire"]["resists_field_state"]["wildfire"] = [[True, 8]]
  typeDict["water"]["resists_field_state"]["cannonade"] = [[True, 8]]
  typeDict["rock"]["resists_field_state"]["volcalith"] = [[True, 8]]

  # Pledges
  typeDict["fire"]["resists_field_state"]["sea_of_fire"] = [[True, 5]]

  # Weather
  typeDict["rock"]["resists_field_state"]["sandstorm"] = [[0.0, 2]]
  typeDict["ground"]["resists_field_state"]["sandstorm"] = [[0.0, 2]]
  typeDict["steel"]["resists_field_state"]["sandstorm"] = [[0.0, 2]]

  typeDict["ice"]["resists_field_state"]["hail"] = [[0.0, 3]]

  # Hazards
  #region

  typeDict["flying"]["resists_field_state"]["spikes"] = [[0.0, 2]]
  typeDict["flying"]["ignores_field_state"]["toxic_spikes"] = [[True, 4]]
  typeDict["flying"]["ignores_field_state"]["sticky_web"] = [[True, 6]]

  typeDict["poison"]["removes_field_state"]["toxic_spikes"] = [[True, 4]]

  # Hazards whose damage depends on type-matchup
  for [typeName, fieldStateAndGen] in [
    ['rock', [
        ['stealth_rock', 4]
      ]
    ],
    ['steel', [
        ['sharp_steel', 8]
      ]
    ]
  ]: 
    for [fieldStateName, fieldStateGen] in fieldStateAndGen:
      for attackingTypeName in typeDict[typeName]["damage_to"].keys():
        typeDict[attackingTypeName]["resists_field_state"][fieldStateName] = []

        for patch in typeDict[typeName]["damage_to"][attackingTypeName]:
          [multiplier, patchGen] = patch

          typeDict[attackingTypeName]["resists_field_state"][fieldStateName].append([multiplier, max(patchGen, fieldStateGen)])

  #endregion

  # Terrains
  typeDict["flying"]["ignores_field_state"]["electric_terrain"] = [[0.0, 6]]
  typeDict["flying"]["ignores_field_state"]["grassy_terrain"] = [[0.0, 6]]
  typeDict["flying"]["ignores_field_state"]["misty_terrain"] = [[0.0, 6]]
  typeDict["flying"]["ignores_field_state"]["psychic_terrain"] = [[0.0, 6]]

  return

def main():
  dataPath = getCSVDataPath() + 'types\\'
  fnamePrefix = dataPath + 'typeMatchupsGen'
  typeDict = makeTypeDict(fnamePrefix)

  addFormattedName(typeDict)

  addFieldStateData(typeDict)

  return typeDict

if __name__ == '__main__':
  typeDict = main()
  
  # check consistency in itemDict
  print('Checking for inconsistencies...')
  for typeName in typeDict.keys():
    for inconsistency in [
      checkConsistency(typeDict[typeName]["damage_to"], 'type', typeDict, 0.0),
      checkConsistency(typeDict[typeName]["damage_from"], 'type', typeDict, 0.0),
    ]:
      if inconsistency:
        print(f'Inconsistency found for {typeName}: {inconsistency}')
    
    for fieldState in typeDict[typeName]["resists_field_state"]:
      if fieldState not in fieldStateList():
        print('Inconsistent field state name', typeName, fieldState)

    for fieldState in typeDict[typeName]["ignores_field_state"]:
      if fieldState not in fieldStateList():
        print('Inconsistent field state name', typeName, fieldState)

    for fieldState in typeDict[typeName]["removes_field_state"]:
      if fieldState not in fieldStateList():
        print('Inconsistent field state name', typeName, fieldState)
  print('Finished.')