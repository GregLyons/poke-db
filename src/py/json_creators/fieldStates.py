from utils import fieldStateList

# dictionary containing usage method names and gen usage method was introduced
# gen is NOT when the earliest move of the corresponding usage method was introduced, but rather when the usage method becomes a mechanic. e.g. mega launcher, the only ability which interacts with pulse moves, was introduced in gen 6, whereas dark pulse, a pulse move, was introduced in gen 4
def makeFieldStateDict():
  fieldStates = [
    # other
    ['mist', 1, 'other', 0],
    ['safeguard', 1, 'other', 0],
    ['tailwind', 4, 'other', 0],
    ['vine_lash', 8, 'other', 16.67],
    ['wildfire', 8, 'other', 16.67],
    ['cannonade', 8, 'other', 16.67],
    ['volcalith', 8, 'other', 16.67],
    # screens
    ['reflect', 1, 'screen', 0],
    ['light_screen', 1, 'screen', 0],
    ['aurora_veil', 7, 'screen', 0],
    # pledges
    ['rainbow', 5, 'pledge', 0],
    ['sea_of_fire', 5, 'pledge', 12.5],
    ['swamp', 5, 'pledge', 0],
    # entry hazards
    ['stealth_rock', 4, 'entry_hazard', 12.5],
    ['spikes', 2, 'entry_hazard', 12.5],
    ['sticky_web', 6, 'entry_hazard'],
    ['toxic_spikes', 4, 'entry_hazard', 12.5],
    ['sharp_steel', 8, 'entry_hazard'],
    # weather
    ['clear_skies', 1, 'weather', 0],
    ['harsh_sunlight', 2, 'weather', 0],
    ['extremely_harsh_sunlight', 6, 'weather', 0],
    ['rain', 2, 'weather', 0],
    ['heavy_rain', 6, 'weather', 0],
    ['sandstorm', 2, 'weather', 6.25],
    ['hail', 3, 'weather', 6.25],
    ['fog', 4, 'weather', 0],
    ['strong_winds', 6, 'weather', 0],
    # terrain
    ['electric_terrain', 6, 'terrain', 0],
    ['grassy_terrain', 6, 'terrain', 0],
    ['misty_terrain', 6, 'terrain', 0],
    ['psychic_terrain', 6, 'terrain', 0],
    # rooms
    ['trick_room', 4, 'room', 0],
    ['magic_room', 8, 'room', 0],
    ['wonder_room', 8, 'room', 0],
  ]

  fieldStateDict = {}
  for [fieldStateName, fieldStateGen, fieldStateClass, fieldStateDamage] in fieldStates:
    layerCount = 1
    if fieldStateName in ['spikes']:
      layerCount = 3
    elif fieldStateName in ['toxic_spikes']:
      layerCount = 2

    formattedFieldStateName = getFormattedName(fieldStateName)
    fieldStateDict[fieldStateName] = {
      "gen": fieldStateGen,
      "formatted_name": formattedFieldStateName,
      "field_state_class": fieldStateClass,
      "damage_percent_over_time": fieldStateDamage,
      "max_layers": layerCount
    }

  # make sure all usage methodsare accounted for
  for fieldStateName in fieldStateList():
    if fieldStateName not in fieldStateDict:
      print(fieldStateName, 'not in fieldStateDict')

  # make sure no typos
  for fieldStateName in fieldStateDict.keys():
    if fieldStateName not in fieldStateList():
      print(fieldStateName, 'not in fieldStateList')

  return fieldStateDict

def getFormattedName(fieldStateName):
  # replace underscores with spaces
  formattedName = fieldStateName.replace('_', ' ')
  
  # make first letter uppercase
  formattedName = formattedName[0].upper() + formattedName[1:]

  return formattedName

def addStatModificationData(fieldStateDict):
  for fieldStateName in fieldStateDict.keys():
    fieldStateDict[fieldStateName]["stat_modifications"] = {}

  # "attack": [[1.5, "user", 100.0, 4]]

  # Screens; after Gen 3, they don't affect stats
  fieldStateDict["reflect"]["stat_modifications"]["defense"] = [[2.0, "all_allies", 100.0, 1], [1.0, "all_allies", 100.0, 3]]
  fieldStateDict["light_screen"]["stat_modifications"]["special_defense"] = [[2.0, "all_allies", 100.0, 1], [1.0, "all_allies", 100.0, 3]]

  # Other
  fieldStateDict["tailwind"]["stat_modifications"]["speed"] = [[2.0, "all_allies", 100.0, 4]]

  # Pledges
  fieldStateDict["rainbow"]["stat_modifications"]["secondary_effect_chance"] = [[2.0, "all_allies", 100.0, 5]]
  fieldStateDict["swamp"]["stat_modifications"]["speed"] = [[2.0, "all_foes", 100.0, 5]]

  # Entry hazards
  fieldStateDict["sticky_web"]["stat_modifications"]["speed"] = [["-1", "all_foes", 100.0, 6]]

  # Weather
  fieldStateDict["fog"]["stat_modifications"]["accuracy"] = [[0.6, "all", 100.0, 4]]
  fieldStateDict["sandstorm"]["stat_modifications"]["special_defense"] = [[1.5, "all_allies", 100.0, 4]]

  return

