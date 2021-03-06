import csv
import re

import effects
import elementalTypes as types
import statuses
import usageMethods
from tests import checkGenConsistency, itemTests
from utils import (checkConsistency, fieldStateList, getCSVDataPath,
                   legendsArceusList, parseName, statList)


# initial item dictionary with item name, item type, gen introduced, gen 2 exclusivity, and sprite URL
def makeInitialItemDict(fnamePrefix):
  # item data from Serebii; has some items which Bulbapedia doesn't have
  with open(fnamePrefix + 'Serebii.csv', 'r', encoding='utf-8') as serebiiCSV:
    reader = csv.DictReader(serebiiCSV)

    itemDict = {}
    for row in reader:
      itemName = row["Item Name"]

      if itemName in legendsArceusList() or itemName == 'amulet_coin':
        continue

      # the gen 2 berries will be handled in the berry section
      gen2Exclusive = itemName in ['berserk_gene', 'polkadot_bow', 'pink_bow']

      itemDict[itemName] = {
        "item_class": [],
        # list of Pokemon who can use the item, if restricted
        "pokemon_specific": {},
        "gen": '',
        "gen2_exclusive": gen2Exclusive,
        # indicates whether knock off does extra damage to a Pokemon holding the item; note that Mega Stones can be knocked off of incompatible Pokemon for a damage boost, but we will assume that the Pokemon-specific items are being held by compatible Pokemon
        "knock_off": True,
        "effects": {},
        "causes_status": {},
        "resists_status": {},
        "boosts_type": {},
        "resists_type": {},
        "boosts_usage_method": {},
        "resists_usage_method": {},
        "stat_modifications": {},
      }

  # item classifications from Bulbapedia
  with open(fnamePrefix + 'Class.csv', 'r', encoding='utf-8') as itemTypeCSV:
    reader = csv.DictReader(itemTypeCSV)

    for row in reader:
      itemName, itemClass, itemGen = row["Item Name"], row["Item Class"], row["Item Gen"]

      if itemName in legendsArceusList() or itemName == 'amulet_coin':
        continue

      if itemName not in itemDict:
        itemDict[itemName] = {
          "item_class": [[itemClass, int(itemGen)]],
          "pokemon_specific": {},
          "gen": int(itemGen),
          "gen2_exclusive": False,
          "knock_off": True,
          "effects": {},
          "causes_status": {},
          "resists_status": {},
          "boosts_type": {},
          "resists_type": {},
          "boosts_usage_method": {},
          "resists_usage_method": {},
          "stat_modifications": {},
        }
      else:
        itemDict[itemName]["item_class"].append([itemClass, int(itemGen)])

  # add gen data
  with open(fnamePrefix + 'Gen.csv', 'r', encoding='utf-8') as genCSV:
    reader = csv.DictReader(genCSV)
    for row in reader:
      itemName, gen = row["Item Name"], int(row["Gen"])
      # list on Bulbapedia includes non-held items, so we must ignore those; this is why we read the Serebii file first
      if itemName in itemDict:
        if itemDict[itemName]["gen"] and itemDict[itemName]["gen"] != gen:
          print('Gens of', itemName, 'don\'t match:', itemDict[itemName]["gen"], gen)

        itemDict[itemName]["gen"] = int(gen)
  

  # Classify other items not already listed on Bulbapedia
  for itemName in ['absorb_bulb', 'assault_vest', 'berserk_gene', 'bright_powder', 'cell_battery', 'electric_seed', 'expert_belt', 'life_orb', 'weakness_policy', 'wide_lens', 'misty_seed', 'psychic_seed', 'grassy_seed', 'zoom_lens', 'throat_spray', 'razor_claw', 'scope_lens']:
    itemGen = itemDict[itemName]["gen"]
    itemDict[itemName]["item_class"] = [['stat_enhancer', itemGen]]

  # Classify all remaining items as 'other' 
  for itemName in itemDict.keys():
    if len(itemDict[itemName]["item_class"]) == 0:
      itemGen = itemDict[itemName]["gen"]
      itemDict[itemName]["item_class"] = [['other', itemGen]]

  # Exception for soul dew, which changed from stat enhancer to type enhancer in gen 7
  itemDict["soul_dew"]["item_class"] = [['stat_enhancer', 3], ['type_enhancer', 7]]

  # for some reason, Serebii doesn't have berry juice or adrenaline orb, or some gen 2 berries
  itemDict["berry_juice"] = {
        "item_class": [['other', 2]],
        "pokemon_specific": {},
        "gen": 2,
        "gen2_exclusive": False,
        "knock_off": True,
        "effects": {"restores_hp": [[True, 2]]},
        "causes_status": {},
        "resists_status": {},
        "boosts_usage_method": {},
        "resists_usage_method": {},
        "boosts_type": {},
        "resists_type": {},
        "stat_modifications": {},
      }
  # we handle adrenaline orb stat modifications below
  itemDict["adrenaline_orb"] = {
        "item_class": [['stat_enhancer', 7]],
        "pokemon_specific": {},
        "gen": 7,
        "gen2_exclusive": False,
        "knock_off": True,
        "effects": {},
        "causes_status": {},
        "resists_status": {},
        "boosts_type": {},
        "resists_type": {},
        "boosts_usage_method": {},
        "resists_usage_method": {},
        "stat_modifications": {},
      }

  for itemName in ['psn_cure_berry', 'prz_cure_berry']:
    itemDict[itemName]["gen"] = 2

  # Associate rusted sword/rusted shield with zacian/zamazenta, respectively
  itemDict['rusted_sword']['pokemon_specific'] = {
    'zacian': [[True, 8]]
  }
  itemDict['rusted_shield']['pokemon_specific'] = {
    'zamazenta': [[True, 8]]
  }

  # Handle dragon scale manually
  itemDict['dragon_scale'] = {
    "item_class": [['type_enhancer', 2]],
    "pokemon_specific": {},
    "gen": 2,
    "gen2_exclusive": True,
    "knock_off": True,
    "effects": {},
    "causes_status": {},
    "resists_status": {},
    "boosts_type": {},
    "resists_type": {},
    "boosts_usage_method": {},
    "resists_usage_method": {},
    "stat_modifications": {},

  }

  return itemDict

