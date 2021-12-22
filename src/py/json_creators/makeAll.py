import json
import re
import abilities
import descriptions
import effects
import elementalTypes as types
import fieldStates
import heldItems
import moves
import natures
import pokemon
import stats
import statuses
import usageMethods
import versionGroups
from utils import statusList, typeList, effectList, usageMethodList, statList, fieldStateList, checkConsistency, getJSONDataPath

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

def checkPokemonAgainstItems(pokemonDict, itemDict): 
  print('Checking consistency of abilityDict with pokemonDict...')

  # set of ability names from abilityDict
  pokemonNames = set()
  for pokemonName in pokemonDict.keys():
    pokemonNames.add(pokemonName)

  for itemName in itemDict.keys():
    for pokemonName in itemDict[itemName]["pokemon_specific"].keys():
      if pokemonName not in pokemonNames:
        print(itemName, 'has an inconsistent Pokemon specificity requirement', pokemonName, '.')
  
  print('Finished.')
  print()

  return

# check that the move requirements match the relevant dicts
def checkMoveRequirements(moveDict, typeDict, pokemonDict, itemDict): 
  print('Checking consistency of move requirements with moveDict, typeDict, itemDict, and pokemonDict.')
  moveNames = set()
  for moveName in moveDict.keys():
    moveNames.add(moveName)
  
  pokemonNames = set()
  for pokemonName in pokemonDict.keys():
    pokemonNames.add(pokemonName)

  typeNames = set()
  for typeName in typeDict.keys():
    typeNames.add(typeName)

  itemNames = set()
  for itemName in itemDict.keys():
    itemNames.add(itemName)

  for moveName in moveDict.keys():
    # ignore moves without requirements
    if 'requirements' not in moveDict[moveName].keys():
      continue
    else:
      requirements = moveDict[moveName]["requirements"]
    
    for entityClass in moveDict[moveName]["requirements"]:
      if entityClass == 'pokemon':
        entitySet = pokemonNames
      elif entityClass == 'move':
        entitySet = moveNames
      elif entityClass == 'item':
        entitySet = itemNames
      elif entityClass == 'type':
        entitySet = typeNames
      else:
        continue
      
      for entityName in requirements[entityClass].keys():
        entityName
        if entityName not in entitySet:
          print(moveName, 'has an inconsistent', entityClass, 'requirement:', entityName)

  print('Finished.')
  print()

  return

# check that the move requirements match the relevant dicts
def checkPokemonRequirements(pokemonDict, itemDict): 
  print('Checking consistency of Pokemon requirements with pokemonDict, itemDict.')
  
  pokemonNames = set()
  for pokemonName in pokemonDict.keys():
    pokemonNames.add(pokemonName)

  itemNames = set()
  for itemName in itemDict.keys():
    itemNames.add(itemName)

  for pokemonName in pokemonDict.keys():
    # ignore moves without requirements
    if 'requirements' not in pokemonDict[pokemonName].keys():
      continue
    else:
      requirements = pokemonDict[pokemonName]["requirements"]
    
    for entityClass in pokemonDict[pokemonName]["requirements"]:
      if entityClass == 'pokemon':
        entitySet = pokemonNames
      elif entityClass == 'item':
        entitySet = itemNames
      else:
        continue
      
      for entityName in requirements[entityClass].keys():
        entityName
        if entityName not in entitySet:
          print(pokemonName, 'has an inconsistent', entityClass, 'requirement:', entityName)

  print('Finished.')
  print()

  return

# check that descriptionDict and entityDict have the same entityNames, where entityType is 'ability', 'item', or 'move'
def checkDescriptionsAgainstEntities(descriptionDict, entityDict, entityType):
  print('Checking consistency of descriptionDict with ' + entityType + ' names...')

  entityDescriptionNames = set([entityName for entityName in descriptionDict if descriptionDict[entityName]["description_class"] == entityType])
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

  global natureDict
  natureDict = natures.main()
  
  global statusDict
  statusDict = statuses.main()
  checkStatuses(statusDict)

  global typeDict
  typeDict = types.main()
  checkTypes(typeDict)

  global usageMethodDict
  usageMethodDict = usageMethods.main()

  # These dicts already have individual tests (i.e. they're tested for their own internal self-consistency, for certain correct data values, and for consistency with effectDict, statusDict, typeDict, usageMethodDict, and natureDict as necessary).
  abilityDict = abilities.main()
  fieldStateDict = fieldStates.main()
  itemDict = heldItems.main()
  moveDict = moves.main()
  pokemonDict = pokemon.main()

  # no need to check description dict against the reference dicts
  descriptionDict = descriptions.main()

  statDict = stats.main()

  versionGroupDict = versionGroups.main()

  # check that the more complicated dictionaries are consistent with each other in terms of ability names
  checkAbilitiesAgainstPokemon(abilityDict, pokemonDict)

  # check that Pokemon specificity requirements have same names as pokemonDict
  checkPokemonAgainstItems(pokemonDict, itemDict)

  # check that move requirements have consistent base move names, type names, and pokemon names
  checkMoveRequirements(moveDict, typeDict, pokemonDict, itemDict)

  # check that the entry names in descriptionDict are consistent with the other dicts
  checkDescriptionsAgainstEntities(descriptionDict, abilityDict, 'ability')
  checkDescriptionsAgainstEntities(descriptionDict, itemDict, 'item')
  checkDescriptionsAgainstEntities(descriptionDict, moveDict, 'move')
  
  # check that the version group codes in descriptionDict agree with those in versionGroupDict
  checkDescriptionsAgainstVersionGroups(descriptionDict, versionGroupDict)

  # now that all the dicts have been checked for consistency, write each of them to a .json file
  dicts_fnames = [
    [effectDict, 'effects.json'],
    [fieldStateDict, 'fieldStates.json'],
    [statusDict, 'statuses.json'],
    [usageMethodDict, 'usageMethods.json'],
    [typeDict, 'elementalTypes.json'],
    [abilityDict, 'abilities.json'],
    [descriptionDict, 'descriptions.json'],
    [itemDict, 'items.json'],
    [moveDict, 'moves.json'],
    [natureDict, 'natures.json'],
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
      output = re.sub(r'",\n\s+"(\d+)', r'", "\1', output)
      # double closing braces
      output = re.sub(r'\n\s+\]\n\s+\]', ']]', output)
      # handle entries of list which have number followed by string
      output = re.sub(r'\[\[[a-zA-Z,\"](\d+),\n\s+"', r'[[\1, "', output)
      # entries of list which have string followed by string, in the first index
      output = re.sub(r'\[\["(.*)",\n\s+"', r'[["\1", "', output)

      jsonFile.write(output)

if __name__ == '__main__':
  main()