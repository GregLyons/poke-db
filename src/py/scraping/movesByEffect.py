import csv
from utils import openLink, getCSVDataPath, parseName, isShadowMove
import re

# columns are Effect Name, Move Name
def makeEffectCSV(label, url, writer):
  bs = openLink(url, 0, 10)
  findSection = bs.find('h2', text=re.compile(r'Pages in category'))
  moves = [link.get_text().rstrip('(move)').strip() for link in findSection.find_all_next('a') if '(move)' in link.get_text()]

  # the moves are listed after an h2 containing the text 'Pages in category', and they are links whose text has the string '(move)'

  for move in moves:
    moveName = parseName(move)

    # ignore shadow moves
    if isShadowMove(moveName):
      continue

    effect = parseName(label)


    writer.writerow([effect, parseName(move)])

# add Z-move data to .csv
def addZMoves(fname):
  # create dictionary of base moves--z-move's add an additional effect onto the base move's effect
  with open(fname, 'r', encoding='utf-8') as originalCSV:
    reader = csv.DictReader(originalCSV)

    moveEffectDict = {}

    for row in reader:
      effectName, moveName = row["Effect Name"], row["Move Name"]

      if moveName not in moveEffectDict:
        moveEffectDict[moveName] = []
      
      if effectName != 'no_effect':
        moveEffectDict[moveName].append(effectName)


  with open(fname, 'a', newline='', encoding='utf-8') as newCSV:
    writer = csv.writer(newCSV)
    bs = openLink('https://bulbapedia.bulbagarden.net/wiki/Z-Move', 0, 10)
    dataRows = bs.find(id='Z-Power_effects_of_status_moves').find_next('table').find('table').find_all('tr')[1:]

    for row in dataRows:
      cells = row.find_all('td')
      baseMoveName = parseName(cells[0].get_text())
      effect = cells[2].get_text().rstrip('\n')

      # the two effects which Z-moves add on are restoring HP, or resetting stats (other consequences, such as stat modifications/statuses, are added elsewhere)
      # move resets stats
      if 'Reset' in effect:
        writer.writerow(['resets_stats', 'z_' + baseMoveName])
      # Z-curse restores HP if user is a Ghost-type
      elif 'Restores' in effect or baseMoveName == 'curse':
        writer.writerow(['restores_hp', 'z_' + baseMoveName])
      
      # add effects for base moves
      if baseMoveName in moveEffectDict:
        for effect in moveEffectDict[baseMoveName]:
          writer.writerow([effect, 'z_' + baseMoveName])

  return

