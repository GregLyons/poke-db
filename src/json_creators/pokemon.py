import csv
import re
import os
from utils import parseName, genSymbolToNumber, dexNumberToGen

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
    return ['Changed hidden ability', parseName(ability), startGen, endGen]
  # Only other cases are Gengar and Basculin, which we will handle outside this code
  else:
    return description

# make initial ability dict
def makeInitialAbilityDict(fname):
  abilityDict = {}

  with open(fname, encoding='utf-8') as abilitiesCSV, open(fname.removesuffix('.csv') + 'Notes.csv', encoding='utf-8') as notesCSV:
    reader = csv.DictReader(abilitiesCSV)
    notesReader = csv.DictReader(notesCSV)

    for row in reader:
      if row["Pokemon Name"] != "Pokemon Name":
        abilityDict[row["Pokemon Name"]] = {
          "dex_number": row["Dex Number"],
          "ability 1": [[row["Ability 1"], max(int(row['Gen']), 3)]],
          "ability_2": [[row["Ability 2"], max(int(row['Gen']), 3)]],
          "hidden": [[row["Hidden"], max(int(row['Gen']), 5)]]
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
        currentHiddenAbility = abilityDict[pokemonName]["hidden"][0][0]
        oldHiddenAbility = action[1]
        startGen = action[2]
        endGen = action[3]
        # the currently listed hidden ability starts in endGen + 1
        abilityDict[pokemonName]["hidden"] = [[oldHiddenAbility, startGen], [currentHiddenAbility, endGen + 1]]

  # Exception for Gengar sinec his note is unique
  abilityDict["gengar"]["ability_1"] = [["levitate", 3], ["cursed_body", 7]]
  
  return abilityDict

def main():
  fname = f'src\\data\\bulbapedia_data\\pokemon\\pokemonByAbilities.csv'
  abilityDict = makeInitialAbilityDict(fname)

  print(abilityDict["gengar"])
  print(abilityDict["chandelure"])

if __name__ == '__main__':
  main()