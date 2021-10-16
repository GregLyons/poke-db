import csv
import re
from bs4.element import Tag
from utils import openLink, getBulbapediaDataPath, parseName, genSymbolToNumber

# EXCEPTIONS: Secret Power
# Only Crunch, Acid, and Diamond Storm have changed their stat modifications between generations
# Psychic and Amnesia have also changed their stat modifications if you count the Special split


# given an <a> element for a move category, parse the text to determine the stat modification and recipient of the modification, and find all moves therein
def handleCategoryLink(link):
  categoryLink = 'https://bulbapedia.bulbagarden.net' + link['href']
  linkText =  link.get_text()

  # 'Special' refers to Gen 1, when Special Attack and Special Defense were combined
  recipient, stat = re.search(r'Moves that can (raise|lower) the (target|user)\'s (accuracy|evasion|Attack|Defense|Special Attack|Special Defense|Special|Speed)', linkText).group(2, 3)
  
  # now need to find specific move and modification
  bs = openLink(categoryLink, 0, 10)

  # each category is divided into groups, based on the first letter of the move name
  groupList = bs.find(id='mw-pages').find_all('div', {'class': 'mw-category-group'})

  for group in groupList:
    moveList = group.find_next('ul').find_all('li')
    for move in moveList:
      moveLink = move.find('a')
      moveName, gen, modifier = handleMoveLink(moveLink, recipient, stat)
  return

# given an <a> element for a move, 
def handleMoveLink(link, recipient, stat):
  moveLink = 'https://bulbapedia.bulbagarden.net' + link['href']
  moveName = parseName(link.get_text().removesuffix('(move)'))

  # handle these moves separately, due to either their complicated nature (Secret Power) or their change between generations (the rest)
  if moveName in ['secret_power', 'crunch', 'diamond_storm', 'acid', 'psychic', 'amnesia', 'kings_shield', 'memento']:
    return moveName, 'exception', 'exception'
  
  bs = openLink(moveLink, 0, 10)
  descriptionStart = bs.find(id='Effect').parent

  # first entry of element is gen, second entry is text
  moveDescriptions = []
  genDescription = []

  nextNode = descriptionStart.nextSibling
  while nextNode.name != 'h2' and nextNode.get_text().strip('\n') != 'Outside of battle':
    if isinstance(nextNode, Tag):
      # Check header for generation
      if (nextNode.name == 'h3' or nextNode.name == 'h4') and 'Generation' in nextNode.get_text():
        if genDescription != []:
          moveDescriptions.append(genDescription)
          genDescription = []

        startGen = genSymbolToNumber(re.search(r'Generation[s]* ([IVX]*)', nextNode.get_text()).group(1).strip())
        genDescription.append(startGen)
      elif nextNode.name == 'p':
        # get text for move in current generation
        genDescription.append(nextNode.get_text().rstrip('\n'))
    nextNode = nextNode.nextSibling
  moveDescriptions.append(genDescription)

  # if the move hasn't been altered since its introduction, then the generation will not be in the 'Effect' description. We get when it was introduced from the first <p> element
  if not isinstance(moveDescriptions[0][0], int):
    genIntroduced = genSymbolToNumber(re.search(r'introduced in Generation ([IVX]*)\.', bs.find('h1').find_next('p').get_text()).group(1))
    moveDescriptions[0] = [genIntroduced] + moveDescriptions[0] 

  # figure out how many stages by which the stat is modified
  for description in moveDescriptions:
    gen = description[0]
    paragraphs = description[1:]
    for paragraph in paragraphs:
      findStage_regex1 = rf"the ({recipient}|foe)'s {stat}[ stat rises]* by (one|two) stage"
      findStage_regex2 = rf"the {stat}[ stat]* of the ({recipient}|foe) by (one|two) stage"
      findStage1 = re.search(findStage_regex1, paragraph)
      findStage2 = re.search(findStage_regex2, paragraph)
      if findStage1 != None:
        return moveName, gen, findStage1.group(2)
      elif findStage2 != None: 
        return moveName, gen, findStage2.group(2)
      else:
        findStage_regex3 = rf"the {stat}[ stat]* of all hit targets by (one|two) stage"
        findStage_regex4 = rf"the {stat}[ stat]* of all adjacent opponents by (one|two) stage"
        findStage_regex3 = re.search(findStage_regex3, paragraph)
        findStage_regex4 = re.search(findStage_regex4, paragraph)
        if findStage_regex3 != None:
          return moveName, gen, findStage_regex3.group(1)
        elif findStage_regex4 != None:
          return moveName, gen, findStage_regex4.group(1)
        else:
          print(moveName)
          print(paragraph)
          return moveName, gen, None

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