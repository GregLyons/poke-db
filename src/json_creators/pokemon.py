import csv
import re
import copy
from utils import parseName, genSymbolToNumber, getCSVDataPath, genSymbolToNumber, typeList

# make initial Pokemon dict, with dex number, gen, species, and type data
# the pokemonByType.csv doesn't contain all the Pokemon forms, since some different forms of the same Pokemon can have the same type. We will rectify this in future functions; for example, base stat data will add in the forms of deoxys since those have different base stats
def makeInitialPokemonDict(fname, changes_fname):
  pokemonDict = {} 

  with open(fname, 'r', encoding='utf-8') as typeCSV:
    reader = csv.DictReader(typeCSV)

    for row in reader:
      gen, dexNumber, speciesName, pokemonName, type1, type2 = row["Gen"], row["Dex Number"], row["Species Name"], row["Pokemon Name"], row["Type 1"], row["Type 2"]

      if dexNumber != '':
        dexNumber = int(dexNumber)

      pokemonDict[pokemonName] = {
        "dex_number": dexNumber,
        "species": speciesName,
        "gen": int(gen),
        "type_1": [[type1, int(gen)]],
        "type_2": [[type2, int(gen)]],
        "evolves_to": [],
        "evolves_from": [],
      }
    
    # partner pikachu and partner eevee
    pokemonDict["pikachu_partner"] = {
        "dex_number": 25,
        "species": 'pikachu',
        "gen": 'lgpe_only',
        "type_1": [['electric', 'lgpe_only']],
        "type_2": [['', 'lgpe_only']],
        "evolves_to": [],
        "evolves_from": [],
      }
    pokemonDict["eevee_partner"] = {
        "dex_number": 133,
        "species": 'eevee',
        "gen": 'lgpe_only',
        "type_1": [['normal', 'lgpe_only']],
        "type_2": [['', 'lgpe_only']],
        "evolves_to": [],
        "evolves_from": [],
      }
    pokemonDict["kyogre_primal"] = {
        "dex_number": 382,
        "species": 'kyogre',
        "gen": 6,
        "type_1": [['water', 6]],
        "type_2": [['', 6]],
        "evolves_to": [],
        "evolves_from": [],
      }
    pokemonDict["groudon_primal"] = {
        "dex_number": 383,
        "species": 'groudon',
        "gen": 6,
        "type_1": [['ground', 6]],
        "type_2": [['fire', 6]],
        "evolves_to": [],
        "evolves_from": [],
      }

  # apply type-change data
  with open(changes_fname, 'r', encoding='utf-8') as changeCSV:
    reader = csv.DictReader(changeCSV)

    for row in reader:
      pokemonName, previousType1, previousType2, genChange = row["Pokemon Name"], row["Old Type 1"], row["Old Type 2"], int(row["Gen"])

      currentType1, currentType2, gen = pokemonDict[pokemonName]["type_1"], pokemonDict[pokemonName]["type_2"], pokemonDict[pokemonName]["gen"]

      pokemonDict[pokemonName]["type_1"] = [[previousType1, gen], [currentType1, genChange]]
      pokemonDict[pokemonName]["type_2"] = [[previousType2, gen], [currentType2, genChange]]

  return pokemonDict

