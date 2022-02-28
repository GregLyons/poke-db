import re

def getCSVDataPath():
  return 'src\\data\\raw_data\\csv\\'

def getJSONDataPath():
  return 'src\\data\\raw_data\\json\\'

# Used for a few calculations--need to alter when gen 9 comes
def numberOfGens():
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

# given gen, returns list of version group codes for that gen
def getVersionGroupsInGen(gen):
  if gen in range(numberOfGens() + 1):
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

    return [versionGroup for versionGroup in versionGroupProtoDict.keys() if versionGroupProtoDict[versionGroup][-1] == gen]
  else:
    raise ValueError("Not a valid Gen!")

# lists of various mechanics to ensure consistent naming
# stats which can be modified during battle
def statList():
  stats = [
    'attack', 'defense', 'special_attack', 'special_defense', 'speed', 'accuracy', 'evasion', 'critical_hit_ratio', 'secondary_effect_chance'
  ]
  return stats

# various effects that don't qualify as statuses
def effectList():
  effects = [
    # crit
    'high_crit_chance', 'always_crits', 'cannot_crit', 'prevents_crit',
    # protect
    'bypasses_protect',
    # heal status
    'heals_nonvolatile', 
    # restore hp or pp
    'restores_hp', 'restores_pp', 'drains', 
    # cost hp
    'recoil', 'costs_hp', 'can_crash',
    # ability-related
    'changes_ability', 'ignores_ability', 'suppresses_ability',
    # changes type or damage category mechanics
    'changes_pokemon_type', 'changes_move_type', 'changes_damage_category', 'removes_type_immunity', 'special_type_effectiveness',
    # switchers
    'switches_out_target', 'switches_out_user', 
    # special accuracy properties
    'hits_semi_invulnerable', 'cannot_miss',
    # different way of calculating power
    'variable_power', 'deals_direct_damage', 'powers_up', 'consecutive', 'counterattack', 
    # weight-related
    'depends_on_weight', 'affects_weight',
    # stat-related
    'resets_stats', 'prevents_stat_drop', 'uses_different_stat',
    # priority-related
    'moves_last_in_priority', 'moves_first_in_priority', 'adds_priority', 'protects_against_priority',
    # contact-related
    'ignores_contact', 'punishes_contact',
    # ground-related
    'grounds', 'ungrounds', 'only_affects_grounded',
    # miscellaneous
    'calls_other_move', 'depends_on_environment', 'multi_hit', 'ohko','changes_form', 'manipulates_item', 'activates_gulp_missile',  'extends_duration', 'other_move_enhancement', 'other_move_resistance',  'anti_mini', 'type_varies', 'other_move_order_change', 'no_effect', 'faints_user',
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

# natures
def natureList():
  natures = [
    'hardy', 'lonely', 'brave', 'adamant', 'naughty', 'bold', 'docile', 'relaxed', 'impish', 'lax', 'timid', 'hasty', 'serious', 'jolly', 'naive', 'modest', 'mild', 'quiet', 'bashful', 'rash', 'calm', 'gentle', 'sassy', 'careful', 'quirky'
  ]
  return natures

# usage methods which interact with abilities, e.g. sound, bite
def usageMethodList():
  usageMethods = [
    'pulse', 'ball', 'bite', 'dance', 'explosive', 'powder', 'punch', 'sound',
  ]
  return usageMethods

# 
def fieldStateList():
  fieldStates = [
    'mist', 'safeguard', 'tailwind', 'vine_lash', 'wildfire', 'cannonade', 'volcalith',
    'gravity',
    'reflect', 'light_screen', 'aurora_veil',
    'rainbow', 'sea_of_fire', 'swamp',
    'stealth_rock', 'spikes', 'sticky_web', 'toxic_spikes', 'sharp_steel',
    'clear_skies', 'harsh_sunlight', 'extremely_harsh_sunlight', 'rain', 'heavy_rain', 'sandstorm', 'hail', 'fog', 'strong_winds',
    'electric_terrain', 'grassy_terrain', 'misty_terrain', 'psychic_terrain',
    'trick_room', 'magic_room', 'wonder_room'
  ]
  return fieldStates

# elemental types
def typeList():
  types = [
    'normal', 'fighting', 'flying', 'poison', 'ground', 'rock', 'bug', 'ghost', 'steel', '???', 'fire', 'water', 'grass', 'electric', 'psychic', 'ice', 'dragon', 'dark', 'fairy',
  ]
  return types

def checkConsistency(entityDict, categoryName, categoryDict, defaultValue):
  try:
    inconsistencies = ''
    for categoryKey, patches in entityDict.items():
      if categoryKey not in categoryDict.keys():
        inconsistencies += f'Inconsistent name: {categoryKey}\n'
        
      categoryGen = categoryDict[categoryKey]["gen"]
        
      for patch in patches:
        value, patchGen = patch
        if type(value) != type(defaultValue):
          inconsistencies += f'Value is not the same type as {defaultValue}: {categoryKey}, {value}\n'
        if patchGen < categoryGen:
          inconsistencies += f'Patch gen is smaller than category gen: {categoryKey}\n'
  except KeyError as e: 
    print(e)
    print(f'Bad key name; make sure key is a {categoryName}.')
    return 'Bad key name.\n'

  return inconsistencies

def baseFormSuffices():
  # By putting 'ice' before 'normal', we ensure that the base forms for Arceus and Silvally are the Normal-type forms (note that they appear twice).
  return ['ice', 'normal', 'plant', 'aria', 'baile', 'standard', 'altered', 'land', 'incarnate', 'shield', 'average', 'midday', 'solo', 'm', '50', 'overcast', 'west', 'red_striped', 'spring', 'ordinary', 'full_belly', 'amped', 'a', 'icy_snow', 'red']

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

      # sometimes on Bulbapedia the form has the species name again
      form = form.replace(speciesName, '')

      # change regional names
      form = form.replace('Alolan', 'Alola')
      form = form.replace('Galarian', 'Galar')
    else:
      speciesName = text
      form = ''

    if 'Nidoran' in speciesName:
      # sometimes Nidoran will have the gender symbol (Bulbapedia)
      speciesName = speciesName.replace('♀', ' Female').replace('Female', 'f')
      speciesName = speciesName.replace('♂', ' Male').replace('Male', 'm')
      
    # ignore 'Mane' and 'Wings' in Necrozma
    if 'Necrozma' in speciesName:
      form = form.replace(' Mane', '').replace(' Wings', '')
    
    # combine species and form name after parsing
    text = (speciesName + ' ' + form).strip().replace('  ', ' ')

    # hyphens to undescores
    text = text.replace('-', '_')

    # remove commas, apostophes, periods, colons, percent signs
    text = re.sub(r'[,\'\.:\%]', '', text)

    # separate lowercase followed by uppercase, e.g. 'ExtremeSpeed' to 'Extreme Speed'--for Bulbapedia typos
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
    
    # replace spaces with underscores, convert to lowercase, and strip any underscores on the ends (e.g. from Ash-Greninja')
    return text.replace(' ', '_').lower().strip('_').replace('é', 'e')
  else:
    return

def legendsArceusList():
  return [
    'wyrdeer',
    'kleavor',
    'ursaluna',
    'basculegion',
    'sneasler',
    'overqwil',
    'enamorus',
  ]