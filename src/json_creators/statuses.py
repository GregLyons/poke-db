from utils import statusList

def makeStatusDict():
  statusDict = {
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

  # make sure all statuss are accounted for
  for status in statusList():
    if status not in statusDict:
      print(status, 'not in statusDict')

  # make sure no typos
  for key in statusDict.keys():
    if key not in statusList():
      print(key, 'not in statusList')

  
  return statusDict

def main():
  statusDict = makeStatusDict()

  return statusDict

if __name__ == '__main__':
  main()