import csv
import re
from utils import openLink, getDataPath, parseName, genSymbolToNumber

# Columns are Gen, Dex Number, Species Name, Pokemon Name, Type 1, and Type 2
# Type 2 possibly equals Type 1
def makePokemonTypeCSV(fname):
  bs = openLink('https://bulbapedia.bulbagarden.net/wiki/List_of_Pok%C3%A9mon_by_National_Pok%C3%A9dex_number', 0, 10)

  with open(fname, 'w', newline='', encoding='utf-8') as speciesCSV:
    writer = csv.writer(speciesCSV)
    writer.writerow(['Gen', 'Dex Number', 'Species Name', 'Pokemon Name', 'Type 1', 'Type 2'])

    genSymbols = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII']
    for genSymbol in genSymbols:
      table = bs.find('span', {'id': f'Generation_{genSymbol}'}).find_next('table')
      dataRows = table.find_next('tr').find_next_siblings('tr')

      speciesName = ''

      # Burmy doesn't have type differences, or differences in ability, but we need to give it multiple different forms for the evolution chain
      burmyCounter = 0
      burmySuffixes = ['plant', 'sandy', 'trash']

      for row in dataRows:
        # for some reason, the MS (menu sprite) column is actually a <th>, not a <td>, so we must keep this in mind when indexing
        cells = row.find_all(['td', 'th'])


        dexNumber = cells[1].get_text().rstrip('\n').lstrip('#').lstrip('0')


        speciesName = cells[3].get_text().rstrip('\n')

        # if Pokemon is Alolan or Galarian form, then their dex number will be missing
        isRegional = '#' not in cells[0].get_text()
        # remove regional forms--certain Gen 4 Pokemon do not have a number in this slot either, so keep them
        if isRegional and speciesName not in ['Heatran', 'Regigigas','Cresselia', 'Phione', 'Darkrai', 'Shaymin', 'Arceus']:
          continue


        # it's easiest to handle Darmanitan separately from all the rest, due to his multiple forms
        if speciesName == 'Darmanitan':
          continue
        
        # this table doesn't have form names, so we don't use 'pokemon' mode
        formattedSpeciesName = parseName(speciesName, 'pokemon')

        type1 = parseName(cells[4].get_text())
        
        # if Pokemon has two types, then there is an extra cell
        if len(cells) == 5:
          type2 = ''
        else:
          type2 = parseName(cells[5].get_text())

        # Bulbapedia also lists unreleased Pokemon, like Basculegion
        released = dexNumber != ''
        if not released:
          continue

        # need to handle Pokemon forms with different types
        if formattedSpeciesName == 'rotom':
          if type2 == 'fire':
            formName = 'heat'
          elif type2 == 'water':
            formName = 'wash'
          elif type2 == 'ice':
            formName = 'frost'
          elif type2 == 'flying':
            formName = 'fan'
          elif type2 == 'grass':
            formName = 'mow'
          elif type2 == 'ghost':
            formName = ''
          else:
            print("Couldn't handle", formattedSpeciesName, type2)
        elif formattedSpeciesName == 'burmy':
          formName = burmySuffixes[burmyCounter]
          burmyCounter += 1
        elif formattedSpeciesName == 'wormadam':
          if type2 == 'grass':
            formName = 'plant'
          elif type2 == 'ground':
            formName = 'sandy'
          elif type2 == 'steel':
            formName = 'trash'
          else:
            print("Couldn't handle", formattedSpeciesName, type2)
        elif formattedSpeciesName == 'meloetta':
          if type2 == 'psychic':
            formName = 'aria'
          elif type2 == 'fighting':
            formName = 'pirouette'
          else:
            print("Couldn't handle", formattedSpeciesName, type2)
        elif formattedSpeciesName == 'hoopa':
          if type2 == 'ghost':
            formName = 'confined'
          elif type2 == 'dark':
            formName = 'unbound'
          else:
            print("Couldn't handle", formattedSpeciesName, type2)
        elif formattedSpeciesName == 'castform':
          if type1 == 'normal':
            formName = 'normal'
          elif type1 == 'fire':
            formName = 'sunny'
          elif type1 == 'water':
            formName = 'rainy'
          elif type1 == 'ice':
            formName = 'snowy'
          else:
            print("Couldn't handle", formattedSpeciesName, type1)
        elif formattedSpeciesName == 'oricorio':
          if type1 == 'fire':
            formName = 'baile'
          elif type1 == 'electric':
            formName = 'pom_pom'
          elif type1 == 'psychic':
            formName = 'pau'
          elif type1 == 'ghost':
            formName = 'sensu'
          else:
            print("Couldn't handle", formattedSpeciesName, type1)
        elif formattedSpeciesName == 'urshifu':
          if type2 == 'water':
            formName = 'rapid_strike'
          elif type2 == 'dark':
            formName = ''
          else:
            print("Couldn't handle", formattedSpeciesName, type2)
        else:
          formName = ''

        if formName != '':
          formName = '_' + formName
      
        writer.writerow([
          genSymbolToNumber(genSymbol), 
          dexNumber, 
          formattedSpeciesName, 
          formattedSpeciesName + formName, 
          type1, 
          type2
        ])
  
    # Add mega forms and regional forms, which are located at different links, to the .csv
    addMegas(writer)
    addRegionalForms(writer)
    addGMax(writer)

    # add Darmanitan
    writer.writerow([5, 555, 'darmanitan', 'darmanitan_standard', 'fire', ''])
    writer.writerow([5, 555, 'darmanitan', 'darmanitan_zen', 'fire', 'psychic'])
    writer.writerow([8, 555, 'darmanitan', 'darmanitan_standard_galar', 'ice', ''])
    writer.writerow([8, 555, 'darmanitan', 'darmanitan_zen_galar', 'ice', 'fire'])

  return

