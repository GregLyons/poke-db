import csv
from utils import openLink, getCSVDataPath, parseName

# In gen 1, Sp. Attack and Sp. Defense are merged into one stat, 'Special', which is after Speed rather than before
def formatGen1(csvRow):
  speed = csvRow[5]
  specialA = csvRow[6]
  specialD = csvRow[6]

  # check for top 
  if specialA == 'Special':
    specialA = 'special_attack'
    specialD = 'special_defense'
  csvRow = csvRow[:5]
  csvRow.extend([specialA, specialD, speed])

  return csvRow

# Makes .csv files for base stats in Gens 1, 5, 6, 7, and 8
# Columns are Dex Number, Pokemon Name, HP, Attack, Sp. Attack, Sp. Defense, Speed
def makeBaseStatCSVs(fnamePrefix):
  urls = [
    'https://bulbapedia.bulbagarden.net/wiki/List_of_Pok%C3%A9mon_by_base_stats_(Generation_I)', 
    'https://bulbapedia.bulbagarden.net/wiki/List_of_Pok%C3%A9mon_by_base_stats_(Generation_II-V)',
    'https://bulbapedia.bulbagarden.net/wiki/List_of_Pok%C3%A9mon_by_base_stats_(Generation_VI)',
    'https://bulbapedia.bulbagarden.net/wiki/List_of_Pok%C3%A9mon_by_base_stats_(Generation_VII)',
    'https://bulbapedia.bulbagarden.net/wiki/List_of_Pok%C3%A9mon_by_base_stats_(Generation_VIII-present)'
  ]

  genMap = [1, 5, 6, 7, 8]


  for i in range(len(genMap)):
    url = urls[i]
    gen = genMap[i]

    bs = openLink(url, 0, 10)
    table = bs.find('table', {'class':'sortable'})
    dataRows = table.findAll('tr')[1:]

    # Make CSV file
    csvFile = open((f'{fnamePrefix + str(gen)}.csv'), 'w', newline='', encoding='utf-8')
    writer = csv.writer(csvFile, quoting=csv.QUOTE_MINIMAL)
    writer.writerow(['Dex Number', 'Pokemon Name', 'hp', 'attack', 'defense', 'special_attack', 'special_defense', 'speed'])

    # Write data to file
    try: 
      for row in dataRows:
        # keep track of columns; we don't need the last two

        csvRow = []
        for cell in row.findAll(['th']):
          value = cell.get_text().rstrip('\n')
          # there's a column with no text in its rows
          if value != '' and value != ' ':
            if value == 'Pokémon':
              csvRow.append('Pokemon Name')
            elif value == '#':
              csvRow.append('Dex Number')
            else:
              csvRow.append(value.lstrip('0'))
        for cell in row.findAll(['td']):
          value = cell.get_text().rstrip('\n')
          # there's a column with no text in its rows
          if value != '':
            # if value is stat or dex entry, add it
            if value.replace('.', '').isnumeric():
              csvRow.append(value.lstrip('0'))
            # otherwise, it's a Pokemon name
            else:
              # force 'zygarde_50' instead of 'zygarde'
              pokemonName = parseName(value, 'pokemon')
              if pokemonName == 'zygarde':
                pokemonName = 'zygarde_50'
              csvRow.append(pokemonName)

        # cut off last two columns, Total and Average
        csvRow = csvRow[:-2]

        # Make gen 1 like other gens
        if (gen == 1):
          csvRow = formatGen1(csvRow)

        # On 11/17/2021, Bulbapedia changed some of its tables, and now the sprites are replaced with an error message; ignore this entry
        for entry in csvRow:
          if 'error_creating' in entry:
            csvRow.remove(entry)

        writer.writerow(csvRow)
    finally: 
      csvFile.close()

def main():
  # the function makes multiple CSVs, according to gen, all with this prefix
  dataPath = getCSVDataPath() + 'pokemon\\'
  fnamePrefix= dataPath + 'pokemonByBaseStatsGen'
  makeBaseStatCSVs(fnamePrefix)

if __name__ == '__main__':
  main()