# add berry data to item dictionary, including nature power data, type resistances, status resistances, and any other effects
def addBerryData(fpath, itemDict):
  # nature power data
  with open(fpath + 'berriesByType.csv', 'r', encoding='utf-8') as naturePowerCSV:
    reader = csv.DictReader(naturePowerCSV)

    for row in reader:
      berryName, type, gen4Power, gen6Power = row["Berry Name"], row["Type"], row["Power in Gen IV-V"], int(row["Power in Gen VI"])
      gen = int(itemDict[berryName]["gen"])

      if berryName in legendsArceusList():
        continue

      if type not in typeDict.keys():
        print(berryName, type)
        continue

      if gen4Power != '':
        itemDict[berryName]["natural_gift"] = [[type, int(gen4Power), gen]]
        # power changed between gens 4 and 6
        if gen6Power != gen4Power:
          itemDict[berryName]["natural_gift"].append([type, int(gen6Power), 6])
      # berry was introduced in gen 6
      else:
        itemDict[berryName]["natural_gift"] = [[type, int(gen6Power), gen]]

  # stat modification data
  with open(fpath + 'berriesModifyStat.csv', 'r', encoding='utf-8') as statModCSV:
    reader = csv.DictReader(statModCSV)

    for row in reader:
      berryName, stat = row["Berry Name"], row["Stat Boosted"]
      gen = itemDict[berryName]["gen"]
      itemDict[berryName]["stat_modifications"][stat] = [['+1', 'user', gen]]

      if stat not in statList():
        print(berryName, stat)
        continue

    # exceptions
    # micle berry
    itemDict["micle_berry"]["stat_modifications"]["accuracy"] = [['+0', 'user', 4], [1.2, 'user', 5]]

    # starf berry
    for stat in statList():
      itemDict["starf_berry"]["stat_modifications"][stat] = [['+2', 'user', 3]]

  # gen 2 berries
  with open(fpath + 'berriesGen2.csv', 'r', encoding='utf-8') as gen2BerriesCSV:
    reader = csv.DictReader(gen2BerriesCSV)

    for row in reader:
      berryName, effect = row["Berry Name"], row["Heals"]
      itemDict[berryName]["gen2_exclusive"] = True


      if berryName == 'mystery_berry':
        itemDict[berryName]["effects"]["restores_pp"] = [[True, 2]]
      elif 'Restores' in effect:
        itemDict[berryName]["effects"]["restores_hp"] = [[True, 2]]
      else:
        if effect not in statusDict.keys() and effect not in effectDict.keys():
          print(berryName, effect)
          continue

        itemDict[berryName]["resists_status"][effect] = [[True, 2]]

  # status healing berries
  with open(fpath + 'berriesStatusHeal.csv', 'r', encoding='utf-8') as statusBerriesCSV:
    reader = csv.DictReader(statusBerriesCSV)

    for row in reader:
      berryName, status = row["Berry Name"], row["Status Healed"]
      gen = itemDict[berryName]["gen"]

      if status != 'any':
        if status not in statusDict.keys():
          print(berryName, status)
          continue

        itemDict[berryName]["resists_status"][status] = [[True, gen]]
      # lum and miracle
      else:
        for anyStatus in ['burn', 'freeze', 'paralysis', 'poison', 'bad_poison', 'sleep', 'confusion']:
          itemDict[berryName]["resists_status"][anyStatus] = [[True, gen]]

  # type resisting berries
  with open(fpath + 'berriesTypeResist.csv', 'r', encoding='utf-8') as typeResistBerriesCSV:
    reader = csv.DictReader(typeResistBerriesCSV)

    for row in reader:
      berryName, type = row["Berry Name"], row["Type Resisted"]
      gen = itemDict[berryName]["gen"]

      if type not in typeDict.keys():
        print(berryName, type)
      
      itemDict[berryName]["resists_type"][type] = [[0.5, gen]]

  # berries which cause confusion if Pokemon doesn't like taste
  for berryName in ['figy_berry', 'wiki_berry', 'mago_berry', 'aguav_berry', 'iapapa_berry']:
    itemDict[berryName]["causes_status"]['confusion'] = [[100.0, 3]]

  return

