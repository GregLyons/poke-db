from ast import parse
import csv
import re
import copy
from utils import parseName, genSymbolToNumber, getCSVDataPath, genSymbolToNumber, typeList, baseFormSuffices

# make initial Pokemon dict, with dex number, gen, species, and type data
# the pokemonByType.csv doesn't contain all the Pokemon forms, since some different forms of the same Pokemon can have the same type. We will rectify this in future functions; for example, base stat data will add in the forms of deoxys since those have different base stats
def makeInitialPokemonDict(fname, changes_fname):
  pokemonDict = {} 

  with open(fname, 'r', encoding='utf-8') as typeCSV:
    reader = csv.DictReader(typeCSV)

    for row in reader:
      gen, dexNumber, speciesName, pokemonName, type1, type2 = row["Gen"], row["Dex Number"], row["Species Name"], row["Pokemon Name"], row["Type 1"], row["Type 2"]

      if dexNumber.isnumeric():
        dexNumber = int(dexNumber)
      # indicates unknown dex number, e.g. for Hisuian pokemon
      elif dexNumber != '':
        continue

      pokemonDict[pokemonName] = {
        "dex_number": dexNumber,
        "species": speciesName,
        "gen": int(gen),
        "type_1": [[type1, int(gen)]],
        "type_2": [[type2, int(gen)]],
        "evolves_to": {},
        "evolves_from": {},
      }
    
    # partner pikachu and partner eevee
    pokemonDict["pikachu_partner"] = {
        "dex_number": 25,
        "species": 'pikachu',
        "gen": 'lgpe_only',
        "type_1": [['electric', 'lgpe_only']],
        "type_2": [['', 'lgpe_only']],
        "evolves_to": {},
        "evolves_from": {},
      }
    pokemonDict["eevee_partner"] = {
        "dex_number": 133,
        "species": 'eevee',
        "gen": 'lgpe_only',
        "type_1": [['normal', 'lgpe_only']],
        "type_2": [['', 'lgpe_only']],
        "evolves_to": {},
        "evolves_from": {},
      }
    pokemonDict["kyogre_primal"] = {
        "dex_number": 382,
        "species": 'kyogre',
        "gen": 6,
        "type_1": [['water', 6]],
        "type_2": [['', 6]],
        "evolves_to": {},
        "evolves_from": {},
      }
    pokemonDict["groudon_primal"] = {
        "dex_number": 383,
        "species": 'groudon',
        "gen": 6,
        "type_1": [['ground', 6]],
        "type_2": [['fire', 6]],
        "evolves_to": {},
        "evolves_from": {},
      }

  # apply type-change data
  with open(changes_fname, 'r', encoding='utf-8') as changeCSV:
    reader = csv.DictReader(changeCSV)

    for row in reader:
      pokemonName, previousType1, previousType2, genChange = row["Pokemon Name"], row["Old Type 1"], row["Old Type 2"], int(row["Gen"])

      currentType1, currentType2, gen = pokemonDict[pokemonName]["type_1"][0][0], pokemonDict[pokemonName]["type_2"][0][0], pokemonDict[pokemonName]["gen"]

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
        pokemonName = row["Pokemon Name"]

        # If Pokemon is new, add it to baseStatDict
        if pokemonName not in baseStatDict.keys():

          # from gens 2 to 5, there are no stat changes. Thus, we need pokemonGen to keep track of when the Pokemon was introduced. If we just use gen[i], then e.g. "turtwig" would have "hp": [[55, 5]] rather than [[55, 4]].
          if gen[i] == 5:
            if pokemonName in pokemonDict.keys():
              pokemonGen = pokemonDict[pokemonName]["gen"]
            # hard code exceptions since there's not many
            else:
              if pokemonName == 'castform' or 'deoxys' in pokemonName:
                pokemonGen = 3
              elif 'giratina' in pokemonName or 'shaymin' in pokemonName or pokemonName in ['burmy', 'arceus']:
                pokemonGen = 4
              else:
                pokemonGen = 5
          else:
            pokemonGen = gen[i]

          baseStatDict[pokemonName] = {
            "gen": gen[i],
            "hp": [[int(row["hp"]), pokemonGen]],
            "attack": [[int(row["attack"]), pokemonGen]],
            "defense": [[int(row["defense"]), pokemonGen]],
            "special_attack": [[int(row["special_attack"]), pokemonGen]],
            "special_defense": [[int(row["special_defense"]), pokemonGen]],
            "speed": [[int(row["speed"]), pokemonGen]]
          }
        # If Pokemon is old, check for changes in its stats
        else:
          for key, value in baseStatDict[pokemonName].items():
            # If change is found, add that to the patch log
            if key in ['dex_number', 'gen']:
              continue
            if int(value[-1][0]) != int(row[key]):
              value.append([int(row[key]), gen[i]])
              baseStatDict[row["Pokemon Name"]][key] = value
      i += 1

  # some forms in baseStatDict do not show up in pokemonDict currently and vice versa, we need to add the forms to the dictionary and remove the less specific species names
  formList = []

  for pokemonName in pokemonDict.keys():
    # pokemon form is in the list of pokemon by type, so it will show up in both pokemonDict and baseStatDict
    try:
      for stat in baseStatDict[pokemonName].keys():
        pokemonDict[pokemonName][stat] = baseStatDict[pokemonName][stat]

    # KeyErrors will occur because pokemonName is not in baseStatDict
    except KeyError:
      # in case (a), formNames will be empty since baseStatDict has the species name, not the form name; in case (b), it will be the list of formNames, and pokemonName will be the species name
      formNames = [formName for formName in baseStatDict.keys() if pokemonName in formName]

      # case (a)
      if len(formNames) == 0:
        # exception for gmax pokemon: gmax Pokemon have the same base stats as their base form counterparts (aside from double hp, which we won't store); generally, we won't need the 'else' clause, but for toxtricity_low_key_gmax and toxtricity_amped_gmax, whose base forms ARE in baseStatDict, the assignment of formName, pokemonName is incorrect, so we need the 'else' clause for that case.
        if 'toxtricity' not in pokemonName or '_gmax' not in pokemonName:
          formName, pokemonName = pokemonName, pokemonName.split('_')[0]
        else:
          formName, pokemonName = pokemonName, '_'.join(pokemonName.split('_')[:-1])
      
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

      # The form may have been added later, so we actually want the gen in which the form was added, rather than that of the base form.
      pokemonDict[formName]["gen"] = baseStatDict[formName]["gen"]

      # enter base stat data for formName
      for stat in baseStatDict[formName].keys():
          pokemonDict[formName][stat] = baseStatDict[formName][stat]

    # remove pokemonName from pokemonDict, leaving all the forms we just entered
    del pokemonDict[pokemonName]

  # there remain forms which show up in baseStatDict but not in pokemonDict since pokemonName may still have been in baseStatDict, so we do one more pass 
  speciesForms = {}
  for formName in baseStatDict.keys():
    # check for '_' to verify it really is a form name and not a species name
    if formName not in pokemonDict and '_' in formName:
      # exception for Mr. Mime, Mime Jr.
      if 'mime_' in formName or '_mime' in formName:
        speciesName = formName.split('_')[0] + '_' + formName.split('_')[1]
        formName = '_'.join(formName.split('_')[2:])
      else:
        speciesName = formName.split('_')[0]
        formName = '_'.join(formName.split('_')[1:])

      if speciesName not in speciesForms.keys():
        speciesForms[speciesName] = []
      speciesForms[speciesName].append(formName)

  for speciesName in speciesForms.keys():
    for formName in speciesForms[speciesName]:
      pokemonName = speciesName + '_' + formName
      pokemonDict[pokemonName] = copy.deepcopy(pokemonDict[speciesName])

      # enter base stat data for formName
      for stat in baseStatDict[pokemonName].keys():
          pokemonDict[pokemonName][stat] = baseStatDict[pokemonName][stat]
    
    # in some cases, baseStatDict has the speciesName as well as the extra form name; this means that the speciesName refers to the default form of the Pokemon, and we wish to maintain that data
    if speciesName not in baseStatDict.keys():
      del pokemonDict[speciesName]
  
  for formName in baseStatDict.keys():
    if formName not in pokemonDict and formName not in ['castform', 'burmy', 'arceus', 'oricorio', 'silvally']:
      print(formName)

  # force greninja_ash to be gen 7, not gen 6
  pokemonDict["greninja_ash"]["gen"] = 7
  pokemonDict["greninja_ash"]["type_1"] = [['water', 7]]
  pokemonDict["greninja_ash"]["type_2"] = [['dark', 7]]

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
          "gen": int(row["Gen"]),
          "dex_number": dexNumber,
          "ability_1": [[row["Ability 1"], max(int(row["Gen"]), 3)]],
          "ability_2": [[row["Ability 2"], max(int(row["Gen"]), 3)]],
          "ability_hidden": [[row["Hidden"], max(int(row["Gen"]), 5)]]
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
        # exception for gmax pokemon: gmax Pokemon have the same abilities as their base form counterparts; generally, we won't need the 'else' clause, but for toxtricity_low_key_gmax and toxtricity_amped_gmax, whose base forms ARE in pokemonAbilityDict, the assignment of formName, pokemonName is incorrect, so we need the 'else' clause for that case.
        if 'toxtricity' not in pokemonName or '_gmax' not in pokemonName:
          formName, pokemonName = pokemonName, pokemonName.split('_')[0]
        else:
          formName, pokemonName = pokemonName, '_'.join(pokemonName.split('_')[:-1])

        for abilitySlot in [keyName for keyName in pokemonAbilityDict[pokemonName].keys() if keyName not in ['gen', 'dex_number']]:
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

      # For new forms, pokemonAbilityDict contains the gen, so we need to overwrite that field in pokemonDict. Otherwise, e.g. pikachu_phd cosplay (gen 6) would have gen 1 instead, since we copied it from Pikachu.
      pokemonDict[formName]["gen"] = pokemonAbilityDict[formName]["gen"]

      # enter base stat data for formName
      for abilitySlot in pokemonAbilityDict[formName].keys():
          pokemonDict[formName][abilitySlot] = pokemonAbilityDict[formName][abilitySlot]

    # remove pokemonName from pokemonDict, leaving all the forms we just entered
    del pokemonDict[pokemonName]

  

  # there remain forms which show up in pokemonAbilityDict but not in pokemonDict since pokemonName may still have been in pokemonAbilityDict, so we do one more pass 
  speciesForms = {}
  for formName in pokemonAbilityDict.keys():
    # check for '_' to verify it really is a form name and not a species name
    if formName not in pokemonDict and '_' in formName:
      speciesName = formName.split('_')[0]
      formName = '_'.join(formName.split('_')[1:])

      if speciesName not in speciesForms.keys():
        speciesForms[speciesName] = []
      speciesForms[speciesName].append(formName)

  for speciesName in speciesForms.keys():
    for formName in speciesForms[speciesName]:
      pokemonName = speciesName + '_' + formName
      pokemonDict[pokemonName] = copy.deepcopy(pokemonDict[speciesName])

      # For new forms, pokemonAbilityDict contains the gen, so we need to overwrite that field in pokemonDict. Otherwise, e.g. pikachu_phd cosplay (gen 6) would have gen 1 instead, since we copied it from Pikachu.
      pokemonDict[pokemonName]["gen"] = pokemonAbilityDict[speciesName]["gen"]

      # enter ability data for formName
      for abilitySlot in pokemonAbilityDict[pokemonName].keys():
          pokemonDict[pokemonName][abilitySlot] = pokemonAbilityDict[pokemonName][abilitySlot]
    
    # in some cases, abilityDict has the speciesName as well as the extra form name; this means that the speciesName refers to the default form of the Pokemon, and we wish to maintain that data
    if speciesName not in pokemonAbilityDict.keys():
      del pokemonDict[speciesName]
  
  for formName in pokemonAbilityDict.keys():
    if formName not in pokemonDict and formName not in ['castform', 'burmy', 'arceus', 'oricorio', 'silvally', 'pumpkaboo', 'gourgeist']:
      print(formName)

  # force rename pikachu_with_partner_cap to pikachu_partner_cap; we couldn't have this before, since the above algorithm would overwrite pikachu_partner with pikachu_with_partner_cap
  pokemonDict["pikachu_partner_cap"] = copy.deepcopy(pokemonDict["pikachu_with_partner_cap"])
  del pokemonDict["pikachu_with_partner_cap"]

  return

