from utils import effectList

def makeEffectDict():
  effectsAndData = {
    # karate chop
    "high_crit_chance": [1, 'crit'],
    # flail
    "cannot_crit": [2, 'crit'],
    # storm throw
    "always_crits": [5, 'crit'],
    # feint
    "bypasses_protect": [4, 'misc'], 
    # rest
    "heals_nonvolatile": [1, 'restore'],
    # recover
    "restores_hp": [1, 'restore'],
    # MysteryBerry
    "restores_pp": [2, 'restore'],
    # doubleedge
    "recoil": [1, 'cost'],
    # substitute
    "costs_hp": [1, 'cost'],
    # high jump kick
    "can_crash": [1, 'cost'],
    # role play
    "changes_ability": [3, 'ability'],
    # mold breaker
    "ignores_ability": [4, 'ability'],
    # gastro acid
    "suppresses_ability": [4, 'ability'],
    # conversion
    "changes_pokemon_type": [1, 'type'],
    # normalize
    "changes_move_type": [4, 'type'],
    # photon geyser
    "changes_damage_category": [7, 'stat'],
    # foresight
    "removes_type_immunity": [2, 'type'],
    # freeze dry
    "special_type_effectiveness": [6, 'type'],
    # roar
    "switches_out_target": [2, 'switch'],
    # baton pass
    "switches_out_user": [2, 'switch'],
    # bide
    "hits_semi_invulnerable": [1, 'accuracy'],
    # bide
    "cannot_miss": [1, 'accuracy'],
    # explosion
    "faints_user": [1, 'misc'],
    # hidden power
    "variable_power": [2, 'power'],
    # sonic boom
    "deals_direct_damage": [1, 'power'],
    # roll-out
    "powers_up": [2, 'power'],
    # thrash
    "consecutive": [1, 'power'],
    # bide
    "counterattack": [1, 'power'],
    # low kick does not depend on weight in gens 1 or 2
    "depends_on_weight": [3, 'size'],
    # automotize
    "affects_weight": [5, 'size'],
    # metronome
    "calls_other_move": [1, 'size'],
    # secret power
    "depends_on_environment": [3, 'misc'],
    # pin missile
    "multi_hit": [1, 'misc'],
    # fissure
    "ohko": [1, 'misc'],
    # transform doesn't count; forecast
    "changes_form": [3, 'misc'],
    # absorb
    "drains": [1, 'restore'],
    # thief
    "manipulates_item": [2, 'misc'],
    # cramorant
    "activates_gulp_missile": [8, 'misc'],
    # static
    "punishes_contact": [3, 'contact'],
    # light clay
    "extends_duration": [4, 'misc'],
    # adaptability; refers to abilities which power up moves via a mechanic other than move type or usage method, e.g. adaptability boosts STAB moves
    "other_move_enhancement": [1, 'power'],
    # lagging tail; refers to priority bracket
    "moves_last_in_priority": [4, 'speed'],
    # quick claw
    "moves_first_in_priority": [2, 'speed'],
    # long reach
    "ignores_contact": [7, 'contact'],
    # stomp started dealing double damage to minimized targets in gen 2
    "anti_mini": [2, 'accuracy'],
    # haze
    "resets_stats": [1, 'stat'],
    # battle armor
    "prevents_crit": [3, 'crit'],
    # mist
    "prevents_stat_drop":[1, 'stat'],
    # prankster
    "adds_priority": [5, 'speed'],
    # after you; e.g. causes target to always use their move next, regardless of priority
    # contrast with instruct or dancer, which causes target to use a previously used move; the target still executes their own turn at the usual time
    "other_move_order_change": [4, 'speed'],
    # quick guard
    "protects_against_priority": [5, 'speed'],
    # wonder guard; refers to abilities which resist moves beyond their move type or class, e.g. wonder guard resists all non-super effective moves
    "other_move_resistance": [3, 'power'],
    # hidden power
    "type_varies": [2, 'type'],
    # splash
    "no_effect": [1, 'misc'],
    # psyshock (target's defense rather than special defense); body press (user's defense rather than attack)
    "uses_different_stat": [5, 'stat'],
    # iron ball; 
    "grounds": [4, 'ground'],
    # levitate; flying type does not count
    "ungrounds": [3, 'ground'],
    # arena trap
    "only_affects_grounded": [3, 'ground'],
  }

  effectDict = {}
  for effectName in effectsAndData.keys():
    effectGen, effectClass = effectsAndData[effectName]
    formattedEffectName = getFormattedName(effectName)
    effectDict[effectName] = {
      "gen": effectGen,
      "formatted_name": formattedEffectName,
      "effect_class": effectClass,
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

def getFormattedName(effectName):
  # replace underscores with spaces
  formattedName = effectName.replace('_', ' ')
  
  # make first letter uppercase
  formattedName = formattedName[0].upper() + formattedName[1:]

  formattedName = formattedName.replace('emi invulnerable', 'emi-invulnerable')
  formattedName = formattedName.replace('Ohko', 'OHKO')

  return formattedName

def addDescriptions(effectDict):
  # high crit chance
  effectDict["high_crit_chance"]["description"] = [
    ['Has an increased chance to crit.', 1],
  ]

  # cannot crit
  effectDict["cannot_crit"]["description"] = [
    ['Cannot score a crit.', 2],
  ]

  # always crits
  effectDict["always_crits"]["description"] = [
    ['When successful, always a crit.', 3],
  ]

  # bypasses protect
  effectDict["bypasses_protect"]["description"] = [
    ['Ignores or mitigates the effectiveness of Protect and other protection moves.', 4],
  ]

  # heals nonvolatile
  effectDict["heals_nonvolatile"]["description"] = [
    ['Heals all nonvolatile status conditions.', 1],
  ]

  # restores hp
  effectDict["restores_hp"]["description"] = [
    ['Restores HP to the target.', 1],
  ]

  # restores pp
  effectDict["restores_pp"]["description"] = [
    ['Restores PP of one or more of the target\'s moves.', 2],
  ]

  # recoil
  effectDict["recoil"]["description"] = [
    ['Damages the user in proportion to the damage caused to the target.', 1],
  ]

  # costs hp
  effectDict["costs_hp"]["description"] = [
    ['Costs some of the user\'s HP.', 1],
  ]

  # can crash
  effectDict["can_crash"]["description"] = [
    ['Has a chance to crash, causing the user to lose a fraction of their HP.', 1],
  ]

  # changes ability
  effectDict["changes_ability"]["description"] = [
    ['Changes the ability of either the user or the target.', 3],
  ]

  # ignores ability
  effectDict["ignores_ability"]["description"] = [
    ['Ignores the ability of the target if that ability would affect the interaction (e.g. Earthquake versus Levitate, but not Earthquake versus Rain Dish).', 3],
  ]

  # suppresses ability
  effectDict["suppresses_ability"]["description"] = [
    ['Nullifies the effects of the target\'s ability.', 4]
  ]

  # changes pokemon type
  effectDict["changes_pokemon_type"]["description"] = [
    ['Changes the type of the user or target.', 1],
  ]

  # changes move type
  effectDict["changes_move_type"]["description"] = [
    ['Changes the element type of a move from its usual type.', 4],
  ]

  # changes damage category
  effectDict["changes_damage_category"]["description"] = [
    ['Causes the damage category of a move to change depending on certain conditions.', 7],
  ]

  # removes type immunity
  effectDict["removes_type_immunity"]["description"] = [
    ['Removes type immunities from the target (e.g. Psychic-type can now affect Dark-type).', 2],
  ]

  # special type effectiveness
  effectDict["special_type_effectiveness"]["description"] = [
    ['Has unique type-effectiveness properties beyond the type of the move (e.g. Freeze Dry against Ice-type).', 6],
  ]

  # switches out target
  effectDict["switches_out_target"]["description"] = [
    ['Forces the target to switch out.', 2],
  ]

  # switches out user
  effectDict["switches_out_user"]["description"] = [
    ['Forces the user to switch out.', 2],
  ]

  # hits semi invulnerable
  effectDict["hits_semi_invulnerable"]["description"] = [
    ['Can affect Pokemon in the semi-invulnerable turn of one or more moves.', 1],
  ]

  # cannot miss
  effectDict["cannot_miss"]["description"] = [
    ['Will bypass accuracy checks to hit the target.', 1],
  ]

  # faints user
  effectDict["faints_user"]["description"] = [
    ['Causes the user to faint.', 1],
  ]

  # variable power
  effectDict["variable_power"]["description"] = [
    ['Moves whose power always varies.', 2],
  ]

  # deals direct damage
  effectDict["deals_direct_damage"]["description"] = [
    ['Damage dealt is unaffected by the damage formula, or the attacker\'s or defender\'s stats.', 1],
  ]

  # power up
  effectDict["powers_up"]["description"] = [
    ['Moves that can have their base power increased under certain conditions.', 2],
    ['Moves that can have their base power increased under certain conditions. Also includes, for example, Earthquake (against Dig), even though in that case the damage is technically doubled rather than the base power.', 5],
  ]

  # consecutive
  effectDict["consecutive"]["description"] = [
    ['Moves which are used automatically for one or more turns after being selected.', 1],
  ]

  # counterattack
  effectDict["counterattack"]["description"] = [
    ['Triggers in response to receiving damage from an opponent, dealing damage in response.', 1],
  ]

  # depends on weight
  effectDict["depends_on_weight"]["description"] = [
    ['Effectiveness depends on the weight of the target.', 3],
  ]

  # affects weight
  effectDict["affects_weight"]["description"] = [
    ['Affects the weight of the target.', 5],
  ]

  # calls other move
  effectDict["calls_other_move"]["description"] = [
    ['Calls another move in addition to the move with this effect.', 1],
  ]

  # depends on environment
  effectDict["depends_on_environment"]["description"] = [
    ['Effects depend on the environment in which the move is used.', 3],
  ]

  # mult hit
  effectDict["multi_hit"]["description"] = [
    ['Strikes multiple times in a single turn.', 1],
  ]

  # ohko
  effectDict["ohko"]["description"] = [
    ['Instantly knocks out the opposing Pokemon if successful.', 1],
  ]

  # changes form
  effectDict["changes_form"]["description"] = [
    ['Changes the user to another one of its forms.', 3],
  ]

  # drains
  effectDict["drains"]["description"] = [
    ['Heals the user proportional to damage dealt to the target.', 1],
  ]

  # manipulates item
  effectDict["manipulates_item"]["description"] = [
    ['Gives items to or removes items from the user or the target, or negates the effects of items.', 2],
  ]

  # activates gulp missile
  effectDict["activates_gulp_missile"]["description"] = [
    ['Allows the Pokemon to use Gulp Missile on the next turn.', 8],
  ]

  # punishes contact
  effectDict["punishes_contact"]["description"] = [
    ['Punishes moves which make contact with the user.', 3],
  ]

  # extends duration
  effectDict["extends_duration"]["description"] = [
    ['Extends the duration of other effects.', 4],
  ]

  # other move enhancement
  effectDict["other_move_enhancement"]["description"] = [
    ['Powers up moves via a mechanic other than type or usage method.', 1],
  ]

  # moves last in priority
  effectDict["moves_last_in_priority"]["description"] = [
    ['Causes the user to move last in the given priority bracket.', 4],
  ]

  # moves first in priority
  effectDict["moves_first_in_priority"]["description"] = [
    ['Causes the user to move first in the given priority bracket.', 2],
  ]

  # ignores contact
  effectDict["ignores_contact"]["description"] = [
    ['Contact-based moves lose their contact property.', 7],
  ]

  # anti mini
  effectDict["anti_mini"]["description"] = [
    ['Deals increased damage to targets that have used Minimize.', 2],
  ]

  # haze
  effectDict["resets_stats"]["description"] = [
    ['Removes the target\'s stat modifications.', 1],
  ]

  # prevents crit
  effectDict["prevents_crit"]["description"] = [
    ['Protects the user from critical hits.', 3],
  ]

  # prevents stat drop
  effectDict["prevents_stat_drop"]["description"] = [
    ['Protects the user from stat drops.', 1],
  ]

  # adds priority
  effectDict["adds_priority"]["description"] = [
    ['Causes moves of the user to be in a higher priority bracket.', 5],
  ]

  # other move order change
  effectDict["other_move_order_change"]["description"] = [
    ['Changes the order in which Pokemon execute moves independently of priority bracket.', 4],
  ]

  # other move resistance
  effectDict["other_move_resistance"]["description"] = [
    ['Resists moves in a manner different from their type or usage method.', 3],
  ]

  # type varies
  effectDict["type_varies"]["description"] = [
    ['The type of the move is not fixed.', 2],
  ]

  # no effect
  effectDict["no_effect"]["description"] = [
    ['Has no effect in battle.', 1],
  ]

  # uses different stat
  effectDict["uses_different_stat"]["description"] = [
    ['The stat used to calculate the move\'s damage differs from the damage category of the move.', 5],
  ]

  # protects aganst priority
  effectDict["protects_against_priority"]["description"] = [
    ['Protects against priority moves.', 5],
  ]

  # grounds
  effectDict["grounds"]["description"] = [
    ['Makes the opponent vulnerable to Ground type-moves, as well as other grounded abilities, moves, and field states.', 4]
  ]

  # ungrounds
  effectDict["ungrounds"]["description"] = [
    ['Makes the opponent invulnerable to Ground-type moves, as well as to other grounded abilities, moves, and field states.', 3]
  ]

  # only_affects_grounded
  effectDict["only_affects_grounded"]["description"] = [
    ['Fails against Flying-type Pokemon, as well as ungrounded Pokemon (e.g. Pokemon with Levitate).', 3]
  ]

  return effectDict

def main():
  effectDict = makeEffectDict()

  addDescriptions(effectDict)

  for effectName in effectDict.keys():
    if 'description' not in effectDict[effectName].keys():
      print(effectName, 'is missing a description.')

  return effectDict

if __name__ == '__main__':
  main()