def addTargetData(fieldStateDict):
  for fieldStateName in fieldStateDict.keys():
    fieldStateGen = fieldStateDict[fieldStateName]["gen"]
    fieldStateClass = fieldStateDict[fieldStateName]["field_state_class"]

    # Based on field state class
    if fieldStateClass in ['weather', 'room', 'terran']:
      targetClass = [['all', fieldStateGen]]
    elif fieldStateClass in ['entry_hazard']:
      targetClass = [['all_foes', fieldStateGen]]
    elif fieldStateClass in ['screen']:
      targetClass = [['all_allies', fieldStateGen]]

    # Specific
    elif fieldStateName in ['tailwind', 'mist', 'safeguard', 'rainbow']:
      targetClass = [['all_allies', fieldStateGen]]
    elif fieldStateName in ['vine_lash', 'wildfire', 'cannonade', 'volcalith', 'sea_of_fire', 'swamp']:
      targetClass = [['all_foes', fieldStateGen]]
    
    fieldStateDict[fieldStateName]["target"] = targetClass

  return

def addEffectData(fieldStateDict):
  for fieldStateName in fieldStateDict.keys():
    fieldStateDict[fieldStateName]["effects"] = {}

  # Other
  fieldStateDict["mist"]["effects"]["prevents_stat_drop"] = [[True, 1]]

  # Terrains
  fieldStateDict["psychic_terrain"]["effects"]["protects_against_priority"] = [[True, 6]]

  # Rooms
  fieldStateDict["magic_room"]["effects"]["manipulates_item"] = [[True, 8]]
  fieldStateDict["trick_room"]["effects"]["other_move_order_change"] = [[True, 4]]

  return

def addStatusData(fieldStateDict):
  for fieldStateName in fieldStateDict.keys():
    fieldStateDict[fieldStateName]["causes_status"] = {}
    fieldStateDict[fieldStateName]["resists_status"] = {}

  # Safeguard and Misty Terrain
  for statusName in ['burn', 'freeze', 'paralysis', 'poison', 'bad_poison', 'sleep', 'confusion', 'drowsy']:
    gen = 2
    # Drowsy is introduced in gen 3
    if statusName == 'drowsy':
      gen = 3

    fieldStateDict["safeguard"]["resists_status"][statusName] = [[True, gen]]
    fieldStateDict["misty_terrain"]["resists_status"][statusName] = [[True, 6]]

  # Entry hazards
  fieldStateDict["toxic_spikes"]["causes_status"]["poison"] = [[100.0, 4]]
  fieldStateDict["toxic_spikes"]["causes_status"]["bad_poison"] = [[100.0, 4]]

  # Electric Terrain
  fieldStateDict["electric_terrain"]["resists_status"]["sleep"] = [[True, 6]]
  fieldStateDict["electric_terrain"]["resists_status"]["drowsy"] = [[True, 6]]

  return

def addTypeData(fieldStateDict):
  # Weather ball
  for fieldStateName in fieldStateDict.keys():
    if fieldStateDict[fieldStateName]["field_state_class"] != 'weather':
      continue
    
    weatherGen = fieldStateDict[fieldStateName]["gen"]
    if fieldStateName in ['clear_skies', 'strong_winds', 'fog']:
      weatherBallType = 'normal'
    elif fieldStateName in ['harsh_sunlight', 'extremely_harsh_sunlight']:
      weatherBallType = 'fire'
    elif fieldStateName in ['rain', 'heavy_rain']:
      weatherBallType = 'water'
    elif fieldStateName in ['hail']:
      weatherBallType = 'ice'
    elif fieldStateName in ['sandstorm']:
      weatherBallType = 'rock'
    else:
      raise Exception(f'{fieldStateName} not handled!')

    fieldStateDict[fieldStateName]["weather_ball"] = [[weatherBallType, weatherGen]]

  # Type boosting/resisting
  #region
  for fieldStateName in fieldStateDict.keys():
    fieldStateDict[fieldStateName]["boosts_type"] = {}
    fieldStateDict[fieldStateName]["resists_type"] = {}

  # Weather
  fieldStateDict["rain"]["boosts_type"]["water"] = [[1.5, 2]]
  fieldStateDict["rain"]["resists_type"]["fire"] = [[0.5, 2]]
  fieldStateDict["heavy_rain"]["boosts_type"]["water"] = [[1.5, 6]]
  fieldStateDict["heavy_rain"]["resists_type"]["fire"] = [[0.0, 6]]

  fieldStateDict["harsh_sunlight"]["boosts_type"]["fire"] = [[1.5, 2]]
  fieldStateDict["harsh_sunlight"]["resists_type"]["water"] = [[0.5, 2]]
  fieldStateDict["extremely_harsh_sunlight"]["boosts_type"]["fire"] = [[1.5, 6]]
  fieldStateDict["extremely_harsh_sunlight"]["resists_type"]["water"] = [[0.0, 6]]

  # Terrains
  fieldStateDict["electric_terrain"]["boosts_type"]["electric"] = [[1.5, 6], [1.3, 8]]
  fieldStateDict["grassy_terrain"]["boosts_type"]["grass"] = [[1.5, 6], [1.3, 8]]
  fieldStateDict["misty_terrain"]["resists_type"]["dragon"] = [[0.5, 6]]
  fieldStateDict["psychic_terrain"]["boosts_type"]["psychic"] = [[1.5, 6], [1.3, 8]]

  #endregion

  return

def main():
  fieldStateDict = makeFieldStateDict()

  addStatModificationData(fieldStateDict)

  addTargetData(fieldStateDict)

  addEffectData(fieldStateDict)

  addStatusData(fieldStateDict)

  addTypeData(fieldStateDict)

  return fieldStateDict

if __name__ == '__main__':
  main()