# add data about evolution relations between Pokemon to pokemonDict
def addEvolutionData(fname, pokemonDict):
  with open(fname, 'r', encoding='utf-8') as evolutionCSV:
    reader = csv.DictReader(evolutionCSV)

    for row in reader:
      pokemon1, method12, pokemon2, method23, pokemon3 = row["Pokemon 1 Name"], row["1 to 2 Method"], row["Pokemon 2 Name"], row["2 to 3 Method"], row["Pokemon 3 Name"]

      # evolution data is only valid in a given gen so long as the Pokemon involved in the relationship have been released
      if pokemon1 in pokemonDict.keys():
        gen1 = pokemonDict[pokemon1]["gen"]
      if pokemon2 in pokemonDict.keys():
        gen2 = pokemonDict[pokemon2]["gen"]
      if pokemon3 in pokemonDict.keys():
        gen3 = pokemonDict[pokemon3]["gen"]

      # special case for silvally
      if pokemon2 == 'silvally':
        for type in typeList():
          if type == '???':
            continue

          pokemonDict[pokemon1]["evolves_to"][pokemon2 + '_' + type] = [[ method12, max(gen1, gen2)]]
          pokemonDict[pokemon2 + '_' + type]["evolves_from"][pokemon1] = [[method12, max(gen1, gen2)]]
        continue
      

      # we need to check for duplicates, which occur whenever the chain splits; e.g. pikachu has two chains, both starting at pichu
      if pokemon2 != '':
        # 1 -> 2 duplicates
        duplicate12to = pokemon2 in pokemonDict[pokemon1]["evolves_to"].keys() and [method12, max(gen1, gen2)] in pokemonDict[pokemon1]["evolves_to"][pokemon2]
        duplicate12from = pokemon1 in pokemonDict[pokemon2]["evolves_from"].keys() and [method12, max(gen1, gen2)] in pokemonDict[pokemon2]["evolves_from"][pokemon1]

        if not duplicate12to:
          # initialize entry
          if pokemon2 not in pokemonDict[pokemon1]["evolves_to"].keys():
            pokemonDict[pokemon1]["evolves_to"][pokemon2] = []

          pokemonDict[pokemon1]["evolves_to"][pokemon2].append([method12, max(gen1, gen2)])

        if not duplicate12from:
          # initialize entry
          if pokemon1 not in pokemonDict[pokemon2]["evolves_from"].keys():
            pokemonDict[pokemon2]["evolves_from"][pokemon1] = []

          pokemonDict[pokemon2]["evolves_from"][pokemon1].append([method12, max(gen1, gen2)])

      if pokemon3 != '':
        # 2 -> 3 duplicates
        duplicate23to = pokemon3 in pokemonDict[pokemon2]["evolves_to"].keys() and [method23, max(gen2, gen3)] in pokemonDict[pokemon2]["evolves_to"][pokemon3]
        duplicate23from = pokemon2 in pokemonDict[pokemon3]["evolves_from"].keys() and [method23, max(gen2, gen3)] in pokemonDict[pokemon3]["evolves_from"][pokemon2]

        if not duplicate23to:
          # initialize entry
          if pokemon3 not in pokemonDict[pokemon2]["evolves_to"].keys():
            pokemonDict[pokemon2]["evolves_to"][pokemon3] = []

          pokemonDict[pokemon2]["evolves_to"][pokemon3].append([method23, max(gen2, gen3)])

        if not duplicate23from:
          # initialize entry
          if pokemon2 not in pokemonDict[pokemon3]["evolves_from"].keys():
            pokemonDict[pokemon3]["evolves_from"][pokemon2] = []

          pokemonDict[pokemon3]["evolves_from"][pokemon2].append([method23, max(gen2, gen3)])

  # Spiky eared pichu gets gen 2 instead of 4 because we copy from pichu in pokemonDict. The ability gens are appropriate, but we need to change the other fields.
  pokemonDict["pichu_spiky_eared"]["gen"] = 4
  pokemonDict["pichu_spiky_eared"]["type_1"] = [["electric", 4]]
  pokemonDict["pichu_spiky_eared"]["type_2"] = [["", 4]]

  # 

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

