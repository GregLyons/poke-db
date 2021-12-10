from pathlib import Path
import os
import glob
import json
import re
from utils import genSymbolToNumber, getVersionGroupsInGen, baseFormSuffices, numberOfGens, getJSONDataPath
import pokemon
import heldItems
from PIL import Image

# Given a version group folder name, get the corresponding version code.
def versionGroupNameToCodes(versionGroupName):
  if versionGroupName == 'red-blue':
    return ['RB']
  elif versionGroupName == 'yellow':
    return ['Y', 'Stad']

  # Gold and Silver have separate sprites
  elif versionGroupName == 'gold':
    return ['GS']
  elif versionGroupName == 'silver':
    return ['GS']

  elif versionGroupName == 'gold-silver':
    return ['GS']
  elif versionGroupName == 'crystal':
    return ['C', 'Stad2']
  elif versionGroupName == 'emerald':
    return ['E', 'Colo', 'XD']
  elif versionGroupName == 'firered-leafgreen':
    return ['FRLG']
  elif versionGroupName == 'ruby-sapphire':
    return ['RS']
  elif versionGroupName == 'diamond-pearl':
    return ['DP']
  elif versionGroupName == 'platinum':
    return ['Pt', 'PBR']
  elif versionGroupName == 'heartgold-soulsilver':
    return ['HGSS']
  elif versionGroupName == 'black-white':
    return ['BW', 'B2W2']
  elif versionGroupName == 'omegaruby-alphasapphire':
    return ['ORAS']
  elif versionGroupName == 'x-y':
    return ['XY']
  elif versionGroupName == 'ultra-sun-ultra-moon':
    return ['SM', 'USUM', 'PE']
  else:
    raise Exception(f'Version code not handled: {versionGroupName}.')


# Returns 'maps', which unpacks as (in order):
#   dex_pokemon: maps a national dex number to an array of Pokemon with that national dex number in pokemonDict.
#   pokeapiID_pokemonName: maps a pokeapi ID to the corresponding Pokemon form name in pokemonDict.
#   unmatchedPokemonName_pokeapiID: maps a pokemonName in pokemonDict, which does not already have a pokeapi ID, to a pokeapi ID. 
def getPokemonSpriteMaps(pokemonDict):
  dex_pokemon = {}
  pokeapiID_pokemonName = {}
  unmatchedPokemonName_pokeapiID = {}
  for pokemonName in pokemonDict.keys():
    dexNumber = pokemonDict[pokemonName]["dex_number"]

    if dexNumber not in dex_pokemon.keys():
      dex_pokemon[dexNumber] = []
    dex_pokemon[dexNumber].append(pokemonName)

    try:
      pokeapiID = pokemonDict[pokemonName]["pokeapi"][-1]
      pokeapiID_pokemonName[pokeapiID] = pokemonName
      if pokeapiID in pokeapiID_pokemonName.keys() and pokeapiID_pokemonName[pokeapiID] != pokemonName:
        print('Duplicate PokeAPI ID:', pokeapiID_pokemonName[pokeapiID], pokemonName)
    except IndexError:
      # a
      if pokemonName == 'unown':
        unmatchedPokemonName_pokeapiID["unown"] = 201
        continue
      # plant
      elif pokemonName == 'mothim':
        unmatchedPokemonName_pokeapiID["mothim"] = 414
        continue
      # icy snow
      elif pokemonName == 'scatterbug':
        unmatchedPokemonName_pokeapiID["scatterbug"] = 664
        continue
      # icy snow
      elif pokemonName == 'spewpa':
        unmatchedPokemonName_pokeapiID["unown"] = 665
        continue
      # icy snow, except meadow for gen 8 icon
      elif pokemonName == 'vivillon':
        unmatchedPokemonName_pokeapiID["vivillon"] = 666
        continue
      # red
      elif pokemonName == 'flabebe':
        unmatchedPokemonName_pokeapiID["flabebe"] = 669
        continue
      # red
      elif pokemonName == 'floette':
        unmatchedPokemonName_pokeapiID["floette"] = 670
        continue
      # red
      elif pokemonName == 'florges':
        unmatchedPokemonName_pokeapiID["florges"] = 671
        continue
      # active
      elif pokemonName == 'xerneas':
        unmatchedPokemonName_pokeapiID["xerneas"] = 718
        continue
      # red 
      elif pokemonName == 'minior':
        unmatchedPokemonName_pokeapiID["minior"] = 10255
        continue
      # phony
      elif pokemonName == 'sinistea':
        unmatchedPokemonName_pokeapiID["sinistea"] = 854
        continue
      # phony
      elif pokemonName == 'polteageist':
        unmatchedPokemonName_pokeapiID["polteageist"] = 855
        continue
      # no pokeapi sprite--assign to pikachu_original_cap
      elif pokemonName == 'pikachu_world_cap':
        unmatchedPokemonName_pokeapiID["pikachu_world_cap"] = 201
        continue
      # dusk
      elif pokemonName == 'necrozma_dusk_mane':
        unmatchedPokemonName_pokeapiID["necrozma_dusk_mane"] = 10314
        continue
      # dawn
      elif pokemonName == 'necrozma_dawn_wings':
        unmatchedPokemonName_pokeapiID["necrozma_dawn_wings"] = 10315
        continue
      # no pokeapi sprite--assign to pikachu
      elif pokemonName == 'pikachu_partner':
        unmatchedPokemonName_pokeapiID["pikachu_partner"] = 25
        continue
      # no pokeapi sprite--assign to eevee
      elif pokemonName == 'eevee_partner':
        unmatchedPokemonName_pokeapiID["eevee_partner"] = 133
        continue
      # red meteor
      elif pokemonName == 'minior_meteor':
        unmatchedPokemonName_pokeapiID["minior_meteor"] = 774
        continue
      else:
        raise Exception(f'{pokemonName} unhandled!')

  maps = dex_pokemon, pokeapiID_pokemonName, unmatchedPokemonName_pokeapiID

  return maps

