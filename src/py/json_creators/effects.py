from utils import effectList

def makeEffectDict():
  effectsAndGens = {
    # karate chop
    "high_crit_chance": 1,
    # flail
    "cannot_crit": 2,
    # storm throw
    "always_crits": 5,
    # feint
    "bypasses_protect": 4,
    # rest
    "heals_nonvolatile": 1,
    # recover
    "restores_hp": 1,
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
    # normalize
    "changes_move_type": 4,
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
    # transform doesn't count; forecast
    "changes_form": 3,
    # absorb
    "drains": 1,
    # thief
    "manipulates_item": 2,
    # cramorant
    "activates_gulp_missile": 8,
    # static
    "punishes_contact": 3,
    # light clay
    "extends_duration": 4,
    # adaptability; refers to abilities which power up moves via a mechanic other than move type or usage method, e.g. adaptability boosts STAB moves
    "other_move_enhancement": 1,
    # lagging tail; refers to priority bracket
    "moves_last_in_priority": 4,
    # quick claw
    "moves_first_in_priority": 2,
    # long reach
    "ignores_contact": 7,
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
    "other_move_order_change": 4,
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
    # iron ball; 
    "grounds": 4,
    # levitate; flying type does not count
    "ungrounds": 3,
    # arena trap
    "only_affects_grounded": 3,
  }

  effectDict = {}
  for effectName in effectsAndGens.keys():
    formattedEffectName = getFormattedName(effectName)
    effectDict[effectName] = {
      "gen": effectsAndGens[effectName],
      "formatted_name": formattedEffectName
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