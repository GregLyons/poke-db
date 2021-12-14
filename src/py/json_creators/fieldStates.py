from utils import fieldStateList

# dictionary containing usage method names and gen usage method was introduced
# gen is NOT when the earliest move of the corresponding usage method was introduced, but rather when the usage method becomes a mechanic. e.g. mega launcher, the only ability which interacts with pulse moves, was introduced in gen 6, whereas dark pulse, a pulse move, was introduced in gen 4
def makeFieldStateDict():
  fieldStates = [
    # other
    ['mist', 1, 'other', 0, False],
    ['safeguard', 1, 'other', 0, False],
    ['tailwind', 4, 'other', 0, False],
    ['vine_lash', 8, 'other', 16.67, False],
    ['wildfire', 8, 'other', 16.67, False],
    ['cannonade', 8, 'other', 16.67, False],
    ['volcalith', 8, 'other', 16.67, False],
    # screens
    ['reflect', 1, 'screen', 0, False],
    ['light_screen', 1, 'screen', 0, False],
    ['aurora_veil', 7, 'screen', 0, False],
    # pledges
    ['rainbow', 5, 'pledge', 0, False],
    ['sea_of_fire', 5, 'pledge', 12.5, False],
    ['swamp', 5, 'pledge', 0, False],
    # entry hazards
    ['stealth_rock', 4, 'entry_hazard', 12.5, False],
    ['spikes', 2, 'entry_hazard', 12.5, True],
    ['sticky_web', 6, 'entry_hazard', 0, True],
    ['toxic_spikes', 4, 'entry_hazard', 12.5, True],
    ['sharp_steel', 8, 'entry_hazard', 12.5, False],
    # weather
    ['clear_skies', 1, 'weather', 0, False],
    ['harsh_sunlight', 2, 'weather', 0, False],
    ['extremely_harsh_sunlight', 6, 'weather', 0, False],
    ['rain', 2, 'weather', 0, False],
    ['heavy_rain', 6, 'weather', 0, False],
    ['sandstorm', 2, 'weather', 6.25, False],
    ['hail', 3, 'weather', 6.25, False],
    ['fog', 4, 'weather', 0, False],
    ['strong_winds', 6, 'weather', 0, False],
    # terrain
    ['electric_terrain', 6, 'terrain', 0, True],
    ['grassy_terrain', 6, 'terrain', 0, True],
    ['misty_terrain', 6, 'terrain', 0, True],
    ['psychic_terrain', 6, 'terrain', 0, True],
    # rooms
    ['trick_room', 4, 'room', 0, False],
    ['magic_room', 8, 'room', 0, False],
    ['wonder_room', 8, 'room', 0, False],
  ]

  fieldStateDict = {}
  for [fieldStateName, fieldStateGen, fieldStateClass, fieldStateDamage, onlyGrounded] in fieldStates:
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
      "damage_percent": [[fieldStateDamage, fieldStateGen]],
      "max_layers": layerCount,
      "only_grounded": onlyGrounded
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
  fieldStateDict["grassy_terrain"]["effects"]["restores_hp"] = [[True, 6]]
  fieldStateDict["psychic_terrain"]["effects"]["protects_against_priority"] = [[True, 6]]

  # Rooms
  fieldStateDict["magic_room"]["effects"]["manipulates_item"] = [[True, 8]]
  fieldStateDict["trick_room"]["effects"]["other_move_order_change"] = [[True, 4]]

  # Strong winds
  fieldStateDict["strong_winds"]["effects"]["other_move_resistance"] = [[True, 6]]

  return

def addStatusData(fieldStateDict):
  for fieldStateName in fieldStateDict.keys():
    fieldStateDict[fieldStateName]["causes_status"] = {}
    fieldStateDict[fieldStateName]["prevents_status"] = {}

  # Safeguard and Misty Terrain
  for statusName in ['burn', 'freeze', 'paralysis', 'poison', 'bad_poison', 'sleep', 'confusion', 'drowsy']:
    gen = 2
    # Drowsy is introduced in gen 3
    if statusName == 'drowsy':
      gen = 3

    fieldStateDict["safeguard"]["prevents_status"][statusName] = [[True, gen]]
    fieldStateDict["misty_terrain"]["prevents_status"][statusName] = [[True, 6]]

  # Sunlight
  fieldStateDict["harsh_sunlight"]["prevents_status"]["freeze"] = [[True, 2]]
  fieldStateDict["extremely_harsh_sunlight"]["prevents_status"]["freeze"] = [[True, 6]]

  # Entry hazards
  fieldStateDict["toxic_spikes"]["causes_status"]["poison"] = [[100.0, 4]]
  fieldStateDict["toxic_spikes"]["causes_status"]["bad_poison"] = [[100.0, 4]]

  # Electric Terrain
  fieldStateDict["electric_terrain"]["prevents_status"]["sleep"] = [[True, 6]]
  fieldStateDict["electric_terrain"]["prevents_status"]["drowsy"] = [[True, 6]]

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

