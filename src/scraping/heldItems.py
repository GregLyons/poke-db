import csv
from utils import openBulbapediaLink, getDataBasePath, parseName, genSymbolToNumber
import re

# TODO colored orbs for Kyogre and Groudon
# exceptions to keep in mind: Soul Dew, Eviolite

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
      type = parseName(re.search(r'effective\s.*-type', description).group().lstrip('effective').rstrip('type').lstrip()).rstrip('_')
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
# Columns of the main berry list .csv are Gen Introduced, Number, Sprite URL, Name, Effect (string)
def berryList(fname, mainWriter):
  fnamePrefix = fname.rstrip('.csv')

  # we will handle berries which restore HP separately
  with open(fname, 'w', newline='', encoding='utf-8') as berryCSV, open(fnamePrefix + 'StatusHeal.csv', 'w', newline='', encoding='utf-8') as statusHealCSV, open(fnamePrefix + 'TypeResist.csv', 'w', newline='', encoding='utf-8') as typeResistCSV, open(fnamePrefix + 'StatBoost.csv', 'w', newline='', encoding='utf-8') as statBoostCSV, open(fnamePrefix + 'Gen2.csv', 'w', newline='', encoding='utf-8') as gen2CSV:
    writer = csv.writer(berryCSV)
    writer.writerow(['Gen', 'Number', 'Sprite URL', 'Berry Name', 'Effect'])

    # write the headers for the other .csv's
    statusWriter = csv.writer(statusHealCSV)
    statusWriter.writerow(['Berry Name', 'Status Healed'])
    typeWriter = csv.writer(typeResistCSV)
    typeWriter.writerow(['Berry Name', 'Type Resisted'])
    statWriter = csv.writer(statBoostCSV)
    statWriter.writerow(['Berry Name', 'Stat Boosted'])
    gen2Writer = csv.writer(gen2CSV)
    gen2Writer.writerow(['Berry Name', 'Heals'])

    bs = openBulbapediaLink('https://bulbapedia.bulbagarden.net/wiki/Berry', 0, 10)
    dataRows = bs.find('span', {'id': 'Generation_III_onwards'}).find_next('table').find_next('table').find_all('tr')[1:]

    
    for row in dataRows:
      # columns are Gen, Number, Sprite, Name, Effects, followed by sprites of the trees
      # gen and number are in <th>'s rather than in <td>'s
      cells = row.find_all(['td', 'th'])

      gen = genSymbolToNumber(cells[0].get_text().rstrip('\n'))
      number = cells[1].get_text().rstrip('\n').replace('—', '').lstrip('0')
      spriteURL = cells[2].find('img')['src']
      berryName = parseName(cells[3].get_text().rstrip('\n'))
      effect = cells[4].get_text().rstrip('\n').replace('—', '')

      # write to the other .csv files according to the effect description
      parseBerryEffect(berryName, effect, statusWriter, typeWriter, statWriter, gen2Writer)
      
      writer.writerow([gen, number, spriteURL, berryName, effect])
      mainWriter.writerow([berryName, 'berry', gen, spriteURL])

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
      mainWriter.writerow([berryName, 'berry', gen, ''])
  return

