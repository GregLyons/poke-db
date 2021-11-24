import csv
from utils import openLink, getCSVDataPath, parseName

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
# Columns are Gen, Priority, Move Name
def makePriorityCSV(fname):

  csvFile = open((fname), 'w', newline='', encoding='utf-8')
  writer = csv.writer(csvFile, quoting=csv.QUOTE_MINIMAL)

  # Write the headers
  writer.writerow(['Gen', 'Priority', 'Move Name'])

  url = 'https://bulbapedia.bulbagarden.net/wiki/Priority'

  bs = openLink(url, 0, 10)
  
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
              move = parseName(move.replace('PE', '').strip())
              writer.writerow(csvRow + [move])

  # exception for grassy glide, not included in table
  writer.writerow([8, '1', 'grassy_glide'])

  csvFile.close()

def main():
  dataPath = getCSVDataPath() + 'moves\\'
  priority_fname = dataPath + 'movesByPriority.csv'
  makePriorityCSV(priority_fname)

if __name__ == '__main__':
  main()