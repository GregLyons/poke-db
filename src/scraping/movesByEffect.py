import os
import csv
from utils import openBulbapediaLink, removeShadowMoves, getDataBasePath, parseName
import re

# columns are Effect Name, Move Name
def makeEffectCSV(label, url, writer):
  bs = openBulbapediaLink(url, 0, 10)
  findSection = bs.find('h2', text=re.compile(r'Pages in category'))
  moves = [link.get_text().rstrip('(move)').strip() for link in findSection.find_all_next('a') if '(move)' in link.get_text()]

  # the moves are listed after an h2 containing the text 'Pages in category', and they are links whose text has the string '(move)'

  for move in moves:
    writer.writerow([parseName(label), parseName(move)])

def main():
  labelsAndLinks = [
    ['consecutive',
    'https://bulbapedia.bulbagarden.net/wiki/Category:Consecutively_executed_moves'],
    ['counterattack',
    'https://bulbapedia.bulbagarden.net/wiki/Category:Counterattacks'],
    ['creates-hazard',
    'https://bulbapedia.bulbagarden.net/wiki/Category:Entry_hazard-creating_moves'],
    ['removes-hazard',
    'https://bulbapedia.bulbagarden.net/wiki/Category:Entry_hazard-removing_moves'],
    ['changes-form',
    'https://bulbapedia.bulbagarden.net/wiki/Category:Form-changing_moves'],
    ['drains',
    'https://bulbapedia.bulbagarden.net/wiki/Category:HP-draining_moves'],
    ['manipualtes-items',
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
    ['mouth',
    'https://bulbapedia.bulbagarden.net/wiki/Category:Moves_that_require_use_of_mouth'],
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
    ['changes-terrain',
    'https://bulbapedia.bulbagarden.net/wiki/Category:Moves_that_change_terrain'],
    ['changes-move-type',
    'https://bulbapedia.bulbagarden.net/wiki/Category:Moves_that_change_type'],
    ['costsHP',
    'https://bulbapedia.bulbagarden.net/wiki/Category:Moves_that_cost_HP_to_use'],
    ['deals-direct-damage',
    'https://bulbapedia.bulbagarden.net/wiki/Category:Moves_that_deal_direct_damage'],
    ['recoil',
    'https://bulbapedia.bulbagarden.net/wiki/Category:Moves_that_have_recoil'],
    ['variable-power',
    'https://bulbapedia.bulbagarden.net/wiki/Category:Moves_that_have_variable_power'],
    ['ignores-ability-of-target',
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
    ['heals-userimmediately',
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
    ['protection',
    'https://bulbapedia.bulbagarden.net/wiki/Category:Protection_moves'],
    ['creates-screen',
    'https://bulbapedia.bulbagarden.net/wiki/Category:Screen-creating_moves'],
    ['removes-screen',
    'https://bulbapedia.bulbagarden.net/wiki/Category:Screen-removing_moves'],
    ['changes-weather',
    'https://bulbapedia.bulbagarden.net/wiki/Category:Weather-changing_moves'],
    ['special-type-effectiveness',
    'https://bulbapedia.bulbagarden.net/wiki/Category:Moves_that_have_special_type_effectiveness_properties']
  ]

  dataPath = getDataBasePath() + 'moves\\'

  fname = dataPath + 'movesByEffectWithShadowMoves.csv'
  csvFile = open(fname, 'w', newline='', encoding='utf-8')
  writer = csv.writer(csvFile, quoting=csv.QUOTE_MINIMAL)
  writer.writerow(['Effect Name', 'Move Name'])

  # 
  for [label, link] in labelsAndLinks:
    makeEffectCSV(label, link, writer)

  csvFile.close()

  removeShadowMoves(fname, 'Effect Name')
  os.remove(fname)

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