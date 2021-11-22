import csv
from utils import openLink, getCSVDataPath, parseName

def makeZMoveCSV(fname):
  with open(fname, 'w', newline='', encoding='utf-8') as zMoveListCSV:
    writer = csv.writer(zMoveListCSV)
    writer.writerow(['Z-Move Name', 'Z-Crystal Name'])

    bs = openLink('https://bulbapedia.bulbagarden.net/wiki/Z-Move', 0, 10)
    genericZMoveRows = bs.find(id='For_each_type').find_next('table').find('table').find_all('tr')[1:]
    specificZMoveRows = bs.find(id='For_specific_Pokémon').find_next('table').find('table').find_all('tr')[1:]

    for row in genericZMoveRows:
      cells = row.find_all(['td', 'th'])
      moveName = parseName(cells[0].get_text())
      crystalName = parseName(cells[-1].get_text())
      writer.writerow([moveName, crystalName])

    for row in specificZMoveRows:
      cells = row.find_all(['td', 'th'])
      moveName = parseName(cells[1].get_text())
      crystalName = parseName(cells[-1].get_text())
      writer.writerow([moveName, crystalName])

  return

def main():
  dataPath = getCSVDataPath() + '/moves/'
  fname = dataPath + 'movesZList.csv'
  makeZMoveCSV(fname)

  return

if __name__ == '__main__':
  main()