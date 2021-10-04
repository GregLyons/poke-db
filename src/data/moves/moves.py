import csv
import urllib.request
from bs4 import BeautifulSoup
from functools import cmp_to_key

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
# Flag OHKO moves
# Flag fixed damage moves
# Flag LGPE: if 'in LGPE'; refers to move damage/accuracy/type and it takes a specific value; if 'LGPE only' refers to presence of move itself and doesn't take specific value; if 'and LGPE', refers to move value present in LGPE and multiple generations prior to VII
# For most changes, it'll just be the value and the latest generation for that value (e.g. 40 Power before and in Generation V would be [40, 5])
def parseNote(note):
  moveID = note[0]
  header = note[1]
  description = note[2]

  # Notes about type change are actually given in the 'Name' column
  if header == 'Name':
    header = 'Type'

  # "Success is calculated using a custom formula" for OHKO moves
  # the success of the OHKO move depends on mechanics which are hard to capture in a list--since there are only four, and they're hardly used, we ignore them
  if 'custom' in description:
    return [moveID, header, ['OHKO', None]]

  # "Always deals X damage"
  if 'Always' in description:
    words = description.split()
    value = words[2] + "fixed"
    # fixed damage moves come from Gen 1
    return [moveID, header, [value, 1]]

  # If value applies for LGPE, replace generation value with LGPE flag
  if 'in LGPE' in description:
    words = description.split() 
    value = words[0].rstrip('%').rstrip('-type')
    return [moveID, header, [value, 'LGPE']]

  # Indicates presence of move itself in LGPE only, rather than a value
  if 'LGPE only' in description:
    return [moveID, header, [None, 'LGPE only']]

  # Smogon doesn't care about these exclusions--e.g. Hypnosis is 70% accurate in Diamond and Pearl, but on Smogon and Pokemon Showdown, Gen 4 Hypnosis is 60% accurate
  if 'Diamond and Pearl' in description or 'ORAS only' in description or 'USUM only' in description: 
    return [moveID, header, None]
  
  # change description is of the form '$value in Generation(s) $start-$end"
  # sometimes description ends in 'LGPE'--ignore that part
  try:
    includeLGPE = False
    if 'and LGPE' in description:
      includeLGPE = True
    
    # remove LGPE for parsing consistently
    description = description.rstrip(' and LGPE')

    words = description.split()
    value = words[0].rstrip('%').rstrip('-type')
    latestGen = genSymbolToNumber(words[-1].split('-')[-1])
    if includeLGPE:
      return [moveID, header, [value, latestGen, 'LGPE']]
    else: 
      # Note is not one of the above cases, the majority of cases
      return [moveID, header, [value, latestGen, 'Standard']]
  # except-clause for debugging
  except:
    print('Something went wrong when handling this description:')
    print(description)
    return None

# a patch is of the form [value, gen], where gen is either 1-8 or "LGPE"
def comparePatches(patch1, patch2):
  # make LGPE last, otherwise sort by gen
  if patch1[1] == "LGPE" or patch1[1] == "LGPE Only":
    return 1
  elif patch2[1] == "LGPE" or patch2[1] == "LGPE Only":
    return -1
  else:
    if patch1[1] > patch2[1]:
      return 1
    else:
      return -1


# creates .csv file for Bulbapedia table with name fp
def makeCSVandExtractNotes(fname):

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

  # keep track of notes
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

