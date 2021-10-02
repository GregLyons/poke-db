import csv
from os import error
import urllib.request
from bs4 import BeautifulSoup

# converts roman numeral for to arabic numeral
def genSymbolToNumber(roman):
  if roman == 'I':
    return 1
  elif roman == 'II':
    return 2
  elif roman == 'III':
    return 3
  elif roman == 'IV':
    return 4
  elif roman == 'V':
    return 5
  elif roman == 'VI':
    return 6
  elif roman == 'VII':
    return 7
  elif roman == 'VIII':
    return 8
  elif roman == 'IX':
    return 9
  else:
    raise ValueError('Not a valid gen.')

# get value(s) and generation(s) from description
def parseDescription(description):
  # filter things which aren't actually notes
  if 'only' in description or 'custom' in description or 'Always' in description:
    return None

  if 'Generation' not in description:
    return None

  # change description is of the form '$value in Generation(s) $start-$end"
  # sometimes description ends in 'LGPE'--ignore that part
  description = description.rstrip(' and LGPE')
  try:
    words = description.split()
    value = words[0].rstrip('%').rstrip('-type')
    latestGen = genSymbolToNumber(words[-1].split('-')[-1])

    return [value, latestGen]
  except:
    print('Something went wrong when handling this description:')
    print(description)
    return None

# a note is of the form [moveID, header, description]  
def getChangesFromNote(note):
  moveID = note[0]
  header = note[1]
  description = note[2]

  # A note may contain multiple changes, separated by a comma
  changesInNote = [[moveID, header, parseDescription(descriptionPart)] for descriptionPart in description.split(',')]

  return changesInNote


# creates .csv file for Bulbapedia table with name fp
def makeCSVandTrackChanges(fname):

  # Open CSV file
  csvFile = open((fname), 'w', newline='', encoding='utf-8')
  writer = csv.writer(csvFile, quoting=csv.QUOTE_MINIMAL)

  url = 'https://bulbapedia.bulbagarden.net/wiki/List_of_moves'

  # Need to look like browser to access Bulbapedia
  req = urllib.request.Request(url, headers={'User-Agent' : "Magic Browser"}) 
  html = urllib.request.urlopen( req )

  # Get the table rows--the desired table has the "sortable class", and is the first inner table of a larger outer table
  bs = BeautifulSoup(html.read(), 'html.parser')
  outerTable = bs.find('table', {'class': 'sortable'})
  moveTable = outerTable.find('table')
  
  # Write header row and keep track of headings
  headerRow = moveTable.find('tr')
  headers = []

  for cell in headerRow.findAll(['th']):
    header = cell.get_text().strip('\n')
    if header == '#': 
      headers.append('Move ID')
    else:
      headers.append(header)

  writer.writerow(headers)

  # Write rows with data
  rows = moveTable.findAll('tr')[1:]

  notes = []

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
            notes.append([moveID, headers[headerIndex], note.get('title')])

        value = cell.get_text().strip('\n').rstrip('*')
        csvRow.append(value)
        headerIndex += 1

      writer.writerow(csvRow)
  finally:
    csvFile.close()

  return notes

# creates dictionary for list of moves using .csv file at fp
def makeMoveDict(fname, notes):
  with open(fname, encoding='utf-8') as movesCSV:
    reader = csv.reader(movesCSV)

    moveDict = {}
    
    # we will track the changes, then filter out "None"
    unfilteredChanges = []

    for note in notes:
      # we use extend rather than append since a note can describe multiple changes
      unfilteredChanges.extend(getChangesFromNote(note))

    # a change is of the form [moveID, header, [value, endGen]], where endGen is the latest generation that value was in effect
    changes = [change for change in unfilteredChanges if change[2] != None]
    print(changes)


  
  return moveDict

fname = f'src\data\moves\movesList.csv'
notes = makeCSVandTrackChanges(fname)
moveDict = makeMoveDict(fname, notes)
