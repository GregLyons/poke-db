import json
import re
import abilities
import descriptions
import effects
import elementalTypes as types
import heldItems
import moves
import pokemon
import stats
import statuses
import usageMethods
import versionGroups
from utils import statusList, typeList, effectList, usageMethodList, statList, checkConsistency, getJSONDataPath

# check that statusDict matches statusList
def checkStatuses(statusDict):
  print('Checking completeness of statusDict...')

  # make sure all statuses are accounted for
  for status in statusList():
    if status not in statusDict:
      print(status, 'not in statusDict')

  # make sure no typos
  for key in statusDict.keys():
    if key not in statusList():
      print(key, 'not in statusList')

  print('Finished.')
  print()

  return

# check that effectDict matches effectList
def checkEffects(effectDict):
  print('Checking completeness of effectDict...')

  # make sure all effects are accounted for
  for effect in effectList():
    if effect not in effectDict:
      print(effect, 'not in effectDict')

  # make sure no typos
  for key in effectDict.keys():
    if key not in effectList():
      print(key, 'not in effectList')

  print('Finished.')
  print()

  return

# check that usageMethodDict matches usageMethodList
def checkUsageMethods(usageMethodDict):
  print('Checking usageMethodDict...')

  # make sure all usage methods are accounted for
  for usageMethod in usageMethodList():
    if usageMethod not in usageMethodDict:
      print(usageMethod, 'not in usageMethodDict')

  # make sure no typos
  for key in usageMethodDict.keys():
    if key not in usageMethodList():
      print(key, 'not in usageMethodList')

  print('Finished usageMethodDict.')
  print()

  return

# checks typeDict is consistent with typeList and has consistent values
def checkTypes(typeDict):
  print('Checking for inconsistencies in typeDict...')
  for typeName in typeDict.keys():
    for inconsistency in [
      checkConsistency(typeDict[typeName]["damage_to"], 'type', typeDict, 0.0),
      checkConsistency(typeDict[typeName]["damage_from"], 'type', typeDict, 0.0),
    ]:
      if inconsistency:
        print(f'Inconsistency found for {typeName}: {inconsistency}')
  print('Finished.')
  print()

  return

# check that moveDict is consistent with effectList, statusList, typeList, usageMethodList, statList and has consistent values
def checkMoves(moveDict):
  # check name consistency in moveDict
  print('Checking for inconsistencies in moveDict...')
  for abilityName in moveDict.keys():
    for inconsistency in [
      checkConsistency(moveDict[abilityName]["effects"], 'effect', effectDict, False),
      checkConsistency(moveDict[abilityName]["causes_status"], 'status', statusDict, 0.0),
      checkConsistency(moveDict[abilityName]["resists_status"], 'status', statusDict, False),
      checkConsistency(moveDict[abilityName]["usage_method"], 'usage_method', usageMethodDict, False),
    ]:
      if inconsistency:
        print(f'Inconsistency found for {abilityName}: {inconsistency}')

    for stat in moveDict[abilityName]["stat_modifications"]:
      if stat not in statList():
        print('Inconsistent stat name', abilityName, stat)
  print('Finished.')
  print()

  return

# check that abilityDict is consistent with effectList, statusList, typeList, usageMethodList, statList and has consistent values
def checkAbilities(abilityDict):

  # check name consistency in abilityDict
  print('Checking for inconsistencies in abilityDict...')
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
  print('Finished.')
  print()

  return

# check that itemDict is consistent with effectList, statusList, typeList, usageMethodList, statList and has consistent values
def checkItems(itemDict):
  print('Checking for inconsistencies in itemDict...')
  for itemName in itemDict.keys():
    for inconsistency in [
      checkConsistency(itemDict[itemName]["effects"], 'effect', effectDict, False),
      checkConsistency(itemDict[itemName]["causes_status"], 'status', statusDict, 0.0),
      checkConsistency(itemDict[itemName]["resists_status"], 'status', statusDict, False),
      checkConsistency(itemDict[itemName]["boosts_type"], 'type', typeDict, 0.0),
      checkConsistency(itemDict[itemName]["resists_type"], 'type', typeDict, 0.0),
      checkConsistency(itemDict[itemName]["resists_usage_method"], 'usage_method', usageMethodDict, 0.0),
    ]:
      if inconsistency:
        print(f'Inconsistency found for {itemName}: {inconsistency}')

    for stat in itemDict[itemName]["stat_modifications"]:
      if stat not in statList():
        print('Inconsistent stat name', itemName, stat)
  print('Finished.')
  print()

  return

