import csv
from utils import openBulbapediaLink, getDataPath, parseName

def makeEvolutionChainCSV(fname):
  with open(fname, 'w', newline='', encoding='utf-8') as evolutionFamilyCSV:
    writer = csv.writer(evolutionFamilyCSV)

    bs = openBulbapediaLink('https://bulbapedia.bulbagarden.net/wiki/List_of_Pok%C3%A9mon_by_evolution_family', 0, 10)
    regions = ['Kanto', 'Johto', 'Hoenn', 'Sinnoh', 'Unova', 'Kalos', 'Alola', 'Galar']
    tables = [bs.find('span', {'id': f'{region}-based_evolution_families'}).find_next('table') for region in regions]

    # write the header
    writer.writerow(['Family', 'Pokemon 1', '1 to 2 Method', 'Pokemon 2', '2 to 3 Method', 'Pokemon 3'])

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
        if currentFamily in ['Unown', 'Kubfu ']:
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
            cellsText.append(cell.get_text().rstrip('\n').replace('→', '').strip(' ').replace(',', '').replace(';', '').replace('Kantonian', ''))
          else:
            cellsText.append(cell)

        currentFamily = parseName(currentFamily, 'pokemon')
        pokemon1 = parseName(cellsText[1], 'pokemon')
        pokemon12Method = cellsText[2]
        pokemon2 = parseName(cellsText[4], 'pokemon')
        pokemon23Method = cellsText[5]
        pokemon3 = parseName(cellsText[7], 'pokemon')

        writer.writerow([currentFamily, pokemon1, pokemon12Method, pokemon2, pokemon23Method, pokemon3])

    # handle exceptions
    writer.writerow(['kubfu','kubfu','Train in The Tower of Darkness(Single Strike Style)','urshifu', '', ''])
    writer.writerow(['kubfu','kubfu','Train in The Tower of Darkness(Single Strike Style)','urshifu_rapid_strike', '', ''])
    writer.writerow(['unown', 'unown', '', '', '', ''])
    writer.writerow(['meltan', 'meltan', '400 Meltan Candy in Pokemon GO', 'melmetal', '', ''])
  return 

def main():
  fname = getDataPath() + 'evolutionChains.csv'
  makeEvolutionChainCSV(fname)

if __name__ == '__main__':
  main()