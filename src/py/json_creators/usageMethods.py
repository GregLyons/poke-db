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
  for statusName in usageMethodsAndGens.keys():
    formattedEffectName = getFormattedName(statusName)
    usageMethodDict[statusName] = {
      "gen": usageMethodsAndGens[statusName],
      "formatted_name": formattedEffectName
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

def main():
  usageMethodDict = makeUsageMethodDict()

  return usageMethodDict

if __name__ == '__main__':
  main()