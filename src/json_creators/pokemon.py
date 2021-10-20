import csv
import re
import copy
from utils import parseName, genSymbolToNumber, getBulbapediaDataPath, genSymbolToNumber


# make initial Pokemon dict, with dex number, gen, species, and type data
# the pokemonByType.csv doesn't contain all the Pokemon forms, since some different forms of the same Pokemon can have the same type. We will rectify this in future functions; for example, base stat data will add in the forms of deoxys since those have different base stats
def makeInitialPokemonDict(fname, changes_fname):
  pokemonDict = {} 

  with open(fname, 'r', encoding='utf-8') as typeCSV:
    reader = csv.DictReader(typeCSV)

    for row in reader:
      gen, dexNumber, speciesName, pokemonName, type1, type2 = row["Gen"], row["Dex Number"], row["Species Name"], row["Pokemon Name"], row["Type 1"], row["Type 2"]
      pokemonDict[pokemonName] = {
        "dex_number": dexNumber,
        "species": speciesName,
        "gen": gen,
        "type1": [[type1, gen]],
        "type2": [[type2, gen]]
      }

  # apply type-change data
  with open(changes_fname, 'r', encoding='utf-8') as changeCSV:
    reader = csv.DictReader(changeCSV)

    for row in reader:
      pokemonName, previousType1, previousType2, genChange = row["Pokemon Name"], row["Old Type 1"], row["Old Type 2"], row["Gen"]

      currentType1, currentType2, gen = pokemonDict[pokemonName]["type1"], pokemonDict[pokemonName]["type2"], pokemonDict[pokemonName]["gen"]

      pokemonDict[pokemonName]["type1"] = [[previousType1, gen], [currentType1, genChange]]
      pokemonDict[pokemonName]["type2"] = [[previousType2, gen], [currentType2, genChange]]

  for pokemonName in pokemonDict:
    if len(pokemonDict[pokemonName]["gen"]) > 1:
      print(pokemonDict[pokemonName])

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
            "hp": [[row["hp"], gen[i]]],
            "attack": [[row["attack"], gen[i]]],
            "defense": [[row["defense"], gen[i]]],
            "special_attack": [[row["special_attack"], gen[i]]],
            "special_defense": [[row["special_defense"], gen[i]]],
            "speed": [[row["speed"], gen[i]]]
          }
        # If Pokemon is old, check for changes in its stats
        else:
          for key, value in baseStatDict[row["Pokemon Name"]].items():
            # If change is found, add that to the patch log
            if key == "dex_number":
              continue
            if value[-1][0] != row[key]:
              value.append([row[key], gen[i]])
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
      # get the different form names in baseStatDict
      formNames = [formName for formName in baseStatDict.keys() if pokemonName in formName]
      formList.append([pokemonName, formNames])

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
        pokemonAbilityDict[row["Pokemon Name"]] = {
          # dex number will be used to keep track of form differences later
          "dex_number": row["Dex Number"],
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
        formName, pokemonName = pokemonName, pokemonName.split('_')[0]
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

  print(pokemonDict['indeedee_f'])
  print(pokemonDict['indeedee_m'])
  print(pokemonDict['chandelure'])
  print(pokemonDict['gengar'])

  return


def main():
  dataPath = getBulbapediaDataPath() + '\\pokemon\\'

  type_fname = dataPath + 'pokemonByType.csv'
  type_changes_fname = dataPath + 'pokemonTypeChanges.csv'
  pokemonDict = makeInitialPokemonDict(type_fname, type_changes_fname)

  
  baseStat_fnamePrefix = dataPath + 'pokemonByBaseStatsGen'
  addBaseStatData(baseStat_fnamePrefix, pokemonDict)

  abilities_fname = dataPath + 'pokemonByAbilities.csv'
  abilityDict = addAbilityData(abilities_fname, pokemonDict)

if __name__ == '__main__':
  main()