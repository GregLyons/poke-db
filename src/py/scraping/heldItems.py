import csv
from utils import openLink, getCSVDataPath, parseName, genSymbolToNumber
import re

# TODO colored orbs for Kyogre and Groudon
# TODO: Soul Dew, Eviolite, berries which restore HP but may confuse, double stab items (e.g. Adamant Orb), Deep Sea items, Wide Lens, Zoom Lens, Ultranecrozium Z, Pikashunium Z, Luck Incense, Air Balloon

# # parse descriptions for the main list to classify item type
# def parseDescription(description):

#   # boost stat sharply--only three such items
#   if 'sharply' in description:
#     return 'boost_stat'

#   # boost stat one stage
#   if re.search(r'boosts (Attack|Defense|Sp. Atk|Sp. Def|Speed)', description):
#     stat = parseName(re.search(r'boosts (Attack|Defense|Sp. Atk|Sp. Def|Speed)', description).group(1))

#     # if stat == 'Sp.Atk': 
#     #   stat = 'special_attack'
#     # elif stat == 'Sp. Def':
#     #   stat = 'special_defense'

#     return 'boost_stat'
#   elif re.search(r'aises (Attack|Defense|Sp. Atk|Sp. Def|Speed)', description):
#     stat = parseName(re.search(r'aises (Attack|Defense|Sp. Atk|Sp. Def|Speed)', description).group(1))
    
#     return 'boost_stat'

#   # incenses
#   if 'incense' in description:
#     return 'incense'

#   # Z-moves
#   if 'It converts' in description:
#     # Exclusive Z-moves, handle in separate function
#     if 'exclusive ' in description:
#       return 'z_crystal_specific'
#     else:
#       type = parseName(re.search(r'upgrade (.*)-type m', description).group(1))
#       return 'z_crystal_' + type
    
#   # plates
#   if 'stone tablet' in description:
#     type = parseName(re.search(r'of (.*)-type', description).group(1))
#     return 'plate_' + type
  
#   # drives
#   if 'cassette' in description:
#     type = parseName(re.search(r'so it becomes (.*) type', description).group(1))
#     return 'drive_' + type

#   # gradual healing from Leftovers, Shell Bell, Black Sludge
#   if re.search(r'(gradually|little|slowly)', description):
#     return 'restore_hp'
  
#   # extenders
#   if 'extends the duration' in description:
#     return 'extender'

#   # gems
#   if 'A gem' in description:
#     type = parseName(re.search(r'power of an* (.*)-type move', description).group(1))
#     return 'gem_' + type

#   # power items
#   if 'reduces Speed but allows' in description:
#     return 'power_item'

#   # toxic and flame orb
#   if 'bizarre orb' in description:
#     return 'status_orb'

#   # contest items
#   if 'contest' in description:
#     return 'contest_item'
  
#   # memories
#   if 'memory disc' in description:
#     type = parseName(re.search(r'contains (.*)-type', description).group(1))
#     return 'memory_' + type

#   # boost type
#   if re.search(r'of (.*)-type', description) or 'spoon' in description:
#     # some descriptions are tricky to handle with a regex
#     if 'spoon' in description:
#       return 'boost_type'
#     elif 'glasses' in description:
#       return 'boost_type'
#     elif 'ice that boosts' in description:
#       return 'boost_type'

#     type = parseName(re.search(r'of (.*)-type m', description).group(1))
    
#     # a few items boost multiple types; we handle those later
#     if 'and' in type:
#       return 'boost_type_specific'
#     else:
#       return 'boost_type'

#   return 'other'

# Columns are Item Name, Item Type, Description, Sprite URL
def mainList(fname):
  with open(fname, 'w', newline='', encoding='utf-8') as mainCSV:
    writer = csv.writer(mainCSV)
    writer.writerow(['Item Name', 'Description', 'Sprite URL'])

    bs = openLink('https://www.serebii.net/itemdex/list/holditem.shtml', 0, 10)
    dataRows = bs.find('table', {'class': 'dextable'}).find('tr').find_next_siblings('tr')

    # does not include berries
    for row in dataRows:
      cells = row.find_all('td')

      # The Gen 2 exclusive Berserk Gene doesn't have a sprite--in this case, there is one less cell, and we go to else clause
      if cells[0].find('img') != None:
        spriteURL = cells[0].find('img')['src']
        # append '_item' to metronome to avoid confusion with the move
        itemName = parseName(cells[2].get_text()).replace('metronome', 'metronome_item') 
        description = cells[3].get_text()
      else:
        spriteURL = ''
        itemName = parseName(cells[1].get_text())
        description = cells[2].get_text()

      writer.writerow([itemName, description, spriteURL])

    # add in berries; their effects are handled separately
    bs = openLink('https://www.serebii.net/itemdex/list/berry.shtml', 0, 10)
    dataRows = bs.find('table', {'class': 'dextable'}).find('tr').find_next_siblings('tr')

    for row in dataRows:
      cells = row.find_all('td')

      spriteURL = cells[0].find('img')['src']
      itemName = parseName(cells[2].get_text())
      description = cells[3].get_text()

      writer.writerow([itemName, 'berry', description, spriteURL])

    # add in Gen 2 berries; their effects are handled separately
    bs = openLink('https://www.serebii.net/itemdex/list/gsberry.shtml', 0, 10)
    dataRows = bs.find('table', {'class': 'dextable'}).find('tr').find_next_siblings('tr')

    for row in dataRows:
      cells = row.find_all('td')

      itemName = parseName(cells[1].get_text())
      description = cells[2].get_text()

      # no sprites of Gen 2 items
      writer.writerow([itemName, 'berry', description, ''])

  return

