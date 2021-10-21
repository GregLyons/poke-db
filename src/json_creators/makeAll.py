import abilities
import effects
import elementalTypes
import items
import moves
import pokemon
import statuses
from utils import statusList, typeList, effectList, usageMethodList, statList

# check that statusDict matches statusList
def checkStatuses(statusDict):
  print('Checking statusDict...')

  # make sure all statuses are accounted for
  for status in statusList():
    if status not in statusDict:
      print(status, 'not in statusDict')

  # make sure no typos
  for key in statusDict.keys():
    if key not in statusList():
      print(key, 'not in statusList')

  print('Finished statusDict.')
  return

# check that effectDict matches effectList
def checkEffects(effectDict):
  print('Checking effectDict...')

  # make sure all effects are accounted for
  for effect in effectList():
    if effect not in effectDict:
      print(effect, 'not in effectDict')

  # make sure no typos
  for key in effectDict.keys():
    if key not in effectList():
      print(key, 'not in effectList')

  print('Finished effectDict.')
  return

# check that typeDict is consistent with typeList, statusList
def checkTypes(typeDict):
  print('Checking typeDict...')

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
  return

# check that moveDict is consistent with effectList, statusList, typeList, usageMethodList, statList
def checkMoves(moveDict):
  print('Checking moveDict...')

  for key in moveDict.keys():
    moveName = moveDict[key]["name"]
    for effect in moveDict[key]["effects"]:
      if effect not in effectList():
        print('Inconsistent effect name:', moveName, effect)
    for status in moveDict[key]["causes_status"]:
      if status not in statusList():
        print('Inconsistent cause-status name:', moveName, status)
    for status in moveDict[key]["resists_status"]:
      if status not in statusList():
        print('Inconsistent resist-status name:', moveName, status)
    for type in [typePatch[0] for typePatch in moveDict[key]["type"]]:
      if type not in typeList():
        print('Inconsistent type name:', moveName, type)
    for usageMethod in moveDict[key]["usage_method"]:
      if usageMethod not in usageMethodList():
        print('Inconsistent usage method name:', moveName, usageMethod)
    for stat in moveDict[key]["stat_modifications"]:
      if stat not in statList():
        print('Inconsistent stat name', moveName, stat)
  
  print('Finished moveDict.')
  return

# check that abilityDict is consistent with effectList, statusList, typeList, usageMethodList, statList
def checkAbilities(abilityDict):
  print('Checking abilityDict...')

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
  
  print('Finished abilityDict.')
  return

# check that itemDict is consistent with effectList, statusList, typeList, usageMethodList, statList
def checkItems(itemDict):
  print('Checking itemDict...')

  for itemName in itemDict.keys():
    for effect in itemDict[itemName]["effects"]:
      if effect not in effectList():
        print('Inconsistent effect name:', itemName, effect)
    for status in itemDict[itemName]["causes_status"]:
      if status not in statusList():
        print('Inconsistent cause-status name:', itemName, status)
    for status in itemDict[itemName]["resists_status"]:
      if status not in statusList():
        print('Inconsistent resist-status name:', itemName, status)
    for type in itemDict[itemName]["boosts_type"]:
      if type not in typeList():
        print('Inconsistent boost-type name:', itemName, type)
    for type in itemDict[itemName]["resists_type"]:
      if type not in typeList():
        print('Inconsistent resist-type name:', itemName, type)
    for stat in itemDict[itemName]["stat_modifications"]:
      if stat not in statList():
        print('Inconsistent stat name', itemName, stat)

  print('Finished itemDict.')
  return

# check that pokemonDict is consistent with typeList
def checkPokemon(pokemonDict):
  for pokemonName in pokemonDict.keys():
    type1, type2 = pokemonDict[pokemonName]["type_1"][0][0], pokemonDict[pokemonName]["type_2"][0][0] if pokemonDict[pokemonName]["type_2"][0][0] else 'normal'

    if type1 not in typeList():
      print('Inconsistent type name', pokemonName, type1)
    if type2 not in typeList():
      print('Inconsistent type name', pokemonName, type2)

  return

# check that pokemonDict and abilityDict have same ability names
def checkAbilitiesAgainstPokemon(abilityDict, pokemonDict):
  print('Checking consistency of abilityDict and pokemonDict...')

  # set of ability names from abilityDict
  abilityNames = set()
  for abilityKey in abilityDict.keys():
    abilityName = abilityDict[abilityKey]["name"]
    abilityNames.add(abilityName)

  for pokemonName in pokemonDict.keys():
    for abilitySlot in ["ability_1", "ability_2", "ability_hidden"]:
      for abilityPatch in pokemonDict[pokemonName][abilitySlot]:
        abilityName = abilityPatch[0]
        if abilityName not in abilityNames and abilityName != '':
          print(pokemonName, 'has an inconsitent ability in slot', abilitySlot, 'with name', abilityName)
  
  print('Finished.')
  return

# This file is for making all the .csv files at once rather than running each individual script
if __name__ == '__main__':
  # initialize the various dictionaries and check that they're consistent with the type, status, usage method, effect, and stat lists
  abilityDict = abilities.main()
  checkAbilities(abilityDict)

  effectDict = effects.main()
  checkEffects(effectDict)

  itemDict = items.main()
  checkItems(itemDict)

  moveDict = moves.main()
  checkMoves(moveDict)

  pokemonDict = pokemon.main()
  checkPokemon(pokemonDict)

  statusDict = statuses.main()
  checkStatuses(statusDict)

  # check that the more complicated dictionaries are consistent with each other
  checkAbilitiesAgainstPokemon(abilityDict, pokemonDict)