# 
def checkPokeAPIForms(fname, pokemonDict):
  pokemonNames = set(pokemonDict.keys())
  pokeapiConversionDict = {}
  for pokemonName in pokemonNames:
    pokeapiConversionDict[pokemonName] = []

  with open(fname, 'r', encoding='utf-8') as pokeAPIcsv:
    reader = csv.DictReader(pokeAPIcsv)

    for row in reader:
      pokeapiName, pokeapiID = row["PokeAPI Form Name"], int(row["PokeAPI ID"])

      # take urshifu-single-strike as default
      parsedPokeapiName = parseName(pokeapiName, 'pokemon').replace('_single_strike', '').replace('_hero', '').replace('_rider', '')
      # gmax
      if parsedPokeapiName.split('_')[-1] == 'gmax':
        pokemonName = '_'.join(parsedPokeapiName.split('_')[:-1]) + '_gmax'
      # gender
      elif parsedPokeapiName.split('_')[-1] == 'male':
        pokemonName = '_'.join(parsedPokeapiName.split('_')[:-1]) + '_m'
      elif parsedPokeapiName.split('_')[-1] == 'female':
        pokemonName = '_'.join(parsedPokeapiName.split('_')[:-1]) + '_f'
      # silvally and arceus
      elif parsedPokeapiName in ['silvally', 'arceus']:
        pokemonName = parsedPokeapiName + '_normal'
      # mimikyu
      elif parsedPokeapiName == 'mimikyu_disguised':
        pokemonName = 'mimikyu'
      # ash greninja
      elif 'battle_bond' in parsedPokeapiName:
        pokemonName = 'greninja_ash'
      # ignore totem pokemon
      elif '_totem' in parsedPokeapiName:
        continue
      # various pokemon default forms
      elif parsedPokeapiName == 'burmy':
        pokemonName = 'burmy_plant'
      elif parsedPokeapiName in ['shellos', 'gastrodon']:
        pokemonName = parsedPokeapiName + '_west'
      elif parsedPokeapiName in ['deerling', 'sawsbuck']:
        pokemonName = parsedPokeapiName + '_spring'
      elif parsedPokeapiName == 'cherrim':
        pokemonName = 'cherrim_overcast'
      elif parsedPokeapiName == 'castform':
        pokemonName = 'castform_normal'
      elif parsedPokeapiName == 'zygarde':
        pokemonName = 'zygarde_50'
      elif parsedPokeapiName == 'furfrou_natural':
        pokemonName = 'furfrou'
      else:
        pokemonName = parsedPokeapiName

      # add new forms
      if pokemonName not in pokemonNames:
        # pikachu
        if 'pikachu' in pokemonName:
          # LGPE
          if 'partner' in pokemonName:
            baseFormName = 'pikachu_partner'
            formGen = 7
          else:
            baseFormName = 'pikachu'
            # cap
            if 'cap' in pokemonName:
              formGen = 7
            # cosplay
            else:
              formGen = 6

        # minior
        elif 'minior' in pokemonName:
          miniorColor = pokemonName.split('_')[1]
          formGen = 7
          if 'meteor' in pokemonName:
            pokemonName = 'minior_meteor_' + miniorColor
            baseFormName = 'minior_meteor'
          else:
            pokemonName = 'minior_' + miniorColor
            baseFormName = 'minior'

        elif pokemonName.split('_')[0] in ['magearna', 'unown', 'spewpa', 'scatterbug', 'vivillon', 'furfrou', 'flabebe', 'floette', 'florges', 'sinistea', 'genesect', 'mothim', 'polteageist', 'zarude', 'xerneas', 'arceus']:
          baseFormName = pokemonName.split('_')[0]

          if 'arceus' not in pokemonName:
            formGen = int(pokemonDict[pokemonName.split('_')[0]]["gen"])
          # arceus-???, i.e. arceus unknown
          else:
            baseFormName = 'arceus_normal'
            formGen = 4

        else:
          print(pokemonName, pokeapiID, 'PokeAPI name not handled!')
          continue
        
        formData = [baseFormName, int(formGen)]
      else:
        formData = [None, None]

      pokeapiConversionDict[pokemonName] = [pokeapiName, pokeapiID, formData]
    
  # add PokeAPI conversion data to pokemonDict
  for pokemonName in pokeapiConversionDict.keys():
    if pokemonName in pokemonDict:
      pokemonDict[pokemonName]["pokeapi"] = pokeapiConversionDict[pokemonName][:2]
    else:
      pokeapiName, pokeapiID, formData = pokeapiConversionDict[pokemonName]
      baseFormName, formGen = formData

      pokemonDict[pokemonName] = copy.deepcopy(pokemonDict[baseFormName])
      pokemonDict[pokemonName]["gen"] = int(formGen)
      pokemonDict[pokemonName]["pokeapi"] = [pokeapiName, pokeapiID]

  # # Remove unown and make unown_a the base form.
  # pokemonDict["unown_a"] = copy.deepcopy(pokemonDict["unown"])
  # del pokemonDict["unown"]

  # # Remove mothim and make mothim_plant the base form.
  # pokemonDict["mothim_plant"] = copy.deepcopy(pokemonDict["mothim"])
  # del pokemonDict["mothim"]

  # # Remove scatterbug/spewpa/vivillon and make scatterbug/spewpa/vivillon_icy_snow the base form.
  # pokemonDict["scatterbug_icy_snow"] = copy.deepcopy(pokemonDict["scatterbug"])
  # del pokemonDict["scatterbug"]
  # pokemonDict["spewpa_icy_snow"] = copy.deepcopy(pokemonDict["spewpa"])
  # del pokemonDict["spewpa"]
  # pokemonDict["vivillon_icy_snow"] = copy.deepcopy(pokemonDict["vivillon"])
  # del pokemonDict["vivillon"]

  # # Remove flabebe/floette/florges and make flabebe/floette/florges-red the base form.
  # pokemonDict["flabebe_red"] = copy.deepcopy(pokemonDict["flabebe"])
  # del pokemonDict["flabebe"]
  # pokemonDict["floette_red"] = copy.deepcopy(pokemonDict["floette"])
  # del pokemonDict["floette"]
  # pokemonDict["florges_red"] = copy.deepcopy(pokemonDict["florges"])
  # del pokemonDict["florges"]

  for pokemonName in pokemonDict.keys():
    pokemonDict[pokemonName]["gen"] = int(pokemonDict[pokemonName]["gen"])

  return

