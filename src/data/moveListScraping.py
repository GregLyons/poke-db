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

def makeMainCSVandExtractNotes(fname):
  csvFile = open((fname), 'w', newline='', encoding='utf-8')
  writer = csv.writer(csvFile, quoting=csv.QUOTE_MINIMAL)

  url = 'https://bulbapedia.bulbagarden.net/wiki/List_of_moves'
  bs = openBulbapediaLink(url, 0, 10) 
  outerTable = bs.find('table', {'class': 'sortable'})
  moveTable = outerTable.find('table')
  headerRow = moveTable.find('tr')
  rows = moveTable.findAll('tr')[1:]

  headers = []
  for cell in headerRow.findAll(['th']):
    header = cell.get_text().strip('\n')
    if header == '#': 
      headers.append('Move ID')
    else:
      headers.append(header)
  writer.writerow(headers)

  notesCSV = open((fname.rstrip('.csv') + 'Notes.csv'), 'w', newline='', encoding='utf-8')
  notesWriter = csv.writer(notesCSV, quoting=csv.QUOTE_MINIMAL)
  notesWriter.writerow(['Move ID', 'Header', 'Description'])

  try:
    # used for keeping track of notes to be applied to move with id moveID
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
            notesWriter.writerow([moveID, headers[headerIndex], note.get('title')])

        value = cell.get_text().strip('\n').rstrip('*').replace(' ', '').replace('—', '--')
        csvRow.append(value)
        headerIndex += 1

      writer.writerow(csvRow)
  finally:
    csvFile.close()
    notesCSV.close()
  
  return

fname = f'src\data\movesList.csv'
makeMainCSVandExtractNotes(fname)



