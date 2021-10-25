import csv
from utils import openLink, getDataPath, parseName

# Columns are status caused, move name, type, category, probability of inflicting status, power, accuracy, and notes

# Used for writing the rows to the main .csv file when the status has a table on Bulbapedia
def addCSVRowsForStatus(statusInfo, writer, wroteHeader, notes):
  status = statusInfo[0]

  findId = statusInfo[1]
  if status == 'Bad Poison':
    findId = findId + '_2'
  if status == 'Semi Invulnerable Turn': 
    findId = findId + '_with_a_semi-invulnerable_turn'

  hasSeparatePage = statusInfo[2]
  if hasSeparatePage:
    url = f'https://bulbapedia.bulbagarden.net/wiki/{status}'
  else: 
    url = f'https://bulbapedia.bulbagarden.net/wiki/Status_condition'

  if status == 'Bad Poison':
    url = f'https://bulbapedia.bulbagarden.net/wiki/Poison'
  elif status == 'Semi Invulnerable Turn':
    url = f'https://bulbapedia.bulbagarden.net/wiki/Semi-invulnerable_turn'
  
  if hasSeparatePage and (status != 'Flinch' and status != 'Semi Invulnerable Turn'):
    url = url + '_(status_condition)'

  bs = openLink(url, 0, 10)
  findSection = bs.find('span', id=findId)
  table = findSection.findNext('table').find('table')
  rows = table.findAll('tr')
  
  # since the tables may have different structure, we need to keep track of the headers of the table
  headers = []
  # assume from the start that the table lacks a probability column
  hasProbability = False
  notesFromTable = []

  for row in rows:
    csvRow = [status]
    headerIndex = 0
    currentMove = ''
  
    for cell in row.findAll(['th']):
      value = cell.get_text().rstrip('\n')

      # the table has a probability column
      if value == 'Probability':
        hasProbability = True

      headers.append(value)

      if not wroteHeader:
        csvRow[0] = 'Status Caused'
        if value == 'Move':
          value = 'Move Name'
        csvRow.append(value)

      headerIndex += 1

    for cell in row.findAll('td'):
      currentHeader = headers[headerIndex]

      value = cell.get_text().rstrip('\n').replace('*', '').replace('—', '')

      if headerIndex == 0:
        currentMove = value

      if cell.find('span', {'class': 'explain'}) != None:
        notesInCell = cell.find_all('span', {'class': 'explain'})
        for note in notesInCell:
          notesFromTable.append([parseName(status), parseName(currentMove), currentHeader, note.get('title')])

      csvRow.append(value)
      headerIndex += 1

    # if row doesn't have probability column, add it in the appropriate spot for consistency
    if not hasProbability:
      csvRow = csvRow[:4] + ['100.0'] + csvRow[4:]

    # exclude shadow moves 
    if len(csvRow) > 2 and csvRow[2] != 'Shadow':

      # One of the tables has a missing <td> in the "Notes" column for Thousand Waves, so we fill it in
      if len(csvRow) == 7:
        csvRow.append('')

      # convert probability to float,  to 100.0
      if csvRow[4] == '':
        csvRow[4] = '100.0'
      if csvRow[4] != 'Probability':
        csvRow[4] = float(csvRow[4].rstrip('%'))

      # convert everything to kebab case except the header
      if csvRow[0] != 'Status Caused':
        for i in range(4):
          csvRow[i] = parseName(csvRow[i])
      writer.writerow(csvRow)

  # we already have notes for type, category, power, and accuracy
  filteredNotes = [note for note in notesFromTable if note[2] not in ['Type', 'Category', 'Power', 'Accuracy']]
  notes = notes.extend(filteredNotes)

# Makes a row for the statuses which do not have tables on Bulbapedia
def makeCSVRow(status, writer):
  status = parseName(status)
  moveName = status
  note = ''

  if status == 'curse':
    note = 'If user is a Ghost-type Pokemon'

  # Go through exceptions where name of status isn't name of move
  # Center of Attention
  if status == 'center_of_attention':
    writer.writerow([status, 'follow_me', '', '', '100.0', '', '', note])
    writer.writerow([status, 'rage_powder', '', '', '100.0', '', '', note])
    writer.writerow([status, 'spotlight', '', '', '100.0', '', '', note])
  # Rooted
  # Braing
  elif status == 'bracing':
    writer.writerow([status, 'endure', '', '', '100.0', '', '', note])
  elif status == 'rooted':
    writer.writerow([status, 'ingrain', '', '', '100.0', '', '', note])
  # Magnetic levitation
  elif status == 'magnetic_levitation':
    writer.writerow([status, 'magnet_rise', '', '', '100.0', '', '', note])
  # Transformed
  elif status == 'transformed':
    writer.writerow([status, 'transform', '', '', '100.0', '', '', note])
  else: 
    writer.writerow([status, moveName, '', '', '100.0', '', '', note])