# add base stat data to pokemonDict
# some Pokemon forms which weren't present before (due to having the same type across forms) are added due to base stat differences; the corresponding base forms are then removed
def addBaseStatData(fnamePrefix, pokemonDict):
  with open(fnamePrefix + '1.csv', encoding='utf-8') as gen1, open(fnamePrefix + '5.csv', encoding='utf-8') as gen5, open(fnamePrefix + '6.csv', encoding='utf-8') as gen6, open(fnamePrefix + '7.csv', encoding='utf-8') as gen7, open(fnamePrefix + '8.csv', encoding='utf-8') as gen8:
    gen1Reader, gen5Reader, gen6Reader, gen7Reader, gen8Reader = csv.DictReader(gen1), csv.DictReader(gen5), csv.DictReader(gen6), csv.DictReader(gen7), csv.DictReader(gen8)

    baseStatDict = {}

    readerList = [gen1Reader, gen5Reader, gen6Reader, gen7Reader, gen8Reader]

    # i keeps track of the generation in the array gen
    # note that there are no base stat changes between gen 2 and gen 5
    gen = [1, 5, 6, 7, 8]
    i = 0

    for reader in readerList:
      for row in reader:
        # If Pokemon is new, add it to baseStatDict
        if row["Pokemon Name"] not in baseStatDict.keys():
          baseStatDict[row["Pokemon Name"]] = {
            "hp": [[int(row["hp"]), gen[i]]],
            "attack": [[int(row["attack"]), gen[i]]],
            "defense": [[int(row["defense"]), gen[i]]],
            "special_attack": [[int(row["special_attack"]), gen[i]]],
            "special_defense": [[int(row["special_defense"]), gen[i]]],
            "speed": [[int(row["speed"]), gen[i]]]
          }
        # If Pokemon is old, check for changes in its stats
        else:
          for key, value in baseStatDict[row["Pokemon Name"]].items():
            # If change is found, add that to the patch log
            if key == "dex_number":
              continue
            if int(value[-1][0]) != int(row[key]):
              value.append([int(row[key]), gen[i]])
              baseStatDict[row["Pokemon Name"]][key] = value
      i += 1

  # some forms in baseStatDict do not show up in pokemonDict currently, since the forms do not differ by type; we need to add them to the dictionary and remove the old entries after iterating over the dictionary once; we keep track of the forms in formList
  formList = []

  for pokemonName in pokemonDict.keys():
    # pokemon form is in the list of pokemon by type, so it will show up in both pokemonDict and baseStatDict
    try:
      for stat in baseStatDict[pokemonName].keys():
          pokemonDict[pokemonName][stat] = baseStatDict[pokemonName][stat]
    # KeyErrors will occur because pokemonName is in pokemonDict but not in baseStatDict; the latter has more form data
    except KeyError:
      # in case (a), formNames will be empty since baseStatDict has the species name, not the form name; in case (b), it will be the list of formNames, and pokemonName will be the species name
      formNames = [formName for formName in baseStatDict.keys() if pokemonName in formName]

      # case (a)
      if len(formNames) == 0:
        # g_max forms are only in the type .csv, as g_max doesn't change base stats (except double HP, which isn't in the Bulbapedia table)
        if 'g_max_' not in pokemonName:
          formName, pokemonName = pokemonName, pokemonName.split('_')[0]
        else:
          formName, pokemonName = pokemonName, '_'.join(pokemonName.split('_')[2:])
        for stat in baseStatDict[pokemonName].keys():
          pokemonDict[formName][stat] = baseStatDict[pokemonName][stat]
      else:
        formList.append([pokemonName, formNames])
      continue

  # add new forms to pokemonDict and remove species
  for forms in formList:
    # forms looks like [pokemonName, [formName1, formName2, ...]]
    pokemonName, formNames = forms

    for formName in formNames:
      # we're considering formName because it didn't show up in the pokemonByType.csv file; this means that the current data (e.g. species, gen, typing) of pokemonName doesn't vary between forms, so formName and pokemonName should have the same data
      pokemonDict[formName] = copy.deepcopy(pokemonDict[pokemonName])

      # enter base stat data for formName
      for stat in baseStatDict[formName].keys():
          pokemonDict[formName][stat] = baseStatDict[formName][stat]

    # remove pokemonName from pokemonDict, leaving all the forms we just entered
    del pokemonDict[pokemonName]

  return

