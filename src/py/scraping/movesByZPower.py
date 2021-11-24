import csv
from utils import openLink, getCSVDataPath, parseName

def handleZMoveLink(link, writer):
  zMoveName = parseName(link.get_text())
  bs = openLink('https://bulbapedia.bulbagarden.net/' + link['href'], 0, 10)

  # typo in all-out pummeling page, 'Genration', so we use id='Effect' instead of 'Generation_VII'
  dataRows = bs.find(id='Effect').find_next('table').find_next('table').find_all('tr')[1:]

  for row in dataRows:
    cells = row.find_all(['td', 'th'])
    moveName, movePower = parseName(cells[0].get_text().replace('*', '')), cells[1].get_text().rstrip('\n')
    writer.writerow([zMoveName, moveName, movePower])

  return moveName

def makeZPowerCSV(fname):
  with open(fname, 'w', encoding='utf-8', newline='') as zPowerCSV:
    writer = csv.writer(zPowerCSV)
    writer.writerow(['Z-Move Name', 'Move Name', 'Z-Power'])

    bs = openLink('https://bulbapedia.bulbagarden.net/wiki/Z-Move', 0, 10)
    zMoveRows = bs.find(id='For_each_type').find_next('table').find_next('table').find_all('tr')[1:]

    for row in zMoveRows:
      cells = row.find_all(['td', 'th'])
      zMoveLink = cells[0].find('a')
      handleZMoveLink(zMoveLink, writer)

  return

def main():
  dataPath = getCSVDataPath() + '/moves/'

  fname = dataPath + 'movesByZPower.csv'
  makeZPowerCSV(fname)

  return

if __name__ == '__main__':
  main()