# add rest of item data
def addOtherItemData(fpath, itemDict):
  # list for debugging purposes
  handledItems = set()

  # mega stones
  with open(fpath + 'megaStones.csv', 'r', encoding='utf-8') as megaStoneCSV:
    reader = csv.DictReader(megaStoneCSV)
    for row in reader:
      itemName, pokemonName, = row["Item Name"], row["Pokemon Name"]
      itemDict[itemName] = {
        "item_class": 'mega_stone',
        # list of Pokemon who can use the item, if restricted
        "pokemon_specific": {
          pokemonName: [[True, 6]]
        },
        "gen": 6,
        "gen2_exclusive": False,
        "knock_off": False,
        "effects": {'changes_form': [[True, 6]]},
        "causes_status": {},
        "resists_status": {},
        "boosts_type": {},
        "resists_type": {},
        "boosts_usage_method": {},
        "resists_usage_method": {},
        "stat_modifications": {},
      }

      handledItems.add(itemName)

  # plates, gems, drives, memories
  with open(fpath + 'typeItems.csv', 'r', encoding='utf-8') as typeItemCSV:
    reader = csv.DictReader(typeItemCSV)
    for row in reader:
      itemType, itemName, type = row["Item Type"], row["Item Name"], row["Elemental Type"]

      if itemName in legendsArceusList():
        continue

      itemGen = itemDict[itemName]["gen"]

      if type not in typeDict.keys():
        print(itemName, type)
        continue

      # move and pokemon type changes
      if itemType in ['drive', 'plate', 'memory']:
        itemDict[itemName]["knock_off"] = False
        effectGen = effectDict["changes_move_type"]["gen"]
        itemDict[itemName]["effects"]["changes_move_type"] = [[True, max(itemGen, effectGen)]]
      if itemType in ['plate', 'memory']:
        effectGen = effectDict["changes_pokemon_type"]["gen"]
        itemDict[itemName]["effects"]["changes_pokemon_type"] = [[True, max(itemGen, effectGen)]]
      
      # type boosters
      if itemType == 'plate':
        itemDict[itemName]["boosts_type"][type] = [[1.2, itemGen]]
      elif itemType == 'gem':
        if type != 'fairy':
          itemDict[itemName]["boosts_type"][type] = [[1.5, itemGen], [1.3, 6]]
        else:
          itemDict[itemName]["boosts_type"][type] = [[1.3, 6]]

      handledItems.add(itemName)

  # type enhancers
  with open(fpath + 'typeEnhancers.csv', 'r', encoding='utf-8') as typeEnhancerCSV:
    reader = csv.DictReader(typeEnhancerCSV)
    for row in reader:
      itemName, itemGen, type = row["Item Name"], int(row["Gen"]), row["Type"]
      if not itemDict[itemName]["gen2_exclusive"]:
        itemDict[itemName]["boosts_type"][type] = [[1.1, itemGen], [1.2, 4]]
      else:
        itemDict[itemName]["boosts_type"][type] = [[1.1, 2]]

      handledItems.add(itemName)

  # pokemon-specific type enhancers
  with open(fpath + 'typeEnhancersSpecific.csv', 'r', encoding='utf-8') as typeEnhancerSpecificCSV:
    reader = csv.DictReader(typeEnhancerSpecificCSV)
    for row in reader:
      itemGen, itemName, pokemonName = int(row["Gen"]), row["Item Name"], row["Pokemon Name"]
      itemDict[itemName]["pokemon_specific"][pokemonName] = [[True, itemGen]]
      # soul dew
      if pokemonName in ['latias', 'latios']:
        # boosted stats in gens 3-6
        for stat in ['special_attack', 'special_defense']:
          itemDict[itemName]["stat_modifications"][stat] = [[1.5, 'user', 3], [1, 'user', 7]]
        # boosted type from gen 7 onward
        for type in ['psychic', 'dragon']:
          itemDict[itemName]["boosts_type"][type] = [[1.2, 7]]
      elif pokemonName == 'dialga':
        for type in ['dragon', 'steel']:
          itemDict[itemName]["boosts_type"][type] = [[1.2, 4]]
      elif pokemonName == 'palkia':
        for type in ['dragon', 'water']:
          itemDict[itemName]["boosts_type"][type] = [[1.2, 4]]
      elif pokemonName == 'giratina_origin':
        for type in ['dragon', 'ghost']:
          itemDict[itemName]["knock_off"] = False
          itemDict[itemName]["boosts_type"][type] = [[1.2, 4]]
      else:
        print(itemName, pokemonName)
        continue
      
      handledItems.add(itemName)

  # stat modifying items
  with open(fpath + 'statEnhancers.csv', 'r', encoding='utf-8') as statEnhancerCSV:
    reader = csv.DictReader(statEnhancerCSV)
    for row in reader:
      itemGen, itemName, pokemonName, stat1, stat2, modifier = int(row["Gen"]), row["Item Name"], row["Pokemon Name"], row["Stat 1"], row["Stat 2"], row["Modifier"]


      if stat2 == '':
        stat2 = stat1

      if '+' not in modifier and '-' not in modifier:
        modifier = float(modifier)

      if stat1 not in statList():
        print(itemName, 'Stat 1', stat1)
        continue
      if stat2 not in statList():
        print(itemName, 'Stat 2', stat2)
        continue
      
      # already handled above
      if itemName == 'soul_dew':
        continue

      if itemName == 'metal_powder':
        itemDict[itemName]["stat_modifications"]["defense"] = [[1.5, 'user', 2], [2.0, 'user', 3]]
        itemDict[itemName]["stat_modifications"]["special_defense"] = [[1.5, 'user', 2], [1.0, 'user', 3]]

        handledItems.add('metal_powder')
        continue

      itemDict[itemName]["stat_modifications"][stat1] = [[modifier, 'user', itemGen]]
      itemDict[itemName]["stat_modifications"][stat2] = [[modifier, 'user', itemGen]]

      if len(pokemonName) > 0: 
        # Add Pokemon specificity data
        pokemonGen = itemGen

        # Exceptions where itemGen doesn't match pokemonGen; 
        if '_galar' in pokemonName or pokemonName == 'sirfetchd':
          pokemonGen = 8
        elif 'pikachu_' in pokemonName:
          if '_cap' in pokemonName:
            pokemonGen = 7
          # cosplay Pikachu
          else:
            pokemonGen = 6
        elif '_alola' in pokemonName:
          pokemonGen = 7
        
        itemDict[itemName]["pokemon_specific"][pokemonName] = [[True, pokemonGen]]

      handledItems.add(itemName)

    # power items halve speed, also iron ball
    for itemName in ['power_weight', 'power_bracer', 'power_belt', 'power_lens', 'power_band', 'power_anklet', 'iron_ball', 'macho_brace']:
      if itemName == 'macho_brace':
        itemGen = 3
      else:
        itemGen = 4

      itemDict[itemName]["stat_modifications"]["speed"] = [[0.5, 'user', itemGen]]
      handledItems.add(itemName)

    # one-stage stat change exceptions
    for exceptions in [
      ['attack', ['snowball', 'cell_battery']],
      ['defense', ['electric_seed', 'grassy_seed']],
      ['special_defense', ['luminous_moss', 'psychic_seed', 'misty_seed']],
      ['special_attack', ['absorb_bulb', 'throat_spray']],
      ['speed', ['room_service', 'adrenaline_orb']],
      ['critical_hit_ratio', ['razor_claw', 'scope_lens']]
    ]:
      stat, items = exceptions
      for itemName in items:
        itemGen = itemDict[itemName]["gen"]
        if itemName == 'room_service':
           itemDict[itemName]["stat_modifications"][stat] = [['-1', 'user', itemGen]]
        else:
          itemDict[itemName]["stat_modifications"][stat] = [['+1', 'user', itemGen]]

        handledItems.add(itemName)

    # two-stage stat change exceptions
    for exceptions in [
      ['attack', ['weakness_policy']],
      ['special_attack', ['weakness_policy']],
      ['speed', ['blunder_policy']],
    ]:
      stat, items = exceptions
      for itemName in items:
        itemGen = itemDict[itemName]["gen"]
        itemDict[itemName]["stat_modifications"][stat] = [['+2', 'user', itemGen]]

        handledItems.add(itemName)

    # other exceptions
    # bright_powder
    itemDict["bright_powder"]["evasion"] = [[1.08, 'user', 2], [1.11, 'user', 3]]
    handledItems.add("bright_powder")

    # wide_lens
    itemDict["wide_lens"]["accuracy"] = [[1.1, 'user', 4]]
    handledItems.add("wide_lens")

    # zoom_lens
    itemDict["zoom_lens"]["accuracy"] = [[1.2, 'user', 4]]
    handledItems.add("zoom_lens")

  # incenses
  with open(fpath + 'incenseList.csv', 'r', encoding='utf-8') as incenseCSV:
    reader = csv.DictReader(incenseCSV)
    for row in reader:
      itemName, description = row["Item Name"], row["Description"]
      itemGen = itemDict[itemName]["gen"]

      # cannot capture effect/effect irrelevant for battling
      if itemName in ['full_incense', 'luck_incense', 'pure_incense']:
        handledItems.add(itemName)
        continue
      # lowers accuracy of moves targetting the holder, which essentially leads to boost in evasion
      elif itemName == 'lax_incense':
        itemDict[itemName]["stat_modifications"]["evasion"] = [[1.05, 'user', 3], [1.11, 'user', 4]]
      # boosts moves of a certain type
      elif itemName != 'sea_incense':
        type = parseName(re.search(r' ([A-Za-z]*)-type', description).group(1))
        itemDict[itemName]["boosts_type"][type] = [[1.2, 4]]
      # stat boost changes from gen 3 to gen 4
      elif itemName == 'sea_incense':
        itemDict[itemName]["boosts_type"]['water'] = [[1.05, 3], [1.2, 4]]
      else:
        print(itemName, description)

      handledItems.add(itemName)
  
  # z-crystals
  with open(fpath + 'zCrystals.csv', 'r', encoding='utf-8') as zCrystalCSV:
    reader = csv.DictReader(zCrystalCSV)
    for row in reader:
      itemName = row["Item Name"]
      itemDict[itemName]["knock_off"] = False

      handledItems.add(itemName)

  # pokemon-specific Z-crystals
  with open(fpath + 'zCrystalsPokemonSpecific.csv', 'r', encoding='utf-8') as zCrystalSpecificCSV:
    reader = csv.DictReader(zCrystalSpecificCSV)
    for row in reader:
      itemName, pokemonName = row["Item Name"], row["Pokemon Name"]
      itemDict[itemName]["pokemon_specific"][pokemonName] = [[True, 7]]

      itemDict[itemName]["knock_off"] = False

      handledItems.add(itemName)

  # miscellaneous exceptions for item effects
  for effect_item in [
    ['punishes_contact', ['sticky_barb', 'rocky_helmet']],
    ['costs_hp', ['black_sludge', 'life_orb']],
    ['restores_hp', ['berry_juice', 'leftovers', 'black_sludge', 'shell_bell']],
    ['switches_out_user', ['eject_button', 'eject_pack']],
    ['switches_out_target', ['red_card']],
    ['removes_type_immunity', ['iron_ball', 'ring_target']],
    ['suppresses_ability', ['utility_umbrella']],
    ['extends_duration', ['grip_claw', 'light_clay', 'terrain_extender', 'damp_rock', 'heat_rock', 'icy_rock', 'smooth_rock']],
    ['other_move_enhancement', ['big_root', 'binding_band', 'expert_belt', 'metronome_item', 'muscle_band', 'wise_glasses']],
    ['affects_weight', ['float_stone']],
    ['moves_last_in_priority', ['lagging_tail', 'full_incense']],
    ['moves_first_in_priority', ['quick_claw', 'custap_berry']],
    ['ignores_contact', ['protective_pads']],
    ['changes_form', ['rusted_sword', 'rusted_shield']],
    ['resets_stats', ['white_herb']],
    ['grounds', ['iron_ball']],
    ['ungrounds', ['air_balloon']],
  ]:
    effect, items = effect_item
    for itemName in items:
      if effect not in effectDict.keys():
        print(itemName, effect)

      effectGen, itemGen = effectDict[effect]["gen"], itemDict[itemName]["gen"]
      itemDict[itemName]["effects"][effect] = [[True, max(effectGen, itemGen)]]

      handledItems.add(itemName)

  # status-causing items
  for status_item in [
    ['burn', ['flame_orb']],
    ['bad_poison', ['toxic_orb']],
    ['confusion', ['berserk_gene']],
    # techically Bulbapedia does not consider the status given by these items 'bracing', but in my opinion it fits
    ['bracing', ['focus_band', 'focus_sash']],
    ['infatuation', ['destiny_knot']],
    ['flinch', ['kings_rock', 'razor_fang']],
    ['trapped', ['shed_shell']],
  ]:
    status, items = status_item
    for itemName in items:
      itemGen = itemDict[itemName]["gen"]
      if itemName == 'focus_band':
        itemDict[itemName]["causes_status"][status] = [[12.0, 2], [10.0, 3]]
      elif itemName == 'kings_rock':
        itemDict[itemName]["causes_status"][status] = [[11.7, 2], [10.0, 3]]
      elif itemName == 'razor_fang':
        itemDict[itemName]["causes_status"][status] = [[10.0, 4]]
      else:
        itemDict[itemName]["causes_status"][status] = [[100.0, itemGen]]

      handledItems.add(itemName)

  # status-resisting items
  for status_item in [
    ['infatuation', ['mental_herb']],
    ['taunt', ['mental_herb']],
    ['encore', ['mental_herb']],
    ['torment', ['mental_herb']],
    ['heal_block', ['mental_herb']],
    ['disable', ['mental_herb']],
    ['telekinesis', ['iron_ball']],
    ['charging_turn', ['power_herb']],
    ['magnetic_levitation', ['power_herb']],
  ]:
    status, items = status_item
    for itemName in items:
      statusGen, itemGen = statusDict[status]["gen"], itemDict[itemName]["gen"]
      if itemName == 'mental_herb' and status != 'infatuation':
        itemDict[itemName]["resists_status"][status] = [[True, 5]]
      else:
        itemDict[itemName]["resists_status"][status] = [[True, max(statusGen, itemGen)]]

      handledItems.add(itemName)
  
  # type-resisting items
  for type_item in [
    ['ground', ['air_balloon']],
  ]:
    type, items = type_item
    for itemName in items:
      typeGen, itemGen = typeDict[type]["gen"], itemDict[itemName]["gen"]
      itemDict[itemName]["resists_type"][type] = [[0.0, max(typeGen, itemGen)]]

      handledItems.add(itemName)

  # items for primal reversion
  for pokemon_item in [
    ['kyogre', 'blue_orb'],
    ['groudon', 'red_orb'],
  ]:
    pokemonName, itemName = pokemon_item
    itemDict[itemName]["pokemon_specific"][pokemonName] = [[True, 6]]

    handledItems.add(itemName)

  # usage-method-resting items
  for usageMethod_item in [
    ['powder', ['safety_goggles']],
  ]:
    usageMethod, items = usageMethod_item
    for itemName in items:
      usageMethodGen, itemGen = usageMethodDict[usageMethod]["gen"], itemDict[itemName]["gen"]
      itemDict[itemName]["resists_usage_method"][usageMethod] = [[0.0, max(usageMethodGen, itemGen)]]

      handledItems.add(itemName)

  # mark items as irrelevant so they don't come up as unhandled
  irrelevantItems = [
    'amulet_coin', 'berry_sweet', 'blue_scarf', 'cleanse_tag', 'clover_sweet', 'dubious_disc', 'flower_sweet', 'green_scarf', 'love_sweet', 'red_scarf', 'pink_scarf', 'ribbon_sweet', 'strawberry_sweet', 'star_sweet', 'yellow_scarf', 'electirizer', 'everstone', 'exp_share', 'lucky_egg', 'magmarizer', 'protector', 'reaper_cloth', 'smoke_ball', 'soothe_bell'
  ]
  for itemName in irrelevantItems:
    handledItems.add(itemName)

  # remove certain items from itemDict
  for itemName in ['golden_nanab_berry', 'golden_pinap_berry', 'golden_razz_berry', 'silver_nanab_berry', 'silver_razz_berry', 'silver_pinap_berry']:
    del itemDict[itemName]
    handledItems.add(itemName)

  # keep track of items to be handled
  for itemName in itemDict.keys():
    # Heavy duty boots is handled in addFieldStateData
    if itemName in ['heavy_duty_boots', 'dragon_scale']:
      continue

    if itemName not in handledItems and 'berry' not in itemDict[itemName]["item_class"][0]:
      print(itemName, 'not handled!')
  return

