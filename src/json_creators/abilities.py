import csv
import re
import os
from utils import getBulbapediaDataPath, genSymbolToNumber

# for the dictionary-valued entries in abilityDict (with key outerKeyName), add a key (innerKeyName) with a default value, for every entry in abilityDict
def initializeKeyValue(abilityDict, outerKeyName, innerKeyName, defaultValue):
  for key in abilityDict.keys():
    if not isinstance(defaultValue, list):
      defaultValue = [defaultValue]

    abilityDict[key][outerKeyName][innerKeyName] = [defaultValue + [abilityDict[key]["gen"]]]
  return

# initialize abilityDict with name, description, and gen; key is Ability ID
def makeInitialAbilityDict(fname):
  with open(fname, 'r', encoding='utf-8') as abilityListCSV:
    reader = csv.DictReader(abilityListCSV)
    abilityDict = {}
    for row in reader:
      abilityID, abilityName, description, gen = int(row["Ability ID"]), row["Ability Name"].replace('*', ''), row["Description"], row["Gen"]
      abilityDict[abilityID] = {
        "name": abilityName,
        "description": description,
        "gen": genSymbolToNumber(gen),
        "effects": {},
        "causes_status": {},
        "resists_status": {},
        "boosts_type": {},
        "resists_type": {},
        "boosts_usage_method": {},
        "resists_usage_method": {},
        "stat_modifications": {},
      }

  return abilityDict

# def 
def makeInverseDict(fname):
  inverseDict = {}

  with open(fname, encoding='utf-8') as abilitiesCSV:
    reader = csv.DictReader(abilitiesCSV)
    for row in reader:
      inverseDict[row["Ability Name"]] = int(row["Ability ID"])

  return inverseDict

