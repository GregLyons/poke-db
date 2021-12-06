import csv
from utils import openLink, parseName, getCSVDataPath

def makeMainCSV(fname):
  with open(fname, 'w', newline='', encoding='utf-8') as csvFile:
    writer = csv.writer(csvFile)
    writer.writerow(['Move ID', 'Move Name', 'Removed from SwSh', 'Removed from BDSP'])
    
    bs = openLink('https://bulbapedia.bulbagarden.net/wiki/List_of_moves_by_availability_(Generation_VIII)', 0, 10)
    dataRows = bs.find(id='bodyContent').find_next('table').find_next('table').find_all('tr')[1:]

    for row in dataRows:
      cells = row.find_all(['td', 'th'])
      moveID = cells[0].get_text().rstrip('\n')
      removedFromSwSh = '✔' not in cells[-2].get_text()
      removedFromBDSP = '✔' not in cells[-1].get_text()

      # Some moves share same move ID, and hence are in same row in the table, e.g. max moves and corresponding g-max moves. Each has its own <a> tag. Write a row for each separate move.
      moveNameCell = cells[1]
      moveNameLinks = moveNameCell.find_all('a')
      for moveNameLink in moveNameLinks:
        moveName = parseName(moveNameLink.get_text())

        writer.writerow([moveID, moveName, removedFromSwSh, removedFromBDSP])

  return

def main():
  dataPath = getCSVDataPath() + 'moves\\'
  fname = dataPath + 'movesRemovedFromGen8.csv'
  makeMainCSV(fname)
  return

if __name__ == '__main__':
  main()