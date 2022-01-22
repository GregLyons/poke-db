from utils import usageMethodList

# dictionary containing usage method names and gen usage method was introduced
# gen is NOT when the earliest move of the corresponding usage method was introduced, but rather when the usage method becomes a mechanic. e.g. mega launcher, the only ability which interacts with pulse moves, was introduced in gen 6, whereas dark pulse, a pulse move, was introduced in gen 4
def makeUsageMethodDict():
  usageMethodsAndGens = {
    # mega launcher
    "pulse": 6, 
    # bulletproof
    "ball": 6,
    # strong jaw
    "bite": 6,
    # Tierno in Pokemon X/Y wants to see dance moves, but first battle interaction is with ability Dancer in gen 7
    "dance": 7,
    # damp
    "explosive": 3,
    # from gen 6 on, Grass-type, Overcoat, and safety goggles are immune to powder moves
    "powder": 6,
    # iron fist
    "punch": 4,
    # soundproof
    "sound": 3,
  }

  usageMethodDict = {}
  for usageMethodName in usageMethodsAndGens.keys():
    formattedUsageMethodName = getFormattedName(usageMethodName)
    usageMethodDict[usageMethodName] = {
      "gen": usageMethodsAndGens[usageMethodName],
      "formatted_name": formattedUsageMethodName
    }

  # make sure all usage methodsare accounted for
  for usageMethod in usageMethodList():
    if usageMethod not in usageMethodDict:
      print(usageMethod, 'not in usageMethodDict')

  # make sure no typos
  for key in usageMethodDict.keys():
    if key not in usageMethodList():
      print(key, 'not in usageMethodList')

  return usageMethodDict

def getFormattedName(usageMethodName):
  # replace underscores with spaces
  formattedName = usageMethodName.replace('_', ' ')
  
  # make first letter uppercase
  formattedName = formattedName[0].upper() + formattedName[1:]

  return formattedName

def addDescriptions(usageMethodDict):
  # pulse
  usageMethodDict["pulse"]["description"] = [
    ['Moves based on aura and pulses.', 6]
  ]

  # ball
  usageMethodDict["ball"]["description"] = [
    ['Moves based on balls and bombs.', 6]
  ]

  # bite
  usageMethodDict["bite"]["description"] = [
    ['Moves based on biting.', 6]
  ]

  # dance
  usageMethodDict["dance"]["description"] = [
    ['Moves based on dancing.', 7]
  ]

  # explosive
  usageMethodDict["explosive"]["description"] = [
    ['Moves based on explosions.', 3]
  ]

  # powder
  usageMethodDict["powder"]["description"] = [
    ['Moves based on powders and spores.', 6]
  ]

  # punch
  usageMethodDict["punch"]["description"] = [
    ['Moves based on punching.', 4]
  ]

  # sound
  usageMethodDict["sound"]["description"] = [
    ['Moves based on sound.', 3]
  ]


  return usageMethodDict

def addActivationData(usageMethodDict):
  for usageMethodName in usageMethodDict.keys():
    usageMethodDict[usageMethodName]["activates_ability"] = {}
    usageMethodDict[usageMethodName]["activates_item"] = {}

  # dancer
  usageMethodDict["dance"]["activates_ability"]["dancer"] = [[True, 7]]

  # sound
  usageMethodDict["sound"]["activates_ability"]["liquid_voice"] = [[True, 7]]
  usageMethodDict["sound"]["activates_item"]["throat_spray"] = [[True, 8]]

  return usageMethodDict

def main():
  usageMethodDict = makeUsageMethodDict()

  addDescriptions(usageMethodDict)

  addActivationData(usageMethodDict)

  for usageMethodName in usageMethodDict.keys():
    if 'description' not in usageMethodDict[usageMethodName].keys():
      print(usageMethodName, 'is missing a description.')

  return usageMethodDict

if __name__ == '__main__':
  main()