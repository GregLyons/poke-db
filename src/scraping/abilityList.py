from utils import openLink, getBulbapediaDataPath, parseName
import csv

# Columns are Ability ID, Ability Name, Ability Description, and Gen Introduced
def makeMainCSV(fname):
  with open(fname, 'w', newline='', encoding='utf-8') as abilityCSV:
    writer = csv.writer(abilityCSV, quoting=csv.QUOTE_MINIMAL)

    # Create basic list of abilities
    bs = openLink('https://bulbapedia.bulbagarden.net/wiki/Ability', 0, 10)
    rows = bs.find('span', {'id': 'List_of_Abilities'}).find_next('table').find('table').find_all('tr')

    headers = ['Ability ID', 'Ability Name', 'Description', 'Gen']
    writer.writerow(headers)

    for row in rows:
      skipRow = False
      csvRow = []
      headerIndex = 0

      for cell in row.find_all('td'):
        value = cell.get_text().rstrip('\n')

        # As One takes up two IDs, and there is one unused ability in the table
        if value == '266/267' or value == '—':
          skipRow = True
          continue
        else:
          if headers[headerIndex] == 'Ability Name':
            value = parseName(value)
          csvRow.append(value)
          headerIndex += 1
      
      if not skipRow:
        writer.writerow(csvRow)

    writer.writerow(['266', 'as_one', 'This Ability combines the effects of both Calyrex\'s Unnerve Ability and Glastrier\'s Chilling Neigh Ability', 'VIII'])
    writer.writerow(['267', 'as_one', 'This Ability combines the effects of both Calyrex\'s Unnerve Ability and Spectrier\'s Grim Neigh Ability', 'VIII'])
  return  

def main():
  dataPath = getBulbapediaDataPath() + 'abilities\\'
  ability_fname = dataPath + 'abilityList.csv'
  makeMainCSV(ability_fname)

if __name__ == '__main__':
  main()