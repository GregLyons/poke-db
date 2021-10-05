import csv
import urllib.request
import re
from bs4 import BeautifulSoup

# We make a single .csv file for all the statuses
def addCSVRowsForStatus(statusInfo, writer, wroteHeader, notes):
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

  findSection = bs.find('span', id=findId)
  table = findSection.findNext('table').find('table')
  rows = table.findAll('tr')

  headers = []
  hasProbability = False
  notesFromTable = []

  for row in rows:
    csvRow = [status]
    headerIndex = 0
    currentMove = ''
  
    for cell in row.findAll(['th']):
      value = cell.get_text().rstrip('\n')
      if value == 'Probability':
        hasProbability = True

      headers.append(value)

      if not wroteHeader:
        csvRow[0] = 'Status caused'
        csvRow.append(value)
      headerIndex += 1

    for cell in row.findAll(['td']):
      currentHeader = headers[headerIndex]

      value = cell.get_text().rstrip('\n').replace('*', '').replace('—', '--')
      
      if headerIndex == 0:
        currentMove = value

      if cell.find('span', {'class': 'explain'}) != None:
        notesInCell = cell.find_all('span', {'class': 'explain'})
        for note in notesInCell:
          notes.append([status, currentMove, currentHeader, note.get('title')])

      csvRow.append(value)
      headerIndex += 1

    if not hasProbability:
      csvRow = csvRow[:4] + ['--'] + csvRow[4:]
    if len(csvRow) > 2:
      writer.writerow(csvRow)

  # we already have notes for type, category, power, and accuracy
  filteredNotes = [note for note in notesFromTable if note[2] not in ['Type', 'Category', 'Power', 'Accuracy']]
  notes = notes + filteredNotes

# For the statuses which do not have tables, make a CSV Row for them
def makeCSVRow(status, writer):
  statusName = status.replace(' ', '')
  moveName = status
  note = ''

  if status == 'Curse':
    note = 'If user is a Ghost-type Pokemon'

  # Center of Attention
  if status == 'Center of Attention':
    writer.writerow([statusName, 'Follow Me', '--', '--', '100%', '--', '--', note])
    writer.writerow([statusName, 'Rage Powder', '--', '--', '100%', '--', '--', note])
  # Rooted
  elif status == 'Rooted':
    writer.writerow([statusName, 'Ingrain', '--', '--', '100%', '--', '--', note])
  # Magnetic levitation
  elif status == 'Magnetic Levitation':
    writer.writerow([statusName, 'Magnet Rise', '--', '--', '100%', '--', '--', note])
  # Transformed
  elif status == 'Transformed':
    writer.writerow([statusName, 'Transform', '--', '--', '100%', '--', '--', note])
  else: 
    writer.writerow([statusName, moveName, '--', '--', '100%', '--', '--', note])

# List of statuses and the HTML "id" attributes for their Bulbapedia tables
# Some statuses are on separate pages
separatePageStatuses = ['Burn', 'Freeze', 'Paralysis', 'Poison', 'BadPoison', 'Sleep', 'Confusion', 'Flinch', 'SemiInvulnerableTurn']
# Boolean indicates status is on separate page
separatePageStatuses = [[status, 'Moves', True] for status in separatePageStatuses]

# Other statuses are on a single page, the 'main page'
mainPageStatuses = ['Bound', 'Trapped', 'Drowsy', 'Identified', 'Infatuation', 'LeechSeed', 'Torment', 'TypeChange', 'ChargingTurn', 'Protection', 'Recharging', 'TakingAim', 'Thrashing']
mainPageStatusIDs = ['Bound', 'Can\'t_escape', 'Drowsy', 'Identified', 'Infatuation', 'Leech_Seed', 'Torment', 'Type_change', 'Charging_turn', 'Protection', 'Recharging', 'Taking_aim', 'Thrashing']
# Boolean indices status is on main page
mainPageStatuses = [[mainPageStatuses[i], mainPageStatusIDs[i], False] for i in range(len(mainPageStatuses))]

# We write all the statuses tables to a single .csv file
fname = 'src\data\statuses\movesThatCauseStatus.csv'
csvFile = open(fname, 'w', newline='', encoding='utf-8')
writer = csv.writer(csvFile, quoting=csv.QUOTE_MINIMAL)

statuses = separatePageStatuses + mainPageStatuses

# A running track of notes which are embedded in HTML "title" attributes
notes = []
wroteHeader = False

for status in statuses:
  addCSVRowsForStatus(status, writer, wroteHeader, notes)
  wroteHeader = True

# Now we handle statuses which are caused by single moves
exceptions = ['Curse', 'Embargo', 'Heal Block', 'Nightmare', 'Perish Song', 'Taunt', 'Telekinesis', 'Aqua Ring', 'Bracing', 'Defense Curl', 'Magic Coat', 'Mimic', 'Minimize', 'Substitute', 'Center of Attention', 'Rooted', 'Magnetic Levitation', 'Transformed']
for status in exceptions:
  makeCSVRow(status, writer)

csvFile.close()
