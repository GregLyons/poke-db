import re
import types

def getBulbapediaDataPath():
  return 'src\\data\\bulbapedia_data\\'

def getSerebiiDataPath():
  return 'src\\data\\serebii_data\\'

# converts dex number to gen
def dexNumberToGen(dexNumber):
  dexNumber = int(dexNumber)
  if dexNumber <= 151:
    return 1
  elif dexNumber <= 251:
    return 2
  elif dexNumber <= 386:
    return 3
  elif dexNumber <= 493: 
    return 4
  elif dexNumber <= 649:
    return 5
  elif dexNumber <= 721:
    return 6
  elif dexNumber <= 809:
    return 7
  else:
    return 8

# converts roman numeral for gen to arabic numeral
def genSymbolToNumber(roman):
  if roman.upper() == 'I':
    return 1
  elif roman.upper() == 'II':
    return 2
  elif roman.upper() == 'III':
    return 3
  elif roman.upper() == 'IV':
    return 4
  elif roman.upper() == 'V':
    return 5
  elif roman.upper() == 'VI':
    return 6
  elif roman.upper() == 'VII':
    return 7
  elif roman.upper() == 'VIII':
    return 8
  elif roman.upper() == 'IX':
    return 9
  else:
    raise ValueError('Not a valid gen.')

# given a dictionary for a certain entity (move, ability, etc.) with a "gen" key, initialize a nested dictionary, with name outerKeyName, by setting outerKeyName[innerKeyName] = [defaultValue, gen]
# e.g. for any ability status dictionary, entityDict would be abilityDict, outerKeyName would be "causes_status", and innerKeyName would be an individual status
# defaultValue can be a list of default values
def initializeKeyValue(entityDict, outerKeyName, innerKeyName, defaultValue):
  for key in entityDict.keys():
    if not isinstance(defaultValue, list):
      defaultValue = [defaultValue]

    entityDict[key][outerKeyName][innerKeyName] = [defaultValue + [entityDict[key]["gen"]]]
  return


# lists of various mechanics to ensure consistent naming
# stats which can be modified during battle
def statList():
  stats = [
    'attack', 'defense', 'special_attack', 'special_defense', 'speed', 'accuracy', 'evasion', 'critical_hit_ratio'
  ]
  return stats

# weather
def weatherList():
  weathers = [
    'rain', 'hail', 'sandstorm', 'harsh_sunlight', 'extremely_harsh_sunlight', 'heavy_rain', 'strong_winds'
  ]
  return weathers

# terrain
def terrainList():
  terrains = [
    'electric', 'grassy', 'misty', 'psychic', 
  ]
  return terrains

# various effects that don't qualify as statuses
def effectList():
  effects = [
    # hazards, screens, terrains, weathers
    'creates_hazard', 'removes_hazard', 'ignores_hazards',
    'creates_terrain', 'removes_terrain', 
    'creates_screen', 'removes_screen', 
    'creates_weather', 'ignores_weather', 
    # crit
    'high_crit_chance', 'always_crits', 'cannot_crit', 'prevents_crit',
    # protect
    'bypasses_protect',
    # heal status
    'thaws_user', 'heals_nonvolatile', 
    # restore hp or pp
    'restores_hp', 'heals_user_immediately', 'restores_pp', 'drains', 
    # cost hp
    'recoil', 'costs_hp', 'can_crash',
    # ability-related
    'changes_ability', 'ignores_ability', 'suppresses_ability',
    # changes type or damage category mechanics
    'changes_pokemon_type', 'changes_move_type', 'changes_damage_category', 'removes_type_immunity', 'special_type_effectiveness',
    # switchers
    'switches_out_target', 'switches_out_user', 
    # special accuracy properties
    'hits_semi_invulnerable', 'cannot_miss', 'faints_user',
    # different way of calculating power
    'variable_power', 'deals_direct_damage', 'powers_up', 'consecutive', 'counterattack', 
    # weight-related
    'depends_on_weight', 'affects_weight',
    # stat-related
    'resets_stats', 'prevents_stat_drop',
    # priority-related
    'move_last_in_priority', 'move_first_in_priority', 'adds_priority', 'protects_against_priority',
    # contact-related
    'ignores_contact', 'punishes_contact',
    # miscellaneous
    'calls_other_move', 'depends_on_environment', 'multi_hit', 'ohko','changes_form', 'manipulates_items', 'activates_gulp_missile',  'extends_duration', 'other_move_enhancement', 'other_move_resistance',  'anti_mini', 'type_varies', 'other_move_order_change', 'no_effect'
  ]
  return effects

