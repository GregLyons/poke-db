from utils import checkConsistency, numberOfGens, fieldStateList, statList, typeList
import effects
import elementalTypes
import statuses
import usageMethods

effectDict = effects.main()
statusDict = statuses.main()
typeDict = elementalTypes.main()
usageMethodDict = usageMethods.main()

class Error(Exception):
  pass

class InconsistentPatchGenError(Error):
  def __init__(self, message):
    self.message = message

class InconsistentDataPointError(Error):
  def __init__(self, message):
    self.message = message

def checkGenConsistency(entityDict):
  for entityName in entityDict.keys():
    entityEntry = entityDict[entityName]
    
    # 
    if 'gen' not in entityEntry.keys():
      return
    entityGen = entityEntry["gen"]

    for key in entityEntry.keys():
      if key in ['pokeapi']:
        continue

      elif type(entityEntry[key]) is list:
        patchList = entityEntry[key]

        for patch in patchList:
          patchGen = patch[-1]

          if patchGen == 'lgpe_only' and entityGen not in ['lgpe_only', 7]:
            raise InconsistentPatchGenError(f'{entityName} has inconsitent gens for {key}:\n\tPatch gen: {patchGen}\n\tEntity gen: {entityGen}')

          elif 'lgpe_only' in [patchGen, entityGen]:
            continue

          elif patchGen < entityGen:
            raise InconsistentPatchGenError(f'{entityName} has inconsitent gens for {key}:\n\tPatch gen: {patchGen}\n\tEntity gen: {entityGen}')

      elif type(entityEntry[key]) is dict:
        for innerKey in entityEntry[key].keys():
          if key in []:
            continue

          elif type(entityEntry[key][innerKey]) is list:
            patchList = entityEntry[key][innerKey]

            for patch in patchList:
              patchGen = patch[-1]

              if patchGen == 'lgpe_only' and entityGen not in ['lgpe_only', 7]:
                raise InconsistentPatchGenError(f'{entityName} has inconsitent gens for {innerKey}:\n\tPatch gen: {patchGen}\n\tEntity gen: {entityGen}')

              elif patchGen == 'lgpe_only':
                continue
              
              elif patchGen < entityGen:
                raise InconsistentPatchGenError(f'{entityName} has gens for {key}, {innerKey}:\n\tPatch gen: {patchGen}\n\tEntity gen: {entityGen}')


  return

def abilityTests(abilityDict):
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

    for fieldState in abilityDict[abilityName]["creates_field_state"]:
      if fieldState not in fieldStateList():
        print('Inconsistent field state name', abilityName, fieldState)

    for fieldState in abilityDict[abilityName]["prevents_field_state"]:
      if fieldState not in fieldStateList():
        print('Inconsistent field state name', abilityName, fieldState)
    
    for fieldState in abilityDict[abilityName]["suppresses_field_state"]:
      if fieldState not in fieldStateList():
        print('Inconsistent field state name', abilityName, fieldState)
        
    for fieldState in abilityDict[abilityName]["ignores_field_state"]:
      if fieldState not in fieldStateList():
        print('Inconsistent field state name', abilityName, fieldState)

    for fieldState in abilityDict[abilityName]["removes_field_state"]:
      if fieldState not in fieldStateList():
        print('Inconsistent field state name', abilityName, fieldState)

  return

def itemTests(itemDict):
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

    for fieldState in itemDict[itemName]["extends_field_state"]:
      if fieldState not in fieldStateList():
        print('Inconsistent field state name', itemName, fieldState)

    for fieldState in itemDict[itemName]["resists_field_state"]:
      if fieldState not in fieldStateList():
        print('Inconsistent field state name', itemName, fieldState)
    
    for fieldState in itemDict[itemName]["ignores_field_state"]:
      if fieldState not in fieldStateList():
        print('Inconsistent field state name', itemName, fieldState)

  return

def moveTests(moveDict):
  for moveName in moveDict.keys():
    for inconsistency in [
      checkConsistency(moveDict[moveName]["effects"], 'effect', effectDict, False),
      checkConsistency(moveDict[moveName]["causes_status"], 'status', statusDict, 0.0),
      checkConsistency(moveDict[moveName]["resists_status"], 'status', statusDict, False),
      checkConsistency(moveDict[moveName]["usage_method"], 'usage_method', usageMethodDict, False),
    ]:
      if inconsistency:
        print(f'Inconsistency found for {moveName}: {inconsistency}')

    for stat in moveDict[moveName]["stat_modifications"]:
      if stat not in statList():
        print('Inconsistent stat name', moveName, stat)

    for fieldState in moveDict[moveName]["creates_field_state"]:
      if fieldState not in fieldStateList():
        print('Inconsistent field state name', moveName, fieldState)

    for fieldState in moveDict[moveName]["removes_field_state"]:
      if fieldState not in fieldStateList():
        print('Inconsistent field state name', moveName, fieldState)
        
  return

def pokemonTests(pokemonDict):
  # Check that number of base forms in each generation is correct
  # Also collect other form classes for later analysis
  megas = {}
  alolas = {}
  galars = {}
  gmaxes = {}

  genCounts = [0] * numberOfGens()
  for pokemonName in pokemonDict.keys():
    pokemonGen = pokemonDict[pokemonName]["gen"]
    if pokemonGen == 'lgpe_only': 
      continue

    formClass = pokemonDict[pokemonName]["form_class"][0]

    # If Pokemon is not base form, add it to appropriate form Set for later
    if formClass[0] != 'base':
      if formClass[0] == 'mega':
        megas[pokemonName] = pokemonGen
      if formClass[0] == 'alola':
        alolas[pokemonName] = pokemonGen
      if formClass[0] == 'galar':
        galars[pokemonName] = pokemonGen
      if formClass[0] == 'gmax':
        gmaxes[pokemonName] = pokemonGen
        
      continue

    genCounts[pokemonGen - 1] += 1
  
  correctGenCounts = [151, 100, 135, 107, 156, 72, 88, 89]
  for i in range(len(correctGenCounts)):
    if correctGenCounts[i] != genCounts[i]:
      raise InconsistentDataPointError(f'Number of base forms pokemonDict in generation {i  + 1}, {genCounts[i]}, does not match the number of Pokemon introduced {correctGenCounts[i]}.')

  # Check that all megas are Gen 6 or later
  for pokemonName in megas.keys():
    if megas[pokemonName] < 6:
      raise InconsistentDataPointError(f'Mega form prior to gen 6: {pokemonName}.')
  # Check that all alolas are Gen 7 or later
  for pokemonName in alolas.keys():
    if alolas[pokemonName] < 7:
      raise InconsistentDataPointError(f'Alola form prior to gen 7: {pokemonName}.')
  # Check that all galars are Gen 8 or later
  for pokemonName in galars.keys():
    if galars[pokemonName] < 8:
      raise InconsistentDataPointError(f'Galar form prior to gen 8: {pokemonName}.')
  # Check that all gmaxes are Gen 8 or later
  for pokemonName in gmaxes.keys():
    if gmaxes[pokemonName] < 8:
      raise InconsistentDataPointError(f'Gmax form prior to gen 8: {pokemonName}.')


  # Check naming consistency
  for pokemonName in pokemonDict.keys():
    type1, type2 = pokemonDict[pokemonName]["type_1"][0][0], pokemonDict[pokemonName]["type_2"][0][0] if pokemonDict[pokemonName]["type_2"][0][0] else 'normal'

    if type1 not in typeList():
      print('Inconsistent type name', pokemonName, type1)
    if type2 not in typeList():
      print('Inconsistent type name', pokemonName, type2)

  return


def typeTests(typeDict):
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

  return