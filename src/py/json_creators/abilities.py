import csv
import effects
import statuses
import usageMethods
import elementalTypes as types
from utils import getCSVDataPath, genSymbolToNumber, effectList, statusList, fieldStateList, usageMethodList, statList, typeList, checkConsistency

# TODO gooey, etc. stat modifications

# initialize abilityDict with name, description, and gen; key is Ability ID
def makeInitialAbilityDict(fname):
  with open(fname, 'r', encoding='utf-8') as abilityListCSV:
    reader = csv.DictReader(abilityListCSV)
    abilityDict = {}
    for row in reader:
      abilityName, gen = row["Ability Name"].replace('*', ''), row["Gen"]
      abilityDict[abilityName] = {
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

# various data about abilities, e.g. stat modifications, interactions with types and usage methods, etc.
def addEffectData(fpath, abilityDict):
  # general effect headers for abilities
  with open(fpath + 'abilitiesByEffect.csv', 'r', encoding='utf-8') as effectCSV:
    reader = csv.DictReader(effectCSV)
    for row in reader:
      abilityName, effect = row["Ability Name"], row["Effect Type"]
      abilityGen = abilityDict[abilityName]["gen"]

      # actually belongs in status
      if effect == 'trapped':
        abilityDict[abilityName]["causes_status"]["trapped"] = [[100.0, abilityGen]]
      # some effects in the abilitiesByEffect.csv do not match with effectList(), so we ignore them
      elif effect not in effectList():
        # print(abilityName, effect)
        continue
      else:
        effectGen = effectDict[effect]["gen"]

        if abilityName == 'disguise' and effect == 'costs_hp':
          abilityGen = 7
          effectGen = 8


        # from abilityGen to effectGen, abilityName didn't have effect; fill in missing gens
        abilityDict[abilityName]["effects"][effect] = []
        diff = effectGen - abilityGen

        for i in range(diff):
          abilityDict[abilityName]["effects"][effect].append([False, abilityGen + i])

        abilityDict[abilityName]["effects"][effect].append([True, max(effectGen, abilityGen)])

  # abilities which can cause status--mainly through contact
  with open(fpath + 'abilitiesContactCausesStatus.csv', 'r', encoding='utf-8') as contactStatusCSV:
    reader = csv.DictReader(contactStatusCSV)
    for row in reader:
      abilityName, status, probability = row["Ability Name"], row["Status"], float(row["Probability"])
      
      if status not in statusList():
        # print(abilityName, status)
        continue

      abilityName
      abilityGen = abilityDict[abilityName]["gen"]
      abilityDict[abilityName]["causes_status"][status] = [[probability, abilityGen]]
      abilityDict[abilityName]["effects"]["punishes_contact"] = [[True, abilityGen]]

    # hardcode exceptions
    # poison_touch
    abilityDict["poison_touch"]["causes_status"]["poison"] = [[30.0, 5]]

    # synchronize
    abilityDict["synchronize"]["causes_status"]["burn"] = [[100.0, 3]]
    abilityDict["synchronize"]["causes_status"]["poison"] = [[100.0, 3]]
    # only inflicts bad_poison from gen 5 onward
    abilityDict["synchronize"]["causes_status"]["bad_poison"] = [[0.0, 3], [100.0, 5]]
    abilityDict["synchronize"]["causes_status"]["paralysis"] = [[100.0, 3]]

    abilityDict["perish_body"]["causes_status"]["perish_song"] = [[100.0, 8]]
    abilityDict["perish_body"]["effects"]["punishes_contact"] = [[True, 8]]

    abilityDict["scrappy"]["causes_status"]["identified"] = [[100.0, 4]]

    # stench
    abilityDict["stench"]["causes_status"]["flinch"] = [[10.0, 5]]

    # sturdy
    abilityDict["sturdy"]["causes_status"]["bracing"] = [[100.0, 3]]

    # truant
    abilityDict["truant"]["causes_status"]["recharging"] = [[100.0, 3]]

    # more abilities which punish contact not handled above
    for abilityName in ['aftermath', 'gooey', 'mummy', 'iron_barbs', 'rough_skin', 'tangling_hair', 'wandering_spirit', 'pickpocket']:
      abilityDict[abilityName]["effects"]["punishes_contact"] = [[True, abilityGen]]

  # abilities which protect against status
  with open(fpath + 'abilitiesProtectAgainstStatus.csv', 'r', encoding='utf-8') as boostMoveClassCSV:
    reader = csv.DictReader(boostMoveClassCSV)
    for row in reader:
      abilityName, status = row["Ability Name"], row["Status Name"]

      if status == 'non_volatile' or status not in statusList():
        continue
      
      abilityGen = abilityDict[abilityName]["gen"]
      abilityDict[abilityName]["resists_status"][status] = [[True, abilityGen]]
    
    # hardcode abilities which protect against non_volatile status
    for abilityName in ['flower_veil', 'sweet_veil', 'natural_cure', 'shed_skin', 'hydration', 'comatose']:
      for status in ['poison', 'bad_poison', 'burn', 'paralysis', 'freeze', 'sleep']:
        abilityGen = abilityDict[abilityName]["gen"]
        abilityDict[abilityName]["resists_status"][status] = [[True, abilityGen]]

    # hardcode exceptions
    for exception in [
      ['sleep', ['early_bird']],
      ['burn', ['water_bubble']],
      ['poison', ['pastel_veil', 'poison_heal']],
      ['trapped', ['shadow_tag']]
    ]: 
      status, abilities = exception
      for abilityName in abilities:
        # shadow tag only provides immunity to shadow tag from gen 4 on
        if abilityName == 'shadow_tag':
          abilityDict[abilityName]["resists_status"][status] = [[False, 3], [True, 4]]
          continue
        else:
          abilityGen = abilityDict[abilityName]["gen"]

        abilityDict[abilityName]["resists_status"][status] = [[True, abilityGen]]

  # abilities which boost types and usage methods
  with open(fpath + 'abilitiesBoostMoveClass.csv', 'r', encoding='utf-8') as boostMoveClassCSV:
    reader = csv.DictReader(boostMoveClassCSV)
    for row in reader:
      abilityName, boosts, multiplier, moveClass = row["Ability Name"], row["Boosts"], row["Multiplier"], row["Move Class"]
      abilityGen = abilityDict[abilityName]["gen"]

      if moveClass == 'method':
        if boosts not in usageMethodList():
          # print(abilityName, boosts)
          continue

        abilityDict[abilityName]["boosts_usage_method"][boosts] = [[float(multiplier), abilityGen]]

      elif moveClass == 'type':
        if boosts not in typeList():
          print(abilityName, boosts)
          continue

        abilityDict[abilityName]["boosts_type"][boosts] = [[float(multiplier), abilityGen]]

  # abilities which resist types and usage methods
  with open(fpath + 'abilitiesResistMoveClass.csv', 'r', encoding='utf-8') as resistMoveClassCSV:
    reader = csv.DictReader(resistMoveClassCSV)
    for row in reader:
      abilityName, resists, multiplier, moveClass = row["Ability Name"], row["Resists"], row["Multiplier"], row["Move Class"]
      abilityGen = abilityDict[abilityName]["gen"]

      # these abilities only got their type-resisting effects in Gen 5
      if abilityName in ['lightning_rod', 'storm_drain']:
        abilityDict[abilityName]["resists_type"][resists] = [[0.0, 5]]
        continue

      if moveClass == 'method':
        if resists not in usageMethodList():
          continue

        abilityDict[abilityName]["resists_usage_method"][resists] = [[float(multiplier), abilityGen]]

      elif moveClass == 'type':
        if resists not in typeList():
          continue

        abilityDict[abilityName]["resists_type"][resists] = [[float(multiplier), abilityGen]]

  # abilities which modify stats
  with open(fpath + 'abilitiesModifyStat.csv', 'r', encoding='utf-8') as resistMoveClassCSV:
    reader = csv.DictReader(resistMoveClassCSV)
    for row in reader:
      abilityName, stat, modifier, recipient = row["Ability Name"], row["Stat Name"], row["Modifier"], row["Recipient"]
      abilityGen = abilityDict[abilityName]["gen"]

      # Indicates multiplier.
      if '.' in modifier:
        modifier = float(modifier)

      if stat not in statList():
        print(abilityName, stat)
        continue
      # only gained stat-modifying properties in Gen 5
      elif abilityName in ['lightning_rod', 'storm_drain']:
        abilityDict[abilityName]["stat_modifications"][stat] = [['+0', recipient, 100.0, abilityGen], ['+1', recipient, 100.0, 5]]
        continue


      abilityDict[abilityName]["stat_modifications"][stat] = [[modifier, recipient, 100.0, abilityGen]]

  # Force Moody
  for statName in ['attack', 'defense', 'special_attack', 'special_defense', 'speed', 'evasion', 'accuracy']:
    abilityDict["moody"]["stat_modifications"][statName] = [['+2', 'user', 14.28, 5]]

    if statName not in ['evasion', 'accuracy']:
      abilityDict["moody"]["stat_modifications"][statName].append([['+2', 'user', 20.00, 8]])
    else:
      abilityDict["moody"]["stat_modifications"][statName].append([['+2', 'user', 0.00, 8]])
  return

def addFieldStateData(abilityDict):
  for abilityName in abilityDict.keys():
    abilityDict[abilityName]["creates_field_state"] = {}
    abilityDict[abilityName]["removes_field_state"] = {}
    abilityDict[abilityName]["prevents_field_state"] = {}
    abilityDict[abilityName]["suppresses_field_state"] = {}

  # Cloud Nine and Air Lock
  #region

  for weatherName in ['harsh_sunlight', 'extremely_harsh_sunlight', 'rain', 'heavy_rain', 'sandstorm', 'hail']:
    gen = 3
    if weatherName in ['extremely_harsh_sunlight', 'heavy_rain']:
      gen = 6

    abilityDict["cloud_nine"]["prevents_field_state"][weatherName] = [[True, gen]]
    abilityDict["cloud_nine"]["suppresses_field_state"][weatherName] = [[True, gen]]
    abilityDict["air_lock"]["prevents_field_state"][weatherName] = [[True, gen]]
    abilityDict["air_lock"]["suppresses_field_state"][weatherName] = [[True, gen]]

  abilityDict["cloud_nine"]["prevents_field_state"]["aurora_veil"] = [[True, 7]]
  abilityDict["air_lock"]["prevents_field_state"]["aurora_veil"] = [[True, 7]]

  #endregion

  # Infiltrator
  for fieldStateName in ['mist', 'safeguard', 'reflect', 'light_screen', 'aurora_veil']:
    gen = 5
    # TYPO: Bulbapedia says in Gen 6, but aurora veil wasn't introduced until gen 7
    if fieldStateName == 'aurora_veil':
      gen = 7
    abilityDict['infiltrator']["ignores_field_state"] = [[True, gen]]

  # Screen Cleaner
  for screenName in ['reflect', 'light_screen', 'aurora_veil']:
    abilityDict["screen_cleaner"]["removes_field_state"][screenName] = [[True, 8]]

  # Terrain and weather creators
  for [abilityName, fieldStateName] in [
    # Weathers
    ['drought', 'harsh_sunlight'],
    ['desolate_land', 'extremely_harsh_sunlight'],
    ['drizzle', 'rain'],
    ['primordial_sea', 'heavy_rain'],
    ['sand_stream', 'sandstorm'],
    ['sand_spit', 'sandstorm'],
    ['snow_warning', 'hail'],
    ['delta_stream', 'strong_winds'],
    # Terrains
    ['electric_surge', 'electric_terrain'],
    ['grassy_surge', 'grassy_terrain'],
    ['misty_surge', 'misty_terrain'],
    ['psychic_surge', 'psychic_terrain']
  ]:
    abilityGen = abilityDict[abilityName]["gen"]

    # Creation
    if abilityGen < 6:
      # Weathers created by abilities lasted until replaced prior to Gen 6
      abilityDict[abilityName]["creates_field_state"][fieldStateName] = [[True, 0, abilityGen], [True, 5, abilityGen]]
    else:
      # Terrains from abilities last 5 turns
      if abilityName not in ['primordial_sea', 'desolate_land', 'delta_stream']:
        abilityDict[abilityName]["creates_field_state"][fieldStateName] = [[True, 5, abilityGen]]
      # Strong weathers last as long as user is out
      else:
        abilityDict[abilityName]["creates_field_state"][fieldStateName] = [[True, 0, abilityGen]]

  #endregion

        
  # Terrain and weather removers
  #region

  terrains = ['electric_terrain', 'grassy_terrain', 'misty_terrain', 'psychic_terrain']
  weathers = ['clear_skies', 'fog', 'harsh_sunlight', 'rain', 'sandstorm', 'hail']
  strongWeathers = ['extremely_harsh_sunlight', 'heavy_rain', 'strong_winds']

  for abilityName in abilityDict.keys():
    creatorDict = abilityDict[abilityName]["creates_field_state"]
    abilityGen = abilityDict[abilityName]["gen"]

    # Terrains overwrite each other
    for terrainName in terrains:
      if terrainName in creatorDict.keys():
        terrainGen = 6

        for otherTerrainName in [t for t in terrains if t != terrainName]:
          otherTerrainGen = 6

          abilityDict[abilityName]["removes_field_state"][otherTerrainName] = [[True, max(abilityGen, terrainGen, otherTerrainGen)]]
    
    # Weathers overwrite each other
    for weatherName in weathers:
      if weatherName in creatorDict.keys():
        weatherGen = 2
        if weatherName == 'hail':
          weatherGen = 3
        if weatherName == 'fog':
          weatherGen = 4
        
        for otherWeatherName in [w for w in weathers if w != weatherName]:
          otherWeatherGen = 2
          if otherWeatherName == 'hail':
            otherWeatherGen = 3
          if otherWeatherName == 'fog':
            otherWeatherGen = 4
          
          abilityDict[abilityName]["removes_field_state"][otherWeatherName] = [[True, max(abilityGen, weatherGen, otherWeatherGen)]]

    # Strong weathers overwrite each other, as well as weaker weathers
    for strongWeatherName in strongWeathers:
      if strongWeatherName in creatorDict.keys():
        strongWeatherGen = 6

        for otherStrongWeatherName in [sw for sw in strongWeathers if sw != strongWeatherName]:
          otherStrongWeatherGen = 6

          abilityDict[abilityName]["removes_field_state"][otherStrongWeatherName] = [[True, max(abilityGen, strongWeatherGen, otherStrongWeatherGen)]]

        # Strong weathers remove weaker weathers
        for otherWeatherName in [w for w in weathers if w != weatherName]:
          otherWeatherGen = 2
          if otherWeatherName == 'hail':
            otherWeatherGen = 3
          if otherWeatherName == 'fog':
            otherWeatherGen = 4
          
          abilityDict[abilityName]["removes_field_state"][otherWeatherName] = [[True, max(abilityGen, strongWeatherGen, otherWeatherGen)]]

  #endregion

  return

def addFormattedName(abilityDict):
  for abilityName in abilityDict.keys():
    abilityDict[abilityName]['formatted_name'] = getFormattedName(abilityName)

  return

def getFormattedName(abilityName):
  if abilityName == 'rks_system':
    return 'RKS System'
  elif abilityName == 'soul_heart':
    return 'Soul-Heart'
  elif 'as_one' in abilityName:
    if 'glastrier' in abilityName:
      return 'As One (Glastrier)'
    else:
      return 'As One (Spectrier)'
  else:
    return ' '.join(abilityName.split('_')).title()

def main():
  # dictionaries containing effect names/gens and status names/gens
  global effectDict
  effectDict = effects.main()
  global statusDict
  statusDict = statuses.main()
  global typeDict
  typeDict = types.main()
  global usageMethodDict
  usageMethodDict = usageMethods.main()

  dataPath = getCSVDataPath() + '\\abilities\\'
  fname = dataPath + 'abilityList.csv'
  abilityDict = makeInitialAbilityDict(fname)

  addEffectData(dataPath, abilityDict)

  addFormattedName(abilityDict)

  addFieldStateData(abilityDict)

  return abilityDict

if __name__ == '__main__':
  abilityDict = main()

  # check name consistency in abilityDict
  print('Checking for inconsistencies...')
  for abilityName in abilityDict.keys():
    for inconsistency in [
      checkConsistency(abilityDict[abilityName]["effects"], 'effect', effectDict, False),
      checkConsistency(abilityDict[abilityName]["causes_status"], 'status', statusDict, 0.0),
      checkConsistency(abilityDict[abilityName]["resists_status"], 'status', statusDict, False),
      checkConsistency(abilityDict[abilityName]["boosts_type"], 'type', typeDict, 0.0),
      checkConsistency(abilityDict[abilityName]["resists_type"], 'type', typeDict, 0.0),
      checkConsistency(abilityDict[abilityName]["boosts_usage_method"], 'usage_method', usageMethodDict, 0.0),
      checkConsistency(abilityDict[abilityName]["resists_usage_method"], 'usage_method', usageMethodDict, 0.0),
    ]:
      if inconsistency:
        print(f'Inconsistency found for {abilityName}: {inconsistency}')

    for stat in abilityDict[abilityName]["stat_modifications"]:
      if stat not in statList():
        print('Inconsistent stat name', abilityName, stat)
        
    for fieldState in abilityDict[abilityName]["extends_field_state"]:
      if fieldState not in fieldStateList():
        print('Inconsistent field state name', abilityName, fieldState)

    for fieldState in abilityDict[abilityName]["resists_field_state"]:
      if fieldState not in fieldStateList():
        print('Inconsistent field state name', abilityName, fieldState)
    
    for fieldState in abilityDict[abilityName]["ignores_field_state"]:
      if fieldState not in fieldStateList():
        print('Inconsistent field state name', abilityName, fieldState)

  print('Finished.')