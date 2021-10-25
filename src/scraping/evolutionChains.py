import csv
import re
from utils import openLink, getDataPath, parseName

# columns are Family Name, Pokemon 1 Name, 1 to 2 Method, Pokemon 2 Name, 2 to 3 Method, Pokemon 3 Name
def makeEvolutionChainCSV(fname):
  with open(fname, 'w', newline='', encoding='utf-8') as evolutionFamilyCSV:
    writer = csv.writer(evolutionFamilyCSV)

    bs = openLink('https://bulbapedia.bulbagarden.net/wiki/List_of_Pok%C3%A9mon_by_evolution_family', 0, 10)
    regions = ['Kanto', 'Johto', 'Hoenn', 'Sinnoh', 'Unova', 'Kalos', 'Alola', 'Galar']
    tables = [bs.find('span', {'id': f'{region}-based_evolution_families'}).find_next('table') for region in regions]

    # write the header
    writer.writerow(['Family Name', 'Pokemon 1 Name', '1 to 2 Method', 'Pokemon 2 Name', '2 to 3 Method', 'Pokemon 3 Name'])

    currentFamily = ''

    for table in tables:
      for row in table.find_all('tr'):
        header = row.find('th')


        # the <th> denotes the family being considered
        if header:
          currentFamily = header.get_text().rstrip('\n').replace('*', '').rstrip('family')

          # variables for working with split evolution chains
          splitPresent = False
          cellsBeforeSplit = []

          continue
        
        # we handle unown separately, since it does not follow the pattern of all the other Pokemon
        # urshifu isn't parsed properly since Bulbapedia doesn't list its form in the table
        if currentFamily == 'Unown':
          continue

        # remove blank cells
        cells = [cell for cell in row.find_all('td') if not cell.has_attr('colspan')]

        # check if there is a split in the evolution family; the cells below the split will have a rowspan attribute
        if cells[0].has_attr('rowspan'):
          # keep track of the cells before the split
          cellsBeforeSplit = []

          i = 0
          while cells[i].has_attr('rowspan'):
            cellsBeforeSplit.append(cells[i])
            i += 1

          splitPresent = True

        # after removing the blank cells, every row will have either 2 modulo 3 cells (no split) or 0 modulo 3 cells (split present) or 0 modulo 3 cells (split not present)
        # the last case indicates a cell which describes the form of the Pokemon; combine the form name with the Pokemon itself
        if len(cells) % 3 == 0 and not splitPresent:
          # extract the form name and then cut off the cell with the form name
          form = cells[-1].get_text().rstrip('\n')
          cells = cells[:-1]

          # now the last cell has the species name
          speciesName = cells[-1].get_text().rstrip('\n')

          # combine species and form name, and replace the text in the cell with the combined name
          speciesAndForm = speciesName + ' (' + form + ')'
          cells[-1].span.string.replace_with(speciesAndForm)

        # now if there are 0 modulo 3 cells, we are in a line after a split
        if len(cells) % 3 == 0 and splitPresent:
          cells = cellsBeforeSplit + cells

        # fill in the remaining cells so that they always have length 8
        while(len(cells) < 8):
          cells.append('')
        
        # finally, format the cells
        cellsText = []
        for cell in cells:
          if cell != '':
            # remove regional suffixes, and fix 'Gararian' typo in corsola
            cellsText.append(cell.get_text(separator=' ').rstrip('\n').replace('→', '').strip(' ').replace('Kantonian', '').replace('Johtonian', '').replace('Hoennian', '').replace('Unovan', '').replace('Gararian', 'Galarian'))
          else:
            cellsText.append(cell)

        currentFamily = parseName(currentFamily, 'pokemon')
        pokemon1 = parseName(cellsText[1], 'pokemon')
        # clean up methods that have sword/shield name in them
        method12 = cellsText[2].replace('Sw Sh', '(Sw/Sh)').replace('XD', '(XD)')
        pokemon2 = parseName(cellsText[4], 'pokemon')
        method13 = cellsText[5].replace('Sw Sh', '(Sw/Sh)').replace('XD', '(XD)')
        pokemon3 = parseName(cellsText[7], 'pokemon')

        # due to how pokemonDict is constructed in pokemon.py, we need to account for form names here when adding in the evolution chain data, since the format of the Bulbapedia table doesn't allow us to use the method we use in pokemon.py to reconcile form names and species names (which we used for adding ability and base stat data)
        #region
        # female burmy/wormadam
        if 'Cloak' in method12:
          cloakType = re.search(r'(Plant|Sandy|Trash) Cloak', method12).group(1)
          pokemon1 += '_' + cloakType.lower()
          pokemon2 += '_' + cloakType.lower()

        # male burmy evolves to mothim regardless of cloak
        elif pokemon1 == 'burmy':
          writer.writerow([currentFamily, pokemon1 + '_plant', method12, pokemon2, method13, pokemon3])
          writer.writerow([currentFamily, pokemon1 + '_sandy', method12, pokemon2, method13, pokemon3])
          writer.writerow([currentFamily, pokemon1 + '_trash', method12, pokemon2, method13, pokemon3])

          continue
        # cherrim forms
        elif pokemon2 == 'cherrim':
          writer.writerow([currentFamily, pokemon1, method12, pokemon2 + '_overcast', method13, pokemon3])
          writer.writerow([currentFamily, pokemon1, method12, pokemon2 + '_sunshine', method13, pokemon3])

          continue
        # shellos forms
        elif pokemon1 == 'shellos':
          # gastrodon already has sea in name on the table
          whichSea = re.search(r'(west|east)', pokemon2).group(1)
          writer.writerow([currentFamily, pokemon1 + '_' + whichSea + '_sea', method12, pokemon2, method13, pokemon3])

          continue
        # darmanitan standard
        elif 'darumaka' in pokemon1:
          if 'galar' in pokemon1:
            # need to insert standard between darmanitan and galar
            writer.writerow([currentFamily, pokemon1, method12, pokemon2.split('_')[0] + '_standard_' + pokemon2.split('_')[-1], method13, pokemon3])
          else:
            # append 'standard' to the end
            writer.writerow([currentFamily, pokemon1, method12, pokemon2 + '_standard', method13, pokemon3])

          continue
        # deerling seasons
        elif 'deerling' in pokemon1:
          whichSeason = re.search(r'(spring|summer|autumn|winter)', pokemon2).group(1)
          writer.writerow([currentFamily, pokemon1 + '_' + whichSeason, method12, pokemon2, method13, pokemon3])

          continue
        # male and female meowstic
        elif 'meowstic' in pokemon2:
          writer.writerow([currentFamily, pokemon1, method12, pokemon2 + '_m', method13, pokemon3])
          writer.writerow([currentFamily, pokemon1, method12, pokemon2 + '_f', method13, pokemon3])

          continue
        # aegislash blade and shield
        elif 'aegislash' in pokemon3:
          writer.writerow([currentFamily, pokemon1, method12, pokemon2, method13, pokemon3 + '_blade'])
          writer.writerow([currentFamily, pokemon1, method12, pokemon2, method13, pokemon3 + '_shield'])

          continue
        # pumpkaboo sizes
        elif 'pumpkaboo' in pokemon1:
          writer.writerow([currentFamily, pokemon1 + '_small', method12, pokemon2 + '_small', method13, pokemon3])
          writer.writerow([currentFamily, pokemon1 + '_average', method12, pokemon2 + '_average', method13, pokemon3])
          writer.writerow([currentFamily, pokemon1 + '_large', method12, pokemon2 + '_large', method13, pokemon3])
          writer.writerow([currentFamily, pokemon1 + '_super', method12, pokemon2 + '_super', method13, pokemon3])
          
          continue
        # rockruff has 'own tempo' in the pokemon name slot rather than the method12 slot; move it
        elif 'own_tempo' in pokemon1:
          method12 = method12 + ' and Own Tempo'
          pokemon1 = pokemon1.replace('_own_tempo', '')
        # toxtricity amped vs low key
        elif 'toxtricity' in pokemon2:
          writer.writerow([currentFamily, pokemon1, method12, pokemon2 + '_amped', method13, pokemon3])
          writer.writerow([currentFamily, pokemon1, method12, pokemon2 + '_low_key', method13, pokemon3])

          continue
        # urshifu has 'single strike' and 'rapid strike' in the method12 slot rather than in the form name; move it
        elif 'urshifu' in pokemon2:
          style = re.search(r'(Single|Rapid)', method12).group(1)
          method12 = re.sub(r'\((Single|Rapid) Strike Style\)', '', method12)
          if style == 'Rapid':
            writer.writerow([currentFamily, pokemon1, method12, 'urshifu_rapid_strike', method13, pokemon3])
          else:
            writer.writerow([currentFamily, pokemon1, method12, 'urshifu', method13, pokemon3])
          continue
        #endregion


        writer.writerow([currentFamily, pokemon1, method12, pokemon2, method13, pokemon3])

    # handle unown and meltan
    writer.writerow(['unown', 'unown', '', '', '', ''])
    writer.writerow(['meltan', 'meltan', '400 Meltan Candy in Pokemon GO', 'melmetal', '', ''])
  return 

def main():
  dataPath = getDataPath() + 'pokemon\\'
  fname = dataPath + 'evolutionChains.csv'
  makeEvolutionChainCSV(fname)

if __name__ == '__main__':
  main()