import csv
from utils import openLink, getDataPath, parseName

# columns are Move ID, Move Name, Type, Category (physical/special/status), Contest Type, PP, Power, Accuracy, and Gen 
def makeMoveListCSVandExtractNotes(fname):
  with open((fname), 'w', newline='', encoding='utf-8') as csvFile, open((fname.rstrip('.csv') + 'Notes.csv'), 'w', newline='', encoding='utf-8') as notesCSV:
    writer = csv.writer(csvFile, quoting=csv.QUOTE_MINIMAL)
    notesWriter = csv.writer(notesCSV, quoting=csv.QUOTE_MINIMAL)
    notesWriter.writerow(['Move ID', 'Header', 'Description'])

    url = 'https://bulbapedia.bulbagarden.net/wiki/List_of_moves'
    bs = openLink(url, 0, 10) 
    moveTable = bs.find('table', {'class': 'sortable'}).find('table')
    headerRow = moveTable.find('tr')
    rows = moveTable.findAll('tr')[1:]

    headers = []
    for cell in headerRow.findAll('th'):
      header = cell.get_text().strip('\n')
      if header == '#': 
        headers.append('Move ID')
      elif header == 'Name':
        headers.append('Move Name')
      else:
        headers.append(header)
    writer.writerow(headers)

    # handle non-G-max moves
    moveID = 0
    for row in rows:
      moveID += 1
      csvRow = []
      headerIndex = 0

      # move changed since its introduction, add that to list of notes to process later

      for cell in row.findAll(['td', 'th']):
        # check if there's a note in this cell
        if cell.find('span', {'class': 'explain'}) != None:
          notesInCell = cell.find_all('span', {'class': 'explain'})
          for note in notesInCell:
            notesWriter.writerow([moveID, headers[headerIndex].lower(), note.get('title')])

        value = parseName(cell.get_text().strip('\n').rstrip('*').replace('—', ''))
        csvRow.append(value)
        headerIndex += 1

      writer.writerow(csvRow)

    # add G-Max moves
    finalNonGmaxID = moveID

    gMaxTable = bs.find('span', {'id': 'List_of_G-Max_Moves'}).find_next('table').find('table')
    gMaxRows = gMaxTable.findAll('tr')[1:]
    for row in gMaxRows:
      csvRow = []

      for cell in row.findAll('td'):
        value = parseName(cell.get_text().rstrip('\n'))
        csvRow.append(value)
      
      # the G-max table only contains ID, name, and type, so we add in the other values
      csvRow[0] = str(int(csvRow[0]) + finalNonGmaxID)
      csvRow.append('varies')
      csvRow = csvRow + 4*['--'] + ['VIII']
      writer.writerow(csvRow)
  
  return

# add Z-move data to .csv
def addZMoves(fname):
  with open(fname, 'r', encoding='utf-8') as oldCSV:
    reader = csv.DictReader(oldCSV)
    statusMoveDict = {}
    for row in reader: 
      if row["Category"] == "status":
        statusMoveDict[row["Move Name"]] = ['', row["Move Name"], row["Type"], row["Category"], '???', '', '', '', 'vii']
    
    # get moveID of last row and add 1, 
    moveID = int(row["Move ID"]) + 1

  with open(fname, 'a', newline='', encoding='utf-8') as newCSV:
    writer = csv.writer(newCSV)

    # the main purpose of referring to the table on the Bulbapedia page is to filter out moves which are introduced in Gen 8, and hence don't have Z- counterparts, e.g. Octolock; the original status table does not have gen data, so if we were to just append 'z_' to all the names, we would get 'z_octolock' in our .csv.
    bs = openLink('https://bulbapedia.bulbagarden.net/wiki/Z-Move', 0, 10)
    dataRows = bs.find(id='Z-Power_effects_of_status_moves').find_next('table').find('table').find_all('tr')[1:]

    for row in dataRows:
      cells = row.find_all('td')
      moveName = parseName(cells[0].get_text())
      if moveName in statusMoveDict:
        writer.writerow([moveID, 'z_' + moveName] + statusMoveDict[moveName][2:])
        moveID += 1
      # for catching any exceptions
      else:
        print(moveName)
  return

def main():
  dataPath = getDataPath() + 'moves\\'
  fname = dataPath + 'moveList.csv'
  makeMoveListCSVandExtractNotes(fname)

  # add Z-move data for status moves, which aren't listed on the main move list page
  addZMoves(fname)

if __name__ == '__main__':
  main()