# Columns are Item Name, Gen
def itemGenList(fname):
  with open(fname, 'w', newline='', encoding='utf-8') as itemGenCSV:
    writer = csv.writer(itemGenCSV)
    writer.writerow(['Item Name', 'Gen'])

    bs = openLink('https://bulbapedia.bulbagarden.net/wiki/List_of_items_by_name', 0, 10)

    # items are organized into tables by first letter
    for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
      dataRows = bs.find(id=letter).find_next('table').find_all('tr')[1:-1]

      for row in dataRows:
        cells = row.find_all('td')
        # append '_item' to metronome to avoid confusion with the move
        itemName = parseName(cells[1].get_text()).replace('metronome', 'metronome_item') 
        # print(itemName)

        # 'Good Rod', only in Gens 1-4, so the gen format is written differently
        if itemName == 'good_rod':
          writer.writerow([itemName, 1])
          continue
        # TYPO: bulbapedia says it's gen 2, but should be gen 3
        elif itemName == 'macho_brace':
          writer.writerow([itemName, 3])
          continue
        # TYPO: bulbapedia says it's gen 3, but should be gen 2
        elif itemName in ['scope_lens', 'smoke_ball']:
          writer.writerow([itemName, 2])
          continue
        # Bulbapedia also lists the Chilan Berry Pokeblock ingredient as a separate item, introduced in Gen 3.
        elif itemName == 'chilan_berry':
          writer.writerow([itemName, 4])
          continue

        gen = genSymbolToNumber(cells[2].get_text())
        writer.writerow([itemName, gen])

  return

