import csv
import re
from utils import openLink, genSymbolToNumber, dexNumberToGen, getCSVDataPath, parseName

# The event Blue-Striped Basculin with Rock Head is not included. My apologies for any inconvenience.

# the notes are somewhat inconsistent, so there are a few different exceptions to consider
def parseNote(note):
  description = note[2]

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
    return note

# each row is a Pokemon, and columns are Dex Number, Sprite URL, Pokemon Name, Ability 1, Ability 2, Hidden
# columns for notes .csv are pokemon name, header (e.g. Ability 1, Ability 2, etc.)
def makeAbilityCSVandExtractNotes(fname):
  url = 'https://bulbapedia.bulbagarden.net/wiki/List_of_Pok%C3%A9mon_by_Ability'
  bs = openLink(url, 0, 10)

  with open(fname, 'w', newline='', encoding='utf-8') as csvFile, open(fname.removesuffix('.csv') + 'Notes.csv', 'w', newline='', encoding='utf-8') as notesCSV:
    writer = csv.writer(csvFile, quoting=csv.QUOTE_MINIMAL)
    notesWriter = csv.writer(notesCSV, quoting=csv.QUOTE_MINIMAL)
    notesWriter.writerow(['Pokemon Name', 'Header', 'Description'])

    for gen in ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII']:

      # the page has eight separate tables, with section labelled by generation number
      findSection = bs.find('span', id=f'Generation_{gen}_families')
      # each desired table is embedded inside another table
      table = findSection.findNext('table').find('table')
      rows = table.findAll('tr')


      headers = ['Dex Number', 'Sprite URL', 'Pokemon Name', 'Ability 1', 'Ability 2', 'Hidden']

      for row in rows:
        csvRow = []
        headerIndex = 0

        # need to keep track of both 
        currentPokemonName = ''

        # table organized by Pokemon family rather than generation introduced, so, for example, Mega Venusaur shows up in the gen 1 table
        # we can determine the generation of the current pokemon based on its name
        # most of the time, the gens will line up--handle exceptions deeper inside the loop
        currentGen = genSymbolToNumber(gen)

        for cell in row.findAll(['td', 'th']):
          # table headers
          # need this since one of the columns in each has a blank header, namely the column for the pokemon sprite
          if row.find('th') != None:
            value = cell.get_text().rstrip('\n')
            if value == '':
              csvRow.append('Sprite URL')
            elif value == '#':
              csvRow.append('Dex Number')
            elif value == 'Pokémon':
              csvRow.append('Pokemon Name')
            else:
              csvRow.append(value)
          # table data
          else:
            # the data entry is a Pokemon sprite
            if cell.find('img') != None:
              csvRow.append(cell.find('img')['src'])
            else: 
              value = cell.get_text().rstrip('\n').lstrip('0').replace('*', '').replace('♂', ' Male').replace('♀', ' Female')
              
              # we need dex entry to know that, e.g. Crobat is in a different gen than Golbat
              if headers[headerIndex] == 'Dex Number':
                currentGen = dexNumberToGen(value)

              # keep track of Pokemon name for notes--dex entry won't suffice since Megas and forms share dex entry
              if headers[headerIndex] == 'Pokemon Name':
                currentPokemonName = value.replace('Sumer', 'Summer')

                # once we know the name, we can determine the current gen of the given Pokemon, if different from default
                if '(Mega ' in currentPokemonName:
                  currentGen = 6
                elif '(Alolan ' in currentPokemonName or '(Cosplay ' in currentPokemonName or 'in a cap' in currentPokemonName:
                  currentGen = 7
                elif '(Galarian ' in currentPokemonName:
                  currentGen = 8

              # the data entry has a note
              if cell.find('span', {'class': 'explain'}) != None:
                notesInCell = cell.find_all('span', {'class': 'explain'})
                for note in notesInCell:
                  notesWriter.writerow([parseName(currentPokemonName, 'pokemon'), parseName(headers[headerIndex]), note.get('title').replace('Lightningrod', 'Lightning Rod')])
              
              if headers[headerIndex] == 'Pokemon Name':
                if 'Disguised' in currentPokemonName:
                  currentPokemonName = 'Mimikyu'
                csvRow.append(parseName(currentPokemonName, 'pokemon'))
              else:
                csvRow.append(parseName(value))

            headerIndex += 1
        if row.find('th') != None:
          csvRow.append('Gen')
        else: 
          csvRow.append(currentGen)

        # rename certain pokemon
        extraFormName = csvRow[2]
        if 'eternal_flower' in extraFormName:
          csvRow[2] = csvRow[2].replace('_flower', '')
        elif extraFormName == 'rockruff_event':
          csvRow[2] = 'rockruff_own_tempo'

        # take disguised mimikyu to be the base form
        writer.writerow(csvRow)

  return

def main():
  dataPath = getCSVDataPath() + 'pokemon\\'
  fname = dataPath + f'pokemonByAbilities.csv'
  makeAbilityCSVandExtractNotes(fname)

if __name__ == '__main__':
  main()