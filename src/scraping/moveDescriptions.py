import csv
import re
from utils import openLink, getSerebiiDataPath, parseName

# Columns are Move Name, Description
def moveDescription(fname):
  with open(fname, 'w', newline='', encoding='utf-8') as moveDescriptionCSV:
    writer = csv.writer(moveDescriptionCSV)
    writer.writerow(['Move Name', 'Move Description'])

    # move descriptions are in three separate tables depending on move category
    for category in ['physical', 'special', 'other']:
      bs = openLink(f'https://www.serebii.net/attackdex-swsh/{category}.shtml', 0, 10)
      dataRows = bs.find('table', {'class': 'dextable'}).find_all('tr')[1:]

      for row in dataRows:
        cells = row.find_all('td')
        moveName = parseName(cells[0].get_text())
        moveDescription = cells[-1].get_text().strip('\n').strip()

        writer.writerow([moveName, moveDescription])

  return

def main():
  dataPath = getSerebiiDataPath() + '\\moves\\'
  moveDescription_fname = dataPath + 'moveDescriptions.csv'
  moveDescription(moveDescription_fname)
  return

if __name__ == '__main__':
  main()