# add mega/regional/gmax flags, and restore dex numbers to such forms
# For mega evolutions, add mega-stone requirements
def addFormFlags(pokemonDict):
  # Force unown_a to be 

  # Dictionary for keeping track of Megas; will add mega stone requirements at end
  megas = {}

  # initialization
  for pokemonName in pokemonDict.keys():
    pokemonDict[pokemonName]["form_data"] = {}

  for pokemonName in pokemonDict.keys():
    baseFormName = pokemonName
    isBaseForm = False

    if '_mega' in pokemonName:
      # will include '_x' and '_y' forms
      baseFormName = pokemonName.split('_')[0]
      formType = 'mega'

      # Keep track of megas for later
      megas[baseFormName] = pokemonName

    # ignore pikachu_alola_cap
    elif '_alola' in pokemonName and '_alola_cap' not in pokemonName:
      baseFormName = '_'.join(pokemonName.split('_')[:-1])
      formType = 'alola'
    elif '_galar' in pokemonName:
      # will include 'darmanitan_standard' and 'darmanitan_zen'
      baseFormName = '_'.join(pokemonName.split('_')[:-1])
      formType = 'galar'
    elif 'gmax' in pokemonName:
      baseFormName = '_'.join(pokemonName.split('_')[:-1])
      formType = 'gmax'
    else:
      # we'll use speciesName to eliminate a lot of the Pokemon which don't have alternate forms
      speciesName = pokemonDict[pokemonName]["species"]

      # check if pokemon species/base form name is one word
      if '_' not in speciesName:
        # if speciesName belongs to pokemonDict, then that is the base form
        if pokemonDict[pokemonName]["species"] in pokemonDict.keys():
          baseFormName = speciesName
          if baseFormName == pokemonName:
            isBaseForm = True
          else:
            formType = 'other'

        # otherwise, need to handle case-by-case
        else:
          handled = False
          for baseFormSuffix in baseFormSuffices():
            if speciesName + '_' + baseFormSuffix in pokemonDict.keys():
              handled = True

              if pokemonName in ['arceus_normal', 'silvally_normal']:
                isBaseForm = True
                continue
              if pokemonName in ['arceus_ice', 'silvally_ice']:
                isBaseForm = False
                baseFormName = speciesName + '_' + 'normal'
                formType = 'other'
                continue

              # indicates base form
              if '_' + baseFormSuffix in pokemonName:
                isBaseForm = True
                continue
              
              baseFormName = speciesName + '_' + baseFormSuffix
              formType = 'other'
            else:
              continue
          
          if not handled:
            print(pokemonName, 'not handled!')

      # Pokemon whose baseForm name includes a '_'
      else:
        isBaseForm = True

        # Currently no Pokemon satisfy this condition; this is for next gen when new Pokemon are introduced. Then we'll figure out what to do with them.
        if not pokemonName == speciesName:
          print(pokemonName, 'form data unhandled!')
          
        continue

    # baseForm and pokemonName refer to each other through "form_data"
    if not isBaseForm:
      baseFormGen = pokemonDict[baseFormName]["gen"]
      formGen = pokemonDict[pokemonName]["gen"]
      pokemonDict[pokemonName]["form_data"][baseFormName] = [['base', formGen]]
      pokemonDict[baseFormName]["form_data"][pokemonName] = [[formType, formGen]]

    # add in dex number for pokemonName, which won't have a dex number yet
    pokemonDict[pokemonName]["dex_number"] = pokemonDict[baseFormName]["dex_number"]

    # add in height and weight data, if not already present
    if "weight" not in pokemonDict[pokemonName].keys():
      pokemonDict[pokemonName]["weight"] = pokemonDict[baseFormName]["weight"]
    
    # g-max pokemon have unknown height, just set to 0
    if "height" not in pokemonDict[pokemonName].keys():
      if formType == 'gmax':
        pokemonDict[pokemonName]["height"] = 0
      else:
        pokemonDict[pokemonName]["height"] = pokemonDict[baseFormName]["height"]

  # Add mega stone requirements
  with open(getCSVDataPath() + '/items/megaStones.csv', encoding='utf-8') as megasCSV: 
    reader = csv.DictReader(megasCSV)

    for row in reader:
      itemName, baseFormName = row["Item Name"], row["Pokemon Name"]
      pokemonName = megas[baseFormName]
      pokemonDict[pokemonName]["requirements"] = {
        "item": { 
          itemName: [[True, 6]]
        }
      }

    # Add blue and red orb for Primal Reversion kyogre and groudon
    pokemonDict["kyogre_primal"]["requirements"] = {
        "item": { 
          'blue_orb': [[True, 6]]
        }
      }

    pokemonDict["groudon_primal"]["requirements"] = {
        "item": { 
          'red_orb': [[True, 6]]
        }
      }

    # Ultra necrozma
    pokemonDict["necrozma_ultra"]["requirements"] = {
        "item": { 
          'ultranecrozium_z': [[True, 7]]
        }
      }

    # Zacian
    pokemonDict["zacian_crowned"]["requirements"] = {
        "item": { 
          'rusted_sword': [[True, 8]]
        }
      }

    # Zamazenta
    pokemonDict["zamazenta_crowned"]["requirements"] = {
        "item": { 
          'rusted_shield': [[True, 8]]
        }
      }

  # Initialize 'form_class' field
  for pokemonName in pokemonDict.keys():
    pokemonDict[pokemonName]["form_class"] = []
  
  # Use form data to assign form classes to Pokemon.
  for pokemonName in pokemonDict.keys():
    # Assign form classes to each of the alternate forms of pokemonName.
    for formName in pokemonDict[pokemonName]["form_data"].keys():
      for patch in pokemonDict[pokemonName]["form_data"][formName]:
        # This will add 'base form' patches to base form Pokemon with multiple alternate forms. We remove the duplicates later.
        if patch not in pokemonDict[formName]["form_class"]:
          pokemonDict[formName]["form_class"].append(patch)
          
  
  # If the Pokemon has no form data (i.e. no other forms), then it is the base form. Do another pass for such Pokemon.
  for pokemonName in pokemonDict.keys():
    # Add 'base' to Pokemon with no form data.
    if len(pokemonDict[pokemonName]["form_class"]) == 0:
      pokemonGen = pokemonDict[pokemonName]["gen"]
      pokemonDict[pokemonName]["form_class"] = [['base', pokemonGen]]
    
    # For base form Pokemon with multiple alternate forms, that Pokemon will have multiple 'base form' patches. Select the one with the lowest gen.
    elif len([patch[0] for patch in pokemonDict[pokemonName]["form_class"] if patch[0] == 'base']) > 0:
      pokemonGen = pokemonDict[pokemonName]["gen"]
      pokemonDict[pokemonName]["form_class"] = [['base', pokemonGen]]

    else:
      continue
  
  # Exceptions

  # darmanitan_zen_galar has base form darmanitan_zen, but darmanitan_zen is itself not a base form (instead, darmanitan_standard)
  pokemonDict["darmanitan_zen"]["form_class"] = [['other', 5]]

  # toxtricity_low_key_gmax has base form toxtricity_low_key, but toxtricity_low_key is itself not a base form (instead, toxtricity_amped)
  pokemonDict["toxtricity_low_key"]["form_class"] = [['other', 8]]

  # urshifu_rapid_strike_gmax has base form urshifu_rapid_strike, but urshifu_rapid_strike is itself not a base form (instead, urshifu)
  pokemonDict["urshifu_rapid_strike"]["form_class"] = [['other', 8]]

  return