def addFormattedName(itemDict):
  for itemName in itemDict.keys():
    itemDict[itemName]['formatted_name'] = getFormattedName(itemName)

  return

def getFormattedName(itemName):
  # apostrophes
  if itemName == 'kings_rock':
    return 'King\'s Rock'
  # gen 2 berries
  elif itemName in ['psn_cure_berry', 'prz_cure_berry', 'miracle_berry', 'mystery_berry']:
    return ''.join((' '.join(itemName.split('_')).title().replace('Psn', 'PSN').replace('Prz', 'PRZ')).split(' '))
  else:
    return ' '.join(itemName.split('_')).title()

def addFieldStateData(itemDict):
  for itemName in itemDict.keys():
    itemDict[itemName]["extends_field_state"] = {}
    itemDict[itemName]["resists_field_state"] = {}
    itemDict[itemName]["ignores_field_state"] = {}
  
  # Extenders
  for [itemName, fieldStatesAndGens] in [
    # Screens
    ['light_clay', [
        ['reflect', 1], ['light_screen', 1], ['aurora_veil', 7]
      ]
    ],
    # Harsh sunlight
    ['heat_rock', [
        ['harsh_sunlight', 2]
      ]
    ],
    # Rain
    ['damp_rock', [
        ['rain', 2]
      ]
    ],
    # Sandstorm
    ['smooth_rock', [
        ['sandstorm', 2]
      ]
    ],
    # Hail
    ['icy_rock', [
        ['hail', 3]
      ]
    ],
    # Terrains
    ['terrain_extender', [
        ['electric_terrain', 6], ['grassy_terrain', 6], ['misty_terrain', 6], ['psychic_terrain', 6]
      ]
    ],
  ]:
    itemGen = itemDict[itemName]["gen"]
    for [fieldStateName, fieldStateGen] in fieldStatesAndGens:
      itemDict[itemName]["extends_field_state"][fieldStateName] = [[True, 8, max(itemGen, fieldStateGen)]]

  # Air balloon
  itemDict["air_balloon"]["resists_field_state"]["spikes"] = [[0.0, 5]]
  itemDict["air_balloon"]["ignores_field_state"]["toxic_spikes"] = [[True, 5]]
  itemDict["air_balloon"]["ignores_field_state"]["sticky_web"] = [[True, 6]]
  itemDict["air_balloon"]["ignores_field_state"]["electric_terrain"] = [[True, 6]]
  itemDict["air_balloon"]["ignores_field_state"]["grassy_terrain"] = [[True, 6]]
  itemDict["air_balloon"]["ignores_field_state"]["misty_terrain"] = [[True, 6]]
  itemDict["air_balloon"]["ignores_field_state"]["psychic_terrain"] = [[True, 6]]

  # Safety goggles
  itemDict["safety_goggles"]["resists_field_state"]["hail"] = [[0.0, 6]]
  itemDict["safety_goggles"]["resists_field_state"]["sandstorm"] = [[0.0, 6]]

  # Heavy duty boots
  itemDict["heavy_duty_boots"]["ignores_field_state"]["stealth_rock"] = [[True, 8]]
  itemDict["heavy_duty_boots"]["ignores_field_state"]["spikes"] = [[True, 8]]
  itemDict["heavy_duty_boots"]["ignores_field_state"]["toxic_spikes"] = [[True, 8]]
  itemDict["heavy_duty_boots"]["ignores_field_state"]["sticky_web"] = [[True, 8]]
  itemDict["heavy_duty_boots"]["ignores_field_state"]["sharp_steel"] = [[True, 8]]

  # Utility umbrella
  itemDict["utility_umbrella"]["ignores_field_state"]["rain"] = [[True, 8]]
  itemDict["utility_umbrella"]["ignores_field_state"]["harsh_sunlight"] = [[True, 8]]

  return

