import csv
from utils import openBulbapediaLink, getDataPath, parseName, genSymbolToNumber
import re

# Columns are Gen Introduced, Number, Sprite URL, Name, Effect (string)
def berryList(fname, mainWriter):
  with open(fname, 'w', newline='', encoding='utf-8') as berryCSV:
    writer = csv.writer(berryCSV)
    
    bs = openBulbapediaLink('https://bulbapedia.bulbagarden.net/wiki/Berry', 0, 10)
    dataRows = bs.find('span', {'id': 'Generation_III_onwards'}).find_next('table').find_next('table').find('tr').find_next_siblings('tr')

    writer.writerow(['Gen', 'Number', 'Sprite URL', 'Name', 'Effect'])
    
    for row in dataRows:
      # columns are Gen, Number, Sprite, Name, Effects, followed by sprites of the trees
      # gen and number are in <th>'s rather than in <td>'s
      cells = row.find_all(['td', 'th'])

      gen = genSymbolToNumber(cells[0].get_text().rstrip('\n'))
      number = cells[1].get_text().rstrip('\n').replace('—', '').lstrip('0')
      spriteURL = cells[2].find('img')['src']
      name = parseName(cells[3].get_text().rstrip('\n'))
      effect = cells[4].get_text().rstrip('\n').replace('—', '')
      
      writer.writerow([gen, number, spriteURL, name, effect])
      mainWriter.writerow([name, 'berry', gen, spriteURL])
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
      effect = cells[3].get_text()

      writer.writerow([gen, spriteURL, name, effect])
      mainWriter.writerow([name, 'incense', gen, spriteURL])
  return

# Columns are Gen Introduced, Sprite URL, Name, Associated Pokemon, Effect, Additional Effect
def statEnhancers(fname, mainWriter):
  with open(fname, 'w', newline='', encoding='utf-8') as statEnhancerCSV:
    writer = csv.writer(statEnhancerCSV)

    # header
    writer.writerow(['Gen', 'Sprite URL', 'Name', 'Pokemon', 'Effect', 'Additional Effect'])

    bs = openBulbapediaLink('https://bulbapedia.bulbagarden.net/wiki/Stat-enhancing_item', 0, 10)
    # there's a blank row at the end
    dataRows = bs.find('span', {'id': 'List_of_stat-enhancing_items'}).find_next('table').find('tr').find_next_siblings('tr')[:-1]

    for row in dataRows:
      # columns are sprite of item, item name, gen, sprite of pokemon, pokemon name, effect
      cells = row.find_all('td')

      spriteURL = cells[0].find('img')['src']
      itemName = parseName(cells[1].get_text().rstrip('\n').rstrip('*'))
      gen = genSymbolToNumber(cells[2].get_text().rstrip('\n'))
      # eviolite row has slightly different structure
      if itemName == 'eviolite':
        # don't add Eviolite to the stat enhancer list, as it doesn't apply to one specific Pokemon
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

      for pokemonName in pokemonNames:
        # exception
        if pokemonName == 'Pikachu in a cap':
          pokemonName = 'Cap Pikachu'

        # in this table, form names come first, e.g. 'Alolan Marowak'--to parse them, we need to switch the order
        pokemonName = re.sub(r'(.+)\s(.+)', r'\2 (\1)', pokemonName)
        pokemonName = parseName(pokemonName, 'pokemon')
        
        # write a row for each Pokemon
        writer.writerow([gen, spriteURL, itemName, pokemonName, effect, additionalEffect])
  return

# We go through the different types of items individually and collect the relevant data in separate .csv's
# At the same time, we compile the basic item info in a main .csv file, whose columns are Name, Type, Gen Introduced, Sprite URL
def main():
  main_fname = getDataPath() + 'heldItemList.csv'
  with open(main_fname, 'w', newline='', encoding='utf-8') as mainCSV:
    mainWriter = csv.writer(mainCSV)

    # berries
    # main list of berries
    # berry_fname = getDataPath() + 'berryList.csv'
    # berryList(berry_fname, mainWriter)

    # # elemental type of berry for Natural Gift
    # berry_type_fname = getDataPath() + 'berriesByType.csv'
    # berryType(berry_type_fname)

    # # memories, plates, and drives
    # type_items_fname = getDataPath() + 'typeItems.csv'
    # typeItems(type_items_fname, mainWriter)

    # # incenses
    # incense_fname = getDataPath() + 'incenseList.csv'
    # incenseList(incense_fname, mainWriter)

    # # stat-enhancing items
    statEnhancers_fname = getDataPath() + 'statEnhancers.csv'
    statEnhancers(statEnhancers_fname, mainWriter)

    # power items

  return

if __name__ == '__main__':
  main()