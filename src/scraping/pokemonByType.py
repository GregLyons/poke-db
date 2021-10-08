import csv
from utils import openBulbapediaLink, getDataPath, titleOrPascalToKebab, genSymbolToNumber

# Columns are Gen, National Dex number, species name, Pokemon name, type 1, and type 2 (possibly equals type 1)
def makePokemonTypeCSV(fname):
  bs = openBulbapediaLink('https://bulbapedia.bulbagarden.net/wiki/List_of_Pok%C3%A9mon_by_National_Pok%C3%A9dex_number', 0, 10)

  with open(fname, 'w', newline='', encoding='utf-8') as speciesCSV:
    writer = csv.writer(speciesCSV)
    writer.writerow(['Gen', 'Dex Number', 'Species Name', 'Pokemon Name', 'Type 1', 'Type 2'])

    genSymbols = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII']
    for genSymbol in genSymbols:
      table = bs.find('span', {'id': f'Generation_{genSymbol}'}).find_next('table')
      dataRows = table.find_next('tr').find_next_siblings('tr')

      speciesName = ''

      for row in dataRows:
        # for some reason, the MS (menu sprite) column is actually a <th>, not a <td>, so we must keep this in mind when indexing
        cells = row.find_all('td')

        # if Pokemon is Alolan or Galarian form, then they will have the same name as the Pokemon before it; we will handle such forms later, so remove them for now
        isDefault = cells[2].get_text().rstrip('\n') != speciesName

        dexNumber = cells[1].get_text().rstrip('\n').lstrip('#').lstrip('0')


        speciesName = cells[2].get_text().rstrip('\n')

        # it's easiest to handle Darmanitan separately from all the rest, due to his multiple forms
        if speciesName == 'Darmanitan':
          continue

        formattedSpeciesName = titleOrPascalToKebab(speciesName)

        type1 = cells[3].get_text().rstrip('\n').lower()
        
        # if Pokemon has two types, then there is an extra cell
        if len(cells) == 4:
          type2 = '--'
        else:
          type2 = cells[4].get_text().rstrip('\n').lower()

        # Bulbapedia also lists unreleased Pokemon, like Basculegion
        released = dexNumber != ''

        if isDefault and released:
        
          writer.writerow([genSymbolToNumber(genSymbol), dexNumber, formattedSpeciesName, formattedSpeciesName, type1, type2])
        else:
          continue
  
    # Add mega forms and regional forms, which are located at different links, to the .csv
    addMegas(writer)
    addRegionalForms(writer)

    # add Darmanitan
    writer.writerow([5, 555, 'darmanitan', 'darmanitan-standard', 'fire', '--'])
    writer.writerow([5, '--', 'darmanitan', 'darmanitan-zen', 'fire', 'psychic'])
    writer.writerow([8, '--', 'darmanitan', 'darmanitan-standard-galar', 'ice', '--'])
    writer.writerow([8, '--', 'darmanitan', 'darmanitan-zen-galar', 'ice', 'fire'])

  return

def addMegas(writer):
  bs = openBulbapediaLink('https://bulbapedia.bulbagarden.net/wiki/Mega_Evolution', 0, 10)

  xyTable = bs.find('span', {'id': 'Introduced_in_X_and_Y'}).find_next('table')
  orasTable = bs.find('span', {'id': 'Introduced_in_Omega_Ruby_and_Alpha_Sapphire'}).find_next('table')

  for table in [xyTable, orasTable]:
    dataRows = table.find_all('tr')[2:]
    for row in dataRows:
      cells = row.find_all('td')

      speciesName = cells[0].get_text().rstrip('\n').rstrip('*')

      # two exceptions for Pokemon with two megas
      if speciesName == 'Charizard':
        writer.writerow([6, '--', titleOrPascalToKebab(speciesName), titleOrPascalToKebab(megaName + ' X'), 'fire', 'dragon'])
        writer.writerow([6, '--', titleOrPascalToKebab(speciesName), titleOrPascalToKebab(megaName + ' Y'), 'fire', 'flying'])
        continue
      elif speciesName == 'Mewtwo':
        writer.writerow([6, '--', titleOrPascalToKebab(speciesName), titleOrPascalToKebab(megaName + ' X'), 'psychic', 'fighting'])
        writer.writerow([6, '--', titleOrPascalToKebab(speciesName), titleOrPascalToKebab(megaName + ' Y'), 'psychic', '--'])
        continue
      # each of these two exceptions actually takes up two table rows, which we must skip as well
      elif len(cells) < 5:
        continue

      # typical case 
      megaName = speciesName + ' Mega'

      # if a Pokemon has two types, they are both listed in the same cell, in separate spans
      megaTypes = [span.get_text().replace(u'\xa0', '') for span in cells[5].find_all('span')]
      megaType1 = megaTypes[0]

      # Bulbapedia lists each type twice 
      if len(megaTypes) == 2:
        megaType2 = '--'
      else:
        megaType2 = megaTypes[3]

      writer.writerow([6, '--', titleOrPascalToKebab(speciesName), titleOrPascalToKebab(megaName), megaType1.lower(), megaType2.lower()])

  return

def addRegionalForms(writer):
  bs = openBulbapediaLink('https://bulbapedia.bulbagarden.net/wiki/Regional_form', 0, 10)

  alolaTable = [bs.find('span', {'id': 'List_of_Alolan_Forms'}).find_next('table'), 'Alola']
  galarTable = [bs.find('span', {'id': 'List_of_Galarian_Forms'}).find_next('table'), 'Galar']

  for table in [alolaTable, galarTable]:
    table, region = table[0], table[1]
    if region == 'Alola':
      gen = 7
    else:
      gen = 8

    dataRows = table.find_all('tr')[2:]
    for row in dataRows:
      cells = row.find_all('td')

      # in the Galar table, there are rows with only one <td> indicating when the Pokemon were added
      if len(cells) == 1:
        continue

      speciesName = cells[0].get_text().rstrip('\n')
      if speciesName in ['Darmanitan', 'Zen Mode']:
        continue

      regionalName = speciesName + ' ' + region

      regionalTypes = [span.get_text().replace(u'\xa0', '') for span in cells[5].find_all('span')]
      regionalType1 = regionalTypes[0]

      # Bulbapedia lists each type twice 
      if len(regionalTypes) == 2:
        regionalType2 = '--'
      else:
        regionalType2 = regionalTypes[3]

      writer.writerow([gen, '--', speciesName, regionalName, regionalType1, regionalType2])

  return

fname = getDataPath() + 'pokemonByType.csv'
makePokemonTypeCSV(fname)