# Given the list of possiblePokemon for a given filename, the given filename, and whether the filepath to that file contains a 'female' folder, return the name of the corresponding pokemon in pokemonDict.
def matchPokemon(possiblePokemon, filename, female):
  # If there's only one possible Pokemon, return that Pokemon.
  if len(possiblePokemon) == 1:
    return possiblePokemon[0]
  
  # If there's no possible Pokemon, throw an error.
  elif len(possiblePokemon) == 0:
    raise Exception(f'No possible Pokemon for {filename}.')

  # Determine base form in possiblePokemon for later use.
  # region

  # We identify the baseform as the one with the least amount of form data in its name (i.e. name in possiblePokemon with fewest parts, separated by underscores).
  minNameParts = 9999
  baseFormName = ''

  for pokemonName in possiblePokemon:
    splitPokemonName = pokemonName.split('_')
    
    #We identify the base form as the one with the fewest name parts.
    if len(splitPokemonName) < minNameParts:
      minNameParts = len(splitPokemonName)
      baseFormName = pokemonName
  # endregion

  # Match Pokemon in the 'female' folder ('female' = True) with their female form, if possible.
  if female:
    # If the only aspect of a Pokemon which depends on gender is the appearance, then we may not have caught it in pokemonDict. We will match both the male and female sprite to such a Pokemon. 
    # The female sprite will be of the Pokemon's base form. 

    # Iterate over possiblePokemon to find either: 
    #   The female form, ending in '_f'.
    #   The base form.
    for pokemonName in possiblePokemon:
      splitPokemonName = pokemonName.split('_')

      # Sometimes, the female form will have tangible, in-game differences (e.g. meowstic). In this case, its name will end with 'f'
      if splitPokemonName[-1] == 'f':
        return pokemonName
      
      # Otherwise, the female form will not have an 'f' suffix. The female sprite will be of the base form for the Pokemon. 

    return baseFormName

  # If sprite is not a female sprite, then we use the filename itself to determine the form of the Pokemon.
  # The first part of the filename is the dex number, which we've already used to create possiblePokemon. Subsequent parts describe the form. In general, the form data will match the form names in pokemonDict.
  filenameFormData = '_'.join(filename.split('-')[1:])

  # If there's no form data, return the baseFormName
  if len(filenameFormData) == 0 and len(baseFormName.split('_')) == 1:
    return baseFormName

  # Handling various exceptions where the form data in the filename doesn't match the form names in pokemonDict.
  # region
  
  # rename calyrex forms
  if '898' in filename:
    filenameFormData = filenameFormData.replace('_rider', '')

  # partner pikachu and eevee
  if filenameFormData.split('_')[-1] == 'starter':
    filenameFormData = filenameFormData.replace('starter', 'partner')

  # minior meteor colors
  if filenameFormData.split('_')[-1] == 'meteor':
    filenameFormDataParts = filenameFormData.split('_')
    filenameFormData = '_'.join([filenameFormDataParts[-1], filenameFormDataParts[0]])

  # mimikyu
  if filename == '778-disguised':
    return 'mimikyu'

  # TYPO: 'sprint' instead of 'spring' for deerling
  if filename == '585-sprint':
    return 'deerling_spring'
  if filename == '586-sprint':
    return 'sawsbuck_spring'

  # furfrou
  if filename == '676-natural':
    return 'furfrou'

  # hoopa
  if filename == '720-confined':
    return 'hoopa'

  # eternatus_eternamax
  if filename == '890-gmax':
    return 'eternatus_eternamax'

  # alcremie
  if '869' in filename:
    return 'alcremie'

  # standard galar darmanitan
  if filename == '555-galar':
    return 'darmanitan_standard_galar'

  # zen galar darmanitan
  if filename == '555-galar-zen':
    return 'darmanitan_zen_galar'

  # mr mime galar
  if filename == '122-galar':
    return 'mr_mime_galar'

  # endregion

  # Search possiblePokemon for a matching form, using filenameFormData.
  for pokemonName in possiblePokemon:
    if filenameFormData == '_'.join(pokemonName.split('_')[1:]):
      return pokemonName
    else:
      continue
  
  # In some cases, the filename is just the dexNumber. It will then be of the base form chosen by PokeAPI. We select this base form from possiblePokemon.
  for pokemonName in possiblePokemon:
    for baseFormSuffix in baseFormSuffices():
      if baseFormSuffix in pokemonName:
        return pokemonName

  # By this point, the function should have returned. Otherwise, we failed to match the Pokemon. For debugging purposes, we raise an Exception.
  raise Exception(f'Pokemon not matched: {filename}, {possiblePokemon}.')

