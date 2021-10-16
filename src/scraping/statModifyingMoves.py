import csv
from os import error
import re
from bs4.element import Tag
from utils import openLink, getBulbapediaDataPath, parseName, genSymbolToNumber


# EXCEPTIONS: ['secret_power', 'crunch', 'diamond_storm', 'acid', 'psychic', 'amnesia', 'shadow_down', 'focus_energy']
# Secret Power has a complicated Bulbapedia description to parse, with tables
# Crunch, Acid, Focus Energy, and Diamond Storm have changed their stat modifications between generations
# Psychic and Amnesia have also changed their stat modifications if you count the Special split
# Shadow Down doesn't exist



# given an <a> element for a move category, parse the text to determine the stat modification and recipient of the modification, and find all moves therein
def handleCategoryLink(link, writer):
  categoryLink = 'https://bulbapedia.bulbagarden.net' + link['href']
  linkText =  link.get_text()

  # 'Special' refers to Gen 1, when Special Attack and Special Defense were combined
  print(linkText)
  sign, recipient, stat = re.search(r'Moves that can (raise|lower) the (target|user)\'s (accuracy|evasion|Attack|Defense|Special Attack|Special Defense|Special|Speed)', linkText).group(1, 2, 3)
  if sign == 'raise':
    sign = '+'
  else:
    sign = '-'
  
  # now need to find specific move and modification
  bs = openLink(categoryLink, 0, 10)

  # each category is divided into groups, based on the first letter of the move name
  moveLists = bs.find(id='mw-pages').find_all('ul')

  print(sign, recipient, stat)

  try:
    for moveList in moveLists:
      for move in moveList.find_all('li'):
        moveLink = move.find('a')
        moveName, gen, modifier = handleMoveLink(moveLink, stat)
        if modifier != 'exception':
          if stat == 'evasiveness':
            stat = 'evasion'

          writer.writerow([moveName, gen, parseName(stat), modifier, sign, recipient])
        else: 
          continue

  except Exception as e:
    print(e)
    print('something went wrong with', sign, recipient, stat)
    print()
    return []

# given an <a> element for a move, 
def handleMoveLink(link, stat):
  moveLink = 'https://bulbapedia.bulbagarden.net' + link['href']
  moveName = parseName(link.get_text().removesuffix('(move)'))

  # handle these moves separately, due to either their complicated nature (Secret Power) or their change between generations (the rest)
  if moveName in ['secret_power', 'crunch', 'diamond_storm', 'acid', 'psychic', 'amnesia', 'shadow_down', 'shadow_mist']:
    return moveName, 'exception', 'exception'
  # moves with descriptions not covered by the regex defined below
  elif moveName in ['mist_ball', 'luster_purge']:
    return moveName, 3, 1
  elif moveName in ['dragon_ascent', 'hyperspace_fury']:
    return moveName, 6, 1
  elif moveName == 'thunderous_kick':
    return moveName, 8, 1
  elif moveName == 'acupressure':
    return moveName, 4, 2
  elif moveName == 'belly_drum':
    return moveName, 2, 'max'

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

        try:
          startGen = genSymbolToNumber(re.search(r'Generation[s]* ([IVX]*)', nextNode.get_text()).group(1).strip())

        except AttributeError:
          print('something went wrong with', moveName)

        genDescription.append(startGen)

      elif nextNode.name == 'p':
        # get text for move in current generation
        genDescription.append(nextNode.get_text().rstrip('\n'))

    nextNode = nextNode.nextSibling
  moveDescriptions.append(genDescription)

  # if the move hasn't been altered since its introduction, then the generation will not be in the 'Effect' description. We get when it was introduced from the first <p> element
  if not isinstance(moveDescriptions[0][0], int):
    try:
      genIntroduced = genSymbolToNumber(re.search(r'introduced in Generation ([IVX]*)\.', bs.find('h1').find_next('p').get_text()).group(1))
      moveDescriptions[0] = [genIntroduced] + moveDescriptions[0] 

    # indicates gen not given in description
    except AttributeError:
      print('something went wrong finding gen of', moveName)

  # figure out how many stages by which the stat is modified
  for description in moveDescriptions:
    gen = description[0]
    paragraphs = description[1:]

    for paragraph in paragraphs:
      findStage_regex = rf"{stat}[\w\s,()-é]* (one|two|1|2|three) [stat ]*(stage|level)"
      other_regex = rf"evasiveness."

      findStage = re.search(findStage_regex, paragraph) 

      if findStage:
        if len(findStage.group(1)) > 1:
          if findStage.group(1) == 'one':
            modifier = 1
          elif findStage.group(1) == 'two':
            modifier = 2
          elif findStage.group(1) == 'three':
            modifier = 3
        else:
          modifier = findStage.group(1)
        
        return moveName, gen, modifier
      elif re.search(other_regex, paragraph):
        return moveName, gen, 1

  # shouldn't be reached unless Bulbapedia changes its descriptions
  print('couldn\'t handle', moveName)

  return 

def statModifyingMoves(fname):
  with open(fname, 'w', newline='', encoding='utf-8') as csvFile:
    writer = csv.writer(csvFile)
    writer.writerow(['Move Name', 'Gen', 'Stat Name', 'Modifier', 'Recipient'])

    bs = openLink('https://bulbapedia.bulbagarden.net/wiki/Category:Moves_by_stat_modification', 0, 10)

    categoryList = bs.find('div', {'class': 'mw-category'}).find('ul').find_all('li')
    for categoryLink in categoryList:
      handleCategoryLink(categoryLink.find('a'), writer)
    
    # critical hit rate
    for moveName in ['z_foresight', 'z_sleep_talk', 'z_tailwind', 'z_acupressure', 'z_heart_swap']:
      writer.writerow([moveName, 7, 'critical_hit_ratio', 2, '+', 'user'])

  return

def main():
  dataPath = getBulbapediaDataPath() + '\\moves\\'
  fname = dataPath + 'statModifyingMoves.csv'
  statModifyingMoves(fname)

  return

if __name__ == '__main__':
  main()