import csv
from utils import getBulbapediaDataPath, genSymbolToNumber, effectList, statusList, usageMethodList, statList, typeList

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

  # initialize fields in abilityDict
  # initialize statuses
  # for status in statusList():
  #   # ability has a chance of causing a status--if it can't cause it, chance is 0
  #   initializeKeyValue(abilityDict, "causes_status", status, 0.0)
  #   # ability does not resist status
  #   initializeKeyValue(abilityDict, "resists_status", status, False)
  # # initialize effects
  # for effect in effectList():
  #   # ability has effect or it does not
  #   initializeKeyValue(abilityDict, "effects", effect, False)
  # # initialize usage methods
  # # for usageMethod in usageMethodList():
  # #   # ability multiplies damage of move of usageMethod by multiplier
  # #   initializeKeyValue(abilityDict, "boosts_usage_method", usageMethod, 1.0)
  # #   # ability multiplies damage taken from move of usageMethod by multiplier
  # #   initializeKeyValue(abilityDict, "resists_usage_method", usageMethod, 1.0)
  # for stat in statList():
  #   # ability changes stat by 0 stages--0 being an int indicates that multiplier is 1
  #   initializeKeyValue(abilityDict, "stat_modifications", stat, [0, 'user'])
  
  return abilityDict

# allows lookup of ability by abilityName, not just abilityID
def makeInverseDict(fname):
  inverseDict = {}

  with open(fname, encoding='utf-8') as abilitiesCSV:
    reader = csv.DictReader(abilitiesCSV)
    for row in reader:
      inverseDict[row["Ability Name"]] = int(row["Ability ID"])

  return inverseDict

# various data about abilities, e.g. stat modifications, interactions with types and usage methods, etc.
def addEffectData(fpath, abilityDict, inverseDict):
  # general effect headers for abilities
  with open(fpath + 'abilitiesByEffect.csv', 'r', encoding='utf-8') as effectCSV:
    reader = csv.DictReader(effectCSV)
    for row in reader:
      abilityName, effect = row["Ability Name"], row["Effect Type"]
      abilityKey = inverseDict[abilityName]
      gen = abilityDict[abilityKey]["gen"]

      # actually belongs in status
      if effect == 'trapped':
        abilityDict[abilityKey]["causes_status"]["trapped"] = [[True, gen]]
      # some effects in the abilitiesByEffect.csv do not match with effectList(), so we ignore them
      elif effect not in effectList():
        # print(abilityName, effect)
        continue
      else:
        if abilityName == 'disguise' and effect == 'costs_hp':
          gen = 8

        abilityDict[abilityKey]["effects"][effect] = [[True, gen]]

  # abilities which can cause status--mainly through contact
  with open(fpath + 'abilitiesContactCausesStatus.csv', 'r', encoding='utf-8') as contactStatusCSV:
    reader = csv.DictReader(contactStatusCSV)
    for row in reader:
      abilityName, status, probability = row["Ability Name"], row["Status"], float(row["Probability"])
      
      if status not in statusList():
        # print(abilityName, status)
        continue

      abilityKey = inverseDict[abilityName]
      gen = abilityDict[abilityKey]["gen"]
      abilityDict[abilityKey]["causes_status"][status] = [[probability, gen]]
      abilityDict[abilityKey]["effects"]["punishes_contact"] = [[True, gen]]

    # hardcode exceptions
    # poison_touch
    poisonTouchKey = inverseDict["poison_touch"]
    abilityDict[poisonTouchKey]["causes_status"]["poison"] = [[30.0, 5]]

    # synchronize
    synchronizeKey = inverseDict["synchronize"]
    abilityDict[synchronizeKey]["causes_status"]["burn"] = [[100.0, 3]]
    abilityDict[synchronizeKey]["causes_status"]["poison"] = [[100.0, 3]]
    # only inflicts bad_poison from gen 5 onward
    abilityDict[synchronizeKey]["causes_status"]["bad_poison"] = [[0.0, 3], [100.0, 5]]
    abilityDict[synchronizeKey]["causes_status"]["paralysis"] = [[100.0, 3]]

    # perish body
    perishBodyKey = inverseDict["perish_body"]
    abilityDict[perishBodyKey]["causes_status"]["perish_song"] = [[100.0, 8]]
    abilityDict[perishBodyKey]["effects"]["punishes_contact"] = [[True, 8]]

    # scrappy
    scrappyKey = inverseDict["scrappy"]
    abilityDict[scrappyKey]["causes_status"]["identified"] = [[100.0, 4]]

    # stench
    stenchKey = inverseDict["stench"]
    abilityDict[stenchKey]["causes_status"]["flinch"] = [[10.0, 5]]

    # sturdy
    sturdyKey = inverseDict["sturdy"]
    abilityDict[sturdyKey]["causes_status"]["bracing"] = [[100.0, 3]]

    # truant
    truantKey = inverseDict["truant"]
    abilityDict[truantKey]["causes_status"]["recharging"] = [[100.0, 3]]

    # more abilities which punish contact not handled above
    for abilityName in ['aftermath', 'gooey', 'mummy', 'iron_barbs', 'rough_skin', 'tangling_hair', 'wandering_spirit', 'pickpocket']:
      abilityDict[abilityKey]["effects"]["punishes_contact"] = [[True, gen]]

  # abilities which protect against status
  with open(fpath + 'abilitiesProtectAgainstStatus.csv', 'r', encoding='utf-8') as boostMoveClassCSV:
    reader = csv.DictReader(boostMoveClassCSV)
    for row in reader:
      abilityName, status = row["Ability Name"], row["Status Name"]

      if status == 'non_volatile' or status not in statusList():
        continue
      
      abilityKey = inverseDict[abilityName]
      gen = abilityDict[abilityKey]["gen"]
      abilityDict[abilityKey]["resists_status"][status] = [[True, gen]]
    
    # hardcode abilities which protect against non_volatile status
    for abilityName in ['flower_veil', 'sweet_veil', 'natural_cure', 'shed_skin', 'hydration', 'comatose']:
      for status in ['poison', 'bad_poison', 'burn', 'paralysis', 'freeze', 'sleep']:
        abilityKey = inverseDict[abilityName]
        gen = abilityDict[abilityKey]["gen"]
        abilityDict[abilityKey]["resists_status"][status] = [[True, gen]]

    # hardcode exceptions
    for exception in [
      ['sleep', ['early_bird']],
      ['burn', ['water_bubble']],
      ['poison', ['pastel_veil', 'poison_heal']],
      ['trapped', ['shadow_tag']]
    ]: 
      status, abilities = exception
      for abilityName in abilities:
        abilityKey = inverseDict[abilityName]

        # shadow tag only provides immunity to shadow tag from gen 4 on
        if abilityName == 'shadow_tag':
          gen = 4
        else:
          gen = abilityDict[abilityKey]["gen"]

        abilityDict[abilityKey]["resists_status"][status] = [[True, gen]]

  # abilities which boost types and usage methods
  with open(fpath + 'abilitiesBoostMoveClass.csv', 'r', encoding='utf-8') as boostMoveClassCSV:
    reader = csv.DictReader(boostMoveClassCSV)
    for row in reader:
      abilityName, boosts, multiplier, moveClass = row["Ability Name"], row["Boosts"], row["Multiplier"], row["Move Class"]
      abilityKey = inverseDict[abilityName]
      gen = abilityDict[abilityKey]["gen"]

      if moveClass == 'method':
        if boosts not in usageMethodList():
          print(abilityName, boosts)
          continue

        abilityDict[abilityKey]["boosts_usage_method"][boosts] = [[multiplier, gen]]

      elif moveClass == 'type':
        if boosts not in typeList():
          print(abilityName, boosts)
          continue

        abilityDict[abilityKey]["boosts_type"][boosts] = [[multiplier, gen]]

  # abilities which resist types and usage methods
  with open(fpath + 'abilitiesResistMoveClass.csv', 'r', encoding='utf-8') as resistMoveClassCSV:
    reader = csv.DictReader(resistMoveClassCSV)
    for row in reader:
      abilityName, resists, multiplier, moveClass = row["Ability Name"], row["Resists"], row["Multiplier"], row["Move Class"]
      abilityKey = inverseDict[abilityName]
      gen = abilityDict[abilityKey]["gen"]

      # these abilities only got their type-resisting effects in Gen 5
      if abilityName in ['lightning_rod', 'storm_drain']:
        gen = 5

      if moveClass == 'method':
        if resists not in usageMethodList():
          continue

        abilityDict[abilityKey]["resists_usage_method"][resists] = [[multiplier, gen]]

      elif moveClass == 'type':
        if resists not in typeList():
          continue

        abilityDict[abilityKey]["resists_type"][resists] = [[multiplier, gen]]

  # abilities which modify stats
  with open(fpath + 'abilitiesModifyStat.csv', 'r', encoding='utf-8') as resistMoveClassCSV:
    reader = csv.DictReader(resistMoveClassCSV)
    for row in reader:
      abilityName, stat, modifier, recipient = row["Ability Name"], row["Stat Name"], row["Modifier"], row["Recipient"]
      abilityKey = inverseDict[abilityName]
      gen = abilityDict[abilityKey]["gen"]

      if stat not in statList():
        print(abilityName, stat)
        continue
      # only gained stat-modifying properties in Gen 5
      elif abilityName in ['lightning_rod', 'storm_drain']:
        abilityDict[abilityKey]["stat_modifications"][stat] = [[0, recipient, gen], ['+1', recipient, gen]]
        continue

      abilityDict[abilityKey]["stat_modifications"][stat] = [[modifier, recipient, gen]]
  return