def itemClassList(fname): 
  with open(fname, 'w', newline='', encoding='utf-8') as itemClassCSV:
    writer = csv.writer(itemClassCSV)
    writer.writerow(['Item Name', 'Item Class', 'Item Gen'])


    # Berries
    # Gen 2 berries
    bs = openLink('https://bulbapedia.bulbagarden.net/wiki/Berry', 0, 10)
    dataRows = bs.find(id='Generation_II').find_next('table').find_all('tr')[1:]

    for row in dataRows:
      cells = row.find_all(['td', 'th'])
      berryName = parseName(cells[0].get_text())

      writer.writerow([berryName, 'berry', 2])

    # Later berries
    # Sometimes there's a useless 'table' between the header and the actual table of interest. 
    dataRows = bs.find(id='Generation_III_onwards').find_next('p').find_next('table').find_all('tr')[1:]

    for row in dataRows:
      cells = row.find_all(['td', 'th'])
      berryGen, berryName = genSymbolToNumber(cells[0].get_text().rstrip('\n')), parseName(cells[3].get_text())

      writer.writerow([berryName, 'berry', berryGen])
    

    # Drives
    writer.writerow(['shock_drive', 'drive', 5])
    writer.writerow(['burn_drive', 'drive', 5])
    writer.writerow(['chill_drive', 'drive', 5])
    writer.writerow(['douse_drive', 'drive', 5])


    # Power items
    writer.writerow(['power_anklet', 'power', 4])
    writer.writerow(['power_band', 'power', 4])
    writer.writerow(['power_belt', 'power', 4])
    writer.writerow(['power_bracer', 'power', 4])
    writer.writerow(['power_lens', 'power', 4])
    writer.writerow(['power_weight', 'power', 4])


    # Choice items
    writer.writerow(['choice_band', 'choice', 3])
    writer.writerow(['choice_specs', 'choice', 4])
    writer.writerow(['choice_scarf', 'choice', 4])


    # Gems
    bs = openLink('https://bulbapedia.bulbagarden.net/wiki/Gem', 0, 10)
    dataRows = bs.find(id='List_of_Gems').find_next('table').find_all('tr')[1:]

    for row in dataRows:
      cells = row.find_all(['td', 'tr'])
      itemName, itemGen = parseName(cells[1].get_text()), genSymbolToNumber(cells[2].get_text().rstrip('\n'))

      writer.writerow([itemName, 'gem', itemGen])

    
    # Incense
    bs = openLink('https://bulbapedia.bulbagarden.net/wiki/Incense', 0, 10)
    dataRows = bs.find(id='List_of_incenses').find_next('table').find_all('tr')[1:]

    for row in dataRows:
      cells = row.find_all(['td', 'tr'])
      itemName, itemGen = parseName(cells[1].get_text()), genSymbolToNumber(cells[2].get_text().rstrip('\n'))

      writer.writerow([itemName, 'incense', itemGen])


    # Mega stones
    bs = openLink('https://bulbapedia.bulbagarden.net/wiki/Mega_Stone', 0, 10)
    dataRows = bs.find(id='List_of_Mega_Stones').find_next('table').find_all('tr')[1:]

    for row in dataRows:
      cells = row.find_all(['td', 'tr'])
      itemName = parseName(cells[1].get_text())

      writer.writerow([itemName, 'mega_stone', 6])


    # Memories
    bs = openLink('https://bulbapedia.bulbagarden.net/wiki/Memory', 0, 10)
    dataRows = bs.find(id='List_of_Memories').find_next('table').find_all('tr')[1:]

    for row in dataRows:
      cells = row.find_all(['td', 'tr'])
      itemName = parseName(cells[1].get_text())

      writer.writerow([itemName, 'memory', 7])


    # Plates
    bs = openLink('https://bulbapedia.bulbagarden.net/wiki/Plate', 0, 10)
    dataRows = bs.find(id='List_of_Plates').find_next('table').find_all('tr')[1:]

    for row in dataRows:
      cells = row.find_all(['td', 'tr'])
      itemName, itemGen = parseName(cells[1].get_text()), genSymbolToNumber(cells[2].get_text().rstrip('\n'))

      writer.writerow([itemName, 'plate', itemGen])

    
    # Stat enhancers
    bs = openLink('https://bulbapedia.bulbagarden.net/wiki/Stat-enhancing_item', 0, 10)
    dataRows = bs.find(id='List_of_stat-enhancing_items').find_next('table').find_all('tr')[1:-1]

    for row in dataRows:
      cells = row.find_all(['td', 'tr'])
      itemName, itemGen = parseName(cells[1].get_text().rstrip('\n*')), genSymbolToNumber(cells[2].get_text().rstrip('\n'))

      writer.writerow([itemName, 'stat_enhancer', itemGen])
    

    # Type enhancers
    bs = openLink('https://bulbapedia.bulbagarden.net/wiki/Type-enhancing_item', 0, 10)
    dataRows = bs.find(id='List_of_type-enhancing_items').find_next('table').find_all('tr')[1:]

    for row in dataRows:
      cells = row.find_all(['td', 'tr'])
      itemName, itemGen = parseName(cells[1].get_text().rstrip('\n*')), genSymbolToNumber(cells[2].get_text().rstrip('\n'))

      writer.writerow([itemName, 'type_enhancer', itemGen])
    
    # Pokemon specific
    dataRows = bs.find(id='Pokémon-specific_type-enhancing_items').find_next('table').find_all('tr')[1:]

    for row in dataRows:
      cells = row.find_all(['td', 'tr'])
      itemName, itemGen = parseName(cells[1].get_text().rstrip('\n*')), genSymbolToNumber(cells[2].get_text().rstrip('\n'))

      # Remove extra text after Soul Dew
      if 'soul_dew' in itemName:
        itemName = 'soul_dew'

      writer.writerow([itemName, 'type_enhancer', itemGen])

    # Z-crystals
    bs = openLink('https://bulbapedia.bulbagarden.net/wiki/Z-Crystal', 0, 10)
    dataRows = bs.find(id='For_each_type').find_next('table').find_all('tr')[1:]

    for row in dataRows:
      cells = row.find_all(['td', 'tr'])
      itemName, itemGen = parseName(cells[1].get_text().rstrip('\n*')), 7

      writer.writerow([itemName, 'z_crystal', itemGen])

    dataRows = bs.find(id='For_specific_Pokémon').find_next('table').find_all('tr')[1:]

    for row in dataRows:
      cells = row.find_all(['td', 'tr'])
      itemName, itemGen = parseName(cells[1].get_text().rstrip('\n*')), 7

      writer.writerow([itemName, 'z_crystal', itemGen])

  return