# check that pokemonDict is consistent with typeList
def checkPokemon(pokemonDict):
  print('Checking for inconsistencies in pokemmonDict...')
  for pokemonName in pokemonDict.keys():

    type1, type2 = pokemonDict[pokemonName]["type_1"][0][0], pokemonDict[pokemonName]["type_2"][0][0] if pokemonDict[pokemonName]["type_2"][0][0] else 'normal'

    if type1 not in typeList():
      print('Inconsistent type name', pokemonName, type1)
    if type2 not in typeList():
      print('Inconsistent type name', pokemonName, type2)

  print('Finished.')
  print()

  return

# check that pokemonDict and abilityDict have same ability names
def checkAbilitiesAgainstPokemon(abilityDict, pokemonDict):
  print('Checking consistency of abilityDict with pokemonDict...')

  # set of ability names from abilityDict
  abilityNames = set()
  for abilityName in abilityDict.keys():
    abilityNames.add(abilityName)

  for pokemonName in pokemonDict.keys():

    for abilitySlot in ["ability_1", "ability_2", "ability_hidden"]:
      for abilityPatch in pokemonDict[pokemonName][abilitySlot]:
        abilityName = abilityPatch[0]
        if abilityName not in abilityNames and abilityName != '':
          print(pokemonName, 'has an inconsitent ability in slot', abilitySlot, 'with name', abilityName)
  
  print('Finished.')
  print()

  return

def checkMoveRequirements(moveDict, typeDict, pokemonDict): 
  moveNames = set()
  for moveName in moveDict.keys():
    moveNames.add(moveName)
  
  pokemonNames = set()
  for pokemonName in pokemonDict.keys():
    pokemonNames.add(pokemonName)

  typeNames = set()
  for typeName in typeDict.keys():
    typeNames.add(typeName)

  for moveName in moveDict.keys():
    # ignore moves without requirements
    if 'requirements' not in moveDict[moveName].keys():
      continue
    else:
      requirements = moveDict[moveName]["requirements"]
    
    if 'pokemon' in requirements.keys():
      for pokemonName in requirements["pokemon"]:
        if pokemonName not in pokemonNames:
          print(moveName, 'has an inconsistent Pokemon requirement:', pokemonName)
    
    if 'type' in requirements.keys():
      typeName = requirements["type"]
      if typeName not in typeNames:
        print(moveName, 'has an inconsistent type requirement:', typeName)

    if 'move' in requirements.keys():
      baseMoveName = requirements["move"]
      if baseMoveName not in moveNames:
        print(moveName, 'has an inconsistent base move name:', baseMoveName)

  return

# check that descriptionDict and entityDict have the same entityNames, where entityType is 'ability', 'item', or 'move'
def checkDescriptionsAgainstEntities(descriptionDict, entityDict, entityType):
  print('Checking consistency of descriptionDict with ' + entityType + ' names...')

  entityDescriptionNames = set([entityName for entityName in descriptionDict if descriptionDict[entityName]["description_type"] == entityType])
  entityNames = set(entityDict.keys())

  if entityDescriptionNames - entityNames:
    print(f'Inconsistencies found for {entityType}:')
    print(entityDescriptionNames - entityNames)

  print('Finished.')
  print()

  return

# Checks that the version group codes in descriptionDict are consistent with versionGroupDict
def checkDescriptionsAgainstVersionGroups(descriptionDict, versionGroupDict):
  print('Checking consistency of descriptionDict with versionGroupDict...')
  
  for entityName in descriptionDict.keys():
    for descriptionIndex in [descriptionKey for descriptionKey in descriptionDict[entityName].keys() if type(descriptionKey) == int]:
      for versionGroupCode in descriptionDict[entityName][descriptionIndex][-1]:
        if versionGroupCode not in versionGroupDict.keys():
          print('Inconsistent version group code: ' + versionGroupCode + '.')

  print('Finished.')
  print()

  return

