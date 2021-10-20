from utils import effectList

def makeEffectDict():
  effectDict = {
    "creates_hazard": 2,
    "removes_hazard": 2,
    "creates_terrain": 6,
    "removes_terrain": 6,
    "creates_screen": 1,
    "removes_screen": 1,
    "creates_weather": 2,
    "high_crit_chance": 1,
    "cannot_crit": 2,
    "always_crits": 5,
    "bypasses_protect": 2,
    "protection": 2,
    "thaws_user": 2,
    "heals_nonvolatile": 2,
    "restores_hp": 1,
    "heals_user_immediately": 1,
    "restores_pp": 2,
    "recoil": 1,
    "costs_hp": 1,
    "can_crash": 1,
    "changes_ability": 3,
    "ignores_ability": 4,
    "suppresses_ability": 4,
    "changes_pokemon_type": 1,
    "changes_move_type": 2,
    "changes_damage_category": 7,
    "removes_type_immunity": 2,
    "special_type_effectiveness": 6,
    "switches_out_target": 2,
    "switches_out_user": 2,
    "hits_semi_invulnerable": 1,
    "cannot_miss": 1,
    "faints_user": 1,
    "variable_power": 2,
    "deals_direct_damage": 1,
    "powers_up": 2,
    "consecutive": 1,
    "counterattack": 1,
    "depends_on_weight": 3,
    "affects_weight": 5,
    "calls_other_move": 1,
    "depends_on_environment": 3,
    "multi_hit": 1,
    "ohko": 1,
    "changes_form": 5,
    "drains": 1,
    "manipulates_items": 2,
    "activates_gulp_missile": 8,
    "punishes_contact": 3,
    "extends_duration": 4,
    "other_move_enhancement": 1,
    "move_last_in_priority": 4,
    "move_first_in_priority": 2,
    "ignores_hazards": 8,
    "ignores_contact": 7,
    "ignores_weather": 6,
    "anti_mini": 2,
    "resets_stats": 1
  }

  # make sure all effects are accounted for
  for effect in effectList():
    if effect not in effectDict:
      print(effect, 'not in effectDict')

  # make sure no typos
  for key in effectDict.keys():
    if key not in effectList():
      print(key, 'not in effectList')

  
  return effectDict

def main():
  makeEffectDict()

  return

if __name__ == '__main__':
  main()