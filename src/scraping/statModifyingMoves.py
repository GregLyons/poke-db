import csv
import re
from bs4.element import NavigableString, Tag
from utils import openLink, getBulbapediaDataPath, parseName, genSymbolToNumber

# given an <a> element for a move category, parse the text to determine the stat modification and recipient of the modification, and find all moves therein
def handleCategoryLink(link):
  categoryLink = 'https://bulbapedia.bulbagarden.net' + link['href']
  linkText =  link.get_text()

  # 'Special' refers to Gen 1, when Special Attack and Special Defense were combined
  recipient, stat = re.search(r'Moves that can (raise|lower) the (target|user)\'s (accuracy|evasion|Attack|Defense|Special Attack|Special Defense|Special|Speed)', linkText).group(2, 3)
  recipient, stat = parseName(recipient), parseName(stat)
  
  # now need to find specific move and modification
  bs = openLink(categoryLink, 0, 10)

  # each category is divided into groups, based on the first letter of the move name
  groupList = bs.find(id='mw-pages').find_all('div', {'class': 'mw-category-group'})

  for group in groupList:
    moveList = group.find_next('ul').find_all('li')
    for move in moveList:
      moveLink = move.find('a')
      handleMoveLink(moveLink)
  return

# given an <a> element for a move, 
def handleMoveLink(link):
  moveLink = 'https://bulbapedia.bulbagarden.net' + link['href']
  moveName = parseName(link.get_text().removesuffix('(move)'))
  print(moveName)
  
  bs = openLink(moveLink, 0, 10)
  descriptionStart = bs.find(id='Effect').parent

  # first entry of element is gen, second entry is text
  moveDescriptions = []

  nextNode = descriptionStart.nextSibling
  while nextNode.name != 'h2' and nextNode.get_text().strip('\n') != 'Outside of battle':
    if isinstance(nextNode, NavigableString):
      print(nextNode.strip())
    if isinstance(nextNode, Tag):
      if (nextNode.name == 'h3' or nextNode.name == 'h4') and 'Generation' in nextNode.get_text():
        print(nextNode.get_text())
        startGen = genSymbolToNumber(re.search(r'Generation[s]* (I |II |III|IV|V |VI |VII |VIII|IX)', nextNode.get_text()).group(1).strip())
        print(startGen)

    nextNode = nextNode.nextSibling

  print(moveDescriptions)

  return

def statModifyingMoves(fname):
  with open(fname, 'w', newline='', encoding='utf-8') as csvFile:
    writer = csv.writer(csvFile)
    bs = openLink('https://bulbapedia.bulbagarden.net/wiki/Category:Moves_by_stat_modification', 0, 10)

    categoryList = bs.find('div', {'class': 'mw-category'}).find('ul').find_all('li')
    for categoryLink in categoryList:
      handleCategoryLink(categoryLink.find('a'))

  return

def main():
  dataPath = getBulbapediaDataPath() + '\\moves\\'
  fname = dataPath + 'statModifyingMoves.csv'
  statModifyingMoves(fname)

  return

if __name__ == '__main__':
  main()