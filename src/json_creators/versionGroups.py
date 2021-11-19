def makeVersionGroupDict():
  # easier to write it this way first, instead of writing all the keys
  versionGroupProtoDict = {
    "Stad": ["Stadium", 1],
    "GS": ["Gold/Silver", 2],
    "C": ["Crystal", 2],
    "Stad2": ["Stadium 2", 2],
    "RS": ["Ruby/Sapphire", 3],
    "E": ["Emerald", 3],
    "Colo": ["Colosseum", 3],
    "XD": ["XD: Gale of Darkness", 3],
    "FRLG": ["Fire Red/Leaf Green", 3],
    "DP": ["Diamond/Pearl", 4],
    "Pt": ["Platinum", 4],
    "HGSS": ["Heart Gold/Soul Silver", 4],
    "PBR": ["Pokemon Battle Revolution", 4],
    "BW": ["Black/White", 5],
    "B2W2": ["Black 2/White 2", 5],
    "XY": ["X/Y", 6],
    "ORAS": ["Omega Ruby/Alpha Sapphire", 6],
    "SM": ["Sun/Moon", 7],
    "USUM": ["Ultra Sun/Ultra Moon", 7],
    "PE": ["Let's Go Pikachu/Let's Go Eeevee", 7],
    "SwSh": ["Sword/Shield", 8]
  }

  versionGroupDict = {}
  for versionGroupCode in versionGroupProtoDict.keys():
    formattedName, gen = versionGroupProtoDict[versionGroupCode]

    versionGroupDict[versionGroupCode] = {
      "gen": gen,
      "formatted_name": formattedName,
    }

  return versionGroupDict

def main():
  versionGroupDict = makeVersionGroupDict()

  return versionGroupDict

if __name__ == '__main__':
  main()