# creates dictionary for moves in csv located at fname
# contains moveID, name, type, category, contest type, PP, power, accuracy, gen introduced, whether move is OHKO, whether move is fixed damage/its fixed damage value, whether the move is LGPE exclusive
def makeInitialMoveDict(fname, unparsedNotes):
  initialMoveDict = {}

  with open(fname, encoding='utf-8') as movesCSV:
    reader = csv.DictReader(movesCSV)

    # make initial move dictionary, capturing state of the moves in Gen VIII

    for row in reader:
      # Bulbapedia has "Stone Axe" as the last entry with ID "???"--not released yet
      if row["Move ID"] != "???":
        # "Type", "Power", and "Accuracy" are lists since those can potentially change across generations--Bulbapedia lists the latest values for each field, with the past values in notes
        isMax = row["Move ID"][:4] == "Max "

        initialMoveDict[row["Move ID"]] = {
          "Name": row["Name"],
          "Type": [[row["Type"], 8]],
          "Category": row["Category"],
          "Contest": row["Contest"],
          "PP": [[row["PP"], 8]],
          "Power": [[row["Power"], 8]],
          "Accuracy": [[row["Accuracy"].rstrip('%'), 8]],
          "Gen": genSymbolToNumber(row["Gen"]),
          "OHKO": False,
          "Fixed Damage": None,
          "LGPE Only": False,
          "Max Move": isMax,
        }

    # we will make a list of all the parsed notes, then filter them out into several other lists
    parsedNotes = []

    for note in unparsedNotes:
      # some moves, such as Disable, have had multiple changes across generations, so a note can describe multiple changes
      description = note[2] 
      parts = description.split(',')

      for part in parts:
        parsedNote = parseNote([note[0], note[1], part])
        if parsedNote[2] != None:
          parsedNotes.append(parsedNote)

    # Standard note, majority of cases [moveID, header, [value, gen]]
    changes = [[note[0], note[1], note[2][:2]] for note in parsedNotes if len(note[2]) == 3 and note[2][2] == 'Standard']
    for change in changes:
      moveID = change[0]
      header = change[1]
      valueAndGen = change[2]
      initialMoveDict[str(moveID)][header].append(valueAndGen)

    # OHKO moves [moveID, header, ['OHKO', None]]
    OHKOMoves = [note for note in parsedNotes if note[2][0] == 'OHKO']
    for OHKOMove in OHKOMoves:
      moveID = OHKOMove[0]
      initialMoveDict[str(moveID)]["OHKO"] = True

    # Fixed damage moves [moveID, header, [value + "fixed", Gen]]
    fixedDamageMoves = [note for note in parsedNotes if note[2][0] != None and 'fixed' in note[2][0]]
    for fixedDamageMove in fixedDamageMoves:
      moveID = fixedDamageMove[0]
      initialMoveDict[str(moveID)]["Fixed Damage"] = fixedDamageMove[2][0].rstrip('fixed')

    # Value for move in LGPE [moveID, header, [value, "LGPE"]]
    LGPEMoveValues = [note for note in parsedNotes if note[2][1] == 'LGPE']
    for LGPEMoveValue in LGPEMoveValues:
      moveID = LGPEMoveValue[0]
      header = LGPEMoveValue[1]
      initialMoveDict[str(moveID)][header].append(LGPEMoveValue[2])

    # LGPE exclusive move [moveID, header, [None, "LGPE only"]]
    LGPEExclusives = [note for note in parsedNotes if note[2][1] == 'LGPE only']
    for LGPEExclusive in LGPEExclusives:
      moveID = LGPEExclusive[0]
      header = LGPEExclusive[1]
      initialMoveDict[str(moveID)]["LGPE Only"] = True
      for header in ['Type', 'PP', 'Power', 'Accuracy']:
        initialMoveDict[str(moveID)][header][0][1] = "LGPE Only"

    # Value for move which holds in LGPE and in other gens [moveID, header, [value, gen, "LGPE"]]
    # only includes Mega Drain 
    LGPEandGenMoves = [note for note in parsedNotes if len(note[2]) == 3 and note[2][2] == 'LGPE']
    for LGPEandGenMove in LGPEandGenMoves:
      moveID = LGPEandGenMove[0]
      header = LGPEandGenMove[1]
      valueAndGen = [LGPEandGenMove[2][0], LGPEandGenMove[2][1]]
      valueAndLGPE = [LGPEandGenMove[2][0], LGPEandGenMove[2][2]]
      initialMoveDict[str(moveID)][header].append(valueAndGen)
      initialMoveDict[str(moveID)][header].append(valueAndLGPE)

  #For each move in initialMoveDict, sort the "Type", "PP", "Power", and "Accuracy" fields by generation
  for key in initialMoveDict:
    for innerKey in ['Type', 'PP', 'Power', 'Accuracy']:
      if len(initialMoveDict[key][innerKey]) > 1:
        initialMoveDict[key][innerKey].sort(key = cmp_to_key(comparePatches))
        print(key, initialMoveDict[key][innerKey])




  return initialMoveDict

fname = f'src\data\moves\movesList.csv'
notes = makeCSVandExtractNotes(fname)

moveDict = makeInitialMoveDict(fname, notes)