# Parses effect description for berries
def parseBerryEffect(berryName, description, statusWriter, typeWriter, statWriter, gen2Writer, gen2 = False):
  if 'Cures' in description:
    # the Gen 2 berries also cure status, so we have to check for that
    status = parseName(description.replace('Cures ', ''))
    if berryName not in ['lum_berry', 'miracle_berry']:
      if gen2:
        gen2Writer.writerow([berryName, status])
      else:
        statusWriter.writerow([berryName, status])
    elif gen2:
      statusWriter.writerow([berryName, 'any'])
    else:
      statusWriter.writerow([berryName, 'any'])
  elif 'Halves' in description:
    if berryName != 'chilan_berry':
      # for some reason, stripping '-type' removes an ending letter on some of the types, e.g. 'Fairy-type' -> 'fair', so we do it this weird way instead
      type = parseName(re.search(r'effective\s.*-type', description).group().lstrip('effective').removesuffix('type').lstrip()).rstrip('_')
      typeWriter.writerow([berryName, type])
    else:
      typeWriter.writerow([berryName, 'normal'])
  elif 'Raises' in description:
    if berryName not in ['starf_berry', 'micle_berry']:
      stat = parseName(re.search(r'\s.*\swhen', description).group().rstrip('when').strip())
      statWriter.writerow([berryName, stat])
    elif berryName == 'starf_berry':
      statWriter.writerow([berryName, 'random'])
    else:
      statWriter.writerow([berryName, 'accuracy'])
  else:
    return 'Not handled'

# Writes several .csv files for the different berry properties
# Columns of the main berry list .csv are Gen Introduced, Number, Name, Effect (string)
def berryList(fname):
  fnamePrefix = fname.removesuffix('.csv')

  # we will handle berries which restore HP separately
  with open(fname, 'w', newline='', encoding='utf-8') as berryCSV, open(fnamePrefix + 'StatusHeal.csv', 'w', newline='', encoding='utf-8') as statusHealCSV, open(fnamePrefix + 'TypeResist.csv', 'w', newline='', encoding='utf-8') as typeResistCSV, open(fnamePrefix + 'ModifyStat.csv', 'w', newline='', encoding='utf-8') as statBoostCSV, open(fnamePrefix + 'Gen2.csv', 'w', newline='', encoding='utf-8') as gen2CSV:
    writer = csv.writer(berryCSV)
    writer.writerow(['Gen', 'Number', 'Berry Name', 'Description'])

    # write the headers for the other .csv's
    statusWriter = csv.writer(statusHealCSV)
    statusWriter.writerow(['Berry Name', 'Status Healed'])
    typeWriter = csv.writer(typeResistCSV)
    typeWriter.writerow(['Berry Name', 'Type Resisted'])
    statWriter = csv.writer(statBoostCSV)
    statWriter.writerow(['Berry Name', 'Stat Boosted'])
    gen2Writer = csv.writer(gen2CSV)
    gen2Writer.writerow(['Berry Name', 'Heals'])

    bs = openLink('https://bulbapedia.bulbagarden.net/wiki/Berry', 0, 10)
    dataRows = bs.find('span', {'id': 'Generation_III_onwards'}).find_next('table').find_next('table').find_all('tr')[1:]

    
    for row in dataRows:
      # columns are Gen, Number, Sprite, Name, Effects, followed by sprites of the trees
      # gen and number are in <th>'s rather than in <td>'s
      cells = row.find_all(['td', 'th'])

      gen = genSymbolToNumber(cells[0].get_text().rstrip('\n'))
      number = cells[1].get_text().rstrip('\n').replace('—', '').lstrip('0')
      
      berryName = parseName(cells[3].get_text().rstrip('\n'))
      effect = cells[4].get_text().rstrip('\n').replace('—', '')

      # write to the other .csv files according to the effect description
      parseBerryEffect(berryName, effect, statusWriter, typeWriter, statWriter, gen2Writer)
      
      writer.writerow([gen, number, berryName, effect])
      

    # finally, handle the Gen 2 berries, which are in another table

    dataRows = bs.find(id='Generation_II').find_next('table').find_all('tr')[1:]
    for row in dataRows:
      cells = row.find_all('td')
      # need to do some additional processing on the berry names since some don't have spaces
      berryName = cells[0].get_text().rstrip('\n')

      # shorter names do have spaces, or they're just 'Berry'
      if ' ' in berryName or berryName == 'Berry':
        berryName = parseName(berryName)
      # if the berry name is 12 letters long, then there are no spaces due to limitations on the Gameboy
      elif 'PSN' in berryName or 'PRZ' in berryName:
        berryName = parseName(berryName[:3] + ' ' + berryName[3:7] + ' ' + berryName[7:])
      else:
        berryName = parseName(berryName[:7] + ' ' + berryName[7:])

      effect = cells[1].get_text().rstrip('\n')
      parsedEffect = parseBerryEffect(berryName, effect, statusWriter, typeWriter, statWriter, gen2Writer, True)
      if parsedEffect == 'Not handled':
        gen2Writer.writerow([berryName, effect])

      # there are no sprites for the Gen 2 berries
      
  return

