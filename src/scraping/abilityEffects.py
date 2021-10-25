import csv
import re
from utils import openLink, getDataPath, parseName

# The table-parsing code in this function is very repetitive, but due to many of the tables being slightly different in terms of number/placement of columns, I couldn't think of a more elegant solution 
# columns are Ability Name, Effect Type
def abilityEffects(fnamePrefix):
  with open(fnamePrefix + 'ByEffect.csv', 'w', newline='', encoding='utf-8') as mainCSV, open(fnamePrefix + 'ByEffectNotes.csv', 'w', newline='', encoding='utf-8') as notesCSV:
    mainWriter = csv.writer(mainCSV)
    mainWriter.writerow(['Ability Name', 'Effect Type'])
    notesWriter = csv.writer(notesCSV)
    notesWriter.writerow(['Ability Name', 'Note'])

    bs = openLink('https://bulbapedia.bulbagarden.net/wiki/Ability_variations', 0, 10)

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

      abilityName = parseName(cells[0].get_text().replace('*',''))
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

      abilityName = parseName(cells[0].get_text().replace('*',''))
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
          type = parseName(re.search(r'.*-type', description).group().split()[-1].removesuffix('type'))
          currentWriter.writerow([abilityName, type, multiplier, 'type'])
          mainWriter.writerow([abilityName, 'boost_type'])
        else:
          if 'recoil' in description or 'effective' in description or 'contact' in description or '60' in description or 'same' in description:
            currentWriter.writerow([abilityName, 'other', multiplier, 'other'])
            mainWriter.writerow([abilityName, 'boost_other'])
          else:
            method = parseName(description.split()[-2])

            # change method name for consistency
            method = method.replace('punching', 'punch').replace('biting', 'bite').replace('sound_based', 'sound')

            currentWriter.writerow([abilityName, method, multiplier, 'method'])
            mainWriter.writerow([abilityName, 'boost_usage_method'])
      
      currentWriter.writerow(['flash_fire', 'fire', '1.5', 'type'])
      mainWriter.writerow(['flash_fire', 'boost_type'])

      # exceptions
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
      abilityName = parseName(cells[0].get_text().replace('*',''))
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
        mainWriter.writerow([row[0], 'creates_weather'])
    #endregion
    
    # create terrain
    #region
    # columns are Ability Name, Terrain
    createTerrainRows = []
    electricSurgeTableRows = bs.find(id='Variations_of_Electric_Surge').find_next('table').find_all('tr')[2:]
    for row in electricSurgeTableRows:
      cells = row.find_all(['td', 'th'])
      abilityName = parseName(cells[0].get_text().replace('*',''))
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
        mainWriter.writerow([row[0], 'creates_terrain'])
    #endregion

    # protect against type or method
    #region
    # columns are Ability Name, Type/Method, Multiplier, Class
    resistMoveClassRows = []

    # it's not worth trying to parse the description for the variations of levitate or of thick fat, so we hardcode them
    resistMoveClassRows.append(['levitate', 'ground', '0.0', 'type'])
    resistMoveClassRows.append(['soundproof', 'sound', '0.0', 'method'])
    resistMoveClassRows.append(['wonder_guard', 'other', '0.0', 'type'])
    resistMoveClassRows.append(['bulletproof', 'ball', '0.0', 'method'])
    resistMoveClassRows.append(['flash_fire', 'fire', '0.0', 'type'])
    resistMoveClassRows.append(['thick_fat', 'fire', '0.5', 'type'])
    resistMoveClassRows.append(['thick_fat', 'ice', '0.5', 'type'])
    resistMoveClassRows.append(['heatproof', 'fire', '0.5', 'type'])
    # also include abilities which INCREASE damage from elemental types
    resistMoveClassRows.append(['dry_skin', 'fire', '1.25', 'type'])
    resistMoveClassRows.append(['fluffy', 'fire', '2.0', 'type'])


    # the rows are so similar that we just combine the tables
    typeImmunityRows = bs.find(id='Variations_of_Lightning_Rod').find_next('table').find_all('tr')[2:] + bs.find(id='Variations_of_Motor_Drive').find_next('table').find_all('tr')[2:] + bs.find(id='Variations_of_Volt_Absorb').find_next('table').find_all('tr')[2:]
    for row in typeImmunityRows:
      cells = row.find_all(['td', 'th'])
      abilityName = parseName(cells[0].get_text().replace('*', ''))
      description = cells[1].get_text()
      type = parseName(re.search(r'.*-type', description).group().removesuffix('type'))
      
      for cell in cells:
        if cell.find('span', {'class': 'explain'}) != None:
            notesInCell = cell.find_all('span', {'class': 'explain'})
            for note in notesInCell:
              notesWriter.writerow([abilityName, note.get('title')])
      
      resistMoveClassRows.append([abilityName, type, '0.0', 'type'])
      
    with open(fnamePrefix + 'ResistMoveClass.csv', 'w', newline='', encoding='utf-8') as currentCSV:
      currentWriter = csv.writer(currentCSV)
      currentWriter.writerow(['Ability Name', 'Resists', 'Multiplier', 'Move Class'])
      
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
      abilityName = parseName(cells[0].get_text().replace('*',''))
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
    protectAgainstStatusRows.append(['immunity', 'bad_poison'])
    protectAgainstStatusRows.append(['pastel_veil', 'poison'])
    protectAgainstStatusRows.append(['pastel_veil', 'bad_poison'])
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
    protectAgainstStatusRows.append(['natural_cure', 'bad_poison'])
    protectAgainstStatusRows.append(['natural_cure', 'sleep'])

    with open(fnamePrefix + 'ProtectAgainstStatus.csv', 'w', newline='', encoding='utf-8') as currentCSV:
      currentWriter = csv.writer(currentCSV)
      currentWriter.writerow(['Ability Name', 'Status Name'])

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
      mainWriter.writerow([abilityName, 'restores_hp'])
    #endregion

    # trapping abilities
    #region
    for abilityName in ['arena_trap', 'magnet_pull', 'shadow_tag']:
      mainWriter.writerow([abilityName, 'trapped'])
    #endregion

    # item-maniuplating abilities
    #region
    bs = openLink('https://bulbapedia.bulbagarden.net/wiki/Held_item', 0, 10)
    dataRows = bs.find(id='Abilities').find_next('table').find('table').find_all('tr')[1:]
    for row in dataRows: 
      cells = row.find_all('td')
      abilityName = parseName(cells[0].get_text())
      mainWriter.writerow([abilityName, 'manipulates_item'])
    #endregion

    # other ability effects not in a table
    #region
    for exception in [
      ["changes_form", ["forecast", "hunger_switch", "imposter", "power_construct", "schooling", "shields_down", "stance_change", "zen_mode", "battle_bond", "disguise", "ice_face"]],
      ["changes_pokemon_type", ["protean", "rks_system", "color_change", "libero", "mimicry", "multitype"]],
      ["changes_move_type", ["aerilate", 'normalize', 'galvanize', 'pixilate', 'refrigerate', 'liquid_voice']],
      ["ignores_ability", ["teravolt", "turboblaze", "mold_breaker"]],
      ["changes_ability", ["receiver"]],
      ["suppresses_ability", ["neutralizing_gas"]],
      ["move_first_in_priority", ["quick_draw"]],
      ["other_move_enhancement", ["sheer_force", "adaptability", "analytic", "battery", "flare_boost", "aerilate", 'normalize', 'galvanize', 'pixilate', "refrigerate", 'reckless', 'technician', 'neuroforce', 'tough_claws', 'tinted_lens']],
      ["bypasses_protect", ["unseen_fist"]],
      ["switches_out_user", ["wimp_out", "emergency_exit"]],
      ["ignores_weather", ["air_lock", "cloud_nine"]],
      ["restores_hp", ["cheek_pouch", "ice_body", "rain_dish", "poison_heal", "regenerator", 'dry_skin']],
      ["resets_stats", ["curious_medicine"]], 
      ['affects_weight', ['heavy_metal', 'light_metal']],
      ['moves_last_in_priority', ['stall']],
      ['ignores_contact', ['long_reach']],
      ['cannot_miss', ['no_guard']],
      ["costs_hp", ['solar_power', 'disguise', 'dry_skin']],
      ['prevents_crit', ['battle_armor', 'shell_armor']],
      ['prevents_stat_drop', ['clear_body', 'white_smoke', "full_metal_body"]],
      ['other_move_resistance', ['wonder_guard', 'filter', 'solid_rock', 'prism_armor', 'multiscale', 'shadow_shield']],
      ['adds_priority', ['prankster', 'gale_wings', 'triage']],
      ['protect_against_priority', ['dazzling', 'queenly_majesty']],
    ]:
      effect, abilities = exception
      for abilityName in abilities:
        mainWriter.writerow([abilityName, effect])
    #endregion

    # modify stat
    # we use a different page, which has a table that lists all the changes more concisely
    #region
    
    with open(fnamePrefix + 'ModifyStat.csv', 'w', newline='', encoding='utf-8') as currentCSV:
      currentWriter = csv.writer(currentCSV)
      currentWriter.writerow(['Ability Name', 'Stat Name', 'Modifier', 'Recipient'])

      bs = openLink('https://bulbapedia.bulbagarden.net/wiki/Stat', 0, 10)
      dataRows = bs.find(id='In-battle_modification').find_next('table').find('tr').find_next_siblings('tr')[1:]
      
      for row in dataRows:
        statName = parseName(row.find('th').get_text())
        cells = row.find('th').find_next_siblings('td')
        
        # the table data is returned such that the stage modifiers and ability names are glued together. 
        # The list comprehension separates sequences like 'asdFgh' into 'asd  Fgh'. 
        # Then, we join the list into a string. 
        # Then, we match the ability names with spaces. e.g. 'Beast BoostBerserk' is sent to 'Beast   Boost  Berserk', where the ability name has 3 spaces between its words, and separate abilities have 2 spaces between them; If we replace the instances of 3 spaces with 1 space, then distinct abilities will have 2 spaces between them, and the ability names will be correctly formatted
        # Then, we replace the stage modifiers and 'other' with numeric codes
        # Lastly, to account for abilities with hyphens, we use a replace() to glue them back together
        boosters = ''.join(['  ' + ch if (ch.isupper() or ch.isnumeric()) else ch for ch in cells[2].get_text().replace('*', '').replace('≥', '')]).replace('   ', ' ').replace('1 stage', '1').replace('2 stages', '2').replace('3 stages', '3').replace('Other', '9').replace('-  ', '-')
        reducers = ''.join(['  ' + ch if (ch.isupper() or ch.isnumeric()) else ch for ch in cells[-1].get_text().replace('*', '').replace('≥', '')]).replace('   ', ' ').replace('1 stage', '1').replace('2 stages', '2').replace('3 stages', '3').replace('Other', '9').replace('-  ', '-')
        
       

        # split up the boosters and reducers according to stage/modifier
        oneStageBoosters = re.search(r'1 ([A-Za-z\s-]*) [\d]', boosters)
        twoStageBoosters = re.search(r'2 ([A-Za-z\s-]*) [\d]', boosters)
        moreStageBoosters = re.search(r'3 ([A-Za-z\s-]*) [\d]', boosters)
        otherBoosters = re.search(r'9 ([A-Za-z\s-]*)', boosters)
        oneStageReducers = re.search(r'1 ([A-Za-z\s-]*) [\d]', reducers)
        twoStageReducers = re.search(r'2 ([A-Za-z\s-]*) [\d]', reducers)
        moreStageReducers = re.search(r'3 ([A-Za-z\s-]*) [\d]', reducers)
        otherReducers = re.search(r'9 ([A-Za-z\s-]*)', reducers)
        if oneStageBoosters != None:
          oneStageBoosters = oneStageBoosters.group(1).strip().split('  ')
        if twoStageBoosters != None:
          twoStageBoosters = twoStageBoosters.group(1).strip().split('  ')
        if moreStageBoosters != None:
          moreStageBoosters = moreStageBoosters.group(1).strip().split('  ')
        if otherBoosters != None:
          otherBoosters = otherBoosters.group(1).strip().split('  ')
        if oneStageReducers != None:
          oneStageReducers = oneStageReducers.group(1).strip().split('  ')
        if twoStageReducers != None:
          twoStageReducers = twoStageReducers.group(1).strip().split('  ')
        if moreStageReducers != None:
          moreStageReducers = moreStageReducers.group(1).strip().split('  ')
        if otherReducers != None:
          otherReducers = otherReducers.group(1).strip().split('  ')

        modifiers = [['1', oneStageBoosters], ['2', twoStageBoosters], ['more+', moreStageBoosters], ['other+', otherBoosters], ['-1', oneStageReducers], ['-2', twoStageReducers], ['more-', moreStageReducers], ['other-', otherReducers]]

        # one- and two-stage modifiers
        for modifier in [modifier for modifier in modifiers if modifier[0][-1].isnumeric() and modifier[1] != None]:
          stage, abilities = modifier
          for abilityName in abilities:
            recipient = 'user'
            abilityName = parseName(abilityName)
            if '-' in stage:
              # minus sign already in stage, so no need to add anything
              sign = '' 
              if abilityName in ['intimidate', 'gulp_missile']:
                recipient = 'all_foes'
            else:
              # indicates stage change rather than multiplier
              sign = '+'

            currentWriter.writerow([abilityName, statName, sign + stage, recipient])
            mainWriter.writerow([abilityName, 'modify_stat'])

        # more-stage modifiers
        for modifier in [modifier for modifier in modifiers if modifier[1] != None and 'more' in modifier[0]]:
          abilities = modifier[1]
          for abilityName in abilities:
            abilityName = parseName(abilityName)
            if abilityName == 'anger_point':
              sign = '+'
              stage = '12'
              recipient = 'user'
            elif abilityName == 'steam_engine':
              sign = '+'
              stage = '6'
              recipient = 'user'
            else:
              print(abilityName, 'not handled')

            currentWriter.writerow([abilityName, statName, sign + stage, recipient])
            mainWriter.writerow([abilityName, 'modify_stat'])

        # other modifiers (i.e. multipliers)
        for modifier in [modifier for modifier in modifiers if modifier[1] != None and 'other' in modifier[0]]:
          abilities = modifier[1]
          for abilityName in abilities:
            abilityName = parseName(abilityName)
            recipient = 'user'
            if abilityName in ['defeatist', 'slow_start']:
              multiplier = 0.5
            elif abilityName in ['victory_star']:
              multiplier = 1.1
            elif abilityName in ['sand_veil', 'snow_cloak']:
              multiplier = 1.25
            elif abilityName in ['battery', 'compound_eyes']:
              multiplier = 1.3
            elif abilityName in ['flower_gift', 'gorilla_tactics', 'guts','grass_pelt', 'marvel_scale', 'plus', 'minus', 'solar_power', 'quick_feet']:
              multiplier = 1.5
            elif abilityName in ['huge_power', 'pure_power', 'fur_coat', 'chlorophyll', 'sand_rush', 'swift_swim', 'unburden', 'slush_rush', 'surge_surfer', 'tangled_feet']:
              multiplier = 2.0
            elif abilityName == 'hustle':
              if statName == 'attack':
                multiplier = 0.5
              # accuracy
              else:
                multiplier = 0.8
            # sets accuracy of status moves against Pokemon to 50%--too compliated to add to .csv, and it doesn't even affect all moves
            elif abilityName == 'wonder_skin':
              continue
            else:
              print('Other', statName, parseName(abilityName))

            currentWriter.writerow([abilityName, statName, multiplier, recipient])
            mainWriter.writerow([abilityName, 'modify_stat'])
      
      # exceptions
      currentWriter.writerow(["flare_boost", "special_attack", 1.5, "user"])
      mainWriter.writerow([abilityName, 'modify_stat'])
      currentWriter.writerow(["ice_scales", "special_defense", 0.5, "user"])
      mainWriter.writerow([abilityName, 'modify_stat'])
      
      # currentWriter.writerow(['Ability Name', 'Stat', 'Modifier'])


        

        


    #endregion
  return

def main():
  dataPath = getDataPath() + 'abilities/'
  abilityEffects_fnamePrefix = dataPath + 'abilities'
  abilityEffects(abilityEffects_fnamePrefix)
  return

if __name__ == '__main__':
  main()