def addNatureData(itemDict):
  for itemName in itemDict.keys():
    itemDict[itemName]["confuses_nature"] = {}
  
  for [berryName, natureNames] in [
    ['aguav_berry', ['naughty', 'rash', 'naive', 'lax']],
    ['figy_berry', ['modest', 'timid', 'calm', 'bold']],
    ['iapapa_berry', ['lonely', 'mild', 'gentle', 'hasty']],
    ['mago_berry', ['brave', 'quiet', 'sassy', 'relaxed']],
    ['wiki_berry', ['adamant', 'jolly', 'careful', 'impish']],
  ]: 
    for natureName in natureNames:
      itemDict[berryName]["confuses_nature"][natureName] = [[True, 3]]

  return

def removeUselessItems(itemDict):
  del itemDict["cleanse_tag"]
  del itemDict["everstone"]
  del itemDict["exp_share"]
  del itemDict["green_scarf"]
  del itemDict["luck_incense"]
  del itemDict["lucky_egg"]
  del itemDict["pink_scarf"]
  del itemDict["pure_incense"]
  del itemDict["red_scarf"]
  del itemDict["smoke_ball"]
  del itemDict["soothe_bell"]
  del itemDict["yellow_scarf"]
  del itemDict["electirizer"]
  del itemDict["magmarizer"]
  del itemDict["reaper_cloth"]
  del itemDict["protector"]
  del itemDict["dubious_disc"]
  del itemDict["blue_scarf"]
  
  # delete sweets
  sweets = []
  for itemName in itemDict.keys():
    if itemName.split('_')[-1] == 'sweet' and itemDict[itemName]["gen"] == 8:
      sweets.append(itemName)
  for sweet in sweets:
    del itemDict[sweet]

  return

