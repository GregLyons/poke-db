import abilities
import effects
import elementalTypes as types
import heldItems
import moves
import pokemon
import statuses
import usageMethods
from utils import statusList, typeList, effectList, usageMethodList, statList, checkConsistency

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
  print()

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
  print()

  return

# check that typeDict is consistent with typeList, statusList
def checkTypes(typeDict):
  print('Checking for inconsistencies in typeDict...')
  for typeName in typeDict.keys():
    for inconsistency in [
      checkConsistency(typeDict[typeName]["damage_to"], 'type', typeDict, 0.0, True),
      checkConsistency(typeDict[typeName]["damage_from"], 'type', typeDict, 0.0, True),
    ]:
      if inconsistency:
        print(f'Inconsistency found for {typeName}: {inconsistency}')
  print('Finished.')
  print()

  return

# check that moveDict is consistent with effectList, statusList, typeList, usageMethodList, statList
def checkMoves(moveDict):
  # check name consistency in moveDict
  print('Checking for inconsistencies in moveDict...')
  for abilityName in moveDict.keys():
    for inconsistency in [
      checkConsistency(moveDict[abilityName]["effects"], 'effect', effectDict, False),
      checkConsistency(moveDict[abilityName]["causes_status"], 'status', statusDict, 0.0),
      checkConsistency(moveDict[abilityName]["resists_status"], 'status', statusDict, False),
      checkConsistency(moveDict[abilityName]["usage_method"], 'usage_method', usageMethodDict, True),
    ]:
      if inconsistency:
        print(f'Inconsistency found for {abilityName}: {inconsistency}')

    for stat in moveDict[abilityName]["stat_modifications"]:
      if stat not in statList():
        print('Inconsistent stat name', abilityName, stat)
  print('Finished.')
  print()

  return

# check that abilityDict is consistent with effectList, statusList, typeList, usageMethodList, statList
def checkAbilities(abilityDict):

  # check name consistency in abilityDict
  print('Checking for inconsistencies in abilityDict...')
  for abilityName in abilityDict.keys():
    for inconsistency in [
      checkConsistency(abilityDict[abilityName]["effects"], 'effect', effectDict, False),
      checkConsistency(abilityDict[abilityName]["causes_status"], 'status', statusDict, 0.0),
      checkConsistency(abilityDict[abilityName]["resists_status"], 'status', statusDict, False),
      checkConsistency(abilityDict[abilityName]["boosts_type"], 'type', typeDict, 0.0, True),
      checkConsistency(abilityDict[abilityName]["resists_type"], 'type', typeDict, 0.0, True),
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

# check that itemDict is consistent with effectList, statusList, typeList, usageMethodList, statList
def checkItems(itemDict):
  print('Checking for inconsistencies in itemDict...')
  for itemName in itemDict.keys():
    for inconsistency in [
      checkConsistency(itemDict[itemName]["effects"], 'effect', effectDict, False),
      checkConsistency(itemDict[itemName]["causes_status"], 'status', statusDict, 0.0),
      checkConsistency(itemDict[itemName]["resists_status"], 'status', statusDict, False),
      checkConsistency(itemDict[itemName]["boosts_type"], 'type', typeDict, 0.0, True),
      checkConsistency(itemDict[itemName]["resists_type"], 'type', typeDict, 0.0, True),
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
  print('Checking consistency of abilityDict and pokemonDict...')

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

# This file is for making all the .csv files at once rather than running each individual script
if __name__ == '__main__':
  # initialize the various dictionaries and check that they're consistent with the type, status, usage method, effect, and stat lists
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


  abilityDict = abilities.main()
  checkAbilities(abilityDict)

  itemDict = heldItems.main()
  checkItems(itemDict)

  moveDict = moves.main()
  checkMoves(moveDict)

  pokemonDict = pokemon.main()
  checkPokemon(pokemonDict)


  # check that the more complicated dictionaries are consistent with each other
  checkAbilitiesAgainstPokemon(abilityDict, pokemonDict)
