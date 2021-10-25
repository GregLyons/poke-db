from utils import effectList

def makeEffectDict():
  effectDict = {
    # spikes
    "creates_hazard": 2,
    # rapid spin
    "removes_hazard": 2,
    # grassy terrain
    "creates_terrain": 6,
    # splintered stormshards
    "removes_terrain": 7,
    # reflect
    "creates_screen": 1,
    # haze removes screens in Gen 1
    "removes_screen": 1,
    # rain dance
    "creates_weather": 2,
    # karate chop
    "high_crit_chance": 1,
    # flail
    "cannot_crit": 2,
    # storm throw
    "always_crits": 5,
    # feint
    "bypasses_protect": 4,
    # mechanic introduced in gen 2; see Freeze page on Bulbapedia
    "thaws_user": 2,
    # rest
    "heals_nonvolatile": 1,
    # recover
    "restores_hp": 1,
    # recover
    "heals_user_immediately": 1,
    # MysteryBerry
    "restores_pp": 2,
    # doubleedge
    "recoil": 1,
    # substitute
    "costs_hp": 1,
    # high jump kick
    "can_crash": 1,
    # role play
    "changes_ability": 3,
    # mold breaker
    "ignores_ability": 4,
    # gastro acid
    "suppresses_ability": 4,
    # conversion
    "changes_pokemon_type": 1,
    # electrify
    "changes_move_type": 6,
    # photon geyser
    "changes_damage_category": 7,
    # foresight
    "removes_type_immunity": 2,
    # freeze dry
    "special_type_effectiveness": 6,
    # roar
    "switches_out_target": 2,
    # baton pass
    "switches_out_user": 2,
    # bide
    "hits_semi_invulnerable": 1,
    # bide
    "cannot_miss": 1,
    # explosion
    "faints_user": 1,
    # hidden power
    "variable_power": 2,
    # sonic boom
    "deals_direct_damage": 1,
    # roll-out
    "powers_up": 2,
    # thrash
    "consecutive": 1,
    # bide
    "counterattack": 1,
    # low kick does not depend on weight in gens 1 or 2
    "depends_on_weight": 3,
    # automotize
    "affects_weight": 5,
    # metronome
    "calls_other_move": 1,
    # secret power
    "depends_on_environment": 3,
    # pin missile
    "multi_hit": 1,
    # fissure
    "ohko": 1,
    # transform doesn't count; secret sword
    "changes_form": 5,
    # absorb
    "drains": 1,
    # thief
    "manipulates_items": 2,
    # cramorant
    "activates_gulp_missile": 8,
    # static
    "punishes_contact": 3,
    # light clay
    "extends_duration": 4,
    # adaptability; refers to abilities which power up moves via a mechanic other than move type or usage method, e.g. adaptability boosts STAB moves
    "other_move_enhancement": 1,
    # lagging tail; refers to priority bracket
    "move_last_in_priority": 4,
    # quick claw
    "move_first_in_priority": 2,
    # heavy duty boots
    "ignores_hazards": 8,
    # long reach
    "ignores_contact": 7,
    # air lock
    "ignores_weather": 6,
    # stomp started dealing double damage to minimized targets in gen 2
    "anti_mini": 2,
    # haze
    "resets_stats": 1,
    # battle armor
    "prevents_crit": 3,
    # mist
    "prevents_stat_drop": 1,
    # prankster
    "adds_priority": 5,
    # after you; e.g. causes target to always use their move next, regardless of priority
    # contrast with instruct or dancer, which causes target to use a previously used move; the target still executes their own turn at the usual time
    "other_move_order_change": 5,
    # quick guard
    "protects_against_priority": 5,
    # wonder guard; refers to abilities which resist moves beyond their move type or class, e.g. wonder guard resists all non-super effective moves
    "other_move_resistance": 3,
    # hidden power
    "type_varies": 2,
    # splash
    "no_effect": 1,
    # psyshock (target's defense rather than special defense); body press (user's defense rather than attack)
    "uses_different_stat": 5,
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
  effectDict = makeEffectDict()

  return effectDict

if __name__ == '__main__':
  main()