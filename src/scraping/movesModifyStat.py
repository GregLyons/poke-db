import csv
from os import error
import re
from bs4.element import Tag
from utils import openLink, getBulbapediaDataPath, parseName, genSymbolToNumber


# EXCEPTIONS: ['secret_power', 'crunch', 'diamond_storm', 'acid', 'psychic', 'amnesia', 'shadow_down', 'focus_energy', 'aurora_beam', 'bubble', 'bubble_beam', 'constrict' 'fell_stinger', 'growth']
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
        moveName, gen, modifier, probability = handleMoveLink(moveLink, stat)
        if modifier != 'exception':
          if stat == 'evasiveness':
            stat = 'evasion'

          writer.writerow([moveName, gen, parseName(stat), modifier, sign, recipient, probability])
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

  # handle these moves separately; some more moves which changed between generations (e.g. bubble) will be overwritten when making the move dictionary .json file
  if moveName in ['secret_power', 'psychic', 'amnesia', 'shadow_down', 'shadow_mist', 'focus_energy', 'growth']:
    return moveName, 'exception', 'exception', 'exception'
  # moves with descriptions not covered by the regex defined below
  elif moveName in ['mist_ball', 'luster_purge']:
    return moveName, 3, 1, 50.0
  elif moveName in ['dragon_ascent', 'hyperspace_fury']:
    return moveName, 6, 1, 100.0
  elif moveName == 'thunderous_kick':
    return moveName, 8, 1, 100.0
  elif moveName == 'acupressure':
    return moveName, 4, 2, 100.0
  elif moveName == 'belly_drum':
    return moveName, 2, 12, 100.0

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
      probability_regex = rf"has a (\d*)% chance"
      findProbability = re.search(probability_regex, paragraph)
      if findProbability:
        probability = float(findProbability.group(1))
      else:
        probability = 100.0

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
        
        return moveName, gen, modifier, probability
      elif re.search(other_regex, paragraph):
        return moveName, gen, 1, probability

  # shouldn't be reached unless Bulbapedia changes its descriptions
  print('couldn\'t handle', moveName)

  return 

def makeCSV(fname):
  with open(fname, 'w', newline='', encoding='utf-8') as csvFile:
    writer = csv.writer(csvFile)
    writer.writerow(['Move Name', 'Gen', 'Stat Name', 'Modifier', 'Sign', 'Recipient'])

    bs = openLink('https://bulbapedia.bulbagarden.net/wiki/Category:Moves_by_stat_modification', 0, 10)

    categoryList = bs.find('div', {'class': 'mw-category'}).find('ul').find_all('li')
    for categoryLink in categoryList:
      handleCategoryLink(categoryLink.find('a'), writer)
    
    # # critical hit rate
    # for moveName in ['z_foresight', 'z_sleep_talk', 'z_tailwind', 'z_acupressure', 'z_heart_swap']:
    #   writer.writerow([moveName, 7, 'critical_hit_ratio', 2, '+', 'user'])

  return

# adds Z-move data; 
def addZMoves(fname):
  # a Z-move's stat boosts are added onto the original move's stat boosts, so we keep track of the original stat boosts via statModMoveDict
  with open(fname, 'r', encoding='utf-8') as originalCSV:
    reader = csv.DictReader(originalCSV)
    statModMoveDict = {}

    for row in reader:
      moveName, gen, stat_name, modifier, sign, recipient = row["Move Name"], int(row["Gen"]), row["Stat Name"], row["Modifier"], row["Sign"], row["Recipient"]

      if gen == 8 or gen == 1 and stat_name == 'special':
        continue
      if modifier == 'max':
        modifier = 12

      # if the move is not already in the dictionary, a
      if moveName not in statModMoveDict:
        statModMoveDict[moveName] = []

      statModMoveDict[moveName] = statModMoveDict[moveName] + [{
        "gen": gen, 
        "stat_name": stat_name, 
        "modifier": modifier, 
        "sign": sign,
        "recipient": recipient
      }]

  with open(fname, 'a', newline = '', encoding='utf-8') as newCSV:
    writer = csv.writer(newCSV)

    bs = openLink('https://bulbapedia.bulbagarden.net/wiki/Z-Move', 0, 10)
    dataRows = bs.find(id='Z-Power_effects_of_status_moves').find_next('table').find('table').find_all('tr')[1:]
    

    for row in dataRows:
      cells = row.find_all('td')
      baseMoveName = parseName(cells[0].get_text())
      effect = cells[2].get_text().rstrip('\n')

      # the stat modifications from Z-moves always affect the user and raise stats
      gen = 7
      sign = '+'
      recipient = 'user'
      
      # keep track of stat modifications from Z-move
      statModDict = {
        "attack": 0,
        "defense": 0,
        "special_attack": 0,
        "special_defense": 0,
        "speed": 0,
        "accuracy": 0,
        "evasion": 0,
        "critical_hit_ratio": 0
      }

      # Curse raises attack if user is not Ghost type; its description in Bulbapedia therefore has a different structure, so we manually add this boost
      if baseMoveName == 'curse':
        statModDict["attack"] = 1

      # add single stat boosts
      stats = ['Attack', 'Defense', 'Special Attack', 'Special Defense', 'Speed', 'Evasiveness']
      for stat in stats:
        if stat == ' '.join(effect.split()[:-1]):
          modifier = effect.count('↑')
          stat = parseName(stat).replace('evasiveness', 'evasion')
          statModDict[stat] = statModDict[stat] + modifier

      # indicates all stats are boosted
      if effect.split()[0] == 'Stats':
        modifier = effect.count('↑')
        for stat in ['attack', 'defense', 'special_attack', 'special_defense', 'speed']:
          statModDict[stat] = statModDict[stat] + modifier
      
      # crit boosts
      if 'critical-hit ratio' in effect:
        # always boosts 2 stages
        statModDict["critical_hit_ratio"] = statModDict["critical_hit_ratio"] + 2

      # add Z-move boosts to stat changes of regular move, if any; Z-moves always boost the user's stats
      if baseMoveName in statModMoveDict:
        # recall that statModMoveDict[baseMoveName] is a list of stat changes which baseMoveName applies
        # note that Z-move stat resets are applied BEFORE the base move stat changes, so e.g. Shell Smash resets stats BEFORE lowering defense and special defense
        for statChange in statModMoveDict[baseMoveName]:
          baseMoveStat, baseMoveModifier, baseMoveSign, baseMoveRecipient = statChange["stat_name"], int(statChange["modifier"]), statChange["sign"], statChange["recipient"]

          # in this case, the Z-move does not affect the base move's stat modifier applied to the target, as it only affects stat modifications for the user
          if baseMoveRecipient == 'target':
            writer.writerow(['z_' + baseMoveName, 7, baseMoveStat, baseMoveModifier, baseMoveSign, 'target', 100.0])
            break

          if baseMoveSign == '+':
            sign = 1
          else:
            sign = -1

          statModDict[baseMoveStat] = statModDict[baseMoveStat] + sign * baseMoveModifier

      # write a row to the .csv for each changed stat
      for stat_name in statModDict:
        modifier = statModDict[stat_name]
        if modifier == 0:
          continue
        elif modifier > 0:
          sign = '+'
        else:
          sign = '-'

        writer.writerow(['z_' + baseMoveName, 7, stat_name, modifier, sign, 'user', 100.0])
  return

def main():
  dataPath = getBulbapediaDataPath() + '\\moves\\'
  fname = dataPath + 'movesModifyStat.csv'
  makeCSV(fname)

  # add in Z-move data
  addZMoves(fname)

  return

if __name__ == '__main__':
  main()