import csv
from utils import openBulbapediaLink, getDataPath, parseName

# Columns are Nature Name, Increased Stat, Decreased Stat, Favorite Flavor, Disliked Flavor
def natureList(fname):
  with open(fname, 'w', newline='', encoding='utf-8') as natureCSV:
    writer = csv.writer(natureCSV)
    writer.writerow(['Nature Name', 'Increased Stat', 'Decreased Stat', 'Favorite Flavor', 'Disliked Flavor'])

    bs = openBulbapediaLink('https://bulbapedia.bulbagarden.net/wiki/Nature', 0, 10)
    dataRows = bs.find(id='List_of_Natures').find_next('table').find_all('tr')[1:-1]

    for row in dataRows:
      cells = row.find_all(['th', 'td'])

      name = parseName(cells[1].get_text())
      increasedStat = parseName(cells[3].get_text().replace('—', ''))
      decreasedStat = parseName(cells[4].get_text().replace('—', ''))
      favoriteFlavor = parseName(cells[5].get_text().replace('—', ''))
      dislikedFlavor = parseName(cells[6].get_text().replace('—', ''))

      writer.writerow([name, increasedStat, decreasedStat, favoriteFlavor, dislikedFlavor])

  return

def main():
  nature_fname = getDataPath() + 'natureList.csv'
  natureList(nature_fname)

  return

if __name__ == '__main__':
  main()
