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
# Used for writing the rows to the main .csv file when the status has a table on Bulbapedia
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

  bs = openBulbapediaLink(url, 0, 10)

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
          notesFromTable.append([status, currentMove, currentHeader, note.get('title')])

      csvRow.append(value)
      headerIndex += 1

    # if row doesn't have probability column, add it in the appropriate spot for consistency
    if not hasProbability:
      csvRow = csvRow[:4] + ['--'] + csvRow[4:]

    if len(csvRow) > 2:
      # One of the tables has a missing <td> in the "Notes" column for Thousand Waves, so we fill it in
      if len(csvRow) == 7:
        csvRow.append('--')

      writer.writerow(csvRow)

  # we already have notes for type, category, power, and accuracy
  filteredNotes = [note for note in notesFromTable if note[2] not in ['Type', 'Category', 'Power', 'Accuracy']]
  notes = notes.extend(filteredNotes)

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
    writer.writeRow([statusName, 'Spotlight', '--', '--', '100%', '--', '--', note])
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

# Makes the main .csv file and extracts any notes
def makeMainCSVAndExtractNotes(fname):
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
  statusesWithoutTables = ['Curse', 'Embargo', 'Heal Block', 'Nightmare', 'Perish Song', 'Taunt', 'Telekinesis', 'Aqua Ring', 'Bracing', 'Defense Curl', 'Magic Coat', 'Mimic', 'Minimize', 'Substitute', 'Center Of Attention', 'Rooted', 'Magnetic Levitation', 'Transformed']
  for status in statusesWithoutTables:
    makeCSVRow(status, writer)

  csvFile.close()

  return notes

# Makes the .csv file of Notes
# A note is of the form [status, move, header, ]
def makeNotesCSV(fname, notes):
  csvFile = open(fname, 'w', newline='', encoding='utf-8')
  writer = csv.writer(csvFile, quoting=csv.QUOTE_MINIMAL)

  writer.writerow(['Status', 'Move Name', 'Header of Note', 'Description'])

  for note in notes:
    writer.writerow(note)

  csvFile.close()

# Make main .csv and extract notes
main_fname = 'src\data\movesThatCauseStatus.csv'
notes = makeMainCSVAndExtractNotes(main_fname)
print(notes)

# Make notes .csv
notes_fname = 'src\data\movesThatCauseStatusNotes.csv'
makeNotesCSV(notes_fname, notes)