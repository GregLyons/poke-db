import csv
import re
from utils import openBulbapediaLink, getDataBasePath, parseName

# TODO Lightning rod and variants only draw moves gen 5 onward

# The table-parsing code in this function is very repetitive, but due to many of the tables being slightly different in terms of number/placement of columns, I couldn't think of a more elegant solution 
# columns are Ability Name, Effect Type
def abilityEffects(fnamePrefix):
  with open(fnamePrefix + 'ByEffect.csv', 'w', newline='', encoding='utf-8') as mainCSV, open(fnamePrefix + 'ByEffectNotes.csv', 'w', newline='', encoding='utf-8') as notesCSV:
    mainWriter = csv.writer(mainCSV)
    mainWriter.writerow(['Ability Name', 'Effect Type'])
    notesWriter = csv.writer(notesCSV)
    notesWriter.writerow(['Ability Name', 'Note'])

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

      for cell in cells:
        if cell.find('span', {'class': 'explain'}) != None:
            notesInCell = cell.find_all('span', {'class': 'explain'})
            for note in notesInCell:
              notesWriter.writerow([abilityName, note.get('title')])

      boostMoveClassRows.append([abilityName, multiplier, description])

    blazeTableRows = bs.find(id='Variations_of_Blaze').find_next('table').find_all('tr')[2:]
    for row in blazeTableRows:
      cells = row.find_all('td')

      abilityName = parseName(cells[0].get_text())
      multiplier = 1.5
      description = cells[1].get_text().rstrip('\n') + '-type'

      for cell in cells:
        if cell.find('span', {'class': 'explain'}) != None:
            notesInCell = cell.find_all('span', {'class': 'explain'})
            for note in notesInCell:
              notesWriter.writerow([abilityName, note.get('title')])

      boostMoveClassRows.append([abilityName, multiplier, description])

    darkAuraRows = bs.find(id='Variations_of_Dark_Aura').find_next('table').find_all('tr')[2:]
    for row in darkAuraRows:
      cells = row.find_all('td')

      abilityName = parseName(cells[0].get_text())
      multiplier = 1.33
      description = cells[1].get_text().rstrip('\n') + '-type'

      for cell in cells:
        if cell.find('span', {'class': 'explain'}) != None:
            notesInCell = cell.find_all('span', {'class': 'explain'})
            for note in notesInCell:
              notesWriter.writerow([abilityName, note.get('title')])

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

      for cell in cells:
        if cell.find('span', {'class': 'explain'}) != None:
            notesInCell = cell.find_all('span', {'class': 'explain'})
            for note in notesInCell:
              notesWriter.writerow([abilityName, note.get('title')])
      
      boostStatRows.append([abilityName, stat, modifier])

    dauntlessShieldTableRows = bs.find(id='Variations_of_Dauntless_Shield').find_next('table').find_all('tr')[2:]
    for row in dauntlessShieldTableRows:
      cells = row.find_all(['td', 'th'])
      abilityName = parseName(cells[0].get_text())
      stat = 'attack'
      modifier = '+1'

      for cell in cells:
        if cell.find('span', {'class': 'explain'}) != None:
            notesInCell = cell.find_all('span', {'class': 'explain'})
            for note in notesInCell:
              notesWriter.writerow([abilityName, note.get('title')])
     
      boostStatRows.append([abilityName, stat, modifier])

    gutsTableRows = bs.find(id='Variations_of_Guts').find_next('table').find_all('tr')[2:]
    for row in gutsTableRows:
      cells = row.find_all(['td', 'th'])
      abilityName = parseName(cells[0].get_text())
      stat = parseName(cells[1].get_text().replace('*', ''))
      modifier = 1.5

      for cell in cells:
        if cell.find('span', {'class': 'explain'}) != None:
            notesInCell = cell.find_all('span', {'class': 'explain'})
            for note in notesInCell:
              notesWriter.writerow([abilityName, note.get('title')])
      
      boostStatRows.append([abilityName, stat, modifier])

    hugePowerTableRows = bs.find(id='Variations_of_Huge_Power').find_next('table').find_all('tr')[2:]
    for row in hugePowerTableRows:
      cells = row.find_all(['td', 'th'])
      abilityName = parseName(cells[0].get_text())
      stat = parseName(cells[1].get_text())
      modifier = 2.0

      for cell in cells:
        if cell.find('span', {'class': 'explain'}) != None:
            notesInCell = cell.find_all('span', {'class': 'explain'})
            for note in notesInCell:
              notesWriter.writerow([abilityName, note.get('title')])
      
      boostStatRows.append([abilityName, stat, modifier])

    defiantTableRows = bs.find(id='Variations_of_Defiant').find_next('table').find_all('tr')[2:]
    for row in defiantTableRows:
      cells = row.find_all(['td', 'th'])
      abilityName = parseName(cells[0].get_text())
      stat = parseName(cells[1].get_text())
      modifier = '+2'
      
      for cell in cells:
        if cell.find('span', {'class': 'explain'}) != None:
            notesInCell = cell.find_all('span', {'class': 'explain'})
            for note in notesInCell:
              notesWriter.writerow([abilityName, note.get('title')])
      
      boostStatRows.append([abilityName, stat, modifier])

    justifiedTableRows =  bs.find(id='Variations_of_Justified').find_next('table').find_all('tr')[2:]
    for row in justifiedTableRows:
      cells = row.find_all(['td', 'th'])
      abilityName = parseName(cells[0].get_text().replace('*', ''))
      stat = parseName(cells[2].get_text())
      if abilityName == 'water_compaction':
        modifier = '+2'
      elif abilityName == 'steam_engine':
        modifier = '+6'
      else:
        modifier = '+1'

      for cell in cells:
        if cell.find('span', {'class': 'explain'}) != None:
            notesInCell = cell.find_all('span', {'class': 'explain'})
            for note in notesInCell:
              notesWriter.writerow([abilityName, note.get('title')])
      
      boostStatRows.append([abilityName, stat, modifier])

    lightningRodTableRows =  bs.find(id='Variations_of_Lightning_Rod').find_next('table').find_all('tr')[2:]

    for row in lightningRodTableRows:
      cells = row.find_all(['td', 'th'])
      abilityName = parseName(cells[0].get_text())
      stat = 'special_attack'
      modifier = '+1'

      notesWriter.writerow([abilityName, 'Does not raise Special Attack or provide immunity prior to Generation V.'])
      
      for cell in cells:
        if cell.find('span', {'class': 'explain'}) != None:
            notesInCell = cell.find_all('span', {'class': 'explain'})
            for note in notesInCell:
              notesWriter.writerow([abilityName, note.get('title')])
      
      boostStatRows.append([abilityName, stat, modifier])

    minusTableRows =  bs.find(id='Variations_of_Minus').find_next('table').find_all('tr')[2:]
    for row in minusTableRows:
      cells = row.find_all(['td', 'th'])
      abilityName = parseName(cells[0].get_text())
      stat = 'special_attack'
      modifier = 1.5
      
      for cell in cells:
        if cell.find('span', {'class': 'explain'}) != None:
            notesInCell = cell.find_all('span', {'class': 'explain'})
            for note in notesInCell:
              notesWriter.writerow([abilityName, note.get('title')])
      
      boostStatRows.append([abilityName, stat, modifier])

    motorDriveTableRows =  bs.find(id='Variations_of_Motor_Drive').find_next('table').find_all('tr')[2:]
    for row in motorDriveTableRows:
      cells = row.find_all(['td', 'th'])
      abilityName = parseName(cells[0].get_text())
      stat = parseName(cells[2].get_text())
      modifier = '+1'
      
      for cell in cells:
        if cell.find('span', {'class': 'explain'}) != None:
            notesInCell = cell.find_all('span', {'class': 'explain'})
            for note in notesInCell:
              notesWriter.writerow([abilityName, note.get('title')])
      
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
      
      for cell in cells:
        if cell.find('span', {'class': 'explain'}) != None:
            notesInCell = cell.find_all('span', {'class': 'explain'})
            for note in notesInCell:
              notesWriter.writerow([abilityName, note.get('title')])
      
      boostStatRows.append([abilityName, stat, modifier])

    sandVeilTableRows =  bs.find(id='Variations_of_Sand_Veil').find_next('table').find_all('tr')[2:]
    for row in sandVeilTableRows:
      cells = row.find_all(['td', 'th'])
      abilityName = parseName(cells[0].get_text())
      stat = 'evasion'
      modifier = 0.8
      
      for cell in cells:
        if cell.find('span', {'class': 'explain'}) != None:
            notesInCell = cell.find_all('span', {'class': 'explain'})
            for note in notesInCell:
              notesWriter.writerow([abilityName, note.get('title')])
      
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
      abilityName = parseName(cells[0].get_text().replace('*', ''))
      weather = parseName(cells[1].get_text())
      
      for cell in cells:
        if cell.find('span', {'class': 'explain'}) != None:
            notesInCell = cell.find_all('span', {'class': 'explain'})
            for note in notesInCell:
              notesWriter.writerow([abilityName, note.get('title')])
      
      createWeatherRows.append([abilityName, weather])

    primordialSeaTableRows = bs.find(id='Variations_of_Primordial_Sea').find_next('table').find_all('tr')[2:]
    for row in primordialSeaTableRows:
      cells = row.find_all(['td', 'th'])
      abilityName = parseName(cells[0].get_text())
      weather = parseName(cells[1].get_text())
      
      for cell in cells:
        if cell.find('span', {'class': 'explain'}) != None:
            notesInCell = cell.find_all('span', {'class': 'explain'})
            for note in notesInCell:
              notesWriter.writerow([abilityName, note.get('title')])
      
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
      
      for cell in cells:
        if cell.find('span', {'class': 'explain'}) != None:
            notesInCell = cell.find_all('span', {'class': 'explain'})
            for note in notesInCell:
              notesWriter.writerow([abilityName, note.get('title')])
      
      createTerrainRows.append([abilityName, terrain])

    with open(fnamePrefix + 'CreateTerrain.csv', 'w', newline='', encoding='utf-8') as currentCSV:
      currentWriter = csv.writer(currentCSV)
      currentWriter.writerow(['Ability Name', 'Terrain'])

      for row in createTerrainRows:
        currentWriter.writerow(row)
        mainWriter.writerow([row[0], 'create_terrain'])
    #endregion

    # protect against type or method
    #region
    # columns are Ability Name, Type/Method, Modifier, Class
    resistMoveClassRows = []

    # it's not worth trying to parse the description for the variations of levitate or of thick fat, so we hardcode them
    resistMoveClassRows.append(['levitate', 'ground', '0.0', 'type'])
    resistMoveClassRows.append(['soundproof', 'sound', '0.0', 'method'])
    resistMoveClassRows.append(['wonder_guard', 'other', '0.0', 'type'])
    resistMoveClassRows.append(['bulletproof', 'ball', '0.0', 'method'])
    resistMoveClassRows.append(['thick_fat', 'fire', '0.5', 'type'])
    resistMoveClassRows.append(['thick_fat', 'ice', '0.5', 'type'])
    resistMoveClassRows.append(['heatproof', 'fire', '0.5', 'type'])

    # the rows are so similar that we just combine the tables
    typeImmunityRows = bs.find(id='Variations_of_Lightning_Rod').find_next('table').find_all('tr')[2:] + bs.find(id='Variations_of_Motor_Drive').find_next('table').find_all('tr')[2:] + bs.find(id='Variations_of_Volt_Absorb').find_next('table').find_all('tr')[2:]
    for row in typeImmunityRows:
      cells = row.find_all(['td', 'th'])
      abilityName = parseName(cells[0].get_text().replace('*', ''))
      description = cells[1].get_text()
      type = parseName(re.search(r'.*-type', description).group().rstrip('type'))
      
      for cell in cells:
        if cell.find('span', {'class': 'explain'}) != None:
            notesInCell = cell.find_all('span', {'class': 'explain'})
            for note in notesInCell:
              notesWriter.writerow([abilityName, note.get('title')])
      
      resistMoveClassRows.append([abilityName, type, '0.0', 'type'])
      
    with open(fnamePrefix + 'ResistMoveClass.csv', 'w', newline='', encoding='utf-8') as currentCSV:
      currentWriter = csv.writer(currentCSV)
      currentWriter.writerow(['Ability Name', 'Resists', 'Modifier', 'Move Class'])
      
      for row in resistMoveClassRows:
        currentWriter.writerow(row)
        if row[3] == 'type':
          mainWriter.writerow([row[0], 'resist_type'])
        else:
          mainWriter.writerow([row[0], 'resist_method'])
    #endregion

    # cause status on contact
    #region
    # just hard code since there's only one table, and few abilities
    with open(fnamePrefix + 'ContactCausesStatus.csv', 'w', newline='', encoding='utf-8') as currentCSV:
      currentWriter = csv.writer(currentCSV)
      currentWriter.writerow(['Ability Name', 'Status', 'Probability'])

      currentWriter.writerow(['cute_charm', 'infatuation', '30.0'])
      mainWriter.writerow(['cute_charm', 'contact_causes_status'])
      currentWriter.writerow(['effect_spore', 'poison', '9.0'])
      currentWriter.writerow(['effect_spore', 'paralysis', '10.0'])
      currentWriter.writerow(['effect_spore', 'sleep', '11.0'])
      mainWriter.writerow(['effect_spore', 'contact_causes_status'])
      currentWriter.writerow(['flame_body', 'burn', '30.0'])
      mainWriter.writerow(['flame_body', 'contact_causes_status'])
      currentWriter.writerow(['poison_point', 'poison', '30.0'])
      mainWriter.writerow(['poison_point', 'contact_causes_status'])
      currentWriter.writerow(['static', 'paralysis', '30.0'])
      mainWriter.writerow(['static', 'contact_causes_status'])
    #endregion

    # protect against status
    #region
    # Ability Name, Status Protected Against
    protectAgainstStatusRows = []

    immunityTableRows = bs.find(id='Variations_of_Immunity').find_next('table').find_all('tr')[2:]
    for row in immunityTableRows:
      cells = row.find_all(['td', 'th'])
      abilityName = parseName(cells[0].get_text())
      if abilityName == 'oblivious':
        protectAgainstStatusRows.append(['oblivious', 'infatuation'])
        protectAgainstStatusRows.append(['oblivious', 'taunt'])
      else:
        status = parseName(cells[1].get_text())
      
      for cell in cells:
        if cell.find('span', {'class': 'explain'}) != None:
            notesInCell = cell.find_all('span', {'class': 'explain'})
            for note in notesInCell:
              notesWriter.writerow([abilityName, note.get('title')])
      
      # oblivious has already been written, but we wanted the note finder to do a pass through the row, since there are two notes in that row
      if abilityName != 'oblivious':
        protectAgainstStatusRows.append([abilityName, status])

    # entries which are easier to hard code
    protectAgainstStatusRows.append(['natural_cure', 'all'])
    protectAgainstStatusRows.append(['aroma_veil', 'infatuation'])
    protectAgainstStatusRows.append(['aroma_veil', 'disable'])
    protectAgainstStatusRows.append(['aroma_veil', 'torment'])
    protectAgainstStatusRows.append(['aroma_veil', 'encore'])
    protectAgainstStatusRows.append(['flower_veil', 'non_volatile'])
    protectAgainstStatusRows.append(['sweet_veil', 'non_volatile'])
    # natural cure heals upon switching out, so it would only affect statuses that persist after switching out
    protectAgainstStatusRows.append(['natural_cure', 'burn'])
    protectAgainstStatusRows.append(['natural_cure', 'paralysis'])
    protectAgainstStatusRows.append(['natural_cure', 'freeze'])
    protectAgainstStatusRows.append(['natural_cure', 'poison'])
    protectAgainstStatusRows.append(['natural_cure', 'sleep'])

    with open(fnamePrefix + 'ProtectsAgainstStatus.csv', 'w', newline='', encoding='utf-8') as currentCSV:
      currentWriter = csv.writer(currentCSV)
      currentWriter.writerow(['Ability Name', 'Status'])

      for row in protectAgainstStatusRows:
        currentWriter.writerow([row[0], row[1]])
        mainWriter.writerow([row[0], 'protect_against_status'])
    #endregion
    
    # finally, a few effects which we don't put in separate .csv, and which we can just hardcode

    # punish contact
    #region
    for abilityName in ['cute_charm', 'effect_spore', 'flame_body', 'poison_point', 'static', 'rough_skin', 'iron_barbs', 'gooey', 'tangling_hair']:
      mainWriter.writerow([abilityName, 'punish_contact'])
    #endregion

    # recover HP
    #region
    for abilityName in ['dry_skin', 'volt_absorb', 'water_absorb', 'ice_body', 'rain_dish']:
      mainWriter.writerow([abilityName, 'restore_hp'])
    #endregion

    # trapping abilities
    #region
    for abilityName in ['arena_trap', 'magnet_pull', 'shadow_tag']:
      mainWriter.writerow([abilityName, 'trapped'])
    #endregion
  return

def main():
  dataPath = getDataBasePath() + 'abilities/'
  abilityEffects_fnamePrefix = dataPath + 'abilities'
  abilityEffects(abilityEffects_fnamePrefix)
  return

if __name__ == '__main__':
  main()