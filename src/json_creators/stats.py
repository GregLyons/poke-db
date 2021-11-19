from utils import statList

def makeStatDict():
  statDict = {}
  for statName in statList():
    formattedEffectName = getFormattedName(statName)
    statDict[statName] = {
      "formatted_name": formattedEffectName
    }

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

def main():
  statDict = makeStatDict()

  return statDict

if __name__ == '__main__':
  main()