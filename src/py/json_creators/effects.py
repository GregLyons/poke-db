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
    [1, 'Has an increased chance to crit.'],
  ]

  # cannot crit
  effectDict["cannot_crit"]["description"] = [
    [2, 'Cannot score a crit.'],
  ]

  # always crits
  effectDict["always_crits"]["description"] = [
    [3, 'When successful, always a crit.'],
  ]

  # bypasses protect
  effectDict["bypasses_protect"]["description"] = [
    [4, 'Ignores or mitigates the effectiveness of Protect and other protection moves.'],
  ]

  # heals nonvolatile
  effectDict["heals_nonvolatile"]["description"] = [
    [1, 'Heals all nonvolatile status conditions.'],
  ]

  # restores hp
  effectDict["restores_hp"]["description"] = [
    [1, 'Restores HP to the target.'],
  ]

  # restores pp
  effectDict["restores_pp"]["description"] = [
    [2, 'Restores PP of one or more of the target\'s moves.'],
  ]

  # recoil
  effectDict["recoil"]["description"] = [
    [1, 'Damages the user in proportion to the damage caused to the target.'],
  ]

  # costs hp
  effectDict["costs_hp"]["description"] = [
    [1, 'Costs some of the user\'s HP.'],
  ]

  # can crash
  effectDict["can_crash"]["description"] = [
    [1, 'Has a chance to crash, causing the user to lose a fraction of their HP.'],
  ]

  # changes ability
  effectDict["changes_ability"]["description"] = [
    [3, 'Changes the ability of either the user or the target.'],
  ]

  # ignores ability
  effectDict["ignores_ability"]["description"] = [
    [3, 'Ignores the ability of the target if that ability would affect the interaction (e.g. Earthquake versus Levitate, but not Earthquake versus Rain Dish).'],
  ]

  # suppresses ability
  effectDict["suppresses_ability"]["description"] = [
    [4, 'Nullifies the effects of the target\'s ability.']
  ]

  # changes pokemon type
  effectDict["changes_pokemon_type"]["description"] = [
    [1, 'Changes the type of the user or target.'],
  ]

  # changes move type
  effectDict["changes_move_type"]["description"] = [
    [4, 'Changes the element type of a move from its usual type.'],
  ]

  # changes damage category
  effectDict["changes_damage_category"]["description"] = [
    [7, 'Causes the damage category of a move to change depending on certain conditions.'],
  ]

  # removes type immunity
  effectDict["removes_type_immunity"]["description"] = [
    [2, 'Removes type immunities from the target (e.g. Psychic-type can now affect Dark-type).'],
  ]

  # special type effectiveness
  effectDict["special_type_effectiveness"]["description"] = [
    [6, 'Has unique type-effectiveness properties beyond the type of the move (e.g. Freeze Dry against Ice-type).'],
  ]

  # switches out target
  effectDict["switches_out_target"]["description"] = [
    [2, 'Forces the target to switch out.'],
  ]

  # switches out user
  effectDict["switches_out_user"]["description"] = [
    [2, 'Forces the user to switch out.'],
  ]

  # hits semi invulnerable
  effectDict["hits_semi_invulnerable"]["description"] = [
    [1, 'Can affect Pokemon in the semi-invulnerable turn of one or more moves.'],
  ]

  # cannot miss
  effectDict["cannot_miss"]["description"] = [
    [1, 'Will bypass accuracy checks to hit the target.'],
  ]

  # faints user
  effectDict["faints_user"]["description"] = [
    [1, 'Causes the user to faint.'],
  ]

  # variable power
  effectDict["variable_power"]["description"] = [
    [2, 'Moves whose power always varies.'],
  ]

  # deals direct damage
  effectDict["deals_direct_damage"]["description"] = [
    [1, 'Damage dealt is unaffected by the damage formula, or the attacker\'s or defender\'s stats.'],
  ]

  # power up
  effectDict["powers_up"]["description"] = [
    [2, 'Moves that can have their base power increased under certain conditions.'],
    [5, 'Moves that can have their base power increased under certain conditions. Also includes, for example, Earthquake (against Dig), even though in that case the damage is technically doubled rather than the base power.'],
  ]

  # consecutive
  effectDict["consecutive"]["description"] = [
    [1, 'Moves which are used automatically for one or more turns after being selected.'],
  ]

  # counterattack
  effectDict["counterattack"]["description"] = [
    [1, 'Triggers in response to receiving damage from an opponent, dealing damage in response.'],
  ]

  # depends on weight
  effectDict["depends_on_weight"]["description"] = [
    [3, 'Effectiveness depends on the weight of the target.'],
  ]

  # affects weight
  effectDict["affects_weight"]["description"] = [
    [5, 'Affects the weight of the target.'],
  ]

  # calls other move
  effectDict["calls_other_move"]["description"] = [
    [1, 'Calls another move in addition to the move with this effect.'],
  ]

  # depends on environment
  effectDict["depends_on_environment"]["description"] = [
    [3, 'Effects depend on the environment in which the move is used.'],
  ]

  # mult hit
  effectDict["multi_hit"]["description"] = [
    [1, 'Strikes multiple times in a single turn.'],
  ]

  # ohko
  effectDict["ohko"]["description"] = [
    [1, 'Instantly knocks out the opposing Pokemon if successful.'],
  ]

  # changes form
  effectDict["changes_form"]["description"] = [
    [3, 'Changes the user to another one of its forms.'],
  ]

  # drains
  effectDict["drains"]["description"] = [
    [1, 'Heals the user proportional to damage dealt to the target.'],
  ]

  # manipulates item
  effectDict["manipulates_item"]["description"] = [
    [2, 'Gives items to or removes items from the user or the target, or negates the effects of items.'],
  ]

  # activates gulp missile
  effectDict["activates_gulp_missile"]["description"] = [
    [8, 'Allows the Pokemon to use Gulp Missile on the next turn.'],
  ]

  # punishes contact
  effectDict["punishes_contact"]["description"] = [
    [3, 'Punishes moves which make contact with the user.'],
  ]

  # extends duration
  effectDict["extends_duration"]["description"] = [
    [4, 'Extends the duration of other effects.'],
  ]

  # other move enhancement
  effectDict["other_move_enhancement"]["description"] = [
    [1, 'Powers up moves via a mechanic other than type or usage method.'],
  ]

  # moves last in priority
  effectDict["moves_last_in_priority"]["description"] = [
    [4, 'Causes the user to move last in the given priority bracket.'],
  ]

  # moves first in priority
  effectDict["moves_first_in_priority"]["description"] = [
    [2, 'Causes the user to move first in the given priority bracket.'],
  ]

  # ignores contact
  effectDict["ignores_contact"]["description"] = [
    [7, 'Contact-based moves lose their contact property.'],
  ]

  # anti mini
  effectDict["anti_mini"]["description"] = [
    [2, 'Deals increased damage to targets that have used Minimize.'],
  ]

  # haze
  effectDict["resets_stats"]["description"] = [
    [1, 'Removes the target\'s stat modifications.'],
  ]

  # prevents crit
  effectDict["prevents_crit"]["description"] = [
    [3, 'Protects the user from critical hits.'],
  ]

  # prevents stat drop
  effectDict["prevents_stat_drop"]["description"] = [
    [1, 'Protects the user from stat drops.'],
  ]

  # adds priority
  effectDict["adds_priority"]["description"] = [
    [5, 'Causes moves of the user to be in a higher priority bracket.'],
  ]

  # other move order change
  effectDict["other_move_order_change"]["description"] = [
    [4, 'Changes the order in which Pokemon execute moves independently of priority bracket.'],
  ]

  # other move resistance
  effectDict["other_move_resistance"]["description"] = [
    [3, 'Resists moves in a manner different from their type or usage method.'],
  ]

  # type varies
  effectDict["type_varies"]["description"] = [
    [2, 'The type of the move is not fixed.'],
  ]

  # no effect
  effectDict["no_effect"]["description"] = [
    [1, 'Has no effect in battle.'],
  ]

  # uses different stat
  effectDict["uses_different_stat"]["description"] = [
    [5, 'The stat used to calculate the move\'s damage differs from the damage category of the move.'],
  ]

  # protects aganst priority
  effectDict["protects_against_priority"]["description"] = [
    [5, 'Protects against priority moves.'],
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