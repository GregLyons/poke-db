import csv
import urllib.request
from bs4 import BeautifulSoup

# converts roman numeral for to arabic numeral
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
def parseNote(note):
  print('hi')

def makeCSVandExtractnotes():
  url = 'https://bulbapedia.bulbagarden.net/wiki/List_of_Pok%C3%A9mon_by_Ability'

  req = urllib.request.Request(url, headers={'User-Agent' : "Magic Browser"}) 
  html = urllib.request.urlopen( req )
  bs = BeautifulSoup(html.read(), 'html.parser')

  csvFile = open((f'src\\data\\abilities\\scraping\\abilities.csv'), 'w', newline='', encoding='utf-8')
  writer = csv.writer(csvFile, quoting=csv.QUOTE_MINIMAL)

  # keep track of notes
  notes = [] 

  try:
    for gen in ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII']:

      # the page has eight separate tables, with section labelled by generation number
      findSection = bs.find('span', id=f'Generation_{gen}_families')
      # each desired table is embedded inside another table
      table = findSection.findNext('table').find('table')
      rows = table.findAll('tr')


      headers = ['Dex Number', 'Sprite URL', 'Pokemon', 'Ability 1', 'Ability 2', 'Hidden']

      for row in rows:
        csvRow = []
        headerIndex = 0

        # need to keep track of both 
        currentPokemonName = ''
        currentDexEntry = ''

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
              csvRow.append('Pokemon')
            else:
              csvRow.append(value)
          # table data
          else:
            # the data entry is a Pokemon sprite
            if cell.find('img') != None:
              csvRow.append(cell.find('img')['src'])
            else: 
              value = cell.get_text().rstrip('\n').lstrip('0').replace('*', '')
              
              # we need dex entry to know that, e.g. Crobat is in a different gen than Golbat
              if headers[headerIndex] == 'Dex Number':
                currentGen = dexNumberToGen(value)

              # keep track of Pokemon name for notes--dex entry won't suffice since Megas share dex entry
              if headers[headerIndex] == 'Pokemon':
                currentPokemonName = value

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
                  notes.append([currentPokemonName, headers[headerIndex], note.get('title')])

              csvRow.append(value)
            headerIndex += 1
        csvRow.append(currentGen)
        writer.writerow(csvRow)
  finally:
    csvFile.close()

  return notes

notes = makeCSVandExtractnotes()

for note in notes:
  print(note)