def main():
  dataPath = getBulbapediaDataPath() + '\\abilities\\'
  fname = dataPath + 'abilityList.csv'
  abilityDict = makeInitialAbilityDict(fname)
  inverseDict = makeInverseDict(fname)

  addEffectData(dataPath, abilityDict, inverseDict)

  return abilityDict

if __name__ == '__main__':
  abilityDict = main()

  # check name consistency in abilityDict
  print()
  print('Checking name consistency...')
  for key in abilityDict.keys():
    abilityName = abilityDict[key]["name"]
    for effect in abilityDict[key]["effects"]:
      if effect not in effectList():
        print('Inconsistent effect name:', abilityName, effect)
    for status in abilityDict[key]["causes_status"]:
      if status not in statusList():
        print('Inconsistent cause-status name:', abilityName, status)
    for status in abilityDict[key]["resists_status"]:
      if status not in statusList():
        print('Inconsistent resist-status name:', abilityName, status)
    for type in abilityDict[key]["boosts_type"]:
      if type not in typeList():
        print('Inconsistent boost-type name:', abilityName, type)
    for type in abilityDict[key]["resists_type"]:
      if type not in typeList():
        print('Inconsistent resist-type name:', abilityName, type)
    for usageMethod in abilityDict[key]["boosts_usage_method"]:
      if usageMethod not in usageMethodList():
        print('Inconsistent boost-usage method name:', abilityName, usageMethod)
    for usageMethod in abilityDict[key]["resists_usage_method"]:
      if usageMethod not in usageMethodList():
        print('Inconsistent resist-usage method name:', abilityName, usageMethod)
    for stat in abilityDict[key]["stat_modifications"]:
      if stat not in statList():
        print('Inconsistent stat name', abilityName, stat)
    
  print()
  print('Checked name consistency.')