import csv
from utils import openLink, getCSVDataPath, parseName, numberOfGens, isShadowMove

def makeInteractionCSV(fname):
  with open(fname, 'w', newline='', encoding='utf-8') as interactionCSV:
    writer = csv.writer(interactionCSV)
    headerRow = ['Active Move Name', 'Target Move Name']
    for i in range(numberOfGens()):
      headerRow.append(i + 1)
    writer.writerow(headerRow)

    # Snatch interactions
    snatchTableRows = openLink('https://bulbapedia.bulbagarden.net/wiki/Snatch_(move)', 0, 10).find(id='Affected_moves').find_next('table').find('table').find_all('tr')[2:]

    for row in snatchTableRows:
      cells = row.find_all(['td', 'th'])
      moveName, genData = parseName(cells[0].get_text()), cells[2:]

      # will store gen info; snatch debuted in Gen 3
      genInfo = ['F', 'F']
      

      # parse the table
      for genDatum in genData:
        if '✔' in genDatum.get_text():
          genInfo.append('T')
        # Each row has <td> elements which aren't displayed and have text like '{{{3}}}'; we ignore those
        elif '{' not in genDatum.get_text():
          genInfo.append('F')

      # can't select Snatch in Gen 8
      while len(genInfo) < numberOfGens():
        genInfo.append('F')

      writer.writerow(['snatch', moveName] + genInfo)

    # Magic coat interactions
    magicCoatTableRows = openLink('https://bulbapedia.bulbagarden.net/wiki/Magic_Coat_(move)', 0, 10).find(id='Affected_moves').find_next('table').find('table').find_all('tr')[2:]

    for row in magicCoatTableRows:
      cells = row.find_all(['td', 'th'])
      moveName, genData = parseName(cells[0].get_text()), cells[2:]

      # will store gen info; Magic Coat debutted in Gen 3
      genInfo = ['F', 'F']
      

      # parse the table
      for genDatum in genData:
        if '✔' in genDatum.get_text():
          genInfo.append('T')
        elif '{' not in genDatum.get_text():
          genInfo.append('F')

      writer.writerow(['magic_coat', moveName] + genInfo)


  return

def makeKingsRockCSV(fname):
  with open(fname, 'w', newline='', encoding='utf-8') as interactionCSV:
    writer = csv.writer(interactionCSV)
    headerRow = ['Move Name']
    # Gen 5 onward, all attacking moves are affected by King's Rock, so we only care about prior generations
    for i in range(4):
      headerRow.append(i + 1)
    writer.writerow(headerRow)

    # Snatch interactions
    dataRows = openLink('https://bulbapedia.bulbagarden.net/wiki/King%27s_Rock', 0, 10).find(id='Moves_affected_before_Generation_V').find_next('table').find('table').find_all('tr')[2:]

    for row in dataRows:
      cells = row.find_all(['td', 'th'])
      moveName, genData = parseName(cells[0].get_text()), cells[3:]

      # ignore shadow moves
      if isShadowMove(moveName):
        continue

      # will store gen info; King's Rock debuted in Gen 2
      genInfo = ['F']

      # parse the table
      for genDatum in genData:
        if '✔' in genDatum.get_text():
          genInfo.append('T')
        elif '{' not in genDatum.get_text():
          genInfo.append('F')

      writer.writerow([moveName] + genInfo)

  return

def main():
  dataPath = getCSVDataPath() + '/moves/'

  fname = dataPath + 'moveInteractions.csv'
  makeInteractionCSV(fname)

  kings_rock_fname = dataPath + 'movesByKingsRock.csv'
  makeKingsRockCSV(kings_rock_fname)

  return

if __name__ == '__main__':
  main()