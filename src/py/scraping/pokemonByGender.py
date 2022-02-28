import csv
from utils import openLink, getCSVDataPath, parseName

# Columns are Pokemon name, male (out of 8), female (out of 8)
def genderRatios(fname):
  with open(fname, 'w', newline='', encoding='utf-8') as genderCSV:
    writer = csv.writer(genderCSV)
    writer.writerow(['Pokemon Name', 'Males out of 8', 'Females out of 8'])

    # 8:0
    bs = openLink('https://bulbapedia.bulbagarden.net/wiki/List_of_Pok%C3%A9mon_by_gender_ratio', 0, 10)
    maleOnlyRows = bs.find(id='Male_only').find_next('table').find('table').find_all('tr')[1:] + bs.find(id='Male_only').find_next('h3').find_next('table').find('table').find_all('tr')[1:]

    for row in maleOnlyRows:
      cells = row.find_all('td')
      pokemonName = parseName(cells[2].get_text(), 'pokemon')
      
      # Ash Greninja forced to be male
      if 'battle_bond' in pokemonName:
        writer.writerow(['greninja_ash', 8, 0])
      else:
        writer.writerow([pokemonName, 8, 0])

    # 1:7
    oneToSevenRows = bs.find(id='1_♀_:_7_♂').find_next('table').find('table').find_all('tr')[1:] + bs.find(id='1_♀_:_7_♂').find_next('h3').find_next('table').find('table').find_all('tr')[1:]

    for row in oneToSevenRows:
      cells = row.find_all('td')
      pokemonName = parseName(cells[2].get_text(), 'pokemon')
      
      writer.writerow([pokemonName, 7, 1])

    # 1:3
    oneToThreeRows = bs.find(id='1_♀_:_3_♂').find_next('table').find('table').find_all('tr')[1:] + bs.find(id='1_♀_:_3_♂').find_next('h3').find_next('table').find('table').find_all('tr')[1:]

    for row in oneToThreeRows:
      cells = row.find_all('td')
      pokemonName = parseName(cells[2].get_text(), 'pokemon')
      
      writer.writerow([pokemonName, 6, 2])

    # 1:1
    oneToOneRows = bs.find(id='1_♀_:_1_♂').find_next('table').find('table').find_all('tr')[1:] + bs.find(id='1_♀_:_1_♂').find_next('h3').find_next('table').find('table').find_all('tr')[1:]

    for row in oneToOneRows:
      cells = row.find_all('td')
      pokemonName = parseName(cells[2].get_text(), 'pokemon')
      
      writer.writerow([pokemonName, 4, 4])

    # 3:1
    threeToOneRows = bs.find(id='3_♀_:_1_♂').find_next('table').find('table').find_all('tr')[1:] + bs.find(id='3_♀_:_1_♂').find_next('h3').find_next('table').find('table').find_all('tr')[1:]

    for row in threeToOneRows:
      cells = row.find_all('td')
      pokemonName = parseName(cells[2].get_text(), 'pokemon')
      
      writer.writerow([pokemonName, 2, 6])

    # 7:1
    # No 'unbreedable' table for this section
    sevenToOneRows = bs.find(id='7_♀_:_1_♂').find_next('table').find('table').find_all('tr')[1:]

    for row in sevenToOneRows:
      cells = row.find_all('td')
      pokemonName = parseName(cells[2].get_text(), 'pokemon')
      
      writer.writerow([pokemonName, 1, 7])

    # Female only
    femaleOnlyRows = bs.find(id='Female_only').find_next('table').find('table').find_all('tr')[1:] + bs.find(id='Female_only').find_next('h3').find_next('table').find('table').find_all('tr')[1:]

    for row in femaleOnlyRows:
      cells = row.find_all('td')
      pokemonName = parseName(cells[2].get_text(), 'pokemon')

      # Cosplay Pikachu
      if 'cosplay' in pokemonName:
        writer.writerow(['pikachu_cosplay', 0, 8])
      elif 'spiky_eared' in pokemonName:
        writer.writerow(['pichu_spiky_eared', 0, 8])
      else:
        writer.writerow([pokemonName, 0, 8])

  # Genderless
    genderUnknownRows = bs.find(id='Gender_unknown').find_next('table').find('table').find_all('tr')[1:] + bs.find(id='Gender_unknown').find_next('h3').find_next('table').find('table').find_all('tr')[1:]

    for row in genderUnknownRows:
      cells = row.find_all('td')
      # Ditto has asterisk in name
      pokemonName = parseName(cells[2].get_text(), 'pokemon').replace('*', '')

      writer.writerow([pokemonName, 0, 0])

  return

def main():
  dataPath = getCSVDataPath() + 'pokemon\\'
  gender_fname = dataPath + 'pokemonByGender.csv'
  genderRatios(gender_fname)

  return

if __name__ == '__main__':
  main()