def addAbilityData(fieldStateDict):
  for fieldStateName in fieldStateDict.keys():
    fieldStateDict[fieldStateName]["activates_ability"] = {}

  for [fieldStateName, abilitiesAndGens] in [
    # Harsh sunlight
    ['harsh_sunlight', [
        ['forecast', 3], ['dry_skin', 4], ['chlorophyll', 3], ['flower_gift', 4], ['leaf_guard', 4], ['solar_power', 4], ['harvest', 5]
      ]
    ],
    # Extremely harsh sunlight
    ['extremely_harsh_sunlight', [
        ['forecast', 3], ['dry_skin', 4], ['chlorophyll', 3], ['flower_gift', 4], ['leaf_guard', 4], ['solar_power', 4], ['harvest', 5]
      ]
    ],
    # Rain
    ['rain', [
        ['forecast', 3], ['dry_skin', 4], ['hydration', 4], ['rain_dish', 3], ['swift_swim', 3]
      ]
    ],
    # Heavy rain
    ['heavy_rain', [
        ['forecast', 3], ['dry_skin', 4], ['hydration', 4], ['rain_dish', 3], ['swift_swim', 3]
      ]
    ],
    # Sand
    ['sandstorm', [
        ['forecast', 3], ['sand_veil', 3], ['sand_rush', 5], ['sand_force', 5]
      ]
    ],
    # Hail
    ['hail', [
        ['ice_body', 4], ['snow_cloak', 4], ['slush_rush', 7], ['ice_face', 8]
      ]
    ],
    # Electric terrain
    ['electric_terrain', [
        ['surge_surfer', 7], ['mimicry', 8]
      ]
    ],
    # Grassy terrain
    ['grassy_terrain', [
        ['grass_pelt', 6], ['mimicry', 8]
      ]
    ],
    # Misty terrain
    ['misty_terrain', [
        ['mimicry', 8]
      ]
    ],
    # Psychic terrain
    ['psychic_terrain', [
        ['mimicry', 8]
      ]
    ],
  ]:
    fieldStateGen = fieldStateDict[fieldStateName]["gen"]
    for [abilityName, abilityGen] in abilitiesAndGens:
      fieldStateDict[fieldStateName]["activates_ability"][abilityName] = [[True, max(abilityGen, fieldStateGen)]]

  return

def addItemData(fieldStateDict):
  for fieldStateName in fieldStateDict.keys():
    fieldStateDict[fieldStateName]["activates_item"] = {}

  for [fieldStateName, itemsAndGens] in [
    # Electric terrain
    ['electric_terrain', [
        ['electric_seed', 7]
      ]
    ],
    # Grassy terrain
    ['grassy_terrain', [
        ['grassy_seed', 7]
      ]
    ],
    # Misty terrain
    ['misty_terrain', [
        ['misty_seed', 7]
      ]
    ],
    # Psychic terrain
    ['psychic_terrain', [
        ['psychic_seed', 7]
      ]
    ],
    # Trick room
    ['trick_room', [
        ['room_service', 8]
      ]
    ],
  ]:
    fieldStateGen = fieldStateDict[fieldStateName]["gen"]
    for [itemName, itemGen] in itemsAndGens:
      fieldStateDict[fieldStateName]["activates_item"][itemName] = [[True, max(itemGen, fieldStateGen)]]

  return