# Given the filepath for a Pokemon sprite (broken up into spritePathComponents) and the size of the image, update the entry for that Pokemon in spriteDict.
# size unpacks as width, height, in pixels.
# maps comes from getSpriteMaps (we pass it as an argument rather than calling the function every pass-through).
def handlePokemonSpriteFilepath(spritePathComponents, size, spriteDict, maps):
  # Unpack size
  width, height = size

  # Unpack maps
  dex_pokemon, pokeapiID_pokemonName, unmatchedPokemonName_pokeapiID = maps

  # Parse spritePathComponents for the filename, as well as the generation and version group of the sprite, if given.
  #region
  # Filename is always the last component.
  filename = spritePathComponents[-1].removesuffix('.png')

  # Many sprites are missing from sprites/pokemon/versions/. In this case, they may be in sprites/pokemon/, and in this case we can't determine the versionGroup.
  if 'versions' not in spritePathComponents:
    versionGroup = 'default'

  # If we're in the 'versions' folder, then the filepath is of the form:
  #
  #   pokemon/versions/generation-[gen symbol]/[version group/'icons']/**/*.png
  #
  # If the sprite is an icon, then 'versionGroup' will be 'icons', rather than the name of a version group.
  else: 
    spriteGen = genSymbolToNumber(spritePathComponents[3].split('-')[-1])
    versionGroup = spritePathComponents[4]

    if versionGroup == 'black-white' and filename.isnumeric() and int(filename) > 10000:
      return

  #endregion

  # Extract more information about the sprite: icon or not, front- or back-facing, female or not, shiny or not, transparent or not.
  # If sprite is of a totem Pokemon, return.
  #region

  icon = False
  back = False
  female = False
  shiny = False
  transparent = False

  # Whether sprite is an icon
  if versionGroup == 'icons':
    icon = True

  # If sprite is not an icon, then the sprite may be in several different states, and we can determine this from the presence of certain directories in spritePathComponents.
  else:
    # Whether sprite is back-facing
    if 'back' in spritePathComponents:
      back = True
    
    # Whether sprite is female
    if 'female' in spritePathComponents:
      female = True

    # Whether sprite is shiny
    if 'female' in spritePathComponents:
      shiny = True

    # For gen 1 and 2 sprites, they're not necessarily transparent; onwards, they always are.
    # We need to make sure we're not in the 'default' folder to access spriteGen.
    if 'transparent' in spritePathComponents or (versionGroup != 'default' and spriteGen > 2):
      transparent = True
    
    # If we're in the 'versions' directory (and not in an 'icons' directory), then we can convert versionGroup to a code.
    if versionGroup != 'default':
      versionGroupCodes = versionGroupNameToCodes(versionGroup)

  #endregion
  
  # Get filename parts.
  # region
  # We will use the filename to determine which Pokemon the sprite belongs to.
  filenameParts = filename.split('-')
  idNumber = filenameParts[0]

  # Indicates sprite for 'substitute' or error sprite (assigned to 0).
  if not idNumber.isnumeric() or idNumber == '0':
    return
  
  # Otherwise, the idNumber is the first part of the filename. In many cases, idNumber is the dex number, but otherwise it lines up with PokeAPI.
  else:
    idNumber = int(filenameParts[0])

  # endregion

  # Various exceptions to ignore
  # region
  # Ignore totem Pokemon
  if int(idNumber) in [10195, 10223, 10224, 10239, 10231, 10263, 10264, 10265, 10268, 10309, 10312, 10313] or 'totem' in filename:
    return

  # Ignore greninja-battle-bond, as we have greninja-ash
  if int(idNumber) == 10218 or filename == '658-battle-bond':
    return

  # Ignore beta pichu, burmy, cherrim
  if filename in ['172-beta', '412-beta', '421-beta']:
    return

  # For some reason, PokeAPI puts both Meowstic genders in both the female and non-female folders.
  if filename in ['678-male', '678-female']:
    return

  # Vivillon gen 8 icon. The filename is '666', but it is an image of 
  if filename == '666' and icon and spriteGen == 8:
    return

  # endregion

  # Match filename with Pokemon
  # region

  # If the idNumber is a dex number, then it can be one of several possible Pokemon.
  if idNumber in dex_pokemon.keys():
    possiblePokemon = dex_pokemon[idNumber]

  # Otherwise, it is a PokeAPI ID, corresponding to a single Pokemon.
  else:
    possiblePokemon = [pokeapiID_pokemonName[idNumber]]

  # toxtricity_low_key_gmax and toxtricity_amped_gmax have same sprite
  if filename == '849-gmax':
    pokemonName = 'toxtricity_low_key_gmax'
  else:
    pokemonName = matchPokemon(possiblePokemon, filename, female)

  # endregion


  pokemonName = possiblePokemon[0]
  spriteInfo = {
    "width": width,
    "height": height,
    "icon": icon,
    "back": back,
    "female": female,
    "shiny": shiny,
    "transparent": transparent,
  }
  spriteIndex = len(spriteDict[pokemonName].keys()) - 2

  if not icon and versionGroup != 'default':
    spriteDict[pokemonName][spriteIndex] = [
      (os.sep).join(spritePathComponents),
      spriteInfo,
      versionGroupCodes
    ]

    # exception for toxtricity_amped_gmax since it shares sprite with toxtricity_low_key_gmax
    if pokemonName == 'toxtricity_low_key_gmax':
      spriteDict['toxtricity_amped_gmax'][spriteIndex] = [
        (os.sep).join(spritePathComponents),
        spriteInfo,
        versionGroupCodes
      ]

  elif versionGroup != 'default':
    spriteDict[pokemonName][spriteIndex] = [
      (os.sep).join(spritePathComponents),
      spriteInfo,
      getVersionGroupsInGen(spriteGen)
    ]

  else:
    spriteDict[pokemonName][spriteIndex] = [
      (os.sep).join(spritePathComponents),
      spriteInfo,
      ['SwSh', 'BDSP']
    ]

  return 

