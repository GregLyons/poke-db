import csv
from utils import openLink, getCSVDataPath, parseName

def makeRequirementCSV(fname): 
  with open(fname, 'w', newline='', encoding='utf-8') as csvFile:
    writer = csv.writer(csvFile)

    # 'Base 1/2 Class' describes requirements for Move Name (e.g. Pokemon, base move, move type)
    writer.writerow(['Move Name', 'Requirement 1 Class', 'Requirement 1 Name', 'Requirement 2 Class', 'Requirement 2 Name'])

    # max moves
    bs = openLink('https://bulbapedia.bulbagarden.net/wiki/Max_Move', 0, 10)
    dataRows = bs.find(id='List_of_Max_Moves').find_next('table').find_all('tr')[1:]

    for row in dataRows:
      cells = row.find_all(['td', 'th'])
      moveName, type = parseName(cells[0].get_text()), parseName(cells[1].get_text())

      if moveName == 'max_guard':
        writer.writerow([moveName, 'category', 'status', '', ''])
      else:
        writer.writerow([moveName, 'type', type, '', ''])

    # gmax moves 
    bs = openLink('https://bulbapedia.bulbagarden.net/wiki/Gigantamax', 0, 10)
    dataRows = bs.find(id='Introduced_in_Pokémon_Sword_and_Shield_v1.0.0').find_next('table').find_all('tr')[2:] + bs.find(id='Introduced_in_The_Isle_of_Armor').find_next('table').find_all('tr')[2:]

    for row in dataRows:
      cells = row.find_all(['th', 'td'])
      pokemonName, moveName, moveType = parseName(cells[0].get_text()), parseName(cells[-2].get_text()), parseName(cells[-1].get_text())

      # pokemon names are formatted differently than usual, as the species and form names are on separate lines
      if 'toxtricity' in pokemonName:
        writer.writerow([moveName, 'pokemon', 'toxtricity_amped', 'type', moveType])
        writer.writerow([moveName, 'pokemon', 'toxtricity_low_key', 'type', moveType])
        continue
      elif 'alcremie' in pokemonName:
        pokemonName = 'alcremie'
      # urshifu
      elif 'urshifu' in pokemonName:
        if 'one_blow' in moveName:
          pokemonName = 'urshifu'
        else:
          pokemonName = 'urshifu_rapid_strike'

      writer.writerow([moveName, 'pokemon', pokemonName, 'type', moveType])

    # generic type-based z-moves 
    bs = openLink('https://bulbapedia.bulbagarden.net/wiki/Z-Move', 0, 10)
    dataRows = bs.find(id='For_each_type').find_next('table').find_next('table').find_all('tr')[1:]

    for row in dataRows:
      cells = row.find_all(['th', 'td'])
      moveName, moveType = parseName(cells[0].get_text()), parseName(cells[1].get_text())
      writer.writerow([moveName, 'type', moveType, '', ''])

    # pokemon specific z-moves
    dataRows = bs.find(id='For_specific_Pokémon').find_next('table').find_next('table').find_all('tr')[1:]

    for row in dataRows:
      cells = row.find_all(['th', 'td'])
      moveName, pokemonNames, baseMove = parseName(cells[1].get_text()), [parseName(cells[2].get_text())], parseName(cells[3].get_text())

      # some of the Pokemon names are very strangely formatted (species name and form name have separate links), so putting separator in get_text() doesn't work well; hard code exceptions
      if 'volt_thunderbolt' in moveName:
        pokemonNames = ['pikachu_in_a_cap']
      elif 'sparksurfer' in moveName:
        pokemonNames = ['raichu_alola']
      elif 'guardian_of_alola' in moveName:
        pokemonNames = ['tapu_bulu', 'tapu_koko', 'tapu_lele', 'tapu_fini']
      elif 'sunraze' in moveName:
        pokemonNames = ['solgaleo', 'necrozma_dusk_mane']
      elif 'moonraze' in moveName:
        pokemonNames = ['lunala', 'necrozma_dawn_wings']
      elif 'burns_the_sky' in moveName:
        pokemonNames = ['necrozma_ultra']
      elif 'stormshards' in moveName:
        pokemonNames = ['lycanroc_dusk', 'lycanroc_midday', 'lycanroc_midnight']

      for pokemonName in pokemonNames:
        writer.writerow([moveName, 'pokemon', pokemonName, 'move', baseMove])

    # status z-moves
    dataRows = bs.find(id='Z-Power_effects_of_status_moves').find_next('table').find_next('table').find_all('tr')[1:]

    for row in dataRows:
      cells = row.find_all(['th', 'td'])
      baseMove = parseName(cells[0].get_text())
      writer.writerow(['z_' + baseMove, 'move', baseMove, '', ''])
  return

def main():
  dataPath = getCSVDataPath() + '/moves/'
  fname = dataPath + 'movesByRequirement.csv'
  makeRequirementCSV(fname)

  return

if __name__ == '__main__':
  main()