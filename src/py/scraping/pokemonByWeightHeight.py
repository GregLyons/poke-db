import csv
import re
from utils import openLink, getCSVDataPath, parseName

# def getPokemonSpecies(fname):
#   # don't want duplicates
#   speciesSet = set() 
#   dexSet = set()

#   with open(fname, 'r', encoding='utf-8') as typeCSV:
#     reader = csv.DictReader(typeCSV)

#     for row in reader:
#       speciesName = row["Species Name"]

#       speciesSet.add(speciesName)

#   return list(speciesSet)


def makeWeightHeightCSV(fname):
  with open(fname, 'w', newline='', encoding='utf-8') as heightCSV:
    writer = csv.writer(heightCSV)
    writer.writerow(["Pokemon Name", "Height m", "Weight kg"])

    bs = openLink('https://pokemondb.net/pokedex/stats/height-weight', 0, 10)
    dataRows = bs.find('table').find_all('tr')[1:]

    for row in dataRows:
      cells = row.find_all('td')

      # indicates Pokemon that hasn't been released yet
      if cells[0].get_text() == '???':
        continue

      speciesName, height, weight = cells[1].find('a').get_text(),  cells[4].get_text(), cells[6].get_text()

      if cells[1].find('small') and 'Hisuian' not in cells[1].get_text():
       formName = ' (' + cells[1].find('small').get_text() + ')'
      else:
        formName = ''
      
      pokemonName = parseName(speciesName + formName, 'pokemon')
      
      writer.writerow([pokemonName, height, weight])

  return

def main():
  dataPath = getCSVDataPath() + '\\pokemon\\'

  # we use our pokemon by type .csv to get the list of species
  # type_fname = dataPath + 'pokemonByType.csv'
  # species = getPokemonSpecies(type_fname)

  fname = dataPath + 'pokemonByWeightHeight.csv'
  makeWeightHeightCSV(fname)

  return

if __name__ == '__main__':
  main()