def checkForMissingDescriptions(items_fname, berries_fname, gen2Berries_fname, itemDict):
  descriptionDict = {}

  with open(items_fname, 'r', encoding='utf-8') as descriptionsCSV:
    reader = csv.DictReader(descriptionsCSV)

    for row in reader:
      itemName = row["Item Name"]
      descriptionDict[itemName] = True

  with open(berries_fname, 'r', encoding='utf-8') as descriptionsCSV:
    reader = csv.DictReader(descriptionsCSV)

    for row in reader:
      itemName = row["Berry Name"]
      descriptionDict[itemName] = True

  with open(gen2Berries_fname, 'r', encoding='utf-8') as descriptionsCSV:
    reader = csv.DictReader(descriptionsCSV)

    for row in reader:
      itemName = row["Gen2Berry Name"]
      descriptionDict[itemName] = True

  for itemName in itemDict.keys():
    if itemName not in descriptionDict.keys():
      print(itemName, 'missing description!')

  for itemName in descriptionDict.keys():
    if itemName not in itemDict.keys():
      # Ignore amulet coin
      if itemName == 'amulet_coin':
        continue
      print(itemName, 'has a description but not in itemDict!')

  return

def main():
  # dictionaries containing effect names/gens and status names/gens
  global effectDict
  effectDict = effects.main()
  global statusDict
  statusDict = statuses.main()
  global typeDict
  typeDict = types.main()
  global usageMethodDict
  usageMethodDict = usageMethods.main()

  dataPath = getCSVDataPath() + 'items/'

  fnamePrefix = dataPath + 'heldItemList'
  itemDict = makeInitialItemDict(fnamePrefix)

  addBerryData(dataPath, itemDict)
  
  addOtherItemData(dataPath, itemDict)

  addFormattedName(itemDict)

  addFieldStateData(itemDict)

  addNatureData(itemDict)

  removeUselessItems(itemDict)

  descriptionDataPath = getCSVDataPath() + 'descriptions/'
  descriptions_fname = descriptionDataPath + 'itemDescriptions.csv'
  berryDescriptions_fname = descriptionDataPath + 'berryDescriptions.csv'
  gen2BerryDescriptions_fname = descriptionDataPath + 'gen2berryDescriptions.csv'
  checkForMissingDescriptions(descriptions_fname, berryDescriptions_fname, gen2BerryDescriptions_fname, itemDict)

  checkGenConsistency(itemDict)
  itemTests(itemDict)

  return itemDict

if __name__ == '__main__':
  itemDict = main()