# the notes are somewhat inconsistent, so there are a few different exceptions to consider
def parseAbilityNote(description):
  # Notes of the form 'Generation {gen} onwards', indicating a Pokemon gained a new ability
  if re.search(r'Generation (IV|V|VI|VII|VIII) onwards', description):
    gen = genSymbolToNumber(description.split()[1])
    return ['New ability', gen]
  # Notes of the form 'Hidden Ability is {ability} in Generation(s) {gen}'
  elif re.search(r'Hidden Ability is (\w+(\s\w+)*) in Generation(s*) (\w+)(-\w+)*', description):
    words = description.split()
    ability = ' '.join(words[3:-3:])
    generations = words[-1].split('-')
    startGen, endGen = genSymbolToNumber(generations[0]), genSymbolToNumber(generations[-1])
    return ['Changed hidden ability', parseName(ability), startGen, endGen]
  # Only other cases are Gengar and Basculin, which we will handle outside this code
  else:
    return description

# make initial ability dict
def addAbilityData(fname, pokemonDict):
  pokemonAbilityDict = {}

  with open(fname, encoding='utf-8') as abilitiesCSV, open(fname.removesuffix('.csv') + 'Notes.csv', encoding='utf-8') as notesCSV:
    reader = csv.DictReader(abilitiesCSV)
    notesReader = csv.DictReader(notesCSV)

    for row in reader:
      if row["Pokemon Name"] != "Pokemon Name":
        dexNumber = row["Dex Number"]
        if dexNumber != '':
          dexNumber = int(dexNumber)

        pokemonAbilityDict[row["Pokemon Name"]] = {
          # dex number will be used to keep track of form differences later
          "dex_number": dexNumber,
          "ability_1": [[row["Ability 1"], max(int(row['Gen']), 3)]],
          "ability_2": [[row["Ability 2"], max(int(row['Gen']), 3)]],
          "ability_hidden": [[row["Hidden"], max(int(row['Gen']), 5)]]
        }

    # Go through majority of notes; handle Gengar
    for note in notesReader:
      action = parseAbilityNote(note["Description"])
      pokemonName = note["Pokemon Name"]
      header = note["Header"]

      # action denotes adding a new ability, ['New Ability', gen]
      if action[0] == 'New ability':
        startGen = action[1]
        # This -1 is due to the structure of the Bulbapedia table: the notes for 'Changed hidden ability' come before those for 'New ability'. The former note moves the ability described by 'New Ability' to the end of the array, so the index of -1 refers to that
        # If the 'Changed hidden ability' did not occur, then the length of the list is 1, so the indices 0 and -1 refer to the same value
        if header == 'hidden':
          header = 'ability_hidden'

        pokemonAbilityDict[pokemonName][header][-1][1] = startGen

      # action denotes change in hidden ability, ['Changed hidden ability', ability, startGen, endGen]
      elif action[0] == 'Changed hidden ability':
        currentHiddenAbility = pokemonAbilityDict[pokemonName]["ability_hidden"][0][0]
        oldHiddenAbility = action[1]
        startGen = action[2]
        endGen = action[3]
        # the currently listed hidden ability starts in endGen + 1
        pokemonAbilityDict[pokemonName]["ability_hidden"] = [[oldHiddenAbility, startGen], [currentHiddenAbility, endGen + 1]]

  # Exception for Gengar since his note is unique
  pokemonAbilityDict["gengar"]["ability_1"] = [["levitate", 3], ["cursed_body", 7]]
  
  # some forms in pokemonAbilityDict do not show up in pokemonDict currently, since the forms do not differ by type; we need to add them to the dictionary and remove the old entries after iterating over the dictionary once; we keep track of the forms in formList
  formList = []
  
  for pokemonName in pokemonDict.keys():
    try:
      for abilitySlot in pokemonAbilityDict[pokemonName].keys():
        pokemonDict[pokemonName][abilitySlot] = pokemonAbilityDict[pokemonName][abilitySlot]
        
    # a KeyError will occur when pokemonName doesn't belong to one of the dictionaries due to either: (a) pokemonAbilityDict has species name but pokemonName is form name, or (b) pokemonAbilityDict has form name but pokemonName is species name
    except KeyError:
      # in case (a), formNames will be empty since pokemonAbilityDict has the species name; in case (b), it will be the list of formNames, and pokemonName will be the species name
      formNames = [formName for formName in pokemonAbilityDict.keys() if pokemonName in formName]

      # case (a)
      if len(formNames) == 0:
        # g_max forms are only in the type .csv, as g_max doesn't change ability
        if 'g_max_' not in pokemonName:
          formName, pokemonName = pokemonName, pokemonName.split('_')[0]
        else:
          formName, pokemonName = pokemonName, '_'.join(pokemonName.split('_')[2:])
        for abilitySlot in pokemonAbilityDict[pokemonName].keys():
          pokemonDict[formName][abilitySlot] = pokemonAbilityDict[pokemonName][abilitySlot]
      else:
        formList.append([pokemonName, formNames])
      continue
  
  # add new forms to pokemonDict and remove species
  for forms in formList:
    # forms looks like [pokemonName, [formName1, formName2, ...]]
    pokemonName, formNames = forms

    for formName in formNames:
      # we're considering formName because it didn't show up in the pokemonByType.csv file; this means that the current data (e.g. species, gen, typing) of pokemonName doesn't vary between forms, so formName and pokemonName should have the same data
      pokemonDict[formName] = copy.deepcopy(pokemonDict[pokemonName])

      # enter base stat data for formName
      for abilitySlot in pokemonAbilityDict[formName].keys():
          pokemonDict[formName][abilitySlot] = pokemonAbilityDict[formName][abilitySlot]

    # remove pokemonName from pokemonDict, leaving all the forms we just entered
    del pokemonDict[pokemonName]

  return

