import csv
import urllib.request
from bs4 import BeautifulSoup
from functools import cmp_to_key

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

def makeContactCSV(fname):
  url = 'https://bulbapedia.bulbagarden.net/wiki/Contact'
  bs = openBulbapediaLink(url, 0, 10)
  rows = bs.find('span', {'id': 'Moves_that_make_contact'}).find_next('table').find('table').find_all('tr')

  csvFile = open(fname, 'w', newline='', encoding='utf-8')
  writer = csv.writer(csvFile, quoting=csv.QUOTE_MINIMAL)
  writer.writerow(['Move Name', 'Note'])

  for row in rows:
    note = '--'
    moveName = ''

    for cell in row.find_all('td'):
      # checks if cell describes a move
      if cell.find('a') and cell.find('a').get('title') and '(move)' in cell.find('a').get('title'):
        # if move is in the table, it's a contact move
        moveName = cell.get_text().rstrip('\n').replace(' ', '')

        # contact moves which were not contact in Gen 3
        if moveName in ['Covet', 'FeintAttack', 'FakeOut']:
          note = 'Gen IV onward'

    if moveName:
      writer.writerow([moveName, note])

  # These exceptions don't show up in the Bulbapedia table, so we add them manually

  # moves which were contact in Gen 3 but not after
  writer.writerow(['AncientPower', 'Only Gen III'])
  writer.writerow(['Overheat', 'Only Gen III'])
  writer.writerow(['ShellSideArm', 'If physical'])

  csvFile.close()
  return

makeContactCSV('src/data/movesByContact.csv')


# genOfMoveName = moveDict[inverseDict[moveName]]["Gen"]
# # contact was introduced as a mechanic in gen 3
# moveDict[inverseDict[moveName]]["Contact"] = [True, max(genOfMoveName, 3)]