# status effects, non-volatile and volatile (as classified by Bulbapedia)
def statusList():
  statuses = [
    # non-volatile status
    'burn', 'freeze', 'paralysis', 'poison', 'bad_poison', 'sleep', 'confusion', 
    # volatile status
    'curse','embargo', 'encore', 'heal_block', 'nightmare', 'perish_song', 'taunt', 'telekinesis', 'flinch', 'semi_invulnerable_turn', 'bound', 'trapped', 'drowsy', 'identified', 'infatuation', 'leech_seed', 'torment', 'type_change', 'disable',
    # volatile battle status
    'charging_turn', 'protection', 'recharging', 'taking_aim', 'thrashing', 'aqua_ring', 'bracing', 'defense_curl', 'magic_coat', 'mimic', 'minimize', 'substitute', 'center_of_attention', 'rooted', 'magnetic_levitation', 'transformed'
  ]
  return statuses

# usage methods which interact with abilities, e.g. sound, bite
def usageMethodList():
  usageMethods = [
    'pulse', 'ball', 'bite', 'dance', 'explosive', 'mouth', 'powder', 'punch', 'sound',
  ]
  return usageMethods

# elemental types
def typeList():
  types = [
    'normal', 'fighting', 'flying', 'poison', 'ground', 'rock', 'bug', 'ghost', 'steel', '???', 'fire', 'water', 'grass', 'electric', 'psychic', 'ice', 'dragon', 'dark', 'fairy',
  ]
  return types


# parse names in different forms from Bulbapedia and Smogon API to a common, snake_case form
def parseName(text, mode='normal'):
  text = text.strip('\n')
  if mode == 'normal':
    # hyphens to underscores
    text = text.replace('-', '_')

    # remove commas, apostrophes, periods, colons
    text = re.sub(r'[,\'\.:]', '', text)

    # separate lowercase followed by uppercase, e.g. 'ExtremeSpeed' to 'Extreme Speed'--for Bulbapedia typos
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
    
    # replace spaces with underscores and convert to lowercase
    return text.replace(' ', '_').lower().strip('_')

  elif mode == 'pokemon':
    # extract species and form data (latter in parentheses, if present)
    if '(' in text:
      speciesAndForm = [part.strip().strip(')') for part in text.split('(')]
      speciesName = speciesAndForm[0]
      form = speciesAndForm[1].replace('(', '').replace(')', '')

      # remove 'Form' and 'Forme'
      form = re.sub(r'Forme*', '', form)

      # various cases to 
      if speciesName == 'Wormadam':
        form = form.replace('Cloak', '')
      elif speciesName == 'Darmanitan':
        form = form.replace('Mode', '')
        # switch order 'Galarian Standard' to 'Standard Galarian'
        form = re.sub(r'Galarian (Standard|Zen)', r'\1 Galarian', form)
      elif speciesName == 'Urshifu':
        #  preserve 'Rapid Strike' to match with Smogon API
        form = form.replace('Single Strike Style', '')
        form = form.replace('Rapid Strike Style', 'Rapid Strike')
      elif speciesName in ['Zacian', 'Zamazenta']:
        # Bulbapedia adds 'Hero of Many Battles', but Smogon does not
        form = form.replace('Hero of Many Battles', '')
        # Zacian and Zamazenta, remove noun in 'Crowned [noun]'
        form = form.replace('Sword', '')
        form = form.replace('Shield', '')
      elif speciesName in ['Pumpkaboo', 'Gourgeist']:
        form = form.replace('Size', '')
      elif speciesName == 'Indeedee':
        form = form.replace('Female', 'f').replace('Male', 'm')
      elif speciesName == 'Calyrex':
        form = form.replace('Rider', '')
      elif speciesName == 'Nidoran':
        # sometimes Nidoran will have the gender symbol (Bulbapedia)
        form = form.replace('♀', ' Female').replace('Female', 'f')
        form = form.replace('♂', ' Male').replace('Male', 'f')

      # sometimes on Bulbapedia the form has the species name again
      form = form.replace(speciesName, '')

      # change regional names
      form = form.replace('Alolan', 'Alola')
      form = form.replace('Galarian', 'Galar')
    else:
      speciesName = text
      form = ''

    # combine species and form name after parsing
    text = (speciesName + ' ' + form).strip().replace('  ', ' ')

    # hyphens to undescores
    text = text.replace('-', '_')

    # remove commas, apostophes, periods, colons, percent signs
    text = re.sub(r'[,\'\.:\%]', '', text)

    # separate lowercase followed by uppercase, e.g. 'ExtremeSpeed' to 'Extreme Speed'--for Bulbapedia typos
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
    
    # replace spaces with underscores, convert to lowercase, and strip any underscores on the ends (e.g. from Ash-Greninja')
    return text.replace(' ', '_').lower().strip('_')
  else:
    return