def addMegas(writer):
  bs = openLink('https://bulbapedia.bulbagarden.net/wiki/Mega_Evolution', 0, 10)

  xyTable = bs.find('span', {'id': 'Introduced_in_X_and_Y'}).find_next('table')
  orasTable = bs.find('span', {'id': 'Introduced_in_Omega_Ruby_and_Alpha_Sapphire'}).find_next('table')

  for table in [xyTable, orasTable]:
    dataRows = table.find_all('tr')[2:]
    for row in dataRows:
      cells = row.find_all('td')

      speciesName = cells[0].get_text().rstrip('\n').rstrip('*')

      # two exceptions for Pokemon with two megas
      if speciesName == 'Charizard':
        megaName = speciesName + ' Mega'
        writer.writerow([6, '', parseName(speciesName), parseName(megaName + ' X'), 'fire', 'dragon'])
        writer.writerow([6, '', parseName(speciesName), parseName(megaName + ' Y'), 'fire', 'flying'])
        continue
      elif speciesName == 'Mewtwo':
        megaName = speciesName + ' Mega'
        writer.writerow([6, '', parseName(speciesName), parseName(megaName + ' X'), 'psychic', 'fighting'])
        writer.writerow([6, '', parseName(speciesName), parseName(megaName + ' Y'), 'psychic', ''])
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
        megaType2 = ''
      else:
        megaType2 = megaTypes[3]

      # this table doesn't have form names, so we don't use 'pokemon' mode
      writer.writerow([6, '', parseName(speciesName), parseName(megaName), megaType1.lower(), megaType2.lower()])

  return

def addRegionalForms(writer):
  bs = openLink('https://bulbapedia.bulbagarden.net/wiki/Regional_form', 0, 10)

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

      speciesName = parseName(cells[0].get_text(), 'pokemon')
      if speciesName in ['darmanitan', 'zen_mode']:
        continue

      regionalName = speciesName + ' ' + region

      regionalTypes = [span.get_text().replace(u'\xa0', '') for span in cells[5].find_all('span')]
      regionalType1 = regionalTypes[0]

      # Bulbapedia lists each type twice 
      if len(regionalTypes) == 2:
        regionalType2 = ''
      else:
        regionalType2 = regionalTypes[3]

      writer.writerow([gen, '', speciesName, regionalName.replace(' Alola', '_alola').replace(' Galar', '_galar'), parseName(regionalType1), parseName(regionalType2)])

  return

