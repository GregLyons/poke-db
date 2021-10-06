import csv
import re

# converts roman numeral for gen to arabic numeral
def genSymbolToNumber(roman):
  if roman == 'I':
    return 1
  elif roman == 'II':
    return 2
  elif roman == 'III':
    return 3
  elif roman == 'IV':
    return 4
  elif roman == 'V':
    return 5
  elif roman == 'VI':
    return 6
  elif roman == 'VII':
    return 7
  elif roman == 'VIII':
    return 8
  elif roman == 'IX':
    return 9
  else:
    raise ValueError('Not a valid gen.')

# converts dex number to gen
def dexNumberToGen(dexNumber):
  dexNumber = int(dexNumber)
  if dexNumber <= 151:
    return 1
  elif dexNumber <= 251:
    return 2
  elif dexNumber <= 386:
    return 3
  elif dexNumber <= 493: 
    return 4
  elif dexNumber <= 649:
    return 5
  elif dexNumber <= 721:
    return 6
  elif dexNumber <= 809:
    return 7
  else:
    return 8

# the notes are somewhat inconsistent, so there are a few different exceptions to consider
def parseNote(description):
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
    return ['Changed hidden ability', ability, startGen, endGen]
  # Only other cases are Gengar and Basculin, which we will handle outside this code
  else:
    return description

def makeInitialAbilityDict(fname):
  abilityDict = {}

  with open(fname, encoding='utf-8') as abilitiesCSV, open(fname.rstrip('.csv') + 'Notes.csv', encoding='utf-8') as notesCSV:
    reader = csv.DictReader(abilitiesCSV)
    notesReader = csv.DictReader(notesCSV)

    for row in reader:
      if row["Pokemon"] != "Pokemon":
        abilityDict[row["Pokemon"]] = {
          "Dex Number": row["Dex Number"],
          "Sprite URL": row["Sprite URL"],
          "Ability 1": [[row["Ability 1"], max(int(row['Introduced']), 3)]],
          "Ability 2": [[row["Ability 2"], max(int(row['Introduced']), 3)]],
          "Hidden": [[row["Hidden"], max(int(row['Introduced']), 5)]]
        }

    # Go through majority of notes; handle Gengar
    for note in notesReader:
      action = parseNote(note["Description"])
      pokemonName = note["Pokemon Name"]
      header = note["Header"]

      # action denotes adding a new ability, ['New Ability', gen]
      if action[0] == 'New ability':
        startGen = action[1]
        # This -1 is due to the structure of the Bulbapedia table: the notes for 'Changed hidden ability' come before those for 'New ability'. The former note moves the ability described by 'New Ability' to the end of the array, so the index of -1 refers to that
        # If the 'Changed hidden ability' did not occur, then the length of the list is 1, so the indices 0 and -1 refer to the same value
        abilityDict[pokemonName][header][-1][1] = startGen

      # action denotes change in hidden ability, ['Changed hidden ability', ability, startGen, endGen]
      elif action[0] == 'Changed hidden ability':
        currentHiddenAbility = abilityDict[pokemonName]["Hidden"][0][0]
        oldHiddenAbility = action[1]
        startGen = action[2]
        endGen = action[3]
        # the currently listed hidden ability starts in endGen + 1
        abilityDict[pokemonName]["Hidden"] = [[oldHiddenAbility, startGen], [currentHiddenAbility, endGen + 1]]

  # Exception for Gengar sinec his note is unique
  abilityDict["Gengar"]["Ability 1"] = [["Levitate", 3], ["Cursed Body", 7]]
  
  return abilityDict

fname = f'src\\data\\pokemonAbilities.csv'
abilityDict = makeInitialAbilityDict(fname)