# Elemental type of Berry for Natural Gift; columns are Name, Type, Power in Gens IV-V, Power in Gen VI
def berryType(fname):
  with open(fname, 'w', newline='', encoding='utf-8') as berryCSV:
    writer = csv.writer(berryCSV)
    
    bs = openBulbapediaLink('https://bulbapedia.bulbagarden.net/wiki/Natural_Gift_(move)', 0, 10)
    # header of table has two rows
    # there's a blank row at the end
    dataRows = bs.find('span', {'id': 'Power'}).find_next('table').find('tr').find_next_sibling('tr').find_next_siblings('tr')[:-1]

    writer.writerow(['Name', 'Type', 'Power IV-V', 'Power VI'])

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
# Columns are Item Type, Sprite URL, Name, Elemental Type
def typeItems(fname, mainWriter):
  with open(fname, 'w', newline='', encoding='utf-8') as berryCSV:
    writer = csv.writer(berryCSV)

    # header
    writer.writerow(['Item Type', 'Sprite URL', 'Name', 'Elemental Type'])

    # memories
    bs = openBulbapediaLink('https://bulbapedia.bulbagarden.net/wiki/Memory', 0, 10)
    dataRows = bs.find('span', {'id': 'List_of_Memories'}).find_next('table').find('tr').find_next_siblings('tr')

    for row in dataRows:
      # columns are sprite, name, type
      cells = row.find_all('td')

      spriteURL = cells[0].find('img')['src']
      name = parseName(cells[1].get_text().rstrip('\n'))
      type = parseName(cells[2].get_text().rstrip('\n'))

      writer.writerow(['memory', spriteURL, name, type])
      mainWriter.writerow([name, 'memory', 7, spriteURL])

    # plates
    bs = openBulbapediaLink('https://bulbapedia.bulbagarden.net/wiki/Plate', 0, 10)
    dataRows = bs.find('span', {'id': 'List_of_Plates'}).find_next('table').find('tr').find_next_siblings('tr')

    for row in dataRows:
      # columns are sprite, name, gen, type
      cells = row.find_all('td')

      spriteURL = cells[0].find('img')['src']
      name = parseName(cells[1].get_text().rstrip('\n'))
      type = parseName(cells[2].get_text().rstrip('\n'))

      writer.writerow(['plate', spriteURL, name, type])

      # plates were introduced in Gen 4 except the Fairy Plate
      if type == 'Fairy':
        gen = 6
      else:
        gen = 4
      mainWriter.writerow([name, 'plate', gen, spriteURL])

    # drives
    bs = openBulbapediaLink('https://bulbapedia.bulbagarden.net/wiki/Drive', 0, 10)
    dataRows = bs.find('span', {'id': 'List_of_Drives'}).find_next('table').find('tr').find_next_siblings('tr')

    for row in dataRows: 
      # columns are sprite, name, type
      cells = row.find_all('td')

      spriteURL = cells[0].find('img')['src']
      name = parseName(cells[1].get_text().rstrip('\n'))
      type = parseName(cells[2].get_text().rstrip('\n'))

      writer.writerow(['drive', spriteURL, name, type])
      mainWriter.writerow([name, 'drive', 5, spriteURL])

    # gems
    bs = openBulbapediaLink('https://bulbapedia.bulbagarden.net/wiki/Gem', 0, 10)
    dataRows = bs.find('span', {'id': 'List_of_Gems'}).find_next('table').find('tr').find_next_siblings('tr')

    for row in dataRows:
      # columns are sprite, name, gen, type 
      cells = row.find_all('td')

      spriteURL = cells[0].find('img')['src']
      name = parseName(cells[1].get_text().rstrip('\n'))
      gen = genSymbolToNumber(cells[2].get_text().rstrip('\n'))
      type = parseName(cells[3].get_text().rstrip('\n'))

      writer.writerow(['gem', spriteURL, name, type])
      mainWriter.writerow([name, 'gem', gen, spriteURL])
  return

# Columns are Gen Introduced, Sprite URL, Name, Effect
def incenseList(fname, mainWriter):
  with open(fname, 'w', newline='', encoding='utf-8') as incenseCSV:
    writer = csv.writer(incenseCSV)

    # header
    writer.writerow(['Gen', 'Sprite URL', 'Name', 'Effect'])

    bs = openBulbapediaLink('https://bulbapedia.bulbagarden.net/wiki/Incense', 0, 10)
    dataRows = bs.find('span', {'id': 'List_of_incenses'}).find_next('table').find('tr').find_next_siblings('tr')

    for row in dataRows:
      # columns are sprite URL, name, gen, effect, other columns
      cells = row.find_all('td')

      spriteURL = cells[0].find('img')['src']
      name = parseName(cells[1].get_text().rstrip('\n'))
      gen = genSymbolToNumber(cells[2].get_text().rstrip('\n'))
      effect = cells[3].get_text().rstrip('\n')

      writer.writerow([gen, spriteURL, name, effect])
      mainWriter.writerow([name, 'incense', gen, spriteURL])
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