# Makes the main .csv file and extracts any notes
def makeStatusCSVAndExtractNotes(fname):
  # List of statuses and the HTML "id" attributes for their Bulbapedia tables
  # Some statuses are on separate pages
  separatePageStatuses = ['Burn', 'Freeze', 'Paralysis', 'Poison', 'Bad Poison', 'Sleep', 'Confusion', 'Flinch', 'Semi Invulnerable Turn']
  # Boolean indicates status is on separate page
  separatePageStatuses = [[status, 'Moves', True] for status in separatePageStatuses]

  # Other statuses are on a single page, the 'main page'
  mainPageStatuses = ['Bound', 'Trapped', 'Drowsy', 'Identified', 'Infatuation', 'Leech Seed', 'Torment', 'Type Change', 'Charging Turn', 'Protection', 'Recharging', 'Taking Aim', 'Thrashing']
  mainPageStatusIDs = ['Bound', 'Can\'t_escape', 'Drowsy', 'Identified', 'Infatuation', 'Leech_Seed', 'Torment', 'Type_change', 'Charging_turn', 'Protection', 'Recharging', 'Taking_aim', 'Thrashing']
  # Boolean indices status is on main page
  mainPageStatuses = [[mainPageStatuses[i], mainPageStatusIDs[i], False] for i in range(len(mainPageStatuses))]

  # We write all the statuses tables to a single .csv file
  csvFile = open(fname, 'w', newline='', encoding='utf-8')
  writer = csv.writer(csvFile, quoting=csv.QUOTE_MINIMAL)

  statuses = separatePageStatuses + mainPageStatuses

  # A running track of notes which are embedded in HTML "title" attributes
  # wroteHeader is used so that everything is in one .csv file. The "Protection" table has different headers, namely Priority instead of Power, but we won't refer to the values in that column at all
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

# Makes the .csv file of notes, which won't be called by another file
# Columns are Status Name, Move Name, Header of Note, Description
def makeStatusNotesCSV(fname, notes):
  csvFile = open(fname, 'w', newline='', encoding='utf-8')
  writer = csv.writer(csvFile, quoting=csv.QUOTE_MINIMAL)

  writer.writerow(['Status Name', 'Move Name', 'Header of Note', 'Description'])

  for note in notes:
    writer.writerow(note)

  csvFile.close()

# add Z-move data to .csv
def addZMoves(fname):
  with open(fname, 'r', encoding='utf-8') as oldCSV:
    reader = csv.DictReader(oldCSV)
    moveStatusDict = {}
    for row in reader:  
      # physical and special moves do not apply status effects when turned into Z-moves; as a consequence, the probability of a status being applied is always 100.0
      if row["Category"] == 'status':
        moveName, status = row["Move Name"], row["Status Caused"]
        if row["Probability"] != '100.0':
          print(moveName)

        if moveName not in moveStatusDict:
          moveStatusDict[moveName] = []
        
        moveStatusDict[moveName].append(status)
      else:
        continue


  with open(fname, 'a', newline='', encoding='utf-8') as newCSV:
    writer = csv.writer(newCSV)

    # the main purpose of referring to the table on the Bulbapedia page is to filter out moves which are introduced in Gen 8, and hence don't have Z- counterparts, e.g. Octolock; the original status table does not have gen data, so if we were to just append 'z_' to all the names, we would get 'z_octolock' in our .csv.
    bs = openLink('https://bulbapedia.bulbagarden.net/wiki/Z-Move', 0, 10)
    dataRows = bs.find(id='Z-Power_effects_of_status_moves').find_next('table').find('table').find_all('tr')[1:]

    for row in dataRows:
      cells = row.find_all('td')
      moveName = parseName(cells[0].get_text())

      if moveName in moveStatusDict:
        for status in moveStatusDict[moveName]:
          writer.writerow([status, 'z_' + moveName, '', '', '100.0', '', '', ''])

    # two exceptions: Z-moves which add status effects
    writer.writerow(['center_of_attention', 'z_grudge', '', '', '100.0', '', '', ''])
    writer.writerow(['center_of_attention', 'z_destiny_bond', '', '', '100.0', '', '', ''])

  return

def main():
  # Make main .csv and extract notes
  dataPath = getDataPath() + 'moves\\'
  main_fname = dataPath + 'movesByStatus.csv'
  notes = makeStatusCSVAndExtractNotes(main_fname)

  # Make notes .csv
  notes_fname = dataPath + 'movesByStatusNotes.csv'
  makeStatusNotesCSV(notes_fname, notes)

  # add Z-move data
  addZMoves(main_fname)

if __name__ == '__main__':
  main()