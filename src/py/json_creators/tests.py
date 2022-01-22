from utils import checkConsistency, numberOfGens, fieldStateList, natureList, statList, typeList
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

def checkOtherEntityNames(entityDict, otherEntityList, otherEntityKey):
  for entityName in entityDict.keys():
    for statName in entityDict[entityName][otherEntityKey]:
      if statName not in otherEntityList:
        raise InconsistentDataPointError(f'Inconsistent stat name: {entityName}, {statName}')

  return

# Goes through the patches in an entityDict (e.g. abilityDict, moveDict) and ensures that all patch gens are greater than or equal to the generation of their corresponding entity (e.g. if a Pokemon was introduced in gen 5, then all patches have a gen at least 5).
def checkGenConsistency(entityDict):
  for entityName in entityDict.keys():
    entityEntry = entityDict[entityName]
    
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

# Checks whether actualValue equals expectedValue. If not, raises InconsistentDataPointError.
def checkDataPoint(actualValue, expectedValue, entityName, key = '', innerKey = ''):
  if actualValue == expectedValue:
    return
  raise InconsistentDataPointError(f'Error when checking {" ".join([key, innerKey])} of {entityName}: {actualValue} should be {expectedValue}')

def abilityTests(abilityDict):
  checkOtherEntityNames(abilityDict, statList(), 'stat_modifications')

  checkOtherEntityNames(abilityDict, fieldStateList(), 'creates_field_state')
  checkOtherEntityNames(abilityDict, fieldStateList(), 'prevents_field_state')
  checkOtherEntityNames(abilityDict, fieldStateList(), 'suppresses_field_state')
  checkOtherEntityNames(abilityDict, fieldStateList(), 'ignores_field_state')
  checkOtherEntityNames(abilityDict, fieldStateList(), 'removes_field_state')

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

  return

def itemTests(itemDict):
  checkOtherEntityNames(itemDict, statList(), 'stat_modifications')

  checkOtherEntityNames(itemDict, fieldStateList(), 'extends_field_state')
  checkOtherEntityNames(itemDict, fieldStateList(), 'resists_field_state')
  checkOtherEntityNames(itemDict, fieldStateList(), 'ignores_field_state')

  checkOtherEntityNames(itemDict, natureList(), 'confuses_nature')

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

    for natureName in itemDict[itemName]["confuses_nature"]:
      if natureName not in natureList():
        raise InconsistentDataPointError(f'Inconsistent nature name: {itemName}, {natureName}')

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
  checkOtherEntityNames(moveDict, statList(), 'stat_modifications')

  checkOtherEntityNames(moveDict, fieldStateList(), 'creates_field_state')
  checkOtherEntityNames(moveDict, fieldStateList(), 'removes_field_state')
  
  for moveName in moveDict.keys():
    for inconsistency in [
      checkConsistency(moveDict[moveName]["effects"], 'effect', effectDict, False),
      checkConsistency(moveDict[moveName]["causes_status"], 'status', statusDict, 0.0),
      checkConsistency(moveDict[moveName]["resists_status"], 'status', statusDict, False),
      checkConsistency(moveDict[moveName]["usage_method"], 'usage_method', usageMethodDict, False),
    ]:
      if inconsistency:
        print(f'Inconsistency found for {moveName}: {inconsistency}')

    for fieldState in moveDict[moveName]["creates_field_state"]:
      if fieldState not in fieldStateList():
        print('Inconsistent field state name', moveName, fieldState)

    for fieldState in moveDict[moveName]["removes_field_state"]:
      if fieldState not in fieldStateList():
        print('Inconsistent field state name', moveName, fieldState)
        
  return