# Columns are Gen Introduced, Sprite URL, Name, Associated Pokemon, Effect, Additional Effect, Stat 1, Stat 2, Modifier
def statEnhancers(fname, mainWriter):
  with open(fname, 'w', newline='', encoding='utf-8') as statEnhancerCSV:
    writer = csv.writer(statEnhancerCSV)

    # header
    writer.writerow(['Gen', 'Sprite URL', 'Name', 'Pokemon', 'Effect', 'Additional Effect', 'Stat 1', 'Stat 2', 'Modifier'])

    bs = openBulbapediaLink('https://bulbapedia.bulbagarden.net/wiki/Stat-enhancing_item', 0, 10)
    # there's a blank row at the end
    dataRows = bs.find('span', {'id': 'List_of_stat-enhancing_items'}).find_next('table').find('tr').find_next_siblings('tr')[:-1]

    for row in dataRows:
      # columns are sprite of item, item name, gen, sprite of pokemon, pokemon name, effect
      cells = row.find_all('td')

      spriteURL = cells[0].find('img')['src']
      itemName = parseName(cells[1].get_text().rstrip('\n').rstrip('*'))
      gen = genSymbolToNumber(cells[2].get_text().rstrip('\n'))
      # eviolite row has slightly different structure, so we handle it separately
      if itemName == 'eviolite':
        effect = cells[4].get_text().rstrip('\n')
        additionalEffect =cells[5].get_text().rstrip('\n')
        statsModified, modifier = parseStatEnhancerEffect(effect)
        writer.writerow([5, spriteURL, 'eviolite', '', effect, additionalEffect, stat1, stat2, modifier])
        mainWriter.writerow([itemName, 'stat_enhancer', gen, spriteURL])
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
        
        # write a row for each Pokemon
        writer.writerow([gen, spriteURL, itemName, pokemonName, effect, additionalEffect, stat1, stat2, modifier])
        mainWriter.writerow([itemName, 'stat_enhancer_specific', gen, spriteURL])
  
    # choice items
    for choiceItem in ['Choice Band', 'Choice Specs', 'Choice Scarf']:
      itemName = parseName(choiceItem)

      if choiceItem == 'Choice Band':
        stat1 = 'attack'
        gen = 3
        spriteURL = 'https://cdn2.bulbagarden.net/upload/0/09/Dream_Choice_Band_Sprite.png'
        effect = 'An item to be held by a Pokémon. This curious headband boosts Attack but only allows the use of one move.'
      elif choiceItem == 'Choice Specs':
        stat1 = 'special_attack'
        gen = 4
        spriteURL = 'https://cdn2.bulbagarden.net/upload/6/6a/Dream_Choice_Scarf_Sprite.png'
        effect = 'An item to be held by a Pokémon. This curious scarf boosts Speed but only allows the use of one move.'
      else:
        stat1 = 'speed'
        gen = 4
        spriteURL = 'https://cdn2.bulbagarden.net/upload/e/e6/Dream_Choice_Specs_Sprite.png'
        effect = 'An item to be held by a Pokémon. These curious glasses boost Sp. Atk but only allow the use of one move.'
      
      writer.writerow([gen, spriteURL, itemName, '', effect, '', stat1, '', '1.5'])
      mainWriter.writerow([itemName, 'choice', gen, spriteURL])

    # assault vest
    writer.writerow([6, 'https://cdn2.bulbagarden.net/upload/b/b1/Dream_Assault_Vest_Sprite.png', 'assault_vest', '', 'An item to be held by a Pokémon. This offensive vest raises Sp. Def but prevents the use of status moves.', additionalEffect, 'special_defense', '', '1.5'])
    mainWriter.writerow(['assault_vest', 'stat_enhancer', 6, 'https://cdn2.bulbagarden.net/upload/b/b1/Dream_Assault_Vest_Sprite.png'])
  return

