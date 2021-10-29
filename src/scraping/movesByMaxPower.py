import csv
from utils import openLink, getCSVDataPath, parseName

def makePowerCSV(fname): 
  with open(fname, 'w', encoding='utf-8', newline='') as maxPowerCSV:
    writer = csv.writer(maxPowerCSV)
    writer.writerow(['Move Name', 'Max Power'])

    # max move power
    bs = openLink('https://bulbapedia.bulbagarden.net/wiki/Max_Move', 0, 10)
    dataRows = bs.find(id='Power').find_next('table').find_next('table').find_all('tr')[1:]
    for row in dataRows:
      cells = row.find_all(['td', 'th'])
      moveName, maxPower = parseName(cells[0].get_text()), cells[-1].get_text().rstrip('\n')

      writer.writerow([moveName, maxPower])


  return

def main():
  dataPath = getCSVDataPath() + '/moves/'

  fname = dataPath + 'movesByMaxPower.csv'
  makePowerCSV(fname)

  return

if __name__ == '__main__':
  main()