# Given the filepath for a Item sprite (broken up into spritePathComponents) and the size of the image, update the entry for that Item in spriteDict.
# size unpacks as width, height, in pixels.
def handleItemSpriteFilepath(spritePathComponents, size, spriteDict):
  width, height = size

  spriteGen = 0

  if 'gen3' in spritePathComponents:
    spriteGen = 3

  elif 'gen5' in spritePathComponents:
    spriteGen = 5

  filename = spritePathComponents[-1].removesuffix('.png')
  if '--bag' in filename:
    return
  elif '--held' in filename:
    filename = filename.replace('--held', '')

  itemName = filename.replace('-', '_')

  if itemName not in spriteDict.keys():
    return
  else: 
    spriteInfo = {
    "width": width,
    "height": height,
    }
    spriteIndex = len(spriteDict[itemName].keys()) - 2

    itemGen = spriteDict[itemName]["gen"]
    versionGroupCodes = []
    if spriteGen == 0 and spriteIndex == 0:
      for gen in range(6, numberOfGens(), 1):
        versionGroupCodes.append(getVersionGroupsInGen(gen))
    else:
      for gen in range(min(itemGen, spriteGen), max(itemGen, spriteGen) + 1, 1):
        versionGroupCodes.append(getVersionGroupsInGen(gen))


    spriteDict[itemName][spriteIndex] = [
      (os.sep).join(spritePathComponents),
      spriteInfo,
      versionGroupCodes
    ]
  
  return