# Elemental type of Berry for Natural Gift; columns are Name, Type, Power in Gen IV-V, Power in Gen VI
def berryType(fname):
  with open(fname, 'w', newline='', encoding='utf-8') as berryCSV:
    writer = csv.writer(berryCSV)
    
    bs = openLink('https://bulbapedia.bulbagarden.net/wiki/Natural_Gift_(move)', 0, 10)
    # header of table has two rows
    # there's a blank row at the end
    dataRows = bs.find('span', {'id': 'Power'}).find_next('table').find('tr').find_next_sibling('tr').find_next_siblings('tr')[:-1]

    writer.writerow(['Berry Name', 'Type', 'Power in Gen IV-V', 'Power in Gen VI'])

    for row in dataRows:
      # there is a number and a sprite column before the berry name; the number is a <th>
      cells = row.find_all('td')[1:]
      name = parseName(cells[0].get_text().rstrip('\n'))
      type = parseName(cells[1].get_text().rstrip('\n'))
      power45 = cells[2].get_text().rstrip('\n').replace('—', '')
      power6 = cells[3].get_text().rstrip('\n')

      writer.writerow([name, type, power45, power6])
  return

# Memories for Silvally, Plates for Arceus, Drives for Genesect, and Gems
# Columns are Item Type, Item Name, Elemental Type
def typeItems(fname):
  with open(fname, 'w', newline='', encoding='utf-8') as berryCSV:
    writer = csv.writer(berryCSV)

    # header
    writer.writerow(['Item Type', 'Item Name', 'Elemental Type'])

    # memories
    bs = openLink('https://bulbapedia.bulbagarden.net/wiki/Memory', 0, 10)
    dataRows = bs.find('span', {'id': 'List_of_Memories'}).find_next('table').find('tr').find_next_siblings('tr')

    for row in dataRows:
      # columns are sprite, name, type
      cells = row.find_all('td')

      
      name = parseName(cells[1].get_text().rstrip('\n'))
      type = parseName(cells[2].get_text().rstrip('\n'))

      writer.writerow(['memory', name, type])
      

    # plates
    bs = openLink('https://bulbapedia.bulbagarden.net/wiki/Plate', 0, 10)
    dataRows = bs.find('span', {'id': 'List_of_Plates'}).find_next('table').find('tr').find_next_siblings('tr')

    for row in dataRows:
      # columns are sprite, name, gen, type
      cells = row.find_all('td')

      
      name = parseName(cells[1].get_text().rstrip('\n'))
      type = parseName(cells[3].get_text().rstrip('\n'))

      writer.writerow(['plate', name, type])

      # plates were introduced in Gen 4 except the Fairy Plate
      if type == 'Fairy':
        gen = 6
      else:
        gen = 4
      

    # drives
    bs = openLink('https://bulbapedia.bulbagarden.net/wiki/Drive', 0, 10)
    dataRows = bs.find('span', {'id': 'List_of_Drives'}).find_next('table').find('tr').find_next_siblings('tr')

    for row in dataRows: 
      # columns are sprite, name, type
      cells = row.find_all('td')

      
      name = parseName(cells[1].get_text().rstrip('\n'))
      type = parseName(cells[2].get_text().rstrip('\n'))

      writer.writerow(['drive', name, type])
      

    # gems
    bs = openLink('https://bulbapedia.bulbagarden.net/wiki/Gem', 0, 10)
    dataRows = bs.find('span', {'id': 'List_of_Gems'}).find_next('table').find('tr').find_next_siblings('tr')

    for row in dataRows:
      # columns are sprite, name, gen, type 
      cells = row.find_all('td')

      
      name = parseName(cells[1].get_text().rstrip('\n'))
      gen = genSymbolToNumber(cells[2].get_text().rstrip('\n'))
      type = parseName(cells[3].get_text().rstrip('\n'))

      writer.writerow(['gem', name, type])
      
  return

# Columns are Gen Introduced, Name, Effect
def incenseList(fname):
  with open(fname, 'w', newline='', encoding='utf-8') as incenseCSV:
    writer = csv.writer(incenseCSV)

    # header
    writer.writerow(['Gen', 'Item Name', 'Description'])

    bs = openLink('https://bulbapedia.bulbagarden.net/wiki/Incense', 0, 10)
    dataRows = bs.find('span', {'id': 'List_of_incenses'}).find_next('table').find('tr').find_next_siblings('tr')

    for row in dataRows:
      # columns are sprite URL, name, gen, effect, other columns
      cells = row.find_all('td')

      
      name = parseName(cells[1].get_text().rstrip('\n'))
      gen = genSymbolToNumber(cells[2].get_text().rstrip('\n'))
      effect = cells[3].get_text().rstrip('\n')

      writer.writerow([gen, name, effect])
      
  return

