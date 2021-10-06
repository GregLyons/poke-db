import csv
import urllib.request
from bs4 import BeautifulSoup

# Returns BeautifulSoup object given Bulbapedia link
def openBulbapediaLink(url, retryCount, retryMax):
  try:
    req = urllib.request.Request(url, headers={'User-Agent' : "Magic Browser"}) 
    html = urllib.request.urlopen( req )
    bs = BeautifulSoup(html.read(), 'html.parser')
    return bs
  except urllib.error.HTTPError:
    if retryCount < retryMax:
      openBulbapediaLink(url, retryCount + 1, retryMax)
  else:
    return None

# In gen 1, Sp. Attack and Sp. Defense are merged into one stat, 'Special', which is after Speed rather than before
def formatGen1(csvRow):
  speed = csvRow[5]
  specialA = csvRow[6]
  specialD = csvRow[6]

  # check for top 
  if specialA == 'Special':
    specialA = 'Sp. Attack'
    specialD = 'Sp. Defense'
  csvRow = csvRow[:5]
  csvRow.extend([specialA, specialD, speed])

  return csvRow

# Makes .csv files for base stats in Gens 1, 5, 6, 7, and 8
def makeBaseStatCSVs():
  urls = [
    'https://bulbapedia.bulbagarden.net/wiki/List_of_Pok%C3%A9mon_by_base_stats_(Generation_I)', 
    'https://bulbapedia.bulbagarden.net/wiki/List_of_Pok%C3%A9mon_by_base_stats_(Generation_II-V)',
    'https://bulbapedia.bulbagarden.net/wiki/List_of_Pok%C3%A9mon_by_base_stats_(Generation_VI)',
    'https://bulbapedia.bulbagarden.net/wiki/List_of_Pok%C3%A9mon_by_base_stats_(Generation_VII)',
    'https://bulbapedia.bulbagarden.net/wiki/List_of_Pok%C3%A9mon_by_base_stats_(Generation_VIII-present)'
  ]

  genMap = [1, 5, 6, 7, 8]


  for i in range(len(genMap)):
    url = urls[i]
    gen = genMap[i]

    bs = openBulbapediaLink(url, 0, 10)
    table = bs.find('table', {'class':'sortable'})
    rows = table.findAll('tr')

    # Make CSV file
    csvFile = open((f'src\\data\\baseStatsGen{gen}.csv'), 'w', newline='', encoding='utf-8')
    writer = csv.writer(csvFile, quoting=csv.QUOTE_MINIMAL)

    # Write data to file
    try: 
      for row in rows:
        # keep track of columns; we don't need the last two

        csvRow = []
        for cell in row.findAll(['td', 'th']):
          value = cell.get_text().rstrip('\n')
          if value != '':
            if value == 'Pokémon':
              csvRow.append('Pokemon')
            elif value == '#':
              csvRow.append('Dex Number')
            else:
              csvRow.append(value.lstrip('0'))

        # cut off last two columns, Total and Average
        csvRow = csvRow[:-2]

        # Make gen 1 like other gens
        if (gen == 1):
          csvRow = formatGen1(csvRow)

        writer.writerow(csvRow)
    finally: 
      csvFile.close()

makeBaseStatCSVs()