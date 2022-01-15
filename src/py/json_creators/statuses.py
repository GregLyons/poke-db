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
  # non-volatile
  # region 

  # burn
  statusDict["burn"]["description"] = [
    [1, 'Inflicts a fraction of the Pokemon\'s max HP every turn and halves the Pokemon\'s attack stat. Fire-type Pokemon cannot be burned by Fire-type moves. The damage is skipped if the opponent faints during that turn.'],
    [3, 'Inflicts a fraction of the Pokemon\'s max HP every turn and halves damage dealt by the Pokemon\'s physical moves. Fire-type Pokemon cannot normally be burned.'],
  ]

  # freeze
  statusDict["freeze"]["description"] = [
    [1, 'The Pokemon is unable to use moves. They cannot be thawed out unless hit by a Fire-type move that can inflict burn, or if the opponent uses haze.'],
    [2, 'The Pokemon is unable to use moves and has a chance to thaw out each turn. It cannot attack on the turn that it thaws. Being hit by most Fire-types move, or using certain moves can thaw frozen Pokemon.'],
    [3, 'The Pokemon is unable to use moves and has a chance to thaw out each turn. Being hit by a damaging Fire-types move (except Hidden Power), or using certain moves can thaw frozen Pokemon.'],
    [4, 'The Pokemon is unable to use moves and has a chance to thaw out each turn. Being hit by a damaging Fire-types move, or using certain moves can thaw frozen Pokemon.'],
  ]

  # paralysis
  statusDict["paralysis"]["description"] = [
    [1, 'The Pokemon may be unable to use moves. Their speed is also reduced by 3/4.'],
    [6, 'The Pokemon may be unable to use moves. Their speed is also reduced by 3/4. Electric-type Pokemon are immune.'],
    [7, 'The Pokemon may be unable to use moves. Their speed is also reduced by 1/2. Electric-type Pokemon are immune.'],
  ]

  # poison
  statusDict["poison"]["description"] = [
    [1, 'Inflicts a fraction of the Pokemon\'s max HP every turn. The damage is skipped if the opponent faints during that turn.'],
    [2, 'Inflicts a fraction of the Pokemon\'s max HP every turn. The damage is skipped if the opponent faints during that turn. Steel-type Pokemon cannot be poisoned except by Twineedle.'],
    [3, 'Inflicts a fraction of the Pokemon\'s max HP every turn. Steel-type Pokemon cannot be poisoned.'],
    [5, 'Inflicts a fraction of the Pokemon\'s max HP every turn. Steel-type and Poison-type Pokemon cannot be poisoned except by a Pokemon with the ability Corrosion.'],
  ]

  # bad poison
  statusDict["bad_poison"]["description"] = [
    [1, 'Inflicts a fraction of the Pokemon\'s max HP each turn, with the damage increasing each turn. The damage is skipped if the opponent faints during that turn. If the opponent switches out while badly poisoned, they become merely poisoned.'],
    [2, 'Inflicts a fraction of the Pokemon\'s max HP every turn, with the damage increasing each turn. The damage is skipped if the opponent faints during that turn. Steel-type Pokemon cannot be badly poisoned except by Twineedle. If the opponent switches out while badly poisoned, they become merely poisoned.'],
    [3, 'Inflicts a fraction of the Pokemon\'s max HP every turn, with the damage increasing each turn. Steel-type Pokemon cannot be badly poisoned.'],
    [5, 'Inflicts a fraction of the Pokemon\'s max HP every turn, with the damage increasing each turn. Steel-type and Poison-type Pokemon cannot be badly poisoned except by a Pokemon with the ability Corrosion.'],
  ]

  # sleep
  statusDict["sleep"]["description"] = [
    [1, 'Prevents the Pokemon from making a move for a random number of turns. The Pokemon cannot move on the turn it wakes up. If the Pokemon is put to sleep by Rest, the sleep lasts two turns.'],
    [2, 'Prevents the Pokemon from making a move for a random number of turns.If the Pokemon is put to sleep by Rest, the sleep lasts two turns.'],
    [3, 'Prevents the Pokemon from making a move for a random number of turns.If the Pokemon is put to sleep by Rest, the sleep lasts two turns.'],
    [5, 'Prevents the Pokemon from making a move for a random number of turns.If the Pokemon is put to sleep by Rest, the sleep lasts two turns. Switching out a sleeping Pokemon resets the turn counter.'],
  ]

  # endregion

  # confusion
  statusDict["confusion"]["description"] = [
    [1, 'The Pokemon has a chance to hurt itself instead of executing a selected move. Multi-turn attacks require confusion to be checked on each turn.'],
  ]

  # curse
  statusDict["curse"]["description"] = [
    [2, 'The Pokemon takes a fraction of its maximum HP each turn. If the cursed Pokemon knocks out its opponent, it will not take damage from the curse that turn.'],
    [3, 'The Pokemon takes a fraction of its maximum HP each turn. If the cursed Pokemon knocks out its opponent, it will not take damage from the curse that turn.'],
  ]

  # encore
  statusDict["encore"]["description"] = [
    [2, 'The Pokemon is forced to repeat its last attack for 2-5 turns.'],
    [3, 'The Pokemon is forced to repeat its last attack for 4-8 turns.'],
    [5, 'The Pokemon is forced to repeat its last attack for 3 turns.'],
  ]

  # minimize
  statusDict["minimize"]["description"] = [
    [2, 'The Pokemon will be affected more harmfully by certain moves, e.g. Stomp.'],
  ]

  # bound
  statusDict["bound"]["description"] = [
    [1, 'The Pokemon takes damage at the end of each turn and cannot switch out. The victim cannot attack.'],
    [2, 'The Pokemon takes damage at the end of each turn and cannot switch out.'],
    [6, 'The Pokemon takes damage at the end of each turn and cannot switch out. Ghost-type Pokemon can still switch out.'],
  ]

  # embargo
  statusDict["embargo"]["description"] = [
    [4, 'The Pokemon is unable to use held items.'],
  ]

  # heal block
  statusDict ["heal_block"]["description"] = [
    [4, 'The Pokemon is prevented from healing. It cannot use healing moves, and it is unaffected by most healing effects. The Pokemon can still use HP-draining moves, but they will not be healed.'],
    [6, 'The Pokemon is prevented from healing. It cannot use healing or HP-draining moves, and it is unaffected by most healing effects.'],
  ]

  # nightmare
  statusDict["nightmare"]["description"] = [
    [2, 'The Pokemon loses a fraction of its max HP each turn; only affects sleeping Pokemon.'],
  ]

  # perish song
  statusDict["perish_song"]["description"] = [
    [2, 'After three turns, all Pokemon who heard the Perish Song will faint unless they are switched out before the counter reaches zero.'],
  ]

  # taunt
  statusDict["taunt"]["description"] = [
    [3, 'The Pokemon cannot use any status moves for 2-4 turns.'],
    [5, 'The Pokemon cannot use any status moves for 3 turns.'],
    [7, 'The Pokemon cannot use any status moves, except status Z-Moves, for 3 turns.'],
    [8, 'The Pokemon cannot use any status moves for 3 turns.'],
  ]

  # telekinesis
  statusDict["telekinesis"]["description"] = [
    [5, 'The Pokemon is immune to Ground-type moves, Spikes, Toxic Spikes, and Arena Trap. All other moves, except OHKO moves, hit the target regardless of accuracy and evasion.'],
  ]

  # flinch
  statusDict["flinch"]["description"] = [
    [2, 'Prevents the Pokemon from attacking. Sleeping Pokemon cannot flinch in most cases.'],
    [3, 'Prevents the Pokemon from attacking.'],
  ]

  # semi invulnerable turn
  statusDict["semi_invulnerable_turn"]["description"] = [
    [1, 'In most cases, moves will miss this Pokemon regardless of accuracy.'],
  ]

  # trapped
  statusDict["trapped"]["description"] = [
    [2, 'The victim cannot switch out or flee as long as the trapper is on the field.'],
    [6, 'The victim cannot switch out or flee as long as the trapper is on the field. Ghost-type Pokemon are immune.'],
  ]

  # drowsy
  statusDict["drowsy"]["description"] = [
    [3, 'At the end of the next turn, the drowsy Pokemon will fall asleep unless it is already afflicted by a non-volatile status.'],
  ]

  # identified
  statusDict["identified"]["description"] = [
    [2, 'The Pokemon\'s evasion modification will not affect the accuracy of moves used against it. Removes certain type-immunities depending on the source.'],
  ]

  # infatuation
  statusDict["infatuation"]["description"] = [
    [2, 'The Pokemon has a 1/2 chance to be unable to use moves, even against Pokemon other than the one the victim is infatuated with'],
  ]

  # leech seed
  statusDict["leech_seed"]["description"] = [
    [1, 'The Pokemon loses a fraction of its max HP each turn, and the opponent gains the same fraction of their own max HP. Grass-type Pokemon are immune (except when transferred by Baton Pass).'],
    [1, 'The Pokemon loses a fraction of its max HP each turn, and the opponent in the same position as the original user (e.g. if the replacement Pokemon if the user switches out in a team battle) gains the same fraction of their own max HP. Grass-type Pokemon are immune (except when transferred by Baton Pass).'],
  ]

  # torment
  statusDict["torment"]["description"] = [
    [3, 'The Pokemon cannot use the same move twice in a row.']
  ]

  # type change
  statusDict["type_change"]["description"] = [
    [5, 'The Pokemon\'s type has been changed by another Pokemon.'],
  ]

  # disable
  statusDict["disable"]["description"] = [
    [1, 'A certain move of the Pokemon is disabled.'],
  ]

  # charging turn
  statusDict["charging_turn"]["description"] = [
    [1, 'The Pokemon is in the first turn of a two-turn move and cannot attack.'],
  ]

  # protection
  statusDict["protection"]["description"] = [
    [2, 'The Pokemon will be unaffected by most damaging moves and status moves.'],
  ]

  # recharging
  statusDict["recharging"]["description"] = [
    [1, 'The Pokemon is in the second turn of a two-turn move and cannot perform an action.'],
  ]

  # taking aim
  statusDict["taking_aim"]["description"] = [
    [2, 'The Pokemon\'s next damage-dealing move will hit the target without fail.'],
  ]

  # thrashing
  statusDict["thrashing"]["description"] = [
    [1, 'The Pokemon is forced to use the same move for 3-4 turns and will get confused at the end.'],
    [2, 'The Pokemon is forced to use the same move for 2-3 turns and will get confused at the end.'],
  ]

  # aqua ring
  statusDict["aqua_ring"]["description"] = [
    [4, 'The Pokemon restores a fraction of its max HP each turn.'],
  ]

  # bracing
  statusDict["bracing"]["description"] = [
    [2, 'Whatever damage the Pokemon takes that turn from moves, it will always survive with at least 1 HP.']
  ]

  # defense curl
  statusDict["defense_curl"]["description"] = [
    [2, 'The power of certain moves (e.g. Rollout) is doubled.']
  ]

  # magic coat
  statusDict["magic_coat"]["description"] = [
    [3, 'Most status moves used against this Pokemon or its side of the field will be reflected back at the user.'],
  ]

  # mimic
  statusDict["mimic"]["description"] = [
    [1, 'Temporarily replaces the move Mimic with a move from the opposing Pokemon\'s moves.'],
    [2, 'Temporarily replaces the move Mimic with the last move used by the target.'],
  ]

  # substitute
  statusDict["substitute"]["description"] = [
    [1, 'The Pokemon is protected by a Subsitute, which has 1/4 of the Pokemon\'s max HP, and which will absorb hits and block certain status conditions until it breaks.'],
    [2, 'The Pokemon is protected by a Subsitute, which has 1/4 of the Pokemon\'s max HP, and which will absorb hits and block status conditions until it breaks.'],
  ]

  # center of attention
  statusDict["center_of_attention"]["description"] = [
    [3, 'Opponents are forced to target this Pokemon regardless of their intended target, unless the move is one with a charging turn.']
  ]
  
  # rooted
  statusDict["rooted"]["description"] = [
    [3, 'Restores a fraction of the Pokemon\'s max HP each turn, but prevents it from switching out or being switched out. Makes the Pokemon susceptible to Ground-type moves and certain grounded field states.'],
  ]

  # magnetic levitation
  statusDict["magnetic_levitation"]["description"] = [
    [4, 'The Pokemon is immune to Ground-type attacks and certain grounded field states.'],
  ]

  # transformed
  statusDict["transformed"]["description"] = [
    [1, 'The Pokemon is transformed into another Pokemon.'],
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