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

# converts gen symbol to number
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

# creates .csv file for priority Bulbapedia tables
def makePriorityCSV(fname):

  csvFile = open((fname), 'w', newline='', encoding='utf-8')
  writer = csv.writer(csvFile, quoting=csv.QUOTE_MINIMAL)

  # Write the headers
  writer.writerow(['Generation', 'Priority', 'Move Name'])

  url = 'https://bulbapedia.bulbagarden.net/wiki/Priority'

  bs = openBulbapediaLink(url, 0, 10)
  
  genSymbols = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII']

  # There are eight tables we need to read, one for each generation
  for genSymbol in genSymbols:
    gen = genSymbolToNumber(genSymbol)
    # in this case, the table of interest is not nested in another, single cell table
    table = bs.find('span', id=f'Generation_{genSymbol}').find_next('table')
    rows = table.findAll('tr')

    # each row can have multiple moves in the 'Moves' column
    for row in rows:
      csvRow = [gen]

      # starts in the priority column
      priorityColumn = True

      # don't keep track of moves which have zero priority
      zeroPriority = False

      for cell in row.findAll('td'):
        if priorityColumn:
          priority = cell.get_text().rstrip('\n')
          if priority == '0':
            zeroPriority = True
          csvRow.append(priority.lstrip('+'))
          priorityColumn = False
        else:
          # ignore moves which have zero priority
          if zeroPriority:
            continue
          else:
            moves = cell.get_text().split(',')
            for move in moves:
              move = move.strip(' ')
              # Handle two cases: Zippy Zap and Teleport--handle Teleport in exception later
              if 'PE' in move: 
                if 'Teleport' not in move:
                  writer.writerow(csvRow + [move.replace('PE', '').rstrip('\n').replace(' ', '')])
                else:
                  continue
              else:
                writer.writerow(csvRow + [move.rstrip('\n').replace(' ', '')])

  csvFile.close()

priority_fname = f'src\data\movesByPriority.csv'
makePriorityCSV(priority_fname)