def addMoveData(fieldStateDict):
  for fieldStateName in fieldStateDict.keys():
    fieldStateDict[fieldStateName]["enhances_move"] = {}
    fieldStateDict[fieldStateName]["hinders_move"] = {}

  # Move enhancers
  for [fieldStateName, movesAndGens] in [
    # Harsh sunlight
    ['harsh_sunlight', [
        ['solar_beam', 1], ['solar_blade', 7], ['growth', 1], ['moonlight', 2], ['synthesis', 2], ['morning_sun', 2], ['weather_ball', 3]
      ]
    ],
    # Extremely harsh sunlight
    ['extremely_harsh_sunlight', [
        ['solar_beam', 1], ['solar_blade', 7], ['growth', 1], ['moonlight', 2], ['synthesis', 2], ['morning_sun', 2], ['weather_ball', 3]
      ]
    ],
    # Rain
    ['rain', [
        ['thunder', 1], ['hurricane', 5], ['weather_ball', 3]
      ]
    ],
    # Heavy rain
    ['heavy_rain', [
        ['thunder', 1], ['hurricane', 5], ['weather_ball', 3]
      ]
    ],
    # Sand
    ['sandstorm', [
        ['shore_up', 7], ['weather_ball', 3]
      ]
    ],
    # Hail
    ['hail', [
        ['blizzard', 1], ['weather_ball', 3]
      ]
    ],
    # Electric terrain
    ['electric_terrain', [
        ['rising_voltage', 8], ['terrain_pulse', 8]
      ]
    ],
    # Grassy terrain
    ['grassy_terrain', [
        ['terrain_pulse', 8], ['grassy_glide', 8], ['floral_healing', 7]
      ]
    ],
    # Misty terrain
    ['misty_terrain', [
        ['misty_explosion', 8], ['terrain_pulse', 8]
      ]
    ],
    # Psychic terrain
    ['psychic_terrain', [
        ['expanding_force', 8], ['terrain_pulse', 8]
      ]
    ],
  ]:
    fieldStateGen = fieldStateDict[fieldStateName]["gen"]
    for [moveName, moveGen] in movesAndGens:
      # For exceptions
      otherGen = 0
      if moveName == 'growth' and fieldStateName in ['harsh_sunlight', 'extremely_harsh_sunlight']:
        otherGen = 5
      if moveName == 'blizzard' and fieldStateName in ['hail']:
        otherGen = 4

      fieldStateDict[fieldStateName]["enhances_move"][moveName] = [[True, max(moveGen, fieldStateGen, otherGen)]]

  # Move hindrances
  for [fieldStateName, movesAndGens] in [
    # Harsh sunlight
    ['harsh_sunlight', [
        ['thunder', 1], ['hurricane', 5]
      ]
    ],
    # Extremely harsh sunlight
    ['extremely_harsh_sunlight', [
        ['thunder', 1], ['hurricane', 5]
      ]
    ],
    # Rain
    ['rain', [
        ['solar_beam', 1], ['solar_blade', 7], ['moonlight', 2], ['synthesis', 2], ['morning_sun', 2]
      ]
    ],
    # Heavy rain
    ['heavy_rain', [
        ['solar_beam', 1], ['solar_blade', 7], ['moonlight', 2], ['synthesis', 2], ['morning_sun', 2]
      ]
    ],
    # Sand
    ['sandstorm', [
        ['solar_beam', 1], ['solar_blade', 7], ['shore_up', 7]
      ]
    ],
    # Fog
    ['fog', [
        ['solar_beam', 1], ['moonlight', 2], ['synthesis', 2], ['morning_sun', 2]
      ]
    ],
    # Hail
    ['hail', [
        ['moonlight', 2], ['synthesis', 2], ['morning_sun', 2]
      ]
    ],
    # Grassy terrain
    ['grassy_terrain', [
        ['bulldoze', 5], ['earthquake', 1], ['magnitude', 1]
      ]
    ],
  ]:
    fieldStateGen = fieldStateDict[fieldStateName]["gen"]
    for [moveName, moveGen] in movesAndGens:
      # For exceptions
      otherGen = 0
      if moveName == 'solar_beam' and fieldStateName in ['rain', 'sandstorm']:
        otherGen = 3

      fieldStateDict[fieldStateName]["hinders_move"][moveName] = [[True, max(moveGen, fieldStateGen, otherGen)]]

  return

def main():
  fieldStateDict = makeFieldStateDict()

  addStatModificationData(fieldStateDict)

  addTargetData(fieldStateDict)

  addEffectData(fieldStateDict)

  addStatusData(fieldStateDict)

  addTypeData(fieldStateDict)

  addAbilityData(fieldStateDict)

  addItemData(fieldStateDict)

  addMoveData(fieldStateDict)

  return fieldStateDict

if __name__ == '__main__':
  main()