def main():
  # Initialize spriteDict, and call pokemonDict. We get our Pokemon names from pokemonDict (see pokemon.py).
  spriteDict = {}
  pokemonDict = pokemon.main()
  for pokemonName in pokemonDict.keys():
    spriteDict[pokemonName] = {
      "gen": pokemonDict[pokemonName]["gen"],
      "sprite_class": "pokemon"
    }

  itemDict = heldItems.main()
  for itemName in itemDict.keys():
    spriteDict[itemName] = {
      "gen": itemDict[itemName]["gen"],
      "sprite_class": "item"
    }

  # Various maps to help assign filenames to Pokemon.
  maps = getPokemonSpriteMaps(pokemonDict)

  # Path to the src folder
  srcFolder = Path(__file__).parents[2]
  # Path to the 'sprites' directory
  spriteDir = os.path.join(srcFolder, 'data', 'sprites')

  # root_dir needs a trailing slash (i.e. /root/dir/)
  pokemonSpritePaths = set()
  itemSpritePaths = set()

  for filepath in glob.iglob(spriteDir + '/**/*.png', recursive=True):

    # Filepath to the sprite starting from the 'sprites' folder
    relSpritePath = filepath.split('data')[1]

    # List consisting of the name of a directory/image in the filepath
    spritePathComponents = [s for s in relSpritePath.split(os.sep) if len(s) > 0]

    entityType = spritePathComponents[1]

    with Image.open(filepath) as img:
      size = img.size

    if entityType == 'pokemon':
      pokemonSpritePaths.add(relSpritePath)
      handlePokemonSpriteFilepath(spritePathComponents, size, spriteDict, maps)

    elif entityType == 'items':
      itemSpritePaths.add(relSpritePath
      )
      handleItemSpriteFilepath(spritePathComponents, size, spriteDict)

    else:
      raise Exception(f'Invalid entity type: {entityType}, {filepath}.')
  
  return spriteDict

if __name__ == '__main__':
  spriteDict = main() 

  with open(getJSONDataPath() + 'sprites.json', 'w', newline='') as jsonFile:
    output = json.dumps(spriteDict, indent=2)

    # formatting for .json file, essentially to get the lists on one line but still have indentations and line breaks
    # double opening braces
    output = re.sub(r': \[\n\s+\[\n\s+', ': [[', output)
    # put most values on same line--after this step, there's a few edge cases
    output = re.sub(r',\n\s+([A-Za-z0-9\.]+)+', r', \1', output)
    # for inner lists which are on separate lines, put them together on the same line
    output = re.sub(r'\n\s+\],\n\s+\[\n\s+', '], [', output)
    # handle entries of list where successive entries are quotes, with a number in quotes
    output = re.sub(r'",\n\s+"(\d+)', r'", "\1', output)
    # double closing braces
    output = re.sub(r'\n\s+\]\n\s+\]', ']]', output)
    # handle entries of list which have number followed by string
    output = re.sub(r'\[\[[a-zA-Z,\"](\d+),\n\s+"', r'[[\1, "', output)
    # entries of list which have string followed by string, in the first index
    output = re.sub(r'\[\["(.*)",\n\s+"', r'[["\1", "', output)

    jsonFile.write(output)