from utils import statusList

def makeStatusDict():
  statusesAndGens = {
    "burn": 1,
    "freeze": 1,
    "paralysis": 1,
    "poison": 1,
    "bad_poison": 1,
    "sleep": 1,
    "confusion": 1,
    "curse": 2,
    "bound": 1,
    "embargo": 4,
    "encore": 2,
    "heal_block": 4,
    "nightmare": 2,
    "perish_song": 2,
    "taunt": 3,
    "telekinesis": 5,
    "flinch": 2,
    "semi_invulnerable_turn": 1,
    "trapped": 2,
    "drowsy": 3,
    "identified": 2,
    "infatuation": 2,
    "leech_seed": 1,
    "torment": 3,
    "type_change": 5,
    "disable": 1,
    "charging_turn": 1,
    "protection": 2,
    "recharging": 1,
    "taking_aim": 2,
    "thrashing": 1,
    "aqua_ring": 4,
    "bracing": 2,
    "defense_curl": 2,
    "magic_coat": 3,
    "mimic": 1,
    "minimize": 2,
    "substitute": 1,
    "center_of_attention": 3,
    "rooted": 3,
    "magnetic_levitation": 4,
    "transformed": 1
  }

  statusDict = {}
  for statusName in statusesAndGens.keys():
    formattedEffectName = getFormattedName(statusName)
    statusDict[statusName] = {
      "gen": statusesAndGens[statusName],
      "formatted_name": formattedEffectName
    }

  # volatility
  for statusName in statusDict.keys():
    statusGen = statusDict[statusName]["gen"]
    if statusName in ['burn', 'freeze', 'paralysis', 'poison', 'bad_poison', 'sleep']:
      statusDict[statusName]["volatile"] = [[False, statusGen]]
    else:
      statusDict[statusName]["volatile"] = [[True, statusGen]]

  # make sure all statuss are accounted for
  for status in statusList():
    if status not in statusDict:
      print(status, 'not in statusDict')

  # make sure no typos
  for key in statusDict.keys():
    if key not in statusList():
      print(key, 'not in statusList')

  return statusDict

def getFormattedName(statusName):
  # replace underscores with spaces
  formattedName = statusName.replace('_', ' ')
  
  # make first letter uppercase
  formattedName = formattedName[0].upper() + formattedName[1:]

  formattedName = formattedName.replace('emi invulnerable', 'emi-invulnerable')

  return formattedName