def addFullName(pokemonDict):
  for pokemonName in pokemonDict.keys():
    pokemonDict[pokemonName]['formatted_name'] = getFormattedName(pokemonName)

  return

def getFormattedName(pokemonName):
  nameParts = pokemonName.split('_')

  if len(nameParts) == 1 and pokemonName != 'urshifu':
    return pokemonName.title()

  speciesName = nameParts[0].title()
  formName = ' '.join([part.title() for part in nameParts[1:]])

  # further processing of form name
  # g-max
  formName = formName.replace('G Max', 'G-Max')

  # gender; ignore unown
  if speciesName != 'Unown':
    if formName == 'M':
      formName = 'Male'
    elif formName == 'F':
      formName = 'Female'

  # Zygarde
  if formName in ['10', '50']:
    formName = formName + '%'

  # Urshifu
  if 'Urshifu' in speciesName:
    if len(formName) < 3:
      formName = 'Single Strike'
    elif formName == 'G-Max':
      formName = 'Single Strike G-Max'

  # Apostrophes
  if speciesName in ['Farfetchd', 'Sirfetchd']:
    speciesName = speciesName[:-2] + "'d"

  # Hyphens
  if [speciesName, formName] in [
    ['Ho', 'Oh'],
    ['Porygon', 'Z'],
    ['Jangmo', 'O'],
    ['Hakamo', 'O'],
    ['Kommo', 'O']
  ]:
    if formName == 'O':
      formName = 'o'
    speciesName, formName = speciesName + '-' + formName, ''

    return speciesName

  # Periods
  if [speciesName, formName] in [
    ['Mr', 'Mime'],
    ['Mr', 'Rime'],
    ['Mime', 'Jr'],
  ]:
    if speciesName == 'Mime':
      speciesName, formName = speciesName + ' ' + formName + '.', ''
    else:
      speciesName, formName = speciesName + '. ' + formName, ''
  
    return speciesName

  # Mr. Mime (Galar)
  if speciesName == 'Mr' and formName == 'Mime Galar':
    return 'Mr. Mime (Galar)'

  # Colons
  if [speciesName, formName] in [
    ['Type', 'Null']
  ]:
    speciesName, formName = speciesName + ': ' + formName, ''
    
    return speciesName

  # Tapus
  if speciesName == 'Tapu':
    return speciesName + ' ' + formName

  return f'{speciesName} ({formName})'

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


  pokeapi_fname = dataPath + 'pokemonFormByID.csv'
  checkPokeAPIForms(pokeapi_fname, pokemonDict)

  addFormFlags(pokemonDict)

  addFullName(pokemonDict)
      
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