# check dicts for internal consistency and for consistency with each other, then write to .json files
def main():
  # initialize the various reference dicts and check that they're consistent with the type, status, usage method, effect, and stat lists
  global effectDict
  effectDict = effects.main()
  checkEffects(effectDict)
  global statusDict
  statusDict = statuses.main()
  checkStatuses(statusDict)
  global typeDict
  typeDict = types.main()
  checkTypes(typeDict)
  global usageMethodDict
  usageMethodDict = usageMethods.main()

  # check that abilityDict is consistent with the reference dicts and that its values are consistent (e.g. values are of correct data type, if it has an effect then it doesn't do in an earlier gen than when the effect was introduced)
  abilityDict = abilities.main()
  checkAbilities(abilityDict)

  # no need to check description dict against the reference dicts
  descriptionDict = descriptions.main()

  # same but for itemDict
  itemDict = heldItems.main()
  checkItems(itemDict)

  # same but for moveDict
  moveDict = moves.main()
  checkMoves(moveDict)

  # check that pokemonDict is consistent with typeList
  pokemonDict = pokemon.main()
  checkPokemon(pokemonDict)

  statDict = stats.main()

  versionGroupDict = versionGroups.main()

  # check that the more complicated dictionaries are consistent with each other in terms of ability names
  checkAbilitiesAgainstPokemon(abilityDict, pokemonDict)

  # check that move requirements have consistent base move names, type names, and pokemon names
  checkMoveRequirements(moveDict, typeDict, pokemonDict)

  # check that the entry names in descriptionDict are consistent with the other dicts
  checkDescriptionsAgainstEntities(descriptionDict, abilityDict, 'ability')
  checkDescriptionsAgainstEntities(descriptionDict, itemDict, 'item')
  checkDescriptionsAgainstEntities(descriptionDict, moveDict, 'move')
  
  # check that the version group codes in descriptionDict agree with those in versionGroupDict
  checkDescriptionsAgainstVersionGroups(descriptionDict, versionGroupDict)

  # now that all the dicts have been checked for consistency, write each of them to a .json file
  dicts_fnames = [
    [effectDict, 'effects.json'],
    [statusDict, 'statuses.json'],
    [usageMethodDict, 'usageMethods.json'],
    [typeDict, 'elementalTypes.json'],
    [abilityDict, 'abilities.json'],
    [descriptionDict, 'descriptions.json'],
    [itemDict, 'items.json'],
    [moveDict, 'moves.json'],
    [pokemonDict, 'pokemon.json'],
    [versionGroupDict, 'versionGroups.json'],
    [statDict, 'stats.json']
  ]
  for dict_fname in dicts_fnames:
    dict, fname = dict_fname
    with open(getJSONDataPath() + fname, 'w', newline='') as jsonFile:
      output = json.dumps(dict, indent=2)

      # formatting for .json file, essentially to get the lists on one line but still have indentations and line breaks
      # double opening braces
      output = re.sub(r': \[\n\s+\[\n\s+', ': [[', output)
      # put most values on same line--after this step, there's a few edge cases
      output = re.sub(r',\n\s+([A-Za-z0-9\.]+)+', r', \1', output)
      # for inner lists which are on separate lines, put them together on the same line
      output = re.sub(r'\n\s+\],\n\s+\[\n\s+', '], [', output)
      # handle entries of list where successive entries are quotes, with a number in quotes
      output = re.sub(r'",\n\s+"(\d)', r'", "\1', output)
      # double closing braces
      output = re.sub(r'\n\s+\]\n\s+\]', ']]', output)
      # handle entries of list which have number followed by string
      output = re.sub(r'\[\[.*(\d),\n\s+"', r'[[\1, "', output)
      # entries of list which have string followed by string, in the first index
      output = re.sub(r'\[\["(.*)",\n\s+"', r'[["\1", "', output)

      jsonFile.write(output)

if __name__ == '__main__':
  main()