# Parses the description to determine which stats the item increases and by how much
def parseStatEnhancerEffect(description):
  if 'Doubles' in description:
    modifier = '2.0'
  elif '50%' in description:
    modifier = '1.5'
  elif 'two stages' in description:
    modifier = '+2'
  else:
    return '1.0'

  stats = ['attack', 'defense', 'special attack', 'special defense', 'speed', 'critical hit ratio']
  statsModified = []
  for stat in stats:
    if stat in description.lower():
      statsModified.append(parseName(stat))

  return statsModified, modifier

# Columns are Gen Introduced, Name, Pokemon Name (if Pokemon specific), Description, Additional Description, Stat 1, Stat 2, Modifier
def statEnhancers(fname):
  with open(fname, 'w', newline='', encoding='utf-8') as statEnhancerCSV:
    writer = csv.writer(statEnhancerCSV)

    # header
    writer.writerow(['Gen', 'Item Name', 'Pokemon Name', 'Description', 'Additional Description', 'Stat 1', 'Stat 2', 'Modifier'])

    bs = openLink('https://bulbapedia.bulbagarden.net/wiki/Stat-enhancing_item', 0, 10)
    # there's a blank row at the end
    dataRows = bs.find('span', {'id': 'List_of_stat-enhancing_items'}).find_next('table').find('tr').find_next_siblings('tr')[:-1]

    for row in dataRows:
      # columns are sprite of item, item name, gen, sprite of pokemon, pokemon name, effect
      cells = row.find_all('td')

      
      itemName = parseName(cells[1].get_text().rstrip('\n').rstrip('*'))
      gen = genSymbolToNumber(cells[2].get_text().rstrip('\n'))
      # eviolite row has slightly different structure, so we handle it separately
      if itemName == 'eviolite':
        effect = cells[4].get_text().rstrip('\n')
        additionalEffect =cells[5].get_text().rstrip('\n')
        statsModified, modifier = parseStatEnhancerEffect(effect)
        writer.writerow([5, 'eviolite', '', effect, additionalEffect, stat1, stat2, modifier])
        
        continue
      else:
        # a single <td> may have multiple Pokemon; e.g. all forms and evolutions of Farfetch'd can use the Leek, and all three are listed in the <td>; we need to split them up
        pokemonNameString = cells[4].get_text().rstrip('\n')

        # the separate names are glued together since in the HTML they are separated by a <br>, e.g. 'LatiasLatios'; we split them apart by three spaces
        pokemonNameString = re.sub(r'([a-z])([A-Z])', r'\1_\2', pokemonNameString)
        pokemonNames = pokemonNameString.split('_')

        # the regional forms have two spaces in the middle for some reason
        pokemonNames = [name.replace('  ', ' ') for name in pokemonNames]

      effect = cells[5].get_text().rstrip('\n')
      additionalEffect = cells[6].get_text().rstrip('\n')

      # parse effect to determine stat modifier
      statsModified, modifier = parseStatEnhancerEffect(effect)
      if len(statsModified) == 2:
        stat1, stat2 = statsModified[0], statsModified[1]
      else:
        stat1, stat2 = statsModified[0], ''

      for pokemonName in pokemonNames:
        # exception
        if pokemonName == 'Pikachu in a cap':
          pokemonName = 'in-a-cap Pikachu'

        # in this table, form names come first, e.g. 'Alolan Marowak'--to parse them, we need to switch the order
        pokemonName = re.sub(r'(.+)\s(.+)', r'\2 (\1)', pokemonName)
        pokemonName = parseName(pokemonName, 'pokemon')

        # handle pikachu forms
        if pokemonName == 'pikachu_cosplay':
          for suffix in ['_rock_star', '_belle', '_pop_star', '_phd', '_libre']:
            writer.writerow([gen, itemName, 'pikachu' + suffix, effect, additionalEffect, stat1, stat2, modifier])
          continue
        elif pokemonName == 'pikachu_in_a_cap':
          for suffix in ['_original', '_kalos', '_alola', '_hoenn', '_sinnoh', '_unova', '_partner', '_world']:
            writer.writerow([gen, itemName, 'pikachu'+ suffix + '_cap', effect, additionalEffect, stat1, stat2, modifier])
          continue
        
        # write a row for each Pokemon
        writer.writerow([gen, itemName, pokemonName, effect, additionalEffect, stat1, stat2, modifier])
        
  
    # choice items
    for choiceItem in ['Choice Band', 'Choice Specs', 'Choice Scarf']:
      itemName = parseName(choiceItem)

      if choiceItem == 'Choice Band':
        stat1 = 'attack'
        gen = 3
        
        effect = 'An item to be held by a Pokémon. This curious headband boosts Attack but only allows the use of one move.'
      elif choiceItem == 'Choice Specs':
        stat1 = 'special_attack'
        gen = 4
        
        effect = 'An item to be held by a Pokémon. This curious scarf boosts Speed but only allows the use of one move.'
      else:
        stat1 = 'speed'
        gen = 4
        
        effect = 'An item to be held by a Pokémon. These curious glasses boost Sp. Atk but only allow the use of one move.'
      
      writer.writerow([gen, itemName, '', effect, '', stat1, '', '1.5'])
      

    # assault vest
    writer.writerow([6, 'assault_vest', '', 'An item to be held by a Pokémon. This offensive vest raises Sp. Def but prevents the use of status moves.', additionalEffect, 'special_defense', '', '1.5'])
    
  return

