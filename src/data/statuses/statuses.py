import csv
import urllib.request
import re
from bs4 import BeautifulSoup

# Make CSV file for move which causes $status, where $status is a nonvolatile status
# Also includes the volatile status Flinch and Confusion, since those have their own separate page on Bulbapedia, so this code works
def makeSeparatePageStatusCSV(statusInfo):
  status = statusInfo[0]

  findId = statusInfo[1]
  if status == 'BadPoison':
    findId = findId + '_2'
  if status == 'SemiInvulnerableTurn': 
    findId = findId + '_with_a_semi-invulnerable_turn'

  hasSeparatePage = statusInfo[2]
  if hasSeparatePage:
    url = f'https://bulbapedia.bulbagarden.net/wiki/{status}'
  else: 
    url = f'https://bulbapedia.bulbagarden.net/wiki/Status_condition'

  if status == 'BadPoison':
    url = f'https://bulbapedia.bulbagarden.net/wiki/Poison'
  elif status == 'SemiInvulnerableTurn':
    url = f'https://bulbapedia.bulbagarden.net/wiki/Semi-invulnerable_turn'
  
  if hasSeparatePage and (status != 'Flinch' and status != 'SemiInvulnerableTurn'):
    url = url + '_(status_condition)'

  req = urllib.request.Request(url, headers={'User-Agent' : "Magic Browser"}) 
  html = urllib.request.urlopen( req )
  bs = BeautifulSoup(html.read(), 'html.parser')

  fname = 'src\data\statuses\movesThatCause' + status + '.csv'
  csvFile = open(fname, 'w', newline='', encoding='utf-8')
  writer = csv.writer(csvFile, quoting=csv.QUOTE_MINIMAL)

  notes = []

  findSection = bs.find('span', id=findId)
  table = findSection.findNext('table').find('table')
  rows = table.findAll('tr')

  headers = []

  try:
    for row in rows:
      csvRow = []
      headerIndex = 0
      currentMove = ''
      
      for cell in row.findAll(['th']):
        value = cell.get_text().rstrip('\n')

        headers.append(value)
        csvRow.append(value)
        headerIndex += 1

      for cell in row.findAll(['td']):
        currentHeader = headers[headerIndex]

        value = cell.get_text().rstrip('\n').replace('*', '')
        if headerIndex == 0:
          currentMove = value

        if cell.find('span', {'class': 'explain'}) != None:
          notesInCell = cell.find_all('span', {'class': 'explain'})
          for note in notesInCell:
            notes.append([status, currentMove, currentHeader, note.get('title')])
        
        csvRow.append(value)
        headerIndex += 1

      writer.writerow(csvRow)

  finally:
    csvFile.close()

  # we already have notes for type, category, power, and accuracy
  filteredNotes = [note for note in notes if note[2] not in ['Type', 'Category', 'Power', 'Accuracy']]
  return filteredNotes

# Make CSV file for move which causes $status, where $status is a volatile status
def makeVolatileStatusCSV(status):
  print('hi')



  findId = 'Moves'
  

# Also includes Flinch and Confusion, which are volatile
separatePageStatuses = ['Burn', 'Freeze', 'Paralysis', 'Poison', 'BadPoison', 'Sleep', 'Confusion', 'Flinch', 'SemiInvulnerableTurn']
separatePageStatuses = [[status, 'Moves', True] for status in separatePageStatuses]
mainPageStatuses = ['Bound', 'Trapped', 'Drowsy', 'Identified', 'Infatuation', 'LeechSeed', 'Torment', 'TypeChange', 'ChargingTurn', 'Protection', 'Recharging', 'TakingAim', 'Thrashing']
mainPageStatusIDs = ['Bound', 'Can\'t_escape',  'Drowsy', 'Identified', 'Infatuation', 'Leech_Seed', 'Torment', 'Type_change', 'Charging_turn', 'Protection', 'Recharging', 'Taking_aim', 'Thrashing']
mainPageStatuses = [[mainPageStatuses[i], mainPageStatusIDs[i], False] for i in range(len(mainPageStatuses))]

statuses = separatePageStatuses + mainPageStatuses
for status in statuses:
  print('Notes for', status[0])
  print(makeSeparatePageStatusCSV(status))
  print()
