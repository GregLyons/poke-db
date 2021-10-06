import csv
import urllib.request
from bs4 import BeautifulSoup
import re

def makeMoveEffectCSV(label, url, writer):
  req = urllib.request.Request(url, headers={'User-Agent' : "Magic Browser"}) 
  html = urllib.request.urlopen( req )
  bs = BeautifulSoup(html.read(), 'html.parser')

  # the moves are listed after an h2 containing the text 'Pages in category', and they are links whose text has the string '(move)'
  findSection = bs.find('h2', text=re.compile(r'Pages in category'))
  moves = [link.get_text().rstrip('(move)').replace(' ', '') for link in findSection.find_all_next('a') if '(move)' in link.get_text()]

  for move in moves:
    writer.writerow([label, move])

labelsAndLinks = [
  ['consecutive',
	'https://bulbapedia.bulbagarden.net/wiki/Category:Consecutively_executed_moves'],
	['counterattack',
	'https://bulbapedia.bulbagarden.net/wiki/Category:Counterattacks'],
	['createsHazard',
	'https://bulbapedia.bulbagarden.net/wiki/Category:Entry_hazard-creating_moves'],
	['removesHazard',
	'https://bulbapedia.bulbagarden.net/wiki/Category:Entry_hazard-removing_moves'],
	['changesForm',
	'https://bulbapedia.bulbagarden.net/wiki/Category:Form-changing_moves'],
	['drains',
	'https://bulbapedia.bulbagarden.net/wiki/Category:HP-draining_moves'],
	['manipualtesItems',
	'https://bulbapedia.bulbagarden.net/wiki/Category:Item-manipulating_moves'],
	['dependsOnWeight',
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
	['activatesGulpMissile',
	'https://bulbapedia.bulbagarden.net/wiki/Category:Moves_that_activate_Gulp_Missile'],
	['changesAbility',
	'https://bulbapedia.bulbagarden.net/wiki/Category:Ability-changing_moves'],
	['antiMini',
  'https://bulbapedia.bulbagarden.net/wiki/Category:Moves_that_become_stronger_against_a_Minimized_target'],
	['bypassesProtect',
	'https://bulbapedia.bulbagarden.net/wiki/Category:Moves_that_break_through_protection'],
	['callsOtherMove',
	'https://bulbapedia.bulbagarden.net/wiki/Category:Moves_that_call_other_moves'],
	['healsNonvolatile',
	'https://bulbapedia.bulbagarden.net/wiki/Category:Moves_that_can_heal_non-volatile_status_conditions'],
	['hitsSemiInvulnerable',
	'https://bulbapedia.bulbagarden.net/wiki/Category:Moves_that_can_hit_semi-invulnerable_Pok%C3%A9mon'],
	['cannotMiss',
	'https://bulbapedia.bulbagarden.net/wiki/Category:Moves_that_cannot_miss'],
	['faintsUser',
	'https://bulbapedia.bulbagarden.net/wiki/Category:Moves_that_cause_the_user_to_faint'],
	['changesPokemonType',
	'https://bulbapedia.bulbagarden.net/wiki/Category:Moves_that_change_a_Pok%C3%A9mon\'s_type'],
	['changesTerrain',
	'https://bulbapedia.bulbagarden.net/wiki/Category:Moves_that_change_terrain'],
	['changesMoveType',
	'https://bulbapedia.bulbagarden.net/wiki/Category:Moves_that_change_type'],
	['costsHP',
	'https://bulbapedia.bulbagarden.net/wiki/Category:Moves_that_cost_HP_to_use'],
	['dealsDirectDamage',
	'https://bulbapedia.bulbagarden.net/wiki/Category:Moves_that_deal_direct_damage'],
	['hasRecoil',
	'https://bulbapedia.bulbagarden.net/wiki/Category:Moves_that_have_recoil'],
	['hasVariablePower',
	'https://bulbapedia.bulbagarden.net/wiki/Category:Moves_that_have_recoil'],
	['ignoresAbilityOfTarget',
	'https://bulbapedia.bulbagarden.net/wiki/Category:Moves_that_ignore_Abilities'],
	['powersUp',
	'https://bulbapedia.bulbagarden.net/wiki/Category:Moves_that_power_up'],
	['removesTypeImmunity',
	'https://bulbapedia.bulbagarden.net/wiki/Category:Moves_that_remove_some_type_immunities'],
	['restoresHP',
	'https://bulbapedia.bulbagarden.net/wiki/Category:Moves_that_restore_HP'],
  ['restoresHP',
  'https://bulbapedia.bulbagarden.net/wiki/Category:Status_moves_that_heal_the_user_immediately'],
  ['restoresHP',
  'https://bulbapedia.bulbagarden.net/wiki/Category:HP-draining_moves'],
	['healsUserImmediately',
	'https://bulbapedia.bulbagarden.net/wiki/Category:Status_moves_that_heal_the_user_immediately'],
	['switchesOutTarget',
	'https://bulbapedia.bulbagarden.net/wiki/Category:Moves_that_switch_the_target_out'],
	['switchesOutUser',
	'https://bulbapedia.bulbagarden.net/wiki/Category:Moves_that_switch_the_user_out'],
	['thawsUser',
	'https://bulbapedia.bulbagarden.net/wiki/Category:Moves_that_thaw_out_the_user'],
  ['healsNonvolatile',
  'https://bulbapedia.bulbagarden.net/wiki/Category:Moves_that_thaw_out_the_user'],
	['dependsOnEnvironment',
	'https://bulbapedia.bulbagarden.net/wiki/Category:Moves_that_vary_with_environment'],
	['hasHighCritChance',
	'https://bulbapedia.bulbagarden.net/wiki/Category:Moves_with_a_high_critical-hit_ratio'],
	['alwaysCrits',
	'https://bulbapedia.bulbagarden.net/wiki/Category:Moves_with_a_perfect_critical_hit_chance'],
	['hasNoEffect',
	'https://bulbapedia.bulbagarden.net/wiki/Category:Moves_with_no_effect'],
	['multiHit',
	'https://bulbapedia.bulbagarden.net/wiki/Category:Multi-strike_moves'],
  ['protection',
	'https://bulbapedia.bulbagarden.net/wiki/Category:Protection_moves'],
	['createsScreen',
	'https://bulbapedia.bulbagarden.net/wiki/Category:Screen-creating_moves'],
	['removesScreen',
	'https://bulbapedia.bulbagarden.net/wiki/Category:Screen-removing_moves'],
	['changesWeather',
	'https://bulbapedia.bulbagarden.net/wiki/Category:Weather-changing_moves'],
  ['specialTypeEffectiveness',
  'https://bulbapedia.bulbagarden.net/wiki/Category:Moves_that_have_special_type_effectiveness_properties']
]

fname = 'src\data\moves\movesByEffect.csv'
csvFile = open(fname, 'w', newline='', encoding='utf-8')
writer = csv.writer(csvFile, quoting=csv.QUOTE_MINIMAL)
writer.writerow(['Effect', 'Move'])

for [label, link] in labelsAndLinks:
  makeMoveEffectCSV(label, link, writer)

csvFile.close()


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