def addDescriptions(statusDict):
  ## non-volatile

  # burn
  statusDict["burn"]["description"] = [
    ['Inflicts a fraction of the Pokemon\'s max HP every turn and halves the Pokemon\'s attack stat. Fire-type Pokemon cannot be burned by Fire-type moves. The damage is skipped if the opponent faints during that turn.', 1],
    ['Inflicts a fraction of the Pokemon\'s max HP every turn and halves damage dealt by the Pokemon\'s physical moves. Fire-type Pokemon cannot normally be burned.', 3],
  ]

  # freeze
  statusDict["freeze"]["description"] = [
    ['The Pokemon is unable to use moves. They cannot be thawed out unless hit by a Fire-type move that can inflict burn, or if the opponent uses haze.', 1],
    ['The Pokemon is unable to use moves and has a chance to thaw out each turn. It cannot attack on the turn that it thaws. Being hit by most Fire-types move, or using certain moves can thaw frozen Pokemon.', 2],
    ['The Pokemon is unable to use moves and has a chance to thaw out each turn. Being hit by a damaging Fire-types move (except Hidden Power), or using certain moves can thaw frozen Pokemon.', 3],
    ['The Pokemon is unable to use moves and has a chance to thaw out each turn. Being hit by a damaging Fire-types move, or using certain moves can thaw frozen Pokemon.', 4],
  ]

  # paralysis
  statusDict["paralysis"]["description"] = [
    ['The Pokemon may be unable to use moves. Their speed is also reduced by 3/4.', 1],
    ['The Pokemon may be unable to use moves. Their speed is also reduced by 3/4. Electric-type Pokemon are immune.', 6],
    ['The Pokemon may be unable to use moves. Their speed is also reduced by 1/2. Electric-type Pokemon are immune.', 7],
  ]

  # poison
  statusDict["poison"]["description"] = [
    ['Inflicts a fraction of the Pokemon\'s max HP every turn. The damage is skipped if the opponent faints during that turn.', 1],
    ['Inflicts a fraction of the Pokemon\'s max HP every turn. The damage is skipped if the opponent faints during that turn. Steel-type Pokemon cannot be poisoned except by Twineedle.', 2],
    ['Inflicts a fraction of the Pokemon\'s max HP every turn. Steel-type Pokemon cannot be poisoned.', 3],
    ['Inflicts a fraction of the Pokemon\'s max HP every turn. Steel-type and Poison-type Pokemon cannot be poisoned except by a Pokemon with the ability Corrosion.', 5],
  ]

  # bad poison
  statusDict["bad_poison"]["description"] = [
    ['Inflicts a fraction of the Pokemon\'s max HP each turn, with the damage increasing each turn. The damage is skipped if the opponent faints during that turn. If the opponent switches out while badly poisoned, they become merely poisoned.', 1],
    ['Inflicts a fraction of the Pokemon\'s max HP every turn, with the damage increasing each turn. The damage is skipped if the opponent faints during that turn. Steel-type Pokemon cannot be badly poisoned except by Twineedle. If the opponent switches out while badly poisoned, they become merely poisoned.', 2],
    ['Inflicts a fraction of the Pokemon\'s max HP every turn, with the damage increasing each turn. Steel-type Pokemon cannot be badly poisoned.', 3],
    ['Inflicts a fraction of the Pokemon\'s max HP every turn, with the damage increasing each turn. Steel-type and Poison-type Pokemon cannot be badly poisoned except by a Pokemon with the ability Corrosion.', 5],
  ]

  # sleep
  statusDict["sleep"]["description"] = [
    ['Prevents the Pokemon from making a move for a random number of turns. The Pokemon cannot move on the turn it wakes up. If the Pokemon is put to sleep by Rest, the sleep lasts two turns.', 1],
    ['Prevents the Pokemon from making a move for a random number of turns.If the Pokemon is put to sleep by Rest, the sleep lasts two turns.', 2],
    ['Prevents the Pokemon from making a move for a random number of turns.If the Pokemon is put to sleep by Rest, the sleep lasts two turns.', 3],
    ['Prevents the Pokemon from making a move for a random number of turns.If the Pokemon is put to sleep by Rest, the sleep lasts two turns. Switching out a sleeping Pokemon resets the turn counter.', 5],
  ]

  ## volatile

  # confusion
  statusDict["confusion"]["description"] = [
    ['The Pokemon has a chance to hurt itself instead of executing a selected move. Multi-turn attacks require confusion to be checked on each turn.', 1],
  ]

  # curse
  statusDict["curse"]["description"] = [
    ['The Pokemon takes a fraction of its maximum HP each turn. If the cursed Pokemon knocks out its opponent, it will not take damage from the curse that turn.', 2],
    ['The Pokemon takes a fraction of its maximum HP each turn. If the cursed Pokemon knocks out its opponent, it will not take damage from the curse that turn.', 3],
  ]

  # encore
  statusDict["encore"]["description"] = [
    ['The Pokemon is forced to repeat its last attack for 2-5 turns.', 2],
    ['The Pokemon is forced to repeat its last attack for 4-8 turns.', 3],
    ['The Pokemon is forced to repeat its last attack for 3 turns.', 5],
  ]

  # minimize
  statusDict["minimize"]["description"] = [
    ['The Pokemon will be affected more harmfully by certain moves, e.g. Stomp.', 2],
  ]

  # bound
  statusDict["bound"]["description"] = [
    ['The Pokemon takes damage at the end of each turn and cannot switch out. The victim cannot attack.', 1],
    ['The Pokemon takes damage at the end of each turn and cannot switch out.', 2],
    ['The Pokemon takes damage at the end of each turn and cannot switch out. Ghost-type Pokemon can still switch out.', 6],
  ]

  # embargo
  statusDict["embargo"]["description"] = [
    ['The Pokemon is unable to use held items.', 4],
  ]

  # heal block
  statusDict ["heal_block"]["description"] = [
    ['The Pokemon is prevented from healing. It cannot use healing moves, and it is unaffected by most healing effects. The Pokemon can still use HP-draining moves, but they will not be healed.', 4],
    ['The Pokemon is prevented from healing. It cannot use healing or HP-draining moves, and it is unaffected by most healing effects.', 6],
  ]

  # nightmare
  statusDict["nightmare"]["description"] = [
    ['The Pokemon loses a fraction of its max HP each turn; only affects sleeping Pokemon.', 2],
  ]

  # perish song
  statusDict["perish_song"]["description"] = [
    ['After three turns, all Pokemon who heard the Perish Song will faint unless they are switched out before the counter reaches zero.', 2],
  ]

  # taunt
  statusDict["taunt"]["description"] = [
    ['The Pokemon cannot use any status moves for 2-4 turns.', 3],
    ['The Pokemon cannot use any status moves for 3 turns.', 5],
    ['The Pokemon cannot use any status moves, except status Z-Moves, for 3 turns.', 7],
    ['The Pokemon cannot use any status moves for 3 turns.', 8],
  ]

  # telekinesis
  statusDict["telekinesis"]["description"] = [
    ['The Pokemon is immune to Ground-type moves, Spikes, Toxic Spikes, and Arena Trap. All other moves, except OHKO moves, hit the target regardless of accuracy and evasion.', 5],
  ]

  # flinch
  statusDict["flinch"]["description"] = [
    ['Prevents the Pokemon from attacking. Sleeping Pokemon cannot flinch in most cases.', 2],
    ['Prevents the Pokemon from attacking.', 3],
  ]

  # semi invulnerable turn
  statusDict["semi_invulnerable_turn"]["description"] = [
    ['In most cases, moves will miss this Pokemon regardless of accuracy.', 1],
  ]

  # trapped
  statusDict["trapped"]["description"] = [
    ['The victim cannot switch out or flee as long as the trapper is on the field.', 2],
    ['The victim cannot switch out or flee as long as the trapper is on the field. Ghost-type Pokemon are immune.', 6],
  ]

  # drowsy
  statusDict["drowsy"]["description"] = [
    ['At the end of the next turn, the drowsy Pokemon will fall asleep unless it is already afflicted by a non-volatile status.', 3],
  ]

  # identified
  statusDict["identified"]["description"] = [
    ['The Pokemon\'s evasion modification will not affect the accuracy of moves used against it. Removes certain type-immunities depending on the source.', 2],
  ]

  # infatuation
  statusDict["infatuation"]["description"] = [
    ['The Pokemon has a 1/2 chance to be unable to use moves, even against Pokemon other than the one the victim is infatuated with', 2],
  ]

  # leech seed
  statusDict["leech_seed"]["description"] = [
    ['The Pokemon loses a fraction of its max HP each turn, and the opponent gains the same fraction of their own max HP. Grass-type Pokemon are immune (except when transferred by Baton Pass).', 1],
    ['The Pokemon loses a fraction of its max HP each turn, and the opponent in the same position as the original user (e.g. if the replacement Pokemon if the user switches out in a team battle) gains the same fraction of their own max HP. Grass-type Pokemon are immune (except when transferred by Baton Pass).', 3],
  ]

  # torment
  statusDict["torment"]["description"] = [
    ['The Pokemon cannot use the same move twice in a row.', 3]
  ]

  # type change
  statusDict["type_change"]["description"] = [
    ['The Pokemon\'s type has been changed by another Pokemon.', 5],
  ]

  # disable
  statusDict["disable"]["description"] = [
    ['A certain move of the Pokemon is disabled.', 1],
  ]

  # charging turn
  statusDict["charging_turn"]["description"] = [
    ['The Pokemon is in the first turn of a two-turn move and cannot attack.', 1],
  ]

  # protection
  statusDict["protection"]["description"] = [
    ['The Pokemon will be unaffected by most damaging moves and status moves.', 2],
  ]

  # recharging
  statusDict["recharging"]["description"] = [
    ['The Pokemon is in the second turn of a two-turn move and cannot perform an action.', 1],
  ]

  # taking aim
  statusDict["taking_aim"]["description"] = [
    ['The Pokemon\'s next damage-dealing move will hit the target without fail.', 2],
  ]

  # thrashing
  statusDict["thrashing"]["description"] = [
    ['The Pokemon is forced to use the same move for 3-4 turns and will get confused at the end.', 1],
    ['The Pokemon is forced to use the same move for 2-3 turns and will get confused at the end.', 2],
  ]

  # aqua ring
  statusDict["aqua_ring"]["description"] = [
    ['The Pokemon restores a fraction of its max HP each turn.', 4],
  ]

  # bracing
  statusDict["bracing"]["description"] = [
    ['Whatever damage the Pokemon takes that turn from moves, it will always survive with at least 1 HP.', 2]
  ]

  # defense curl
  statusDict["defense_curl"]["description"] = [
    ['The power of certain moves (e.g. Rollout) is doubled.', 2]
  ]

  # magic coat
  statusDict["magic_coat"]["description"] = [
    ['Most status moves used against this Pokemon or its side of the field will be reflected back at the user.', 3],
  ]

  # mimic
  statusDict["mimic"]["description"] = [
    ['Temporarily replaces the move Mimic with a move from the opposing Pokemon\'s moves.', 1],
    ['Temporarily replaces the move Mimic with the last move used by the target.', 2],
  ]

  # substitute
  statusDict["substitute"]["description"] = [
    ['The Pokemon is protected by a Subsitute, which has 1/4 of the Pokemon\'s max HP, and which will absorb hits and block certain status conditions until it breaks.', 1],
    ['The Pokemon is protected by a Subsitute, which has 1/4 of the Pokemon\'s max HP, and which will absorb hits and block status conditions until it breaks.', 2],
  ]

  # center of attention
  statusDict["center_of_attention"]["description"] = [
    ['Opponents are forced to target this Pokemon regardless of their intended target, unless the move is one with a charging turn.', 3]
  ]
  
  # rooted
  statusDict["rooted"]["description"] = [
    ['Restores a fraction of the Pokemon\'s max HP each turn, but prevents it from switching out or being switched out. Makes the Pokemon susceptible to Ground-type moves and certain grounded field states.', 3],
  ]

  # magnetic levitation
  statusDict["magnetic_levitation"]["description"] = [
    ['The Pokemon is immune to Ground-type attacks and certain grounded field states.', 4],
  ]

  # transformed
  statusDict["transformed"]["description"] = [
    ['The Pokemon is transformed into another Pokemon.', 1],
  ]

  return statusDict

def main():
  statusDict = makeStatusDict()

  addDescriptions(statusDict)

  for statusName in statusDict.keys():
    if 'description' not in statusDict[statusName].keys():
      print(statusName, 'is missing a description.')

  return statusDict

if __name__ == '__main__':
  main()