def main():
  labelsAndLinks = [
    ['consecutive',
    'https://bulbapedia.bulbagarden.net/wiki/Category:Consecutively_executed_moves'],
    ['counterattack',
    'https://bulbapedia.bulbagarden.net/wiki/Category:Counterattacks'],
    ['changes-form',
    'https://bulbapedia.bulbagarden.net/wiki/Category:Form-changing_moves'],
    ['drains',
    'https://bulbapedia.bulbagarden.net/wiki/Category:HP-draining_moves'],
    ['manipulates-item',
    'https://bulbapedia.bulbagarden.net/wiki/Category:Item-manipulating_moves'],
    ['depends-on-weight',
    'https://bulbapedia.bulbagarden.net/wiki/Category:Moves_affected_by_weight'],
    ['pulse',
    'https://bulbapedia.bulbagarden.net/wiki/Category:Aura_and_pulse_moves'],
    ['ball',
    'https://bulbapedia.bulbagarden.net/wiki/Category:Ball_and_bomb_moves'],
    ['bite',
    'https://bulbapedia.bulbagarden.net/wiki/Category:Biting_moves'],
    ['dance',
    'https://bulbapedia.bulbagarden.net/wiki/Category:Dance_moves'],
    ['explosive',
    'https://bulbapedia.bulbagarden.net/wiki/Category:Explosive_moves'],
    ['powder',
    'https://bulbapedia.bulbagarden.net/wiki/Category:Powder_and_spore_moves'],
    ['punch',
    'https://bulbapedia.bulbagarden.net/wiki/Category:Punching_moves'],
    ['sound',
    'https://bulbapedia.bulbagarden.net/wiki/Category:Sound-based_moves'],
    ['activates-gulp-missile',
    'https://bulbapedia.bulbagarden.net/wiki/Category:Moves_that_activate_Gulp_Missile'],
    ['changes-ability',
    'https://bulbapedia.bulbagarden.net/wiki/Category:Ability-changing_moves'],
    ['anti-mini',
    'https://bulbapedia.bulbagarden.net/wiki/Category:Moves_that_become_stronger_against_a_Minimized_target'],
    ['bypasses-protect',
    'https://bulbapedia.bulbagarden.net/wiki/Category:Moves_that_break_through_protection'],
    ['calls-other-move',
    'https://bulbapedia.bulbagarden.net/wiki/Category:Moves_that_call_other_moves'],
    ['heals-nonvolatile',
    'https://bulbapedia.bulbagarden.net/wiki/Category:Moves_that_can_heal_non-volatile_status_conditions'],
    ['hits-semi-invulnerable',
    'https://bulbapedia.bulbagarden.net/wiki/Category:Moves_that_can_hit_semi-invulnerable_Pok%C3%A9mon'],
    ['cannot-miss',
    'https://bulbapedia.bulbagarden.net/wiki/Category:Moves_that_cannot_miss'],
    ['faints-user',
    'https://bulbapedia.bulbagarden.net/wiki/Category:Moves_that_cause_the_user_to_faint'],
    ['changes-pokemon-type',
    'https://bulbapedia.bulbagarden.net/wiki/Category:Moves_that_change_a_Pok%C3%A9mon\'s_type'],
    ['type-varies',
    'https://bulbapedia.bulbagarden.net/wiki/Category:Moves_that_change_type'],
    ['costsHP',
    'https://bulbapedia.bulbagarden.net/wiki/Category:Moves_that_cost_HP_to_use'],
    ['deals-direct-damage',
    'https://bulbapedia.bulbagarden.net/wiki/Category:Moves_that_deal_direct_damage'],
    ['recoil',
    'https://bulbapedia.bulbagarden.net/wiki/Category:Moves_that_have_recoil'],
    ['variable-power',
    'https://bulbapedia.bulbagarden.net/wiki/Category:Moves_that_have_variable_power'],
    ['ignores-ability',
    'https://bulbapedia.bulbagarden.net/wiki/Category:Moves_that_ignore_Abilities'],
    ['powers-up',
    'https://bulbapedia.bulbagarden.net/wiki/Category:Moves_that_power_up'],
    ['removes-type-immunity',
    'https://bulbapedia.bulbagarden.net/wiki/Category:Moves_that_remove_some_type_immunities'],
    ['restores-hp',
    'https://bulbapedia.bulbagarden.net/wiki/Category:Moves_that_restore_HP'],
    ['restores-hp',
    'https://bulbapedia.bulbagarden.net/wiki/Category:Status_moves_that_heal_the_user_immediately'],
    ['restores-hp',
    'https://bulbapedia.bulbagarden.net/wiki/Category:HP-draining_moves'],
    ['heals-user-immediately',
    'https://bulbapedia.bulbagarden.net/wiki/Category:Status_moves_that_heal_the_user_immediately'],
    ['switches-out-target',
    'https://bulbapedia.bulbagarden.net/wiki/Category:Moves_that_switch_the_target_out'],
    ['switches-out-user',
    'https://bulbapedia.bulbagarden.net/wiki/Category:Moves_that_switch_the_user_out'],
    ['thaws-user',
    'https://bulbapedia.bulbagarden.net/wiki/Category:Moves_that_thaw_out_the_user'],
    ['heals-nonvolatile',
    'https://bulbapedia.bulbagarden.net/wiki/Category:Moves_that_thaw_out_the_user'],
    ['depends-on-environment',
    'https://bulbapedia.bulbagarden.net/wiki/Category:Moves_that_vary_with_environment'],
    ['high-crit-chance',
    'https://bulbapedia.bulbagarden.net/wiki/Category:Moves_with_a_high_critical-hit_ratio'],
    ['always-crits',
    'https://bulbapedia.bulbagarden.net/wiki/Category:Moves_with_a_perfect_critical_hit_chance'],
    ['no-effect',
    'https://bulbapedia.bulbagarden.net/wiki/Category:Moves_with_no_effect'],
    ['multi-hit',
    'https://bulbapedia.bulbagarden.net/wiki/Category:Multi-strike_moves'],
    ['special-type-effectiveness',
    'https://bulbapedia.bulbagarden.net/wiki/Category:Moves_that_have_special_type_effectiveness_properties'],
    ['changes_move_type',
    'https://bulbapedia.bulbagarden.net/wiki/Category:Effects_that_can_modify_move_types']
  ]

  dataPath = getCSVDataPath() + 'moves\\'

  fname = dataPath + 'movesByEffect.csv'
  csvFile = open(fname, 'w', newline='', encoding='utf-8')
  writer = csv.writer(csvFile, quoting=csv.QUOTE_MINIMAL)
  writer.writerow(['Effect Name', 'Move Name'])

  # make main .csv 
  for [label, link] in labelsAndLinks:
    makeEffectCSV(label, link, writer)
  
  # exceptions
  for exception in [
    ['restores_pp', ['lunar_dance']],
    ['protects_against_priority', ['quick_guard']],
    ['prevents_stat_drop', ['mist']],
    ['resets_stats', ['clear_smog', 'haze']],
    ['prevents_crit', ['lucky_chant']],
    ['other_move_enhancement', ['me_first']],
    ['other_move_order_change', ['quash', 'after_you']]
  ]:
    effect, moves = exception
    for moveName in moves:
      writer.writerow([effect, moveName])

  csvFile.close()

  # add Z-move data to .csv
  fname = dataPath + 'movesByEffect.csv'
  addZMoves(fname)

  # the following exceptions are handled in moves.py when generating the .json
  #region
    # ['modifyStat',
    # 'https://bulbapedia.bulbagarden.net/wiki/Category:Moves_by_stat_modification']


      
    # SuppressAbility
    # 	Core Enforcer
    # 	Gastro Acid

    # 	SetDamage
    # 	Dragon Rage
    # 	Sonic Boom

    # 	UseDifferentStat
    # 	Body Press
    # 	Psyshock
    # 	Psystrike
    # 	Secret Sword


    # 	Crash
    # 	High Jump Kick
    # 	Jump Kick
      
    # ChangeDamageCategory
    # 	Light That Burns the Sky
    # 	Photon Geyser
    # 	Shell Side Arm
    
    # Powers up
    #   Dig

    # antiMini
    # Astonish


    # ['cannotCrit',
    # 'https://bulbapedia.bulbagarden.net/wiki/Critical_hit'],
  #/region



if __name__ == '__main__':
  main()