# 
def addEffectData(fpath, abilityDict, inverseDict):
  # general effect headers for abilities
  with open(fpath + 'abilitiesByEffect.csv', 'r', encoding='utf-8') as effectCSV:
    reader = csv.DictReader(effectCSV)
    for row in reader:
      abilityName, effect = row["Ability Name"], row["Effect Type"]
      if effect not in abilityDict[1]["effects"]:
        initializeKeyValue(abilityDict, "effects", effect, False)
      
      abilityKey = inverseDict[abilityName]
      gen = abilityDict[abilityKey]["gen"]
      abilityDict[abilityKey]["effects"][effect] = [[True, gen]]

    # hard-code exceptions
    # lightning_rod
    lightningRodKey = inverseDict["lightning_rod"]
    abilityDict[lightningRodKey]["effects"]["resists_type"] = [[False, 3], [True, 5]]

    # storm_drain
    stormDrainKey = inverseDict["storm_drain"]
    abilityDict[stormDrainKey]["effects"]["resists_type"] = [[False, 4], [True, 5]]

  # abilities which can cause status--mainly through contact
  with open(fpath + 'abilitiesContactCausesStatus.csv', 'r', encoding='utf-8') as contactStatusCSV:
    reader = csv.DictReader(contactStatusCSV)
    for row in reader:
      abilityName, status, probability = row["Ability Name"], row["Status"], float(row["Probability"])
      if status not in abilityDict[1]["causes_status"]:
        initializeKeyValue(abilityDict, "causes_status", status, 0.0)

      abilityKey = inverseDict[abilityName]
      gen = abilityDict[abilityKey]["gen"]
      abilityDict[abilityKey]["causes_status"][status] = [[probability, gen]]

      # hardcode exceptions
      # poison_touch
      poisonTouchKey = inverseDict["poison_touch"]
      abilityDict[poisonTouchKey]["causes_status"]["poison"] = [[30.0, gen]]

      # synchronize
      synchronizeKey = inverseDict["synchronize"]
      abilityDict[synchronizeKey]["causes_status"]["burn"] = [[100.0, 3]]
      abilityDict[synchronizeKey]["causes_status"]["poison"] = [[100.0, 3]]
      # only inflicts bad_poison from gen 5 onward
      abilityDict[synchronizeKey]["causes_status"]["bad_poison"] = [[0.0, 3], [100.0, 5]]
      abilityDict[synchronizeKey]["causes_status"]["paralysis"] = [[100.0, 3]]

  # abilities which protect against status
  with open(fpath + 'abilitiesProtectAgainstStatus.csv', 'r', encoding='utf-8') as boostMoveClassCSV:
    reader = csv.DictReader(boostMoveClassCSV)
    for row in reader:
      abilityName, status = row["Ability Name"], row["Status Name"]
      if status not in abilityDict[1]["resists_status"] and status != 'non_volatile':
        initializeKeyValue(abilityDict, "resists_status", status, False)
      
      abilityKey = inverseDict[abilityName]
      gen = abilityDict[abilityKey]["gen"]
      abilityDict[abilityKey]["resists_status"][status] = [[True, gen]]
    
    # hardcode abilities which protect against non_volatile status
    for abilityName in ['flower_veil', 'sweet_veil']:
      for status in ['poison', 'bad_poison', 'burn', 'paralysis', 'freeze', 'sleep']:
        abilityKey = inverseDict[abilityName]
        gen = abilityDict[abilityKey]["gen"]
        abilityDict[abilityKey]["resists_status"][status] = [[True, gen]]

    # hardcode exceptions
    exceptions = [
      ['sleep', ['early_bird']],
      ['burn', ['water bubble']],
      ['poison', ['pastel_veil', 'poison_heal']]
    ]

    for exception in exceptions:
      status = exception[0]
      abilities = exception[1]
      for abilityName in abilities:
        abilityKey = inverseDict[abilityName]
        gen = abilityDict[abilityKey]["gen"]
        abilityDict[abilityKey]["resists_status"][status] = [[True, gen]]

  # abilities which boost types and usage methods
  with open(fpath + 'abilitiesBoostMoveClass.csv', 'r', encoding='utf-8') as boostMoveClassCSV:
    reader = csv.DictReader(boostMoveClassCSV)
    for row in reader:
      abilityName, boosts, multiplier, moveClass = row["Ability Name"], row["Boosts"], row["Multiplier"], row["Move Class"]
      if moveClass == 'method':
        abilityKey = inverseDict[abilityName]
        gen = abilityDict[abilityKey]["gen"]

        abilityDict[abilityKey]["boosts_usage_method"][boosts] = [[boosts, multiplier, gen]]
      elif moveClass == 'type':
        abilityKey = inverseDict[abilityName]
        gen = abilityDict[abilityKey]["gen"]

        abilityDict[abilityKey]["boosts_type"][boosts] = [[boosts, multiplier, gen]]

  # abilities which resist types and usage methods
  with open(fpath + 'abilitiesResistMoveClass.csv', 'r', encoding='utf-8') as resistMoveClassCSV:
    reader = csv.DictReader(resistMoveClassCSV)
    for row in reader:
      abilityName, boosts, multiplier, moveClass = row["Ability Name"], row["Boosts"], row["Multiplier"], row["Move Class"]
      if moveClass == 'method':
        abilityKey = inverseDict[abilityName]
        gen = abilityDict[abilityKey]["gen"]

        abilityDict[abilityKey]["boosts_usage_method"][boosts] = [[boosts, multiplier, gen]]
      elif moveClass == 'type':
        abilityKey = inverseDict[abilityName]
        gen = abilityDict[abilityKey]["gen"]

        abilityDict[abilityKey]["boosts_type"][boosts] = [[boosts, multiplier, gen]]

  # abilities which modify stats
  with open(fpath + 'abilitiesBoostStat.csv', 'r', encoding='utf-8') as resistMoveClassCSV:
    reader = csv.DictReader(resistMoveClassCSV)
    for row in reader:
      abilityName, boosts, multiplier, moveClass = row["Ability Name"], row["Boosts"], row["Multiplier"], row["Move Class"]
      if moveClass == 'method':
        abilityKey = inverseDict[abilityName]
        gen = abilityDict[abilityKey]["gen"]

        abilityDict[abilityKey]["boosts_usage_method"][boosts] = [[boosts, multiplier, gen]]
      elif moveClass == 'type':
        abilityKey = inverseDict[abilityName]
        gen = abilityDict[abilityKey]["gen"]

        abilityDict[abilityKey]["boosts_type"][boosts] = [[boosts, multiplier, gen]]
  return

def main():
  dataPath = getBulbapediaDataPath() + '\\abilities\\'
  fname = dataPath + 'abilityList.csv'
  abilityDict = makeInitialAbilityDict(fname)
  inverseDict = makeInverseDict(fname)

  addEffectData(dataPath, abilityDict, inverseDict)

  return

  

if __name__ == '__main__':
  main()