# add data about evolution relations between Pokemon to pokemonDict
def addEvolutionData(fname, pokemonDict):
  with open(fname, 'r', encoding='utf-8') as evolutionCSV:
    reader = csv.DictReader(evolutionCSV)

    for row in reader:
      pokemon1, method12, pokemon2, method23, pokemon3 = row["Pokemon 1 Name"], row["1 to 2 Method"], row["Pokemon 2 Name"], row["2 to 3 Method"], row["Pokemon 3 Name"]

      # special case for silvally
      if pokemon2 == 'silvally':
        for type in typeList():
          if type == '???':
            continue

          pokemonDict[pokemon1]["evolves_to"].append([pokemon2 + '_' + type, method12])
          pokemonDict[pokemon2 + '_' + type]["evolves_from"].append([pokemon1, method12])
        continue

      if pokemon2 != '':
        pokemonDict[pokemon1]["evolves_to"].append([pokemon2, method12])
        pokemonDict[pokemon2]["evolves_from"].append([pokemon1, method12])
      if pokemon3 != '':
        pokemonDict[pokemon2]["evolves_to"].append([pokemon3, method23])
        pokemonDict[pokemon3]["evolves_from"].append([pokemon2, method23])

  return

# add height/weight data
def addHeightWeightData(fname, pokemonDict):
  with open(fname, 'r', encoding='utf-8') as bmiCSV:
    reader = csv.DictReader(bmiCSV)

    for row in reader:
      pokemonName, height, weight = row["Pokemon Name"], float(row["Height m"]), float(row["Weight kg"])

      try:
        pokemonDict[pokemonName]["height"], pokemonDict[pokemonName]["weight"] = height, weight
      # indicates height/weight .csv doesn't have the form of Pokemon, so the forms don't differ in terms of weight and height
      except KeyError:
        formNames = [formName for formName in pokemonDict.keys() if pokemonName in formName]

        for formName in formNames:
          pokemonDict[formName]["height"], pokemonDict[formName]["weight"] = height, weight
        continue

  return

