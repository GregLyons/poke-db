import csv
import os
import re
from utils import openBulbapediaLink, removeShadowMoves, getDataPath

def makeMainCSV(label, url, writer):
  bs = openBulbapediaLink(url, 0, 10)
  findSection = bs.find('h2', text=re.compile(r'Pages in category'))
  moves = [link.get_text().rstrip('(move)').replace(' ', '') for link in findSection.find_all_next('a') if '(move)' in link.get_text()]

  # the moves are listed after an h2 containing the text 'Pages in category', and they are links whose text has the string '(move)'

  for move in moves:
    writer.writerow([label, move])

labelsAndLinks = [
  ['userAndAllAllies', 'https://bulbapedia.bulbagarden.net/wiki/Category:Moves_that_target_the_user_and_all_allies'],
  ['adjacentFoe', 'https://bulbapedia.bulbagarden.net/wiki/Category:Moves_that_can_target_any_adjacent_foe_Pok%C3%A9mon'],
  ['anyOther', 'https://bulbapedia.bulbagarden.net/wiki/Category:Moves_that_can_target_any_Pok%C3%A9mon'],
  ['allAdjacentFoes', 'https://bulbapedia.bulbagarden.net/wiki/Category:Moves_that_target_all_adjacent_foes'],
  ['allAdjacent', 'https://bulbapedia.bulbagarden.net/wiki/Category:Moves_that_target_all_adjacent_Pok%C3%A9mon'],
  ['allAllies', 'https://bulbapedia.bulbagarden.net/wiki/Category:Moves_that_target_all_allies'],
  ['allFoes', 'https://bulbapedia.bulbagarden.net/wiki/Category:Moves_that_target_all_foes'],
  ['all', 'https://bulbapedia.bulbagarden.net/wiki/Category:Moves_that_target_all_Pok%C3%A9mon']
]

fname = getDataPath() + 'movesByTargetWithShadowMoves.csv'
csvFile = open(fname, 'w', newline='', encoding='utf-8')
writer = csv.writer(csvFile, quoting=csv.QUOTE_MINIMAL)
writer.writerow(['Target', 'Move Name'])

# 
for [label, link] in labelsAndLinks:
  makeMainCSV(label, link, writer)

csvFile.close()

removeShadowMoves(fname, 'Target')
os.remove(fname)

# acupressure targets user or adjacent ally

# most moves are any adjacent 