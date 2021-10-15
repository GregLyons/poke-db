import csv
import os
import re
from utils import openBulbapediaLink, removeShadowMoves, getDataBasePath, parseName

# Columns are Targets, Move Name
def makeMainCSV(label, url, writer):
  bs = openBulbapediaLink(url, 0, 10)
  findSection = bs.find('h2', text=re.compile(r'Pages in category'))
  moves = [link.get_text().rstrip('(move)').strip() for link in findSection.find_all_next('a') if '(move)' in link.get_text()]

  # the moves are listed after an h2 containing the text 'Pages in category', and they are links whose text has the string '(move)'

  for move in moves:
    writer.writerow([parseName(label), parseName(move)])

def main():
  labelsAndLinks = [
    ['user-and-all-allies', 'https://bulbapedia.bulbagarden.net/wiki/Category:Moves_that_target_the_user_and_all_allies'],
    ['adjacent-foe', 'https://bulbapedia.bulbagarden.net/wiki/Category:Moves_that_can_target_any_adjacent_foe_Pok%C3%A9mon'],
    ['any-other', 'https://bulbapedia.bulbagarden.net/wiki/Category:Moves_that_can_target_any_Pok%C3%A9mon'],
    ['all-adjacent-foes', 'https://bulbapedia.bulbagarden.net/wiki/Category:Moves_that_target_all_adjacent_foes'],
    ['all-adjacent', 'https://bulbapedia.bulbagarden.net/wiki/Category:Moves_that_target_all_adjacent_Pok%C3%A9mon'],
    ['all-allies', 'https://bulbapedia.bulbagarden.net/wiki/Category:Moves_that_target_all_allies'],
    ['all-foes', 'https://bulbapedia.bulbagarden.net/wiki/Category:Moves_that_target_all_foes'],
    ['all', 'https://bulbapedia.bulbagarden.net/wiki/Category:Moves_that_target_all_Pok%C3%A9mon']
  ]

  dataPath = getDataBasePath() + 'moves\\'

  fname = dataPath + 'movesByTargetWithShadowMoves.csv'
  csvFile = open(fname, 'w', newline='', encoding='utf-8')
  writer = csv.writer(csvFile, quoting=csv.QUOTE_MINIMAL)
  writer.writerow(['Targets', 'Move Name'])

  # 
  for [label, link] in labelsAndLinks:
    makeMainCSV(label, link, writer)

  csvFile.close()

  removeShadowMoves(fname, 'Targets')
  os.remove(fname)

  # acupressure targets user or adjacent ally

  # most moves are any adjacent 

if __name__ == '__main__':
  main()