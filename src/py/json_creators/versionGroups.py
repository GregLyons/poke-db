def makeVersionGroupDict():
  # easier to write it this way first, instead of writing all the keys
  versionGroupProtoDict = {
    "RB": ["Red/Blue", 1],
    "Y": ["Yellow", 1],
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
    "SwSh": ["Sword/Shield", 8],
    "BDSP": ["Brilliant Diamond/Shining Pearl", 8]
  }

  versionGroupDict = {}
  for versionGroupCode in versionGroupProtoDict.keys():
    formattedName, gen = versionGroupProtoDict[versionGroupCode]

    versionGroupDict[versionGroupCode] = {
      "gen": gen,
      "formatted_name": formattedName,
    }

  return versionGroupDict

# Given the code for a version group, return the name, formatted with the version names in snake case, separated by a '/'
def getVersionGroupName(code):
  if code == 'RB':
    return 'red/blue'
  elif code == 'Y':
    return 'yellow'
  elif code == 'Stad':
    return 'stadium'
  elif code == 'GS':
    return 'gold/silver'
  elif code == 'C':
    return 'crystal'
  elif code == 'Stad2':
    return 'stadium_2'
  elif code == 'RS':
    return 'ruby/sapphire'
  elif code == 'E':
    return 'emerald'
  elif code == 'Colo':
    return 'colosseum'
  elif code == 'XD':
    return 'xd_gale_of_darkness'
  elif code == 'FRLG':
    return 'fire_red/leaf_green'
  elif code == 'DP':
    return 'diamond/pearl'
  elif code == 'Pt':
    return 'platinum'
  elif code == 'HGSS':
    return 'heart_gold/soul_silver'
  elif code == 'PBR':
    return 'pokemon_battle_revolution'
  elif code == 'BW':
    return 'black/white'
  elif code == 'B2W2':
    return 'black_2/white_2'
  elif code == 'XY':
    return 'x/y'
  elif code == 'ORAS':
    return 'omega_ruby/alpha_sapphire'
  elif code == 'SM':
    return 'sun/moon'
  elif code == 'USUM':
    return 'ultra_sun/ultra_moon'
  elif code == 'PE':
    return 'lets_go_pikachu/lets_go_eevee'
  elif code == 'SwSh':
    return 'sword/shield'
  elif code == 'BDSP':
    return 'brilliant_diamond/shining_pearl'
  else:
    print('Couldn\'t find name for version group code:', code, '.')

def main():
  versionGroupDict = makeVersionGroupDict()

  return versionGroupDict

if __name__ == '__main__':
  main()