# 2 .csv's: one for general, and one for specific Pokemon
# For general .csv, Columns are Gen Introduced, Name, Type
# For Pokemon-specific .csv, Columns are Gen Introduced, Item Name, Pokemon Name (the types are the type of that Pokemon)
def typeEnhancers(fname):
  with open(fname, 'w', newline='', encoding='utf-8') as generalCSV, open(fname.removesuffix('.csv') + 'Specific.csv', 'w', newline='', encoding='utf-8') as specificCSV:
    generalWriter = csv.writer(generalCSV)
    specificWriter = csv.writer(specificCSV)

    # general
    generalWriter.writerow(['Gen', 'Item Name', 'Type'])

    bs = openLink('https://bulbapedia.bulbagarden.net/wiki/Type-enhancing_item', 0, 10)
    dataRows = bs.find('span', {'id': 'List_of_type-enhancing_items'}).find_next('table').find_all('tr')[1:]

    for row in dataRows:
      cells = row.find_all('td')
      
      pokemonName = parseName(cells[1].get_text())
      gen = genSymbolToNumber(cells[2].get_text())
      type = parseName(cells[3].get_text())

      generalWriter.writerow([gen, pokemonName, type])
      

    # Pokemon-specific
    specificWriter.writerow(['Gen', 'Item Name', 'Pokemon Name'])

    dataRows = bs.find('span', {'id': 'Pok.C3.A9mon-specific_type-enhancing_items'}).find_next('table').find_all('tr')[1:]

    for row in dataRows:
      cells = row.find_all('td')
      
      itemName = parseName(cells[1].get_text())
      if 'soul_dew' in itemName:
        itemName = 'soul_dew'

      gen = genSymbolToNumber(cells[2].get_text())

      # a <td> may have multiple Pokemon--we handle the two exceptions here
      pokemonNamesString = cells[4].get_text().rstrip('\n')
      if pokemonNamesString == 'LatiasLatios':
        pokemonNames = ['Latias', 'Latios']
      elif pokemonNamesString == 'GiratinaOrigin Forme':
        pokemonNames = ['Giratina (Origin Forme)']
      else:
        pokemonNames = [pokemonNamesString]

      for pokemonName in pokemonNames:
        specificWriter.writerow([gen, itemName, parseName(pokemonName, 'pokemon')])
      
  return

