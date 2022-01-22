from utils import statList

def makeStatDict():
  statDict = {}
  for statName in statList():
    formattedEffectName = getFormattedName(statName)
    statDict[statName] = {
      "gen": 1,
      "formatted_name": formattedEffectName
    }

  # Serene grace 
  statDict["secondary_effect_chance"]["gen"] = 3

  # make sure all stats are accounted for
  for stat in statList():
    if stat not in statDict:
      print(stat, 'not in statDict')

  # make sure no typos
  for key in statDict.keys():
    if key not in statList():
      print(key, 'not in statList')

  
  return statDict

def getFormattedName(statName):
  # replace underscores with spaces
  formattedName = statName.replace('_', ' ')
  
  # make first letter uppercase
  formattedName = formattedName[0].upper() + formattedName[1:]

  formattedName = formattedName.replace('ritical hit', 'ritical-hit')

  return formattedName

def addDescriptions(statDict):
  # attack
  statDict["attack"]["description"] = [
    ['Determines the damage done by physical moves used by the Pokemon.', 1],
  ]

  # defense
  statDict["defense"]["description"] = [
    ['Determines the damage inflicted by physical moves used against this Pokemon.', 1],
  ]

  # special attack
  statDict["special_defense"]["description"] = [
    ['Determines the damage done by special moves used by this Pokemon. In Generation 1, Special Attack and Special Defense are combined into a single stat, \'Special\'.', 1],
    ['Determines the damage done by special moves used by this Pokemon.', 2],
  ]

  # special defense
  statDict["special_defense"]["description"] = [
    ['Determines the damage inflicted by special moves used against this Pokemon. In Generation 1, Special Attack and Special Defense are combined into a single stat, \'Special\'.', 1],
    ['Determines the damage inflicted by special moves used against this Pokemon.', 2],
  ]

  # speed
  statDict["speed"]["description"] = [
    ['Determines the order in which Pokemon act in battle. For Pokemon moving in the same priority bracket, the Pokemon with the higher Speed goes first, with ties broken randomly.', 1]
  ]

  # critical hit ratio
  statDict["critical_hit_ratio"]["description"] = [
    ['The rate at which the Pokemon scores critical hits.', 1],
  ]

  # secondary effect chance
  statDict["secondary_effect_chance"]["description"] = [
    ['The rate at which the secondary effects of the Pokemon\'s moves occur.', 3],
  ]

  # evasion
  statDict["evasion"]["description"] = [
    ['The rate at which the Pokemon avoids attacks.', 1],
  ]

  # accuracy
  statDict["accuracy"]["description"] = [
    ['The rate at which the Pokemon lands its moves.', 1
    ],
  ]

  return statDict

def main():
  statDict = makeStatDict()

  addDescriptions(statDict)

  for statName in statDict.keys():
    if 'description' not in statDict[statName].keys():
      print(statName, 'is missing a description.')

  return statDict

if __name__ == '__main__':
  main()