# Add G-max pokemon
def addGMax(writer):
  bs = openLink('https://bulbapedia.bulbagarden.net/wiki/Gigantamax', 0, 10)
  dataRows = bs.find(id='Introduced_in_Pokémon_Sword_and_Shield_v1.0.0').find_next('table').find_all('tr')[2:] + bs.find(id='Introduced_in_The_Isle_of_Armor').find_next('table').find_all('tr')[2:]

  for row in dataRows:
    cells = row.find_all('td')
    pokemonName = cells[0].get_text(separator=' ')
    speciesName = parseName(pokemonName.split()[0], 'pokemon')

    if 'Urshifu' in pokemonName:
      # parseName method already handles Urshifu forms of the format in the table
      pokemonName = 'g_max_' + parseName(pokemonName, 'pokemon')
    elif 'Toxtricity' in pokemonName:
      writer.writerow([8, '', speciesName, 'g_max_' + speciesName + '_low_key', 'electric', 'poison'])
      writer.writerow([8, '', speciesName, 'g_max_' + speciesName + '_amped', 'electric', 'poison'])
      continue
    else: 
      pokemonName = 'g_max_' + parseName(pokemonName.split('(')[0], 'pokemon')

    gmaxTypes = [span.get_text().replace(u'\xa0', '') for span in cells[1].find_all('span')]
    gmaxType1 = gmaxTypes[0]

    # Bulbapedia lists each type twice 
    if len(gmaxTypes) == 2:
      gmaxType2 = ''
    else:
      gmaxType2 = gmaxTypes[3]

    writer.writerow([8, '', speciesName, pokemonName, parseName(gmaxType1), parseName(gmaxType2)])

  return

# columns are Pokemon Name, Old Typing, Gen (of type change)
def pokemonTypeChanges(fname):
  with open(fname, 'w', newline='', encoding='utf-8') as changeCSV:
    writer = csv.writer(changeCSV)
    writer.writerow(["Pokemon Name", "Old Type 1", "Old Type 2", "Gen"])

    bs = openLink('https://bulbapedia.bulbagarden.net/wiki/Category:Pok%C3%A9mon_that_have_had_their_type_changed', 0, 10)
    pokemonLinkGroups = bs.find_all('div', {'class': 'mw-category-group'})

    for linkGroup in pokemonLinkGroups:
      pokemonLinks = linkGroup.find('ul').find_all('li')

      for pokemonLink in pokemonLinks:
        pokemonLink = pokemonLink.find('a')
        pokemonName = parseName(pokemonLink.get_text().rstrip('\n').removesuffix(' (Pokémon)'), 'pokemon')
        
        # handle rotom form separately since its page description is more complicated
        if pokemonName == 'rotom':
          writer.writerow(['rotom_fan', 'electric', 'ghost', '5'])
          writer.writerow(['rotom_heat', 'electric', 'ghost', '5'])
          writer.writerow(['rotom_mow', 'electric', 'ghost', '5'])
          writer.writerow(['rotom_frost', 'electric', 'ghost', '5'])
          writer.writerow(['rotom_wash', 'electric', 'ghost', '5'])
          continue

        # open link and check first paragraph for type change information
        description = openLink('https://bulbapedia.bulbagarden.net' + pokemonLink['href'], 0, 10).find(id='mw-content-text').find('p').get_text()
        
        # type change is in a sentence of the form "Prior to [<a> element with generaton number in its text], it was a pure [type name]-type"
        genChange, previousType = re.search(r'Prior to Generation (I,|II,|III,|IV,|V,|VI,|VII,|VIII,|IX,) it was a [pure ]*([A-Za-z]*)-type', description).group(1, 2)
        
        # indicates Pokemon had two types in the past
        if previousType == 'dual':
          previousType1, previousType2 = re.search(r'Prior to Generation [IXV]*, it was a dual-type ([A-Za-z]*)/([A-Za-z]*) ', description).group(1, 2)
        else:
          previousType1, previousType2 = previousType, ''

        previousType1, previousType2, genChange = parseName(previousType1), parseName(previousType2), genSymbolToNumber(genChange.rstrip(','))

        writer.writerow([pokemonName, previousType1, previousType2, genChange])


  return

def main():
  dataPath = getDataPath() + '\\pokemon\\'
  main_fname = dataPath + 'pokemonByType.csv'
  makePokemonTypeCSV(main_fname)

  change_fname = dataPath + 'pokemonTypeChanges.csv'
  pokemonTypeChanges(change_fname)

if __name__ == '__main__':
  main()