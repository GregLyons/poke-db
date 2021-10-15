import csv
from utils import openBulbapediaLink, parseName, getDataBasePath

def makeMainCSV(fname):
  with open(fname, 'w', newline='', encoding='utf-8') as csvFile:
    writer = csv.writer(csvFile)
    writer.writerow(['Move ID', 'Move Name'])
    
    bs = openBulbapediaLink('https://bulbapedia.bulbagarden.net/wiki/List_of_moves_by_availability_(Generation_VIII)', 0, 10)
    dataRows = bs.find(id='bodyContent').find_next('table').find_next('table').find_all('tr')[1:]
    for row in dataRows:
      cells = row.find_all(['td', 'th'])
      moveID = cells[0].get_text().rstrip('\n')
      moveName = parseName(cells[1].get_text())

      if '✔' not in cells[-1].get_text():
        writer.writerow([moveID, moveName])
      else:
        continue
  return

def main():
  dataPath = getDataBasePath() + 'moves\\'
  fname = dataPath + 'movesRemovedFromGen8.csv'
  makeMainCSV(fname)
  return

if __name__ == '__main__':
  main()