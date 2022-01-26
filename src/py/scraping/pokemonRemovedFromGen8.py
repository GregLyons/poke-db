import csv
from utils import openLink, parseName, getCSVDataPath

def makeMainCSV(fname):
  with open(fname, 'w', newline='', encoding='utf-8') as csvFile:
    writer = csv.writer(csvFile)
    writer.writerow(['Pokemon Name', 'Version Group'])
    
    # SwSh
    bs = openLink('https://www.serebii.net/swordshield/unobtainable.shtml', 0, 10)
    # Extra row for stats
    dataRows = bs.find('h2').find_next('table').find_all('tr')[2:]

    for row in dataRows:
      cells = row.find_all(['td', 'th'])
      if len(cells) == 1:
        continue
      
      pokemonName = parseNameMore(parseName(cells[3].get_text(strip=True, separator='\n').splitlines()[0]).replace('é', 'e'))

      writer.writerow([pokemonName, 'SwSh'])
    
    # BDSP
    bs = openLink('https://www.serebii.net/brilliantdiamondshiningpearl/unobtainable.shtml', 0, 10)
    dataRows = bs.find('h2').find_next('table').find_all('tr')[1:]

    for row in dataRows:
      cells = row.find_all(['td', 'th'])
      if len(cells) == 1:
        continue
      
      pokemonName = parseNameMore(parseName(cells[3].get_text(strip=True, separator='\n').splitlines()[0]).replace('é', 'e'))

      writer.writerow([pokemonName, 'BDSP'])

  return

# Add form suffices--maybe move to 'json_creators/pokemon.py' instead
def parseNameMore(name):
  if name in ['castform', 'deoxys', 'arceus', 'silvally']:
    return name + '_normal'

  elif name in ['burmy', 'wormadam']:
    return name + '_plant'

  elif name in ['shaymin']:
    return name + '_land'

  elif name in ['deerling', 'sawsbuck']: 
    return name + '_spring'

  elif name in ['oricorio']:
    return name + '_baile'

  elif name in ['meloetta']:
    return name + '_aria'

  elif 'mime' in name:
    return 'mr_mime_galar'

  elif 'basculin' in name:
    return 'basculin_red_striped'

  elif name in ['landorus', 'thundurus', 'tornadus']:
    return name + '_incarnate'

  elif name in ['meowstic', 'indeedee']:
    return name + '_m'

  elif name in ['keldeo']:
    return name + '_ordinary'

  elif name in ['pumpkaboo', 'gourgeist']:
    return name + '_average'

  elif name in ['pumpkaboo', 'gourgeist']:
    return name + '_average'

  elif name in ['zygarde']:
    return name + '_50'

  elif name in ['lycanroc']:
    return name + '_midday'

  elif name in ['wishiwashi']:
    return name + '_solo'

  elif name in ['toxtricity']:
    return name + '_amped'

  elif name in ['morpeko']:
    return name + '_full_belly'

  elif name in ['aegislash']:
    return name + '_shield'

  elif name in ['eiscue']:
    return name + '_ice'

  elif 'alolan' in name or 'galarian' in name:
    return (name.split('_')[1] + '_' + name.split('_')[0]).replace('alolan', 'alola').replace('galarian', 'galar').replace('darmanitan', 'darmanitan_standard')

  elif name == 'darmanitan':
    return 'darmanitan_standard'

  return name

def main():
  dataPath = getCSVDataPath() + 'pokemon\\'
  fname = dataPath + 'pokemonRemovedFromGen8.csv'

  makeMainCSV(fname)
  return

if __name__ == '__main__':
  main()