# 2 .csv's: one for general, and one for specific Pokemon
# For general .csv, Columns are Gen Introduced, Sprite URL, Name, Type
# For Pokemon-specific .csv, Columns are Gen Introduced, Sprite URL, Item Name, Pokemon Name (the types are the type of that Pokemon)
def typeEnhancers(fname, mainWriter):
  with open(fname, 'w', newline='', encoding='utf-8') as generalCSV, open(fname.rstrip('.csv') + 'Specific.csv', 'w', newline='', encoding='utf-8') as specificCSV:
    generalWriter = csv.writer(generalCSV)
    specificWriter = csv.writer(specificCSV)

    # general
    generalWriter.writerow(['Gen', 'Sprite URL', 'Item Name', 'Type'])

    bs = openBulbapediaLink('https://bulbapedia.bulbagarden.net/wiki/Type-enhancing_item', 0, 10)
    dataRows = bs.find('span', {'id': 'List_of_type-enhancing_items'}).find_next('table').find_all('tr')[1:]

    for row in dataRows:
      cells = row.find_all('td')
      spriteURL = cells[0].find('img')['src']
      pokemonName = parseName(cells[1].get_text())
      gen = genSymbolToNumber(cells[2].get_text())
      type = parseName(cells[3].get_text())

      generalWriter.writerow([gen, spriteURL, pokemonName, type])
      mainWriter.writerow([pokemonName, 'type_enhancer', gen, spriteURL])

    # Pokemon-specific
    specificWriter.writerow(['Gen', 'Sprite URL', 'Item Name', 'Pokemon Name'])

    dataRows = bs.find('span', {'id': 'Pok.C3.A9mon-specific_type-enhancing_items'}).find_next('table').find_all('tr')[1:]

    for row in dataRows:
      cells = row.find_all('td')
      spriteURL = cells[0].find('img')['src']
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
        specificWriter.writerow([gen, spriteURL, itemName, pokemonName])
      mainWriter.writerow([itemName, 'type_enhancer_specific', gen, spriteURL])  
  return

# 2 .csv's: one for general Z-moves, one for specific Pokemon
# Columns for general are Sprite URL, Name, Z-Move, Type
# Columns for specific are Sprite URL, Name, Pokemon Name, Base Move, Z-Move
def zCrystals(fname, mainWriter):
  with open(fname, 'w', newline='', encoding='utf-8') as generalCSV, open(fname.rstrip('.csv') + 'PokemonSpecific.csv', 'w', newline='', encoding='utf-8') as specificCSV:
    generalWriter, specificWriter = csv.writer(generalCSV), csv.writer(specificCSV)

    bs = openBulbapediaLink('https://bulbapedia.bulbagarden.net/wiki/Z-Crystal', 0, 10)

    # general Z-crystals
    generalWriter.writerow(['Sprite URL', 'Name', 'Z-Move', 'Type'])
    dataRows = bs.find('span', {'id': 'For_each_type'}).find_next('table').find('tr').find_next_siblings('tr')

    for row in dataRows:
      # columns are sprite, name, z-move name, type
      cells = row.find_all('td')

      # sprite column has two sprites, and we want the second one
      spriteURL = cells[0].find_all('img')[-1]['src']
      pokemonName = parseName(cells[1].get_text().rstrip('\n'))
      zMove = parseName(cells[2].get_text().rstrip('\n'))
      type = parseName(cells[3].get_text().rstrip('\n'))

      generalWriter.writerow([spriteURL, pokemonName, zMove, type])
      mainWriter.writerow([pokemonName, 'z_crystal', 7, spriteURL])

    # specific Z-crystals
    specificWriter.writerow(['Sprite URL', 'Item Name', 'Pokemon Name', 'Base Move', 'Z-Move'])
    dataRows = bs.find('span', {'id': 'For_specific_Pokémon'}).find_next('table').find('tr').find_next_siblings('tr')

    for row in dataRows:
      # columns are item sprite, item name, debut games, pokemon sprite (a <th>, so it is not counted), pokemon name, base move, z-move
      cells = row.find_all('td')
      spriteURL = cells[0].find_all('img')[-1]['src']
      itemName = parseName(cells[1].get_text().rstrip('\n'))
      baseMove = parseName(cells[4].get_text().rstrip('\n'))
      zMove = parseName(cells[5].get_text().rstrip('\n'))

      pokemonNames = cells[3].get_text().rstrip('\n').split(' or ')
      for pokemonName in pokemonNames:
        # Some exceptions for Pokemon name
        if pokemonName == 'Alolan Raichu':
          pokemonName == 'Raichu (Alolan)'
        # Form name comes first, 'Necrozma' comes last
        elif 'Necrozma' in pokemonName:
          pokemonName = re.sub(r'(.*)(Necrozma)', r'\2 (\1)', pokemonName)
        
        pokemonName = parseName(pokemonName, 'pokemon')

        specificWriter.writerow([spriteURL, itemName, pokemonName, baseMove, zMove])
        mainWriter.writerow([itemName, 'z_crystal_specific', 7, spriteURL])

