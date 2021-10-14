import csv
import re
from utils import openBulbapediaLink, getDataBasePath, parseName

# TODO Lightning rod and variants only draw moves gen 5 onward

# columns are Ability Name, Effect Type
def abilityEffects(fnamePrefix):
  with open(fnamePrefix + 'ByEffect.csv', 'w', newline='', encoding='utf-8') as mainCSV:
    mainWriter = csv.writer(mainCSV)
    mainWriter.writerow(['Ability Name', 'Effect Type'])

    bs = openBulbapediaLink('https://bulbapedia.bulbagarden.net/wiki/Ability_variations', 0, 10)

    # boost moves of type or effect
    #region
    # We will extract data from several different tables and then add them to 'boostRows'; after that, we'll go through the boostRows list to add the data
    boostMoveClassRows = []

    adaptabilityTableRows = bs.find(id='Variations_of_Adaptability').find_next('table').find_all('tr')[2:]
    for row in adaptabilityTableRows:
      cells = row.find_all('td')

      abilityName = parseName(cells[0].get_text().replace('*', ''))
      multiplier = float(cells[2].get_text().rstrip('\n').replace('*', '').replace('x', ''))
      description = cells[1].get_text().rstrip('\n')

      boostMoveClassRows.append([abilityName, multiplier, description])

    blazeTableRows = bs.find(id='Variations_of_Blaze').find_next('table').find_all('tr')[2:]
    for row in blazeTableRows:
      cells = row.find_all('td')

      abilityName = parseName(cells[0].get_text())
      multiplier = 1.5
      description = cells[1].get_text().rstrip('\n') + '-type'

      boostMoveClassRows.append([abilityName, multiplier, description])

    darkAuraRows = bs.find(id='Variations_of_Dark_Aura').find_next('table').find_all('tr')[2:]
    for row in darkAuraRows:
      cells = row.find_all('td')

      abilityName = parseName(cells[0].get_text())
      multiplier = 1.33
      description = cells[1].get_text().rstrip('\n') + '-type'

      boostMoveClassRows.append([abilityName, multiplier, description])

    with open(fnamePrefix + 'BoostMoveClass.csv', 'w', newline='', encoding='utf-8') as currentCSV:
      currentWriter = csv.writer(currentCSV)
      currentWriter.writerow(['Ability Name', 'Boosts', 'Multiplier', 'Move Class'])

      for row in boostMoveClassRows:
        abilityName, multiplier, description = row[0], row[1], row[2] 

        if '-type' in description and 'same' not in description:
          type = parseName(re.search(r'.*-type', description).group().split()[-1].rstrip('type'))
          currentWriter.writerow([abilityName, type, multiplier, 'type'])
          mainWriter.writerow([abilityName, 'boost_type'])
        else:
          if 'recoil' in description or 'effective' in description or 'contact' in description or '60' in description or 'same' in description:
            currentWriter.writerow([abilityName, 'other', multiplier, 'other'])
            mainWriter.writerow([abilityName, 'boost_other'])
          else:
            method = parseName(description.split()[-2].rstrip('ing'))
            currentWriter.writerow([abilityName, method, multiplier, 'method'])
            mainWriter.writerow([abilityName, 'boost_method'])
    #endregion

    # boost stat
    #region
    boostStatRows = []

    chlorophyllTableRows = bs.find(id='Variations_of_Chlorophyll').find_next('table').find_all('tr')[2:]
    for row in chlorophyllTableRows:
      cells = row.find_all(['td', 'th'])
      abilityName = parseName(cells[0].get_text())
      stat = 'speed'
      modifier = 2.0
      boostStatRows.append([abilityName, stat, modifier])

    dauntlessShieldTableRows = bs.find(id='Variations_of_Dauntless_Shield').find_next('table').find_all('tr')[2:]
    for row in dauntlessShieldTableRows:
      cells = row.find_all(['td', 'th'])
      abilityName = parseName(cells[0].get_text())
      stat = 'attack'
      modifier = '+1'
      boostStatRows.append([abilityName, stat, modifier])

    gutsTableRows = bs.find(id='Variations_of_Guts').find_next('table').find_all('tr')[2:]
    for row in gutsTableRows:
      cells = row.find_all(['td', 'th'])
      abilityName = parseName(cells[0].get_text())
      stat = parseName(cells[1].get_text().replace('*', ''))
      modifier = 1.5
      boostStatRows.append([abilityName, stat, modifier])

    hugePowerTableRows = bs.find(id='Variations_of_Huge_Power').find_next('table').find_all('tr')[2:]
    for row in hugePowerTableRows:
      cells = row.find_all(['td', 'th'])
      abilityName = parseName(cells[0].get_text())
      stat = parseName(cells[1].get_text())
      modifier = 2.0
      boostStatRows.append([abilityName, stat, modifier])

    defiantTableRows = bs.find(id='Variations_of_Defiant').find_next('table').find_all('tr')[2:]
    for row in defiantTableRows:
      cells = row.find_all(['td', 'th'])
      abilityName = parseName(cells[0].get_text())
      stat = parseName(cells[1].get_text())
      modifier = '+2'
      boostStatRows.append([abilityName, stat, modifier])

    justifiedTableRows =  bs.find(id='Variations_of_Defiant').find_next('table').find_all('tr')[2:]
    for row in defiantTableRows:
      cells = row.find_all(['td', 'th'])
      abilityName = parseName(cells[0].get_text().replace('*', ''))
      stat = parseName(cells[2].get_text())
      if abilityName == 'water_compaction':
        modifier = '+2'
      elif abilityName == 'steam_engine':
        modifier = '+6'
      else:
        modifier = '+1'
      boostStatRows.append([abilityName, stat, modifier])

    lightningRodTableRows =  bs.find(id='Variations_of_Lightning_Rod').find_next('table').find_all('tr')[2:]
    for row in lightningRodTableRows:
      cells = row.find_all(['td', 'th'])
      abilityName = parseName(cells[0].get_text())
      stat = 'special_attack'
      modifier = '+1'
      boostStatRows.append([abilityName, stat, modifier])

    minusTableRows =  bs.find(id='Variations_of_Minus').find_next('table').find_all('tr')[2:]
    for row in minusTableRows:
      cells = row.find_all(['td', 'th'])
      abilityName = parseName(cells[0].get_text())
      stat = 'special_attack'
      modifier = 1.5
      boostStatRows.append([abilityName, stat, modifier])

    motorDriveTableRows =  bs.find(id='Variations_of_Motor_Drive').find_next('table').find_all('tr')[2:]
    for row in motorDriveTableRows:
      cells = row.find_all(['td', 'th'])
      abilityName = parseName(cells[0].get_text())
      stat = parseName(cells[2].get_text())
      modifier = '+1'
      boostStatRows.append([abilityName, stat, modifier])

    moxieTableRows =  bs.find(id='Variations_of_Motor_Drive').find_next('table').find_all('tr')[2:]
    for row in moxieTableRows:
      cells = row.find_all(['td', 'th'])
      abilityName = parseName(cells[0].get_text())
      if abilityName == 'beast_boost':
        stat = 'highest'
      else:
        stat = parseName(cells[1].get_text())
      modifier = '+1'
      boostStatRows.append([abilityName, stat, modifier])

    sandVeilTableRows =  bs.find(id='Variations_of_Sand_Veil').find_next('table').find_all('tr')[2:]
    for row in sandVeilTableRows:
      cells = row.find_all(['td', 'th'])
      abilityName = parseName(cells[0].get_text())
      stat = 'evasion'
      modifier = 0.8
      boostStatRows.append([abilityName, stat, modifier])

    boostStatRows.append(['super_luck', 'critical_hit_ratio', '+1'])

    with open(fnamePrefix + 'BoostStat.csv', 'w', newline='', encoding='utf-8') as currentCSV:
      currentWriter = csv.writer(currentCSV)
      currentWriter.writerow(['Ability Name', 'Stat', 'Modifier'])

      for row in boostStatRows:
        currentWriter.writerow([row[0], row[1], row[2]])
        mainWriter.writerow([row[0], 'boost_stat'])
    #endregion

    # create weather
    #region
    # columns are Ability Name, Weather
    createWeatherRows = []

    drizzleTableRows = bs.find(id='Variations_of_Drizzle').find_next('table').find_all('tr')[2:]
    for row in drizzleTableRows:
      cells = row.find_all(['td', 'th'])
      abilityName = parseName(cells[0].get_text())
      weather = parseName(cells[1].get_text())
      createWeatherRows.append([abilityName, weather])

    primordialSeaTableRows = bs.find(id='Variations_of_Primordial_Sea').find_next('table').find_all('tr')[2:]
    for row in primordialSeaTableRows:
      cells = row.find_all(['td', 'th'])
      abilityName = parseName(cells[0].get_text())
      weather = parseName(cells[1].get_text())
      createWeatherRows.append([abilityName, weather])

    with open(fnamePrefix + 'CreateWeather.csv', 'w', newline='', encoding='utf-8') as currentCSV:
      currentWriter = csv.writer(currentCSV)
      currentWriter.writerow(['Ability Name', 'Weather'])

      for row in createWeatherRows:
        currentWriter.writerow(row)
        mainWriter.writerow([row[0], 'create_weather'])
    #endregion
    
    # create terrain
    #region
    # columns are Ability Name, Terrain
    createTerrainRows = []
    electricSurgeTableRows = bs.find(id='Variations_of_Electric_Surge').find_next('table').find_all('tr')[2:]
    for row in electricSurgeTableRows:
      cells = row.find_all(['td', 'th'])
      abilityName = parseName(cells[0].get_text())
      terrain = parseName(cells[1].get_text())
      createTerrainRows.append([abilityName, terrain])

    with open(fnamePrefix + 'CreateTerrain.csv', 'w', newline='', encoding='utf-8') as currentCSV:
      currentWriter = csv.writer(currentCSV)
      currentWriter.writerow(['Ability Name', 'Terrain'])

      for row in createTerrainRows:
        currentWriter.writerow(row)
        mainWriter.writerow([row[0], 'create_terrain'])
    #endregion



  return

def main():
  dataPath = getDataBasePath() + 'abilities\\'
  abilityEffects_fnamePrefix = dataPath + 'abilities'
  abilityEffects(abilityEffects_fnamePrefix)
  return

if __name__ == '__main__':
  main()