# 2 .csv's: one for general Z-moves, one for specific Pokemon
# Columns for general are Name, Z-Move, Type
# Columns for specific are Name, Pokemon Name, Base Move, Z-Move
def zCrystals(fname):
  with open(fname, 'w', newline='', encoding='utf-8') as generalCSV, open(fname.removesuffix('.csv') + 'PokemonSpecific.csv', 'w', newline='', encoding='utf-8') as specificCSV:
    generalWriter, specificWriter = csv.writer(generalCSV), csv.writer(specificCSV)

    bs = openLink('https://bulbapedia.bulbagarden.net/wiki/Z-Crystal', 0, 10)

    # general Z-crystals
    generalWriter.writerow(['Item Name', 'Z-Move', 'Type'])
    dataRows = bs.find('span', {'id': 'For_each_type'}).find_next('table').find('tr').find_next_siblings('tr')

    for row in dataRows:
      # columns are sprite, name, z-move name, type
      cells = row.find_all('td')

      # sprite column has two sprites, and we want the second one
      
      pokemonName = parseName(cells[1].get_text().rstrip('\n'))
      zMove = parseName(cells[2].get_text().rstrip('\n'))
      type = parseName(cells[3].get_text().rstrip('\n'))

      generalWriter.writerow([pokemonName, zMove, type])
      

    # specific Z-crystals
    specificWriter.writerow(['Item Name', 'Pokemon Name', 'Base Move', 'Z-Move'])
    dataRows = bs.find('span', {'id': 'For_specific_Pokémon'}).find_next('table').find('tr').find_next_siblings('tr')

    for row in dataRows:
      # columns are item sprite, item name, debut games, pokemon sprite (a <th>, so it is not counted), pokemon name, base move, z-move
      cells = row.find_all('td')
      
      itemName = parseName(cells[1].get_text().rstrip('\n'))
      baseMove = parseName(cells[4].get_text().rstrip('\n'))
      zMove = parseName(cells[5].get_text().rstrip('\n'))

      pokemonNames = cells[3].get_text().rstrip('\n').split(' or ')
      for pokemonName in pokemonNames:
        # Form name comes first, 'Necrozma' comes last
        if 'Necrozma' in pokemonName:
          pokemonName = re.sub(r'(.*)(Necrozma)', r'\2 (\1)', pokemonName)
        
        pokemonName = parseName(pokemonName, 'pokemon')

        if pokemonName == 'alolan_raichu':
          pokemonName = 'raichu_alola'
        elif pokemonName == 'pikachu_normal':
          pokemonName = 'pikachu'
        
        # pikachu_in_a_cap
        if pokemonName == 'pikachu_in_a_cap':
          for suffix in ['_original', '_kalos', '_alola', '_hoenn', '_sinnoh', '_unova', '_partner', '_world']:
            specificWriter.writerow([itemName, 'pikachu' + suffix + '_cap', baseMove, zMove])
          continue

        # lycanroc forms
        if pokemonName == 'lycanroc':
          for suffix in ['_midday', '_dusk', '_midnight']:
            specificWriter.writerow([itemName, 'lycanroc' + suffix, baseMove, zMove])
          continue


        # hard to parse string in such a way so as to handle the Tapus and Necrozma at the same time.
        if pokemonName == 'tapu_koko_tapu_lele_tapu_bulu':
          for tapu in ['tapu_koko', 'tapu_lele', 'tapu_bulu']:
            specificWriter.writerow([itemName, tapu, baseMove, zMove])
        else:
          specificWriter.writerow([itemName, pokemonName, baseMove, zMove])
        
# Columns are Name, Pokemon Name
def megaStones(fname):
  with open(fname, 'w', newline='', encoding='utf-8') as megaStoneCSV:
    writer = csv.writer(megaStoneCSV)

    writer.writerow(['Item Name', 'Pokemon Name', 'Sprite URL', 'Description'])

    bs = openLink('https://bulbapedia.bulbagarden.net/wiki/Mega_Stone', 0, 10)
    dataRows = bs.find('span', {'id': 'List_of_Mega_Stones'}).find_next('table').find('tr').find_next_siblings('tr')

    for row in dataRows:
      cells = row.find_all('td')
      
      spriteURL = cells[0].find('img')['src']
      itemName = parseName(cells[1].get_text().rstrip('\n'))
      pokemonName = parseName(cells[4].get_text().rstrip('\n'), 'pokemon')
      description = 'Mega stone for ' + cells[4].get_text().rstrip('\n') + '.'

      writer.writerow([itemName, pokemonName, spriteURL, description])
      
  return

# We go through the different types of items individually and collect the relevant data in separate .csv's
# At the same time, we compile the basic item info in a main .csv file, whose columns are Item Name, Item Type, Gen, 
def main():
  dataPath = getCSVDataPath() + 'items\\'

  # main list
  # Serebii has a more comprehensive list of held items than I could find on Bulbapedia
  main_fname = dataPath + 'heldItemListSerebii.csv'
  mainList(main_fname)

  # Serebii doesn't list the Gen that the item was introduced--the only place I could find was Bulbapedia, which lists ALL items, not just held items
  itemGen_fname = dataPath + 'heldItemListGen.csv'
  itemGenList(itemGen_fname)

  # Bulbapedia has a list of most of the held items by class. We list these classifications here.
  itemClass_fname = dataPath + 'heldItemListClass.csv'
  itemClassList(itemClass_fname)

  # berries
  # main list of berries
  berry_fname = dataPath + 'berries.csv'
  berryList(berry_fname)

  # elemental type of berry for Natural Gift
  berry_type_fname = dataPath + 'berriesByType.csv'
  berryType(berry_type_fname)

  # memories, plates, and drives
  type_items_fname = dataPath + 'typeItems.csv'
  typeItems(type_items_fname)

  # incenses
  incense_fname = dataPath + 'incenseList.csv'
  incenseList(incense_fname)

  # stat-enhancing items
  statEnhancers_fname = dataPath + 'statEnhancers.csv'
  statEnhancers(statEnhancers_fname)

  # Z-crystals
  zCrystals_fname = dataPath + 'zCrystals.csv'
  zCrystals(zCrystals_fname)

  # Mega stones
  megaStones_fname = dataPath + 'megaStones.csv'
  megaStones(megaStones_fname)

  # type enhancers
  typeEnhancers_fname = dataPath + 'typeEnhancers.csv'
  typeEnhancers(typeEnhancers_fname)

  return

if __name__ == '__main__':
  main()