# add mega/regional/gmax flags, and restore dex numbers to such forms
def addFormFlags(pokemonDict):
  # initialization
  for pokemonName in pokemonDict.keys():
    pokemonDict[pokemonName]["form_data"] = {}

  for pokemonName in pokemonDict.keys():
    if '_mega' in pokemonName:
      # will include '_x' and '_y' forms
      baseForm = pokemonName.split('_')[0]
      formType = 'mega'
    elif '_alola' in pokemonName:
      baseForm = '_'.join(pokemonName.split('_')[:-1])
      formType = 'alola'
    elif '_galar' in pokemonName:
      # will include 'darmanitan_standard' and 'darmanitan_zen'
      baseForm = '_'.join(pokemonName.split('_')[:-1])
      formType = 'galar'
    elif 'g_max_' in pokemonName:
      baseForm = '_'.join(pokemonName.split('_')[2:])
      formType = 'g_max'
    else:
      continue
    
    # baseForm and pokemonName refer to each other through "form_data"
    pokemonDict[baseForm]["form_data"][formType] = pokemonName
    pokemonDict[pokemonName]["form_data"]["base_form"] = baseForm

    # add in dex number for pokemonName, which won't have a dex number yet
    pokemonDict[pokemonName]["dex_number"] = pokemonDict[baseForm]["dex_number"]
  return

def checkPokeAPIForms(fname, pokemonDict):
  pokemonNames = set(pokemonDict.keys())
  pokeapiConversionDict = {}
  for pokemonName in pokemonNames:
    pokeapiConversionDict[pokemonName] = []

  print(fname)
  with open(fname, 'r', encoding='utf-8') as pokeAPIcsv:
    reader = csv.DictReader(pokeAPIcsv)
    for row in reader:
      pokeapiName, pokeapiID = row["PokeAPI Name"], row["PokeAPI ID"]

      parsedPokeapiName = parseName(pokeapiName, 'pokemon')
      if parsedPokeapiName.split('_')[-1] == 'gmax':
        pokemonName = 'g_max_' + '_'.join(parsedPokeapiName.split('_')[:-1])
      else:
        pokemonName = parsedPokeapiName

      if pokemonName not in pokemonNames:
        print(pokemonName, pokeapiID)
      else:
        pokeapiConversionDict[pokemonName] = [pokeapiName, pokeapiID]

  print(pokeapiConversionDict)
  return

def main():
  dataPath = getCSVDataPath() + '\\pokemon\\'

  type_fname = dataPath + 'pokemonByType.csv'
  type_changes_fname = dataPath + 'pokemonTypeChanges.csv'
  pokemonDict = makeInitialPokemonDict(type_fname, type_changes_fname)

  baseStat_fnamePrefix = dataPath + 'pokemonByBaseStatsGen'
  addBaseStatData(baseStat_fnamePrefix, pokemonDict)

  abilities_fname = dataPath + 'pokemonByAbilities.csv'
  addAbilityData(abilities_fname, pokemonDict)

  evolution_fname = dataPath + 'evolutionChains.csv'
  addEvolutionData(evolution_fname, pokemonDict)

  bmi_fname = dataPath + 'pokemonByWeightHeight.csv'
  addHeightWeightData(bmi_fname, pokemonDict)

  addFormFlags(pokemonDict)

  pokeapi_fname = dataPath + 'pokemonByID.csv'
  checkPokeAPIForms(pokeapi_fname, pokemonDict)

  return pokemonDict

if __name__ == '__main__':
  pokemonDict = main()

  print('Checking pokemonDict...')

  for pokemonName in pokemonDict.keys():
    type1, type2 = pokemonDict[pokemonName]["type_1"][0][0], pokemonDict[pokemonName]["type_2"][0][0] if pokemonDict[pokemonName]["type_2"][0][0] else 'normal'
    if type1 not in typeList():
      print('Inconsistent type name', pokemonName, type1)
    if type2 not in typeList():
      print('Inconsistent type name', pokemonName, type2)

  print('Finished pokemonDict.')