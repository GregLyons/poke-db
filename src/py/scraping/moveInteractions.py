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

    # Protect interactions; data is given in terms of moves which bypass protect, i.e. those which DON'T interact with Protect
    protectTableRows = openLink('https://bulbapedia.bulbagarden.net/wiki/Protect_(move)', 0, 10).find(id='Moves_that_bypass_Protect').find_next('table').find('table').find_all('tr')[2:]

    for row in protectTableRows:
      cells = row.find_all(['td', 'th'])
      moveName, genData = parseName(cells[0].get_text()), cells[3:]

      # will store gen info; Protect debutted in Gen 2
      genInfo = ['F']

      # parse the table
      for genDatum in genData:
        # move bypasses protect, so it DOESN'T interact with protect
        if '✔' in genDatum.get_text():
          genInfo.append('F')
        # move doesn't bypass protect, so it DOES interact with protect
        elif '{' not in genDatum.get_text():
          genInfo.append('T')

      # table is missing all the <td>'s in some rows
      while len(genInfo) < numberOfGens():
        genInfo.append('F')

      writer.writerow(['protect', moveName] + genInfo)
      # detect is functionally identical to Protect, so we add that as well
      writer.writerow(['detect', moveName] + genInfo)

    # Spiky Shield interactions; like with Protect, the moves listed DON'T interact with spiky shield
    spikyShieldTableRows = openLink('https://bulbapedia.bulbagarden.net/wiki/Spiky_Shield_(move)', 0, 10).find(id='Effect').find_next('table').find('table').find_all('tr')[1:]

    for row in spikyShieldTableRows:
      cells = row.find_all(['td', 'th'])
      moveName = parseName(cells[0].get_text())

      # will store gen info; Spiky Shield debutted in Gen VI
      genInfo = ['F', 'F', 'F', 'F', 'F']

      # the moves don't interact with spiky shield
      while len(genInfo) < numberOfGens():
        genInfo.append('F')

      writer.writerow(['spiky_shield', moveName] + genInfo)

    # Baneful Bunker; similar to Protect
    banefulBunkerTableRows = openLink('https://bulbapedia.bulbagarden.net/wiki/Baneful_Bunker_(move)', 0, 10).find(id='Effect').find_next('table').find('table').find_all('tr')[1:]

    for row in banefulBunkerTableRows:
      cells = row.find_all(['td', 'th'])
      moveName = parseName(cells[0].get_text())

      # will store gen info; debutted in Gen VII
      genInfo = ['F', 'F', 'F', 'F', 'F', 'F']

      # the moves don't interact with baneful bunker
      while len(genInfo) < numberOfGens():
        genInfo.append('F')

      writer.writerow(['baneful_bunker', moveName] + genInfo)

    # King's Shield interactions, similar to Protect; note that all status moves bypass King's Shield
    kingsShieldTableRows = openLink('https://bulbapedia.bulbagarden.net/wiki/King%27s_Shield_(move)', 0, 10).find(id='Moves_that_bypass_King.27s_Shield').find_next('table').find('table').find_all('tr')[1:]

    for row in kingsShieldTableRows:
      cells = row.find_all(['td', 'th'])
      moveName = parseName(cells[0].get_text())

      # will store gen info; debutted in Gen VI
      genInfo = ['F', 'F', 'F', 'F', 'F']

      # the moves don't interact with king's shield
      while len(genInfo) < numberOfGens():
        genInfo.append('F')

      writer.writerow(['kings_shield', moveName] + genInfo)

    # Mat Block doesn't have a table, but is bypassed by the following moves (we don't list status moves); similarly for Obstruct
    for bypassingMove in ['feint', 'hyperspace_fury', 'hyperspace_hole', 'phantom_force', 'shadow_force', 'future_sight', 'doom_desire']:
      writer.writerow(['mat_block', bypassingMove] + ['F'] * 8)
      writer.writerow(['obstruct', bypassingMove] + ['F'] * 8)

    # Max Guard doesn't have a table, but is bypassed by the following moves:
    for bypassingMove in ['feint', 'mean_look', 'role_play', 'perish_song', 'decorate', 'g_max_one_blow', 'g_max_rapid_flow']:
      writer.writerow(['max_guard', bypassingMove] + ['F'] * 8)

  return

def makeKingsRockCSV(fname):
  with open(fname, 'w', newline='', encoding='utf-8') as interactionCSV:
    writer = csv.writer(interactionCSV)
    headerRow = ['Move Name']
    # Gen 5 onward, all attacking moves are affected by King's Rock, so we only care about prior generations
    for i in range(4):
      headerRow.append(i + 1)
    writer.writerow(headerRow)

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