# Columns are Sprite URL, Name, Pokemon Name
def megaStones(fname, mainWriter):
  with open(fname, 'w', newline='', encoding='utf-8') as megaStoneCSV:
    writer = csv.writer(megaStoneCSV)

    writer.writerow(['Sprite URL', 'Item Name', 'Pokemon Name'])

    bs = openBulbapediaLink('https://bulbapedia.bulbagarden.net/wiki/Mega_Stone', 0, 10)
    dataRows = bs.find('span', {'id': 'List_of_Mega_Stones'}).find_next('table').find('tr').find_next_siblings('tr')

    for row in dataRows:
      cells = row.find_all('td')
      spriteURL = cells[0].find('img')['src']
      itemName = parseName(cells[1].get_text().rstrip('\n'))
      pokemonName = parseName(cells[4].get_text().rstrip('\n'), 'pokemon')

      writer.writerow([spriteURL, itemName, pokemonName])
      mainWriter.writerow([itemName, 'mega_stone', 6, spriteURL])
  return

# No need for separate .csv, as we don't keep track of the corresponding stat; EVs-gained aren't relevant here
def powerItems(mainWriter):
  bs = openBulbapediaLink('https://bulbapedia.bulbagarden.net/wiki/Power_item', 0, 10)
  dataRows = bs.find('span', {'id': 'Types_of_Power_items'}).find_next('table').find_all('tr')[1:]

  for row in dataRows:
    cells = row.find_all('td')

    spriteURL = cells[0].find('img')['src']
    name = parseName(cells[1].get_text())

    mainWriter.writerow([name, 'power_item', 4, spriteURL])
  return

# We go through the different types of items individually and collect the relevant data in separate .csv's
# At the same time, we compile the basic item info in a main .csv file, whose columns are Name, Type, Gen Introduced, Sprite URL
def main():
  dataPath = getDataBasePath() + 'items\\'
  main_fname = dataPath + 'heldItemList.csv'
  with open(main_fname, 'w', newline='', encoding='utf-8') as mainCSV:
    mainWriter = csv.writer(mainCSV)

    # berries
    # main list of berries
    berry_fname = dataPath + 'berryList.csv'
    berryList(berry_fname, mainWriter)

    # elemental type of berry for Natural Gift
    berry_type_fname = dataPath + 'berriesByType.csv'
    berryType(berry_type_fname)

    # memories, plates, and drives
    type_items_fname = dataPath + 'typeItems.csv'
    typeItems(type_items_fname, mainWriter)

    # incenses
    incense_fname = dataPath + 'incenseList.csv'
    incenseList(incense_fname, mainWriter)

    # stat-enhancing items
    statEnhancers_fname = dataPath + 'statEnhancers.csv'
    statEnhancers(statEnhancers_fname, mainWriter)

    # Z-crystals
    zCrystals_fname = dataPath + 'zCrystals.csv'
    zCrystals(zCrystals_fname, mainWriter)

    # Mega stones
    megaStones_fname = dataPath + 'megaStones.csv'
    megaStones(megaStones_fname, mainWriter)

    # power items
    powerItems(mainWriter)

    typeEnhancers_fname = dataPath + 'typeEnhancers.csv'
    typeEnhancers(typeEnhancers_fname, mainWriter)

  return

if __name__ == '__main__':
  main()