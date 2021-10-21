import csv
from utils import openLink, parseName, getBulbapediaDataPath

# Makes a .csv for each generation's type matchup chart; rows are attacking types, columns are defending types
def typeMatchups(fnamePrefix):
  for gen in [[1, 'Generation_I'], [2, 'Generations_II-V'], [6, 'Generation_VI_onward']]:
    with open(fnamePrefix + f'{gen[0]}.csv', 'w', newline='', encoding='utf-8') as typeMatchupCSV:
      writer = csv.writer(typeMatchupCSV)

      bs = openLink('https://bulbapedia.bulbagarden.net/wiki/Type/Type_chart', 0, 10)
      rows = bs.find(id=gen[1]).find_next('table').find_all('tr')[1:-1]
      headerRow, dataRows = rows[0], rows[1:]

      csvHeader = ['Attacking Type']
      headers = headerRow.find_all('th')
      for header in headers:
        csvHeader.append(parseName(header.a['title']))
      writer.writerow(csvHeader)

      for row in dataRows:
        csvRow = []

        attackingType = parseName(row.find_all('th')[-1].a['title'])
        csvRow.append(attackingType)

        cells = row.find_all('td')
        for cell in cells:
          multiplier = float(cell.get_text().rstrip('\n').rstrip('×').replace('½', '0.5'))
          csvRow.append(multiplier)
        
        writer.writerow(csvRow)
  return

def main():
  dataPath = getBulbapediaDataPath() + 'types\\'
  typeMatchups_fnamePrefix = dataPath + 'typeMatchupsGen'
  typeMatchups(typeMatchups_fnamePrefix)
  return

if __name__ == '__main__':
  main()