def natureTests(natureDict):
  for natureName in natureDict.keys():
    if natureName not in natureList():
      raise InconsistentDataPointError(f'{natureName} not in natureList.')
    
  checkOtherEntityNames(natureDict, statList(), 'stat_modifications')

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

  # Check that certain classes of forms belong to the appropriate generations
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

  # Unit tests
  #region
  
  # Type data checks

  # Type changes handled
  checkDataPoint(pokemonDict["clefairy"]["type_1"], [["normal", 1], ["fairy", 6]], 'clefairy', 'type_1', '')


  # Ability data checks

  # Ability changes handled
  checkDataPoint(pokemonDict["gengar"]["ability_1"], [["levitate", 3], ["cursed_body", 7]], 'gengar', 'ability_1', '')
  checkDataPoint(pokemonDict["chandelure"]["ability_hidden"], [["shadow_tag", 5], ["infiltrator", 6]], 'chandelure', 'ability_hidden', '')


  # Base stat checks

  # Stat changes handled
  checkDataPoint(pokemonDict["charmander"]["special_attack"], [[50, 1], [60, 5]], 'charmander', 'special_attack', '')

  checkDataPoint(pokemonDict["butterfree"]["special_attack"], [[80, 1], [90, 6]], 'butterfree', 'special_attack', '')
  

  # Form data checks

  # Megas and g-max handled
  charizardFormData = {
    "charizard_mega_x": [["mega", 6]],
    "charizard_mega_y": [["mega", 6]],
    "charizard_gmax": [["gmax", 8]]
  }
  checkDataPoint(pokemonDict["charizard"]["form_data"], charizardFormData, 'charizard', 'form_data', '')

  # All Pikachu forms handled
  pikachuFormData = {
    "pikachu_gmax": [["gmax", 8]],
    "pikachu_original_cap": [["cosmetic", 7]],
    "pikachu_kalos_cap": [["cosmetic", 7]],
    "pikachu_alola_cap": [["cosmetic", 7]],
    "pikachu_hoenn_cap": [["cosmetic", 7]],
    "pikachu_sinnoh_cap": [["cosmetic", 7]],
    "pikachu_unova_cap": [["cosmetic", 7]],
    "pikachu_world_cap": [["cosmetic", 7]],
    "pikachu_rock_star": [["cosmetic", 6]],
    "pikachu_belle": [["cosmetic", 6]],
    "pikachu_pop_star": [["cosmetic", 6]],
    "pikachu_phd": [["cosmetic", 6]],
    "pikachu_libre": [["cosmetic", 6]],
    "pikachu_partner_cap": [["cosmetic", 7]],
    "pikachu_cosplay": [["cosmetic", 6]]
  }
  checkDataPoint(pokemonDict["pikachu"]["form_data"], pikachuFormData, 'pikachu', 'form_data', '')

  # Arceus forms handled
  arceusFormData = {
    "arceus_grass": [["type", 4]],
    "arceus_fairy": [["type", 6]],
    "arceus_electric": [["type", 4]],
    "arceus_steel": [["type", 4]],
    "arceus_flying": [["type", 4]],
    "arceus_dark": [["type", 4]],
    "arceus_ice": [["type", 4]],
    "arceus_poison": [["type", 4]],
    "arceus_bug": [["type", 4]],
    "arceus_ground": [["type", 4]],
    "arceus_fighting": [["type", 4]],
    "arceus_psychic": [["type", 4]],
    "arceus_ghost": [["type", 4]],
    "arceus_water": [["type", 4]],
    "arceus_fire": [["type", 4]],
    "arceus_rock": [["type", 4]],
    "arceus_dragon": [["type", 4]]
  }
  checkDataPoint(pokemonDict["arceus_normal"]["form_data"], arceusFormData, 'arceus', 'form_data', '')

  # Arceus Ice not classified as base form (even though '_ice' and '_normal' are both suffices for base forms).
  checkDataPoint(pokemonDict["arceus_ice"]["form_class"], [["type", 4]], 'arceus', 'form_class', '')


  # Evolution data checks
  pikachuEvolutionData = {
    "raichu": [["Thunder Stone", 1]],
    "raichu_alola": [["Thunder Stone (Alola)", 7]]
  }
  checkDataPoint(pokemonDict["pikachu"]["evolves_to"], pikachuEvolutionData, 'pikachu', 'evolves_to', '')

  eeveeEvolutionData = {
    "vaporeon": [["Water Stone", 1]],
    "jolteon": [["Thunder Stone", 1]],
    "flareon": [["Fire Stone", 1]],
    "espeon": [["Friendship (day) Level up with Sun Shard (XD)", 2]],
    "umbreon": [["Friendship (night) Level up with Moon Shard (XD)", 2]],
    "leafeon": [["Level up near Moss Rock Leaf Stone (Sw/Sh)", 4]],
    "glaceon": [["Level up near Ice Rock Ice Stone (Sw/Sh)", 4]],
    "sylveon": [["Level up with a Fairy-type move and either two hearts of Affection or high friendship (Sw/Sh)", 6]]
  }
  checkDataPoint(pokemonDict["eevee"]["evolves_to"], eeveeEvolutionData, 'eevee', 'evolves_to', '')

  # Evolution data for slowpoke is a bit complicated
  slowpokeEvolutionData = {
    "slowbro": [["Level 37", 1]],
    "slowking": [["Trade holding King's Rock", 2]]
  }
  checkDataPoint(pokemonDict["slowpoke"]["evolves_to"], slowpokeEvolutionData, 'slowpoke', 'evolves_to', '')

  slowbroPrevolutionData = {
    "slowpoke": [["Level 37", 1]]
  }
  checkDataPoint(pokemonDict["slowbro"]["evolves_from"], slowbroPrevolutionData, 'slowbro', 'evolves_from', '')

  slowpokeGalarEvolutionData = {
    "slowbro_galar": [["Galarica Cuff", 8]],
    "slowking_galar": [["Galarica Wreath", 8]]
  }
  checkDataPoint(pokemonDict["slowpoke_galar"]["evolves_to"], slowpokeGalarEvolutionData, 'slowpoke_galar', 'evolves_to', '')
  
  # Evolution chains rerouted
  spewpaIcySnowEvolutionData = {
    "vivillon_icy_snow": [["Level 12", 6]]
  }
  checkDataPoint(pokemonDict["spewpa_icy_snow"]["evolves_to"], spewpaIcySnowEvolutionData, 'spewpa_icy_snow', 'evolves_to', '')
  spewpaIcySnowPrevolutionData = {
    "scatterbug_icy_snow": [["Level 9", 6]]
  }
  checkDataPoint(pokemonDict["spewpa_icy_snow"]["evolves_from"], spewpaIcySnowPrevolutionData, 'spewpa_icy_snow', 'evolves_from', '')

  #endregion

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