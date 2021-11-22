import csv
import elementalTypes as types
import effects
import usageMethods
import statuses
from functools import cmp_to_key
from utils import getCSVDataPath, genSymbolToNumber, statList, numberOfGens, checkConsistency


# Create move .json file with the following data:
# name, description, power, PP, accuracy, category, priority, contact, target, type, gen introduced, where it affects item
# also include whether the move affects stats, and whose stats it affects
# also include whether the move inflicts status, and the probability of inflicting status
# also include any effects the move has
# also include any usage methods the move has

# get value(s) and generation(s) from description
def parseMoveListNote(note):
  moveID = int(note[0])
  header = note[1]
  description = note[2]

  # Flag ohko moves
  # Flag fixed damage moves
  # Flag LGPE: if 'in LGPE'; refers to move damage/accuracy/type and it takes a specific value; if 'LGPE only' refers to presence of move itself and doesn't take specific value; if 'and LGPE', refers to move value present in LGPE and multiple generations prior to VII
  # For most changes, it'll just be the value and the latest generation for that value (e.g. 40 Power before and in Generation V would be [40, 5])

  # Notes about type change are actually given in the 'Name' column
  if header == 'name':
    header = 'type'

  # "Success is calculated using a custom formula" for ohko moves
  # the success of the ohko move depends on mechanics which are hard to capture in a list--since there are only four, and they're hardly used, we ignore them
  if 'custom' in description:
    return [moveID, header, ['ohko', None]]

  # "Always deals X damage"
  if 'Always' in description:
    words = description.split()
    value = words[2] + "fixed"
    # fixed damage moves come from Gen 1
    return [moveID, header, [value, 1]]

  # If value applies for LGPE, replace generation value with LGPE flag
  if 'in LGPE' in description:
    words = description.split() 
    value = words[0].rstrip('%').rstrip('-type')
    return [moveID, header, [value, 'LGPE']]

  # Indicates presence of move itself in LGPE only, rather than a value
  if 'LGPE only' in description:
    return [moveID, header, [None, 'LGPE only']]

  # Smogon doesn't care about these exclusions--e.g. Hypnosis is 70% accurate in Diamond and Pearl, but on Smogon and Pokemon Showdown, Gen 4 Hypnosis is 60% accurate
  if 'Diamond and Pearl' in description or 'ORAS only' in description or 'USUM only' in description: 
    return [moveID, header, None]
  
  # change description is of the form '$value in Generation(s) $start-$end"
  # sometimes description ends in 'LGPE'--ignore that part
  try:
    includeLGPE = False
    if 'and LGPE' in description:
      includeLGPE = True
    
    # remove LGPE for parsing consistently
    description = description.rstrip(' and LGPE')

    words = description.split()
    value = words[0].rstrip('%').rstrip('-type')
    latestGen = genSymbolToNumber(words[-1].split('-')[-1])
    if includeLGPE:
      return [moveID, header, [value, latestGen, 'LGPE']]
    else: 
      # Note is not one of the above cases, the majority of cases
      return [moveID, header, [value, latestGen, 'Standard']]
  # except_clause for debugging
  except:
    print('Something went wrong when handling this description:')
    print(description)
    return None

# a patch is of the form [value, gen], where gen is either 1_8 or "LGPE"
def comparePatches(patch1, patch2):
  # make LGPE last, otherwise sort by gen
  if patch1[1] == "LGPE" or patch1[1] == "lgpe_only":
    return 1
  elif patch2[1] == "LGPE" or patch2[1] == "lgpe_only":
    return -1
  else:
    if patch1[1] > patch2[1]:
      return 1
    else:
      return -1

# creates dictionary for moves in csv located at fname
# contains moveID, name, type, category, contest type, PP, power, accuracy, gen introduced, whether move is ohko, whether move is fixed damage/its fixed damage value, whether the move is LGPE exclusive
def makeInitialMoveDict(fname):
  moveDict = {}
  parsedNotes = []

  # Initialize moveDict and parse the notes to apply afterwards
  with open(fname, encoding='utf-8') as movesCSV, open(fname.rstrip('.csv') + 'Notes.csv', encoding='utf-8') as notesCSV:
    reader, notesReader = csv.DictReader(movesCSV), csv.DictReader(notesCSV)

    # make initial move dictionary, capturing state of the moves in Gen VIII

    for row in reader:
      # Bulbapedia has "Stone Axe" as the last entry with ID "???"--not released yet
      if row["Move ID"] != "???":
        moveName = row["Move Name"]
        moveID = int(row["Move ID"])

        isMax = moveName[:3] == "max"
        isGMax = moveName[:5] == "g_max"

        # For status Z-moves; will correct Z-move flags for, e.g. breakneck_blitz, at end of function.
        isZMove = 'z_' in moveName

        # Many values are lists since they can potentially change across generations--Bulbapedia lists the latest values for each field, with the past values in notes
        moveDict[moveName] = {
          "id": moveID,
          # Treat Curse in Gens 2-4 as Ghost-type move, not ???-type.
          "type": [[row["Type"], 8]],
          "category": [[row["Category"], 8]],
          "pp": [[row["PP"], 8]],
          "power": [[row["Power"], 8]],
          "accuracy": [[row["Accuracy"].rstrip('%'), 8]],
          "gen": genSymbolToNumber(row["Gen"]),
          "removed_from_gen8": False,
          "fixed_damage": False,
          "z_move": isZMove,
          "lgpe_only": False,
          "max_move": isMax,
          "g_max_move": isGMax,
          "effects": {},
          "causes_status": {},
          "resists_status": {},
          "stat_modifications": {},
          "usage_method": {},
          "contact": [],
          "priority": [],
          "target": [],
        }

    inverseDict = makeInverseDict(fname)

    # we will make a list of all the parsed notes, then filter them out into several other lists
    for note in notesReader:
      # some moves, such as Disable, have had multiple changes across generations, so a note can describe multiple changes
      moveID, header, description = note["Move ID"], note["Header"], note["Description"]

      parts = description.split(',')
      for part in parts:
        parsedNote = parseMoveListNote([moveID, header, part])
        if parsedNote[2] != None:
          parsedNotes.append(parsedNote)

  # Apply parsed notes to moveDict

  # Standard note, majority of cases [moveID, header, [value, gen]]
  changes = [[note[0], note[1], note[2][:2]] for note in parsedNotes if len(note[2]) == 3 and note[2][2] == 'Standard']
  for change in changes:
    # Exception is Water Shuriken, moveID = 594
    if change[0] == 594:
      moveDict[inverseDict[594]]["category"] = [['physical', 6], ['special', 8]]
      continue

    moveID = change[0]
    # type data is under 'move name' header
    header = change[1]
    if header == 'move name':
      header = 'type'
      change[2][0] = change[2][0].lower()
    valueAndGen = change[2]
    
    moveDict[inverseDict[moveID]][header].append(valueAndGen)

  # ohko moves [moveID, header, ['ohko', None]]
  ohkoMoves = [note for note in parsedNotes if note[2][0] == 'ohko']
  for ohkoMove in ohkoMoves:
    moveID = int(ohkoMove[0])
    gen = moveDict[inverseDict[moveID]]["gen"]
    moveDict[inverseDict[moveID]]["effects"]["ohko"] = [[True, gen]]

  # Fixed damage moves [moveID, header, [value + "fixed", Gen]]
  fixedDamageMoves = [note for note in parsedNotes if note[2][0] != None and 'fixed' in note[2][0]]
  for fixedDamageMove in fixedDamageMoves:
    moveID = fixedDamageMove[0]
    moveDict[inverseDict[moveID]]["fixed_damage"] = fixedDamageMove[2][0].rstrip('fixed')

  # Value for move in LGPE [moveID, header, [value, "LGPE"]]
  LGPEMoveValues = [note for note in parsedNotes if note[2][1] == 'LGPE']
  for LGPEMoveValue in LGPEMoveValues:
    moveID = LGPEMoveValue[0]
    header = LGPEMoveValue[1]
    moveDict[inverseDict[moveID]][header].append(LGPEMoveValue[2])

  # LGPE exclusive move [moveID, header, [None, "LGPE only"]]
  LGPEExclusives = [note for note in parsedNotes if note[2][1] == 'LGPE only']
  for LGPEExclusive in LGPEExclusives:
    moveID = LGPEExclusive[0]
    header = LGPEExclusive[1]
    moveDict[inverseDict[moveID]]["lgpe_only"] = True
    for header in ['type', 'pp', 'power', 'accuracy']:
      moveDict[inverseDict[moveID]][header][0][1] = "lgpe_only"

  # Value for move which holds in LGPE and in other gens [moveID, header, [value, gen, "LGPE"]]
  # only includes Mega Drain 
  LGPEandGenMoves = [note for note in parsedNotes if len(note[2]) == 3 and note[2][2] == 'LGPE']
  for LGPEandGenMove in LGPEandGenMoves:
    moveID = LGPEandGenMove[0]
    header = LGPEandGenMove[1]
    valueAndGen = [LGPEandGenMove[2][0], LGPEandGenMove[2][1]]
    valueAndLGPE = [LGPEandGenMove[2][0], LGPEandGenMove[2][2]]
    moveDict[inverseDict[moveID]][header].append(valueAndGen)
    moveDict[inverseDict[moveID]][header].append(valueAndLGPE)

  # For each move in initialMoveDict, sort the "Type", "PP", "Power", and "Accuracy" fields by generation
  for moveName in moveDict:
    for innerKey in ['type', 'pp', 'power', 'accuracy']:
      if len(moveDict[moveName][innerKey]) > 1:
        moveDict[moveName][innerKey].sort(key = cmp_to_key(comparePatches))

  # For each move in initialMoveDict, rewrite the patches in "Type", "PP", "Power", and "Accuracy" fields so that the generation represents the starting gen rather than the ending gen of that value
  for moveName in moveDict:
    moveDict[moveName]["lgpe_exclusive_values"] = {}
    for innerKey in ['type', 'pp', 'power', 'accuracy', 'category']:
      # If the move is LGPE_only, no change required; move on
      if moveDict[moveName]["lgpe_only"]:
        # set values for LGPE
        if innerKey in ['pp', 'power', 'accuracy'] and moveDict[moveName][innerKey][0][0] != '':
          moveDict[moveName]["lgpe_exclusive_values"][innerKey] = int(moveDict[moveName][innerKey][0][0])
        else:
          moveDict[moveName]["lgpe_exclusive_values"][innerKey] = moveDict[moveName][innerKey][0][0]

        # removed in Gen 8
        if innerKey in ['pp', 'power', 'accuracy']:
          moveDict[moveName][innerKey] = [[0, 8]]
        else:
          moveDict[moveName][innerKey] = [[moveDict[moveName][innerKey][0][0], 8]]

        continue

      # Split up patch into LGPE_only and other
      LGPEOnlyPatch = [patch for patch in moveDict[moveName][innerKey] if patch[1] in ['lgpe_only', 'LGPE']]
      # Remove gen info from LGPE only patch
      if len(LGPEOnlyPatch) == 1:
        LGPEOnlyPatch = LGPEOnlyPatch[0][0]
        if LGPEOnlyPatch.isnumeric():
          LGPEOnlyPatch = int(LGPEOnlyPatch)
        moveDict[moveName]["lgpe_exclusive_values"][innerKey] = LGPEOnlyPatch

      # non-LGPE patches
      noLGPEOnlyPatches = [patch for patch in moveDict[moveName][innerKey] if patch[1] not in ['lgpe_only', 'LGPE']]

      moveDict[moveName][innerKey] = noLGPEOnlyPatches

      modifiedPatchList = []
      for i in range(len(moveDict[moveName][innerKey])):
        # first 'patch' applied in gen the move was introduced
        if i == 0:
          modifiedPatchList.append([moveDict[moveName][innerKey][0][0], moveDict[moveName]["gen"]])
        # send [value, endGen] to [value, oldEndGen + 1]
        else:
          oldValueEndGen = moveDict[moveName][innerKey][i - 1][1]
          value = moveDict[moveName][innerKey][i][0]
          modifiedPatchList.append([value, oldValueEndGen + 1])
      
      moveDict[moveName][innerKey] = modifiedPatchList

  # hard code water shuriken type
  moveDict["water_shuriken"]["category"] = [['physical', 6], ['special', 8]]
  moveDict["water_shuriken"]["type"] = [['water', 6]]

  # force hidden power to have power 0 (representing variable power) in gen 2, 60 in gen 6
  moveDict["hidden_power"]["power"] = [[0, 2], [60, 6]]

  # force double iron bash to have its lgpe values be non-exclusive, as it is also present in gen 8
  moveDict["double_iron_bash"]["type"] = [['steel', 7]]
  moveDict["double_iron_bash"]["pp"] = [[5, 7]]
  moveDict["double_iron_bash"]["power"] = [[60, 7]]
  moveDict["double_iron_bash"]["accuracy"] = [[100, 7]]
  moveDict["double_iron_bash"]["category"] = [['physical', 7]]
  moveDict["double_iron_bash"]["lgpe_exclusive_values"] = {}

  # force curse to always have ghost type
  moveDict["curse"]["type"] = [['ghost', 2]]

  # Add Z-Move flags
  with open(getCSVDataPath() + '/moves/movesZList.csv', encoding='utf-8') as zMoveCSV:
    reader = csv.DictReader(zMoveCSV)

    for row in reader:
      moveName = row["Z-Move Name"]
      moveDict[moveName]["z_move"] = True


  return moveDict

# Uses move list located at fname to make inverse lookup of moveID from moveName possible
def makeInverseDict(fname):
  inverseDict = {}

  with open(fname, encoding='utf-8') as movesCSV:
    reader = csv.DictReader(movesCSV)
    for row in reader:
      if row["Move ID"] != "???":
        inverseDict[int(row["Move ID"])] = row["Move Name"]

  return inverseDict

# read priority data and update moveDict
def addPriorityToMoveDict(fname, moveDict):
  with open(fname, encoding='utf-8') as priorityCSV:
    reader = csv.DictReader(priorityCSV)

    for row in reader:
      if row["Move Name"] != 'none' and row["Move Name"] != 'fleeing':
        moveName = row["Move Name"]
        # we add duplicate entries for when moves maintain the same priority across generations--we will handle this in the next loop to account for zero_priority moves
        moveDict[moveName]["priority"].append([int(row["Priority"]), int(row["Gen"])])

  # handle priority zero moves
  for key in moveDict.keys():
    numGensPresent = numberOfGens() - moveDict[key]["gen"] + 1

    # indicates that either the move had zero priority in some gens, or it was removed in gen 8
    # we will account for the moves removed from gen 8 later--for now, give them 0 priority
    if len(moveDict[key]["priority"]) != numGensPresent:
      gensAccountedFor = [entry[1] for entry in moveDict[key]["priority"]]
      for gen in range(moveDict[key]["gen"], moveDict[key]["gen"] + numGensPresent):
        if gen not in gensAccountedFor:
          moveDict[key]["priority"].append([0, gen])

    # sort the patches by gen
    if len(moveDict[key]["priority"]) > 1:
      moveDict[key]["priority"].sort(key = cmp_to_key(comparePatches))

    # remove duplicates
    priorities_noDuplicates = []
    for patch in moveDict[key]["priority"]:
      # add on first patch and continue to next patch
      if len(priorities_noDuplicates) == 0:
        priorities_noDuplicates.append(patch)
        continue
      else:
        priority = patch[0]
        # if priority doesn't change, continue
        if priorities_noDuplicates[-1][0] == priority:
          continue
        else:
          priorities_noDuplicates.append(patch)

    moveDict[key]["priority"] = priorities_noDuplicates
  
  # lastly, we add Teleport, ID 100 with -6 priority in LGPE
  moveDict["teleport"]["lgpe_exclusive_values"]["priority"] = -6

  return

# read contact data and update moveDict
def addContactToMoveDict(fname, moveDict):
  # initially, no moves make contact
  for moveName in moveDict.keys():
    # We do not take the max of moveGen with 3. Otherwise, we will get NULL values when we process the data later, which would be a problem since we take 'contact' to be a non-nullable column in our move table. Specifically, e.g. 'pound' would have NULL values for 'contact' in gens 1 and 2.
    moveDict[moveName]["contact"] = [[False, moveDict[moveName]["gen"]]]

  with open(fname, encoding='utf-8') as contactCSV:
    reader = csv.DictReader(contactCSV)
    for row in reader:
      moveName = row["Move Name"]
      note = row["Note"]
      moveGen = moveDict[moveName]["gen"]

      if note == '':
        # contact as a mechanic was introduced in Gen 3
        if moveGen < 3:
          # if moveName was released prior to gen 3, then it had previous values for 'contact'
          moveDict[moveName]["contact"].append([True, 3])
        else:
          # if moveName was released gen 3 or onward, then it didn't have previous values for 'contact' in the sense of the 'if'-clause.
          moveDict[moveName]["contact"] = [[True, max(moveGen, 3)]]
      else:
        if note == 'Gen IV onward':
          moveDict[moveName]["contact"].append([True, 4])
        elif note == 'Only Gen III':
          if moveGen < 3:
            moveDict[moveName]["contact"].append([True, 3])
            moveDict[moveName]["contact"].append([False, 4])
          else:
            moveDict[moveName]["contact"] = [[True, 3], [False, 4]]

  return

# read effect data and update moveDict
def addEffectToMoveDict(fname, moveDict):

  with open(fname, encoding='utf-8') as effectCSV:
    reader = csv.DictReader(effectCSV)

    # get effects and add them to moveDict with initial value False
    for row in reader:
      effect = row["Effect Name"]
      moveName = row["Move Name"]
      moveGen = moveDict[moveName]["gen"]

      # distinguish between usage method and other effects
      if effect in usageMethodDict.keys():
        usageMethodGen = usageMethodDict[effect]["gen"]
        moveDict[moveName]["usage_method"][effect] = [[True, max(usageMethodGen, moveGen)]]
      else:      
        effectGen = effectDict[effect]["gen"]
      # # if effect isn't in moveDict, add it and initialize as False
        moveDict[moveName]["effects"][effect] = [[True, max(effectGen, moveGen)]]
      
  # EXCEPTIONS SECTION
  # not covered in the above .csv
  effect_moves = [
    ['suppresses_ability', ['core_enforcer', 'gastro_acid']],
    ['uses_different_stat', ['body_press', 'psyshock', 'psystrike', 'secret_sword']],
    ['can_crash', ['high_jump_kick', 'jump_kick']],
    ['changes_damage_category', ['light_that_burns_the_sky', 'photon_geyser', 'shell_side_arm']],
    ['punishes_contact', ['baneful_bunker', 'beak_blast', 'kings_shield', 'obstruct', 'spiky_shield']],
    ['affects_weight', ['autotomize']]
  ]
  for exception in effect_moves:
    effect, moveNames = exception
    effectGen = effectDict[effect]["gen"]
    for moveName in moveNames:
      moveGen = moveDict[moveName]["gen"]
      moveDict[moveName][effect] = [[True, max(effectGen, moveGen)]]

  # EXCEPTIONS WHERE EFFECT CHANGES ACROSS GENERATIONS
  # miscellaneous
  moveDict["astonish"]["effects"]["anti_mini"] = [[True, 3], [False, 4]]
  moveDict["earthquake"]["effects"]["hits_semi_invulnerable"] = [[False, 1], [True, 2]]

  # cannot crit effects
  moveDict["flail"]["effects"]["cannot_crit"] = [[True, 2], [False, 3]]
  moveDict["future_sight"]["effects"]["cannot_crit"] = [[True, 2], [False, 5]]
  moveDict["reversal"]["effects"]["cannot_crit"] = [[True, 2], [False, 3]]
  moveDict["doom_desire"]["effects"]["cannot_crit"] = [[True, 3], [False, 5]]
  moveDict["spit_up"]["effects"]["cannot_crit"] = [[True, 3], [False, 4]]

  # high crit ratio
  moveDict["razor_wind"]["effects"]["high_crit_chance"] = [[False, 1], [True, 2]]
  moveDict["sky_attack"]["effects"]["high_crit_chance"] = [[False, 1], [True, 3]]

  # haze
  moveDict["haze"]["effects"]["resets_stats"] = [[True, 1]]
  moveDict["haze"]["effects"]["removes_screen"] = [[True, 1], [False, 2]]

  # defog
  moveDict["defog"]["effects"]["removes_terrain"] = [[True, 8]]

  return

# read status data and update moveDict
def addStatusToMoveDict(fname, moveDict):
  with open(fname, encoding='utf-8') as csvFile:
    reader = csv.DictReader(csvFile)

    for row in reader:
      status = row["Status Caused"]
      moveName = row["Move Name"]
      probability = float(row["Probability"])

      moveGen, statusGen = moveDict[moveName]["gen"], statusDict[status]["gen"]
      
      moveDict[moveName]["causes_status"][status] = [[probability, max(statusGen, moveGen)]]

  # EXCEPTIONS SECTION
  # Fire Blast had 30% to burn in Gen 1
  moveDict["fire_blast"]["causes_status"]["burn"] = [
    [30.0, 1], 
    [10.0, 2]
  ]

  # Tri Attack only applied statuses from Gen 2 on
  for status in ['burn', 'freeze', 'paralysis']:
    moveDict["tri_attack"]["causes_status"][status] = [
      [0.0, 1],
      [6.67, 2]
    ]

  # Thunder had 10% change to paralyze in Gen 1
  moveDict["thunder"]["causes_status"]["paralysis"] = [
    [10.0, 1], 
    [30.0, 2]
  ]

  # Poison Sting had 20% chance to poison in Gen 1
  moveDict["poison_sting"]["causes_status"]["poison"] = [
    [20.0, 1], 
    [30.0, 2]
  ]

  # sludge
  moveDict["sludge"]["causes_status"]["poison"] = [
    [40.0, 1], 
    [30.0, 2]
  ]

  # Chatter has variable chance to confuse in Gens 4 and 5--we choose the highest value in each gen
  moveDict["chatter"]["causes_status"]["confusion"] = [
    [31.0, 4],
    [10.0, 5],
    [100.0, 6]
  ]

  # Sky Attack only causes Flinch starting in Gen 3
  moveDict["sky_attack"]["causes_status"]["flinch"] = [
    [0.0, 2],
    [30.0, 3]
  ]

  # add status resistors/healers
  for exception in [
    ['burn', ['refresh', 'heal_bell', 'aromatherapy', 'jungle_healing', 'g_max_sweetness', 'psycho_shift']],
    ['poison', ['refresh', 'heal_bell', 'aromatherapy', 'jungle_healing', 'g_max_sweetness', 'psycho_shift']],
    ['bad_poison', ['refresh', 'heal_bell', 'aromatherapy', 'jungle_healing', 'g_max_sweetness', 'psycho_shift']],
    ['paralysis', ['refresh', 'heal_bell', 'aromatherapy', 'jungle_healing', 'g_max_sweetness', 'psycho_shift']],
    ['freeze', ['heal_bell', 'aromatherapy', 'jungle_healing', 'g_max_sweetness', 'psycho_shift']],
    ['sleep', ['heal_bell', 'aromatherapy', 'jungle_healing', 'g_max_sweetness', 'psycho_shift']]
  ]:
    status, moves = exception
    statusGen = statusDict[status]["gen"]
    for moveName in moves:
      moveGen = moveDict[moveName]["gen"]
      moveDict[moveName]["resists_status"][status] = [[True, max(statusGen, moveGen)]]

  # Other notes in movesThatCauseStatusNotes.csv don't apply to status

  return

# read target data and update moveDict
def addTargetToMoveDict(fname, moveDict):
  with open(fname, encoding='utf-8') as targetCSV:
    reader = csv.DictReader(targetCSV)

    # 'any_adjacent' is the most common targetting class
    for moveName in moveDict.keys():
      moveDict[moveName]["target"] = [['any_adjacent', moveDict[moveName]["gen"]]]

    for row in reader:
      target = row["Targets"]
      if target not in ['adjacent_ally', 'adjacent_foe', 'all_adjacent','all_adjacent_foes', 'all', 'all_allies', 'all_foes', 'any', 'any_adjacent', 'user', 'user_and_all_allies', 'user_or_adjacent_ally']:
        print(moveName, 'has invalid target name.')

      moveName = row["Move Name"]
      
      moveDict[moveName]["target"] = [[target, moveDict[moveName]["gen"]]]

    # Z-status moves have same target data as their base moves, but we need to update this since they aren't listed in the target data scraped from Bulbapedia.
    for moveName in moveDict.keys():
      if 'z_' in moveName:
        moveDict[moveName]["target"] = [[moveDict[moveName[2:]]["target"][0][0], 7]]

    # hard code exceptions
    #region
    # helping_hand
    moveDict["helping_hand"]["target"] = [["user", 3], ["adjacent_ally", 4]]

    # surf
    moveDict["surf"]["target"] = [["all_foes", 1], ["all_adjacent", 4]]

    # conversion_2
    moveDict["conversion_2"]["target"] = [["user", 2], ["any_adjacent", 5]]

    # poison_gas
    moveDict["poison_gas"]["target"] = [["any_adjacent", 1], ["all_adjacent_foes", 5]]

    # cotton_spore
    moveDict["cotton_spore"]["target"] = [["adjacent_foe", 2], ["all_adjacent_foes", 6]]

    # nature_power
    moveDict["nature_power"]["target"] = [["user", 3], ["any_adjacent", 6]]

    # howl
    moveDict["howl"]["target"] = [["user", 3], ["user_and_all_allies", 8]]
    #endregion

  return

# read stat modification data and update moveDict
def addStatModToMoveDict(fname, moveDict):
  with open(fname, encoding='utf-8') as statModCSV:
    reader = csv.reader(statModCSV)
    next(reader)

    for row in reader:
      moveName, gen, stat, modifier, sign, recipient, probability = row

      # for belly drum--it always sets attack stage to +6, even if it's negative beforehand
      gen, modifier, probability = int(gen), sign + modifier, float(probability)

      # if stat not in moveDict[1]["stat_modifications"]:
      #   for key in moveDict:
      #     moveDict[key]["stat_modifications"][stat] = [[0, '', moveDict[key], 0.0, ["gen"]]]
      
      # indicates move has always modified that stat as described
      if gen == moveDict[moveName]["gen"]:
        moveDict[moveName]["stat_modifications"][stat] = [[modifier, recipient, probability, gen]]
      # indicate move's stat modification was introduced in a later gen
      else:
        if stat not in moveDict[moveName]["stat_modifications"]:
          moveDict[moveName]["stat_modifications"][stat] = []

        moveDict[moveName]["stat_modifications"][stat].append([modifier, recipient, probability, gen])

  # hard code exceptions 
  # note that since we leave these out of the original .csv, the z-move counterparts aren't added either since the addZMoves method in the .csv creator file goes based on moves already present in the .csv
  #region
  # acid
  moveDict["acid"]["stat_modifications"]["defense"] = [['-1', 'target', 33.2, 1], ['-1', 'target', 10.0, 2], ['+0', 'target', 0.0, 4]]
  moveDict["acid"]["stat_modifications"]["special_defense"] = [['+0', 'target', 0.0, 1], ['-1', 'target', 10.0, 4]]

  # aurora beam
  moveDict["aurora_beam"]["attack"] = [['-1', 'target', 33.2, 1], ['-1', 'target', 10.0, 2]]

  # bubble
  moveDict["bubble"]["speed"] = [['-1', 'target', 33.2, 1], ['-1', 'target', 10.0, 2]]
  
  # bubble beam
  moveDict["bubble_beam"]["speed"] = [['-1', 'target', 33.2, 1], ['-1', 'target', 10.0, 2]]

  # constrict
  moveDict["constrict"]["speed"] = [['-1', 'target', 33.2, 1], ['-1', 'target', 10.0, 2]]

  # psychic
  moveDict["psychic"]["special_attack"] = [['-1', 'target', 33.2, 1], ['+0', 'target', 0.0, 2]]
  moveDict["psychic"]["special_defense"] = [['-1', 'target', 33.2, 1], ['-1', 'target', 10.0, 2]]

  # amnesia
  moveDict["amnesia"]["special_attack"] = [['+2', 'user', 100.0, 1], ['+0', 'user', 0.0, 2]]
  moveDict["amnesia"]["special_defense"] = [['+2', 'user', 100.0, 1], ['+2', 'user', 100.0, 2]]
  moveDict["z_amnesia"]["special_defense"] = [['+7', 'user', 100.0, 1], ['+2', 'user', 100.0, 2]]

  # crunch
  moveDict["crunch"]["stat_modifications"]["defense"] = [['-1', 'target', 20.0, 2], ['+0', 'target', 0.0, 4]]
  moveDict["crunch"]["stat_modifications"]["special_defense"] = [['+0', 'target', 0.0, 2], ['-1', 'target', 20.0, 4]]

  # diamond_storm
  moveDict["diamond_storm"]["stat_modifications"]["defense"] = [['+1', 'user', 50.0, 6], ['+2', 'user', 50.0, 7]]

  # fell_stinger
  moveDict["fell_stinger"]["stat_modifications"]["attack"] = [['+2', 'user', 100.0, 6], ['+3', 'user', 100.0, 7]]

  # focus_energy
  moveDict["focus_energy"]["stat_modifications"]["critical_hit_ratio"] = [['+1', 'user', 100.0, 2], ['+2', 'user', 100.0, 3]]
  moveDict["z_focus_energy"]["stat_modifications"]["critical_hit_ratio"] = [['+7', 'user', 100.0, 7]]
  moveDict["z_focus_energy"]["stat_modifications"]["accuracy"] = [['+1', 'user', 100.0, 7]]

  # growth
  moveDict["growth"]["stat_modifications"]["special_attack"] = [['+1', 'user', 100.0, 1]]
  moveDict["growth"]["stat_modifications"]["attack"] = [['+2', 'user', 100.0, 1]]
  moveDict["growth"]["stat_modifications"]["special_defense"] = [['+1', 'user', 100.0, 1], ["+0", 'user', 0.0, 2]]
  moveDict["z_growth"]["stat_modifications"]["special_attack"] = [['+2', 'user', 100.0, 1]]
  #endregion

  return

# update types to account for physical/special split, and add other exceptions
def updateMoveCategory(moveDict):
  for moveName in moveDict.keys():
    # compute type for move to account for physical/special split
    type = moveDict[moveName]["type"][-1][0]
    moveGen = moveDict[moveName]["gen"]
    category = moveDict[moveName]["category"][0][0]

    if category == 'status':
      moveDict[moveName]["category"] = [["status", moveGen]]
      continue
    elif category == '???':
      moveDict[moveName]["category"] == [["varies", moveGen]]
    elif moveGen < 4:
      # special moves which were physical prior to gen 4 due to their type
      if type in ['normal', 'fighting', 'flying', 'poison', 'ground', 'rock', 'bug', 'ghost', 'steel'] and category == 'special':
         moveDict[moveName]["category"] = [['physical', moveGen]] + [[category, 4]]
      # physical moves which were special prior to gen 4 due to their type
      elif type in ['fire', 'water', 'grass', 'electric', 'psychic', 'ice', 'dragon', 'dark'] and category == 'physical':
        moveDict[moveName]["category"] = [['special', moveGen]] + [[category, 4]]

  # hard-code exceptions; moves whose type varies
  moveDict["hidden_power"]["category"] = [['varies', 2], ['special', 4]]

  moveDict["weather_ball"]["category"] = [['varies', 3], ['special', 4]]

  return

# add flag for moves removed from gen 8
def removedFromGen8(fname, moveDict):
  with open(fname, 'r', encoding='utf-8') as removedCSV:
    reader = csv.DictReader(removedCSV)
    for row in reader:
      moveDict[row["Move Name"]]["removed_from_gen8"] = True

  return

# turn various strings into numeric types
def enforceDataTypes(moveDict):
  for moveName in moveDict.keys():
    # update pp, power, accuracy to be ints
    for keyName in ["pp", "power", "accuracy"]:
      patches = moveDict[moveName][keyName]

      transformedPatches = []
      for patch in patches:
        value, patchGen = patch
        if str(value).isnumeric():
          transformedPatches.append([int(value), patchGen])
        elif value == '':
          transformedPatches.append([0, patchGen])
        else:
          transformedPatches.append(patch)
      moveDict[moveName][keyName] = transformedPatches

  return

# add base moves/pokemon/move type requirements for max, gmax, and z moves
def addRequirementData(fname, moveDict):
  with open(fname, 'r', encoding='utf-8') as requirementCSV: 
    reader = csv.DictReader(requirementCSV)

    # # dict for easy access to elemental type of moves in gen 7
    # gen7MoveTypes = {}
    # for moveName in moveDict.keys():
    #   # ignore lgpe moves
    #   gen7MoveType = [patch for patch in moveDict[moveName]["type"] if patch[-1] != 'lgpe_only' and patch[-1] <= 7]
    #   if gen7MoveType:
    #     gen7MoveTypes[moveName] = gen7MoveType[0][0]

    for row in reader:
      moveName, requirement1, requirement2 = row["Move Name"], [row["Requirement 1 Class"], row["Requirement 1 Name"]], [row["Requirement 2 Class"], row["Requirement 2 Name"]]

      moveGen = moveDict[moveName]["gen"]
      
      if 'requirements' not in moveDict[moveName].keys():
        moveDict[moveName]["requirements"] = {}

      for requirement in [requirement1, requirement2]:
        reqClass, reqName = requirement

        # indicates empty requirement, e.g. requirement2 is empty when there's only one requirement.
        if reqClass == '':
          continue

        if reqClass not in moveDict[moveName]["requirements"].keys():
          moveDict[moveName]["requirements"][reqClass] = {}
        moveDict[moveName]["requirements"][reqClass][reqName] = [[True, moveGen]]
        
        # # g-max moves and certain z-moves
        # if reqClass == 'pokemon':
        #   if 'pokemon' not in moveDict[moveName]["requirements"].keys():
        #     moveDict[moveName]["requirements"]["pokemon"] = []
        #   moveDict[moveName]["requirements"]["pokemon"].append(reqName)
        # # max moves, g-max moves, and z-moves
        # elif reqClass == 'type':
        #   moveDict[moveName]["requirements"]["type"] = reqName
        # # status z-moves and max guard
        # elif reqClass == 'category':
        #   moveDict[moveName]["requirements"]["category"] = reqName
        # elif reqClass == 'move':
        #   moveDict[moveName]["requirements"]["move"] = reqName
  
  # add item requirement data for status and generic Z-moves.
  for moveName in [moveName for moveName in moveDict.keys() if 'z_' in moveName]:
    moveType = moveDict[moveName]["type"][0][0]

    if 'item' not in moveDict[moveName]["requirements"].keys():
      moveDict[moveName]["requirements"]["item"] = {}

    if not mapZCrystalToType(moveType):
      print(moveName, moveType, 'has no Z-Crystal!')
    else: 
      crystalName = mapZCrystalToType(moveType)
      moveDict[moveName]["requirements"]["item"][crystalName] = [[True, 7]]


  with open(getCSVDataPath() + '/moves/movesZList.csv', encoding='utf-8') as zMoveListCSV:
    reader = csv.DictReader(zMoveListCSV)


    for row in reader:
      moveName, crystalName = row["Z-Move Name"], row["Z-Crystal Name"]

      if 'item' not in moveDict[moveName]["requirements"].keys():
        moveDict[moveName]["requirements"]["item"] = {}
        
      moveDict[moveName]["requirements"]["item"][crystalName] = [[True, 7]]

  return

def mapZCrystalToType(typeName):
  if typeName in ['bug', 'dark']:
    return typeName + 'inium_z'
  elif typeName in ['dragon', 'ghost', 'grass', 'ground', 'normal', 'poison', 'rock', 'steel', 'water']:
    return typeName + 'ium_z'
  elif typeName in ['fairy', 'fighting', 'fire', 'ice', 'flying']:
    return typeName[:-1] + 'ium_z'
  elif typeName in ['psychic', 'electric']:
    return typeName[:-1] + 'um_z'
  else:
    print(f'{typeName} not handled!')
    return False

# add data for power that a base move gives to the corresponding z-move, max move, or g-max move
def addZPowerMaxPowerData(maxPower_fname, zPower_fname, moveDict):
  # add power for g-max and max moves
  with open(maxPower_fname, 'r', encoding='utf-8') as maxPowerCSV:
    reader = csv.DictReader(maxPowerCSV)

    for row in reader:
      moveName, maxPower = row["Move Name"], int(row["Max Power"])
      moveDict[moveName]["max_power"] = maxPower

      # most g-max moves have the same power as the max move of the same type, except for the 3 galar starters
      if moveName in ['g_max_drum_solo', 'g_max_fireball', 'g_max_hydrosnape']:
        moveDict[moveName]["g_max_power"] = 160
      else:
        moveDict[moveName]["g_max_power"] = maxPower
  
  with open(zPower_fname, 'r', encoding='utf-8') as zPowerCSV:
    reader = csv.DictReader(zPowerCSV)

    for row in reader:
      moveName, zPower = row["Move Name"].replace('vice_grip', 'vise_grip'), int(row["Z-Power"])
      moveDict[moveName]["z_power"] = zPower

  return

# Add moves which interact with other moves, as well as those which work with King's Rock
def addInteractionData(interaction_fname, kings_rock_fname, moveDict):
  # Add move interaction data
  with open(interaction_fname, 'r', encoding='utf-8') as interactionCSV:
    reader = csv.reader(interactionCSV)

    for moveName in moveDict.keys():
      moveDict[moveName]["move_interactions"] = {}

    # skip header
    next(reader, None)

    for row in reader:
      activeMoveName, targetMoveName, genInfo = row[0], row[1], row[2:]
      
      moveDict[targetMoveName]["move_interactions"][activeMoveName] = []
      for gen in range(1, len(genInfo) + 1):
        # ignore gens where targetMoveName wasn't present
        if gen < moveDict[targetMoveName]["gen"]:
          continue
        moveDict[targetMoveName]["move_interactions"][activeMoveName].append([genInfo[gen - 1] == 'T', gen])
    
  # add protect data to other moves, since the Bulbapedia data is given in terms of moves which DON'T interact with Protect in one or more generations (which we have accounted for in the .csv; 'T' still indicates the move interacts with Protect), there are additional moves which DO interact with Protect
  # We also add data for moves whose protection effects are virtually identical to Protect (i.e. block both damaging AND status moves), up to potentially some differences in moves which bypass it (which are handled in the moveInteractions.csv)
  for protectLikeMoveName in ['protect', 'baneful_bunker', 'spiky_shield', 'detect']:
    for moveName in moveDict.keys():
      protectLikeMoveGen = moveDict[protectLikeMoveName]["gen"]

      # indicates moveName has already been handled
      if protectLikeMoveName in moveDict[moveName]["move_interactions"].keys():
        continue
      else:
        moveDict[moveName]["move_interactions"][protectLikeMoveName] = []

      for gen in range(max(protectLikeMoveGen, moveDict[moveName]["gen"]), numberOfGens() + 1):
        # Check targetting
        targetData = ''
        # iterate over patches and choose the latest patch up to/prior to gen
        for patch in moveDict[moveName]["target"]:
          if patch[-1] > gen:
            continue
          targetData = patch[0]

        hostileMove = targetData in ['all_adjacent', 'adjacent_foe', 'all_adjacent_foes', 'all_foes', 'any', 'any_adjacent']
        
        # moves which target user, allies, or all Pokemon bypass protect
        if targetData in ['user', 'all', 'user_and_all_allies'] or not hostileMove:
          moveDict[moveName]["move_interactions"][protectLikeMoveName].append([False, gen])
          continue

        # Check whether moves creates hazards
        createsHazard = False
        if 'creates_hazard' in moveDict[moveName]["effects"].keys():
          # iterate over patches and choose the latest patch up to/prior to gen
          for patch in moveDict[moveName]["effects"]["creates_hazard"]:
            if patch[-1] > gen:
              continue
            createsHazard = patch[0]
        
        # hazard moves ignore Protect
        if createsHazard:
          moveDict[moveName]["move_interactions"][protectLikeMoveName].append([False, gen])
          continue
        
        # Z-moves and max moves technically bypass Protect, but they still interact with it in that Protect reduces their damage, so we include them
        # Status Z-Moves are blocked by Protect
        moveDict[moveName]["move_interactions"][protectLikeMoveName].append([True, gen])

  # add protect data for moves which block damaging-but-not-status moves
  for obstructLikeMoveName in ['obstruct', 'kings_shield', 'mat_block', 'obstruct']:
    for moveName in moveDict.keys():
      obstructLikeMoveGen = moveDict[obstructLikeMoveName]["gen"]

      # indicates moveName has already been handled
      if obstructLikeMoveName in moveDict[moveName]["move_interactions"].keys():
        continue
      else:
        moveDict[moveName]["move_interactions"][obstructLikeMoveName] = []

      for gen in range(max(obstructLikeMoveGen, moveDict[moveName]["gen"]), numberOfGens() + 1):
        # Check targetting
        targetData = ''
        # iterate over patches and choose the latest patch up to/prior to gen
        for patch in moveDict[moveName]["target"]:
          if patch[-1] > gen:
            continue
          targetData = patch[0]

        hostileMove = targetData in ['all_adjacent', 'adjacent_foe', 'all_adjacent_foes', 'all_foes', 'any', 'any_adjacent']

        # Check whether moveName is Status
        statusMove = False

        # iterate over patches and choose the latest patch up to/prior to gen
        for patch in moveDict[moveName]["category"]:
          # indicates patch is later than gen, so irrelevant to the calculation
          if patch[-1] > gen:
            continue
          else:
            statusMove = patch[0] == 'status'
        
        # status moves bypass Obstruct
        if not hostileMove or statusMove:
          moveDict[moveName]["move_interactions"][obstructLikeMoveName].append([False, gen])
        else:
          moveDict[moveName]["move_interactions"][obstructLikeMoveName].append([True, gen])


  # add protect data for moves which block status moves; we write it this way even though there's only one move like crafty shield (itself), in anticipation of future moves
  for craftyShieldLikeMoveName in ['crafty_shield']:
    for moveName in moveDict.keys():
      craftyShieldLikeMoveGen = moveDict[craftyShieldLikeMoveName]["gen"]

      # indicates moveName has already been handled
      if craftyShieldLikeMoveName in moveDict[moveName]["move_interactions"].keys():
        continue
      else:
        moveDict[moveName]["move_interactions"][craftyShieldLikeMoveName] = []

      for gen in range(max(craftyShieldLikeMoveGen, moveDict[moveName]["gen"]), numberOfGens() + 1):
        # Check targetting
        targetData = ''
        # iterate over patches and choose the latest patch up to/prior to gen
        for patch in moveDict[moveName]["target"]:
          if patch[-1] > gen:
            continue
          targetData = patch[0]

        hostileMove = targetData in ['all_adjacent', 'adjacent_foe', 'all_adjacent_foes', 'all_foes', 'any', 'any_adjacent']

        # Check whether moveName is Status
        statusMove = False

        # iterate over patches and choose the latest patch up to/prior to gen
        for patch in moveDict[moveName]["category"]:
          # indicates patch is later than gen, so irrelevant to the calculation
          if patch[-1] > gen:
            continue
          else:
            statusMove = patch[0] == 'status'
        
        # crafty shield blocks hostile status moves
        if hostileMove and statusMove:
          moveDict[moveName]["move_interactions"][craftyShieldLikeMoveName].append([True, gen])
        else:
          moveDict[moveName]["move_interactions"][craftyShieldLikeMoveName].append([False, gen])

  # add protect data for moves which block status moves; we write it this way even though there's only one move like Wide Guard (itself), in anticipation of future moves
  for wideGuardLikeMoveName in ['wide_guard']:
    for moveName in moveDict.keys():
      wideGuardLikeMoveGen = moveDict[wideGuardLikeMoveName]["gen"]

      # indicates moveName has already been handled
      if wideGuardLikeMoveName in moveDict[moveName]["move_interactions"].keys():
        continue
      else:
        moveDict[moveName]["move_interactions"][wideGuardLikeMoveName] = []

      for gen in range(max(wideGuardLikeMoveGen, moveDict[moveName]["gen"]), numberOfGens() + 1):
        # Check targetting

        targetData = ''
        # iterate over patches and choose the latest patch up to/prior to gen
        for patch in moveDict[moveName]["target"]:
          if patch[-1] > gen:
            continue
          targetData = patch[0]

        # Check whether moveName is Status
        statusMove = False

        # iterate over patches and choose the latest patch up to/prior to gen
        for patch in moveDict[moveName]["category"]:
          # indicates patch is later than gen, so irrelevant to the calculation
          if patch[-1] > gen:
            continue
          else:
            statusMove = patch[0] == 'status'
        
        # damaging moves which target multiple Pokemon are blocked
        if targetData in ['all_adjacent', 'all_adjacent_foes', 'all_foes']:
          if not statusMove:
            moveDict[moveName]["move_interactions"][wideGuardLikeMoveName].append([True, gen]) 
          # status moves which target multiple Pokemon are blocked after Gen 7  
          elif gen > 7:
            moveDict[moveName]["move_interactions"][wideGuardLikeMoveName].append([True, gen]) 
        else:
          moveDict[moveName]["move_interactions"][wideGuardLikeMoveName].append([False, gen])

  # add protect data for moves which block priority moves; we write it this way even though there's only one move like Quick Guard (itself), in anticipation of future moves 
  for quickGuardLikeMoveName in ['quick_guard']:
    for moveName in moveDict.keys():
      quickGuardLikeMoveGen = moveDict[quickGuardLikeMoveName]["gen"]

      # indicates moveName has already been handled
      if quickGuardLikeMoveName in moveDict[moveName]["move_interactions"].keys():
        continue
      else:
        moveDict[moveName]["move_interactions"][quickGuardLikeMoveName] = []

      for gen in range(max(quickGuardLikeMoveGen, moveDict[moveName]["gen"]), numberOfGens() + 1):
        # Check targetting
        targetData = ''
        # iterate over patches and choose the latest patch up to/prior to gen
        for patch in moveDict[moveName]["target"]:
          if patch[-1] > gen:
            continue
          targetData = patch[0]

        hostileMove = targetData in ['all_adjacent', 'adjacent_foe', 'all_adjacent_foes', 'all_foes', 'any', 'any_adjacent']

        # Calculate priority of moveName
        priority = 0

        # iterate over patches and choose the latest patch up to/prior to gen
        for patch in moveDict[moveName]["priority"]:
          # indicates patch is later than gen, so irrelevant to the calculation
          if patch[-1] > gen:
            continue
          else:
            priority = patch[0]
        
        # blocks moves which target the user's side and have increased priority; note that Quick Guard only has +3 priority, so moves which have priority > 3 will bypass it
        # Feint is an increased priority move which bypasses quick guard; note that Quick Guard DOES block Feint if the user of Feint is an ally
        if hostileMove and priority > 0 and priority <= 3 and moveName != 'feint':
          moveDict[moveName]["move_interactions"][quickGuardLikeMoveName].append([True, gen]) 
        else:
          moveDict[moveName]["move_interactions"][quickGuardLikeMoveName].append([False, gen])
  
  # Max Guard
  for moveName in moveDict.keys():
    # indicates moveName has already been handled
    if 'max_guard' in moveDict[moveName]["move_interactions"].keys():
      continue
    else:
      moveDict[moveName]["move_interactions"]["max_guard"] = []

      for gen in range(max(8, moveDict[moveName]["gen"]), numberOfGens() + 1):
        # Check targetting

        targetData = ''
        # iterate over patches and choose the latest patch up to/prior to gen
        for patch in moveDict[moveName]["target"]:
          if patch[-1] > gen:
            continue
          targetData = patch[0]

        hostileMove = targetData in ['all_adjacent', 'adjacent_foe', 'all_adjacent_foes', 'all_foes', 'any', 'any_adjacent']
        
        # blocks hostile moves, including Z-Moves and G-Max moves
        if hostileMove:
          moveDict[moveName]["move_interactions"]["max_guard"].append([True, gen]) 
        else:
          moveDict[moveName]["move_interactions"]["max_guard"].append([False, gen])

  # Add King's Rock data
  with open(kings_rock_fname, 'r', encoding='utf-8') as kingsRockCSV:
    reader = csv.reader(kingsRockCSV)

    for moveName in moveDict.keys():
      moveDict[moveName]["item_interactions"] = {}

    # skip header
    next(reader, None)

    for row in reader:
      moveName, genInfo = row[0], row[1:]
      
      moveDict[moveName]["item_interactions"]["kings_rock"] = []
      
      # .csv only has data up to Gen 4, since from Gen 5 onwards, all non-flinching damagaing move are affected by King's Rock
      for gen in range(1, 5):
        # ignore gens where moveName wasn't present
        if gen < moveDict[moveName]["gen"]:
          continue
        moveDict[moveName]["item_interactions"]["kings_rock"].append([genInfo[gen - 1] == 'T', gen])

    # add data for Gen 5 onward
    for moveName in moveDict.keys():
      moveGen = moveDict[moveName]["gen"]

      # initialize king's rock data for unhandled moves
      if "kings_rock" not in moveDict[moveName]["item_interactions"].keys():
        moveDict[moveName]["item_interactions"]["kings_rock"] = []
        for gen in range(max(2, moveGen), 5):
          moveDict[moveName]["item_interactions"]["kings_rock"].append([False, gen])
      
      for gen in range(max(5, moveGen), numberOfGens() + 1):

        # check criteria for moveName to be affected by King's Rock: damaging and not flinching
        # Check whether moveName is Physical, Special, or Varies in Generation gen
        damagingMove = False

        # iterate over patches and choose the latest patch up to/prior to gen
        for patch in moveDict[moveName]["category"]:
          # indicates patch is later than gen, so irrelevant to the calculation
          if patch[-1] > gen:
            continue
          else:
            damagingMove = patch[0] in ['physical', 'special', 'varies']

        # Check that moveName does not flinch in Generation gen
        if 'flinch' in moveDict[moveName]["causes_status"].keys():
          # iterate over patches and choose the latest patch up to/prior to gen
          for patch in moveDict[moveName]["causes_status"]["flinch"]:
            if patch[-1] > gen:
              continue
            else:
              flinchingMove = patch[0] > 0
        else:
          flinchingMove = False

        if damagingMove and not flinchingMove:
          moveDict[moveName]["item_interactions"]["kings_rock"].append([True, gen])
        else:
          moveDict[moveName]["item_interactions"]["kings_rock"].append([False, gen])
      

      

  return

def addFormattedNames(moveDict):
  for moveName in moveDict.keys():
    moveDict[moveName]['formatted_name'] = getFormattedName(moveName)

  return

def getFormattedName(moveName):
  # 10,000,000 Volt Thunderbolt
  if moveName == '10000000_volt_thunderbolt':
    return '10,000,000 Volt Thunderbolt'

  # hyphens
  if moveName in [
    'double_edge',
    'self_destruct',
    'soft_boiled',
    'mud_slap',
    'lock_on',
    'will_o_wisp',
    'wake_up_slap',
    'u_turn',
    'x_scissor',
    'v_create',
    'trick_or_treat',
    'topsy_turvy',
    'baby_doll_eyes',
    'power_up_punch',
    'all_out_pummeling',
    'savage_spin_out',
    'never_ending_nightmare',
    'soul_stealing_7_star_strike',
    'multi_attack'
  ]:
    # first handle special cases of hyphenation
    # Will-O-Wisp
    if moveName == 'will_o_wisp':
      return 'Will-O-Wisp'
    # U-turn
    elif moveName == 'u_turn':
      return 'U-turn'
    # V-create
    elif moveName == 'v_create':
      return 'V-create'
    # Trick-or-Treat
    elif moveName == 'trick_or_treat':
      return 'Trick-or_Treat'
    # Freeze-Dry
    elif moveName == 'freeze_dry':
      return 'Freeze-Dry'
    # Savage Spin-Out
    elif moveName == 'savage_spin_out':
      return 'Savage Spin-Out'
    # Soul-Stealing 7-Star Strike
    elif moveName == 'soul_stealing_7_star_strike':
      return 'Soul-Stealing 7-Star Strike'
    # Otherwise, connect first two words with a hyphen
    else:
      moveName = moveName.replace('_', '-', 1)

  # apostrophes
  if moveName in [
    'forests_curse',
    'kings_shield',
    'lands_wrath',
    'natures_madness',
    'lets_snuggle_forever'
  ]:
    moveName = moveName.replace('s_', '\'s_', 1)

  # Z-moves and G-Max moves
  if 'z_' in moveName or 'g_max_' in moveName:
    moveName = moveName.replace('_', '-', 1)

  return ' '.join(moveName.split('_')).title().replace('\'S', '\'s')

def main():
  # dictionaries containing effect names/gens and status names/gens
  global effectDict
  effectDict = effects.main()
  global statusDict
  statusDict = statuses.main()
  global typeDict
  typeDict = types.main()
  global usageMethodDict
  usageMethodDict = usageMethods.main()

  # holds moveID, Name, Type, Category, Contest, PP, Power, Accuracy, Gen
  dataPath = getCSVDataPath() + '/moves/'

  moveList_fname = dataPath + 'moveList.csv'
  moveDict = makeInitialMoveDict(moveList_fname)

  priority_fname = dataPath + 'movesByPriority.csv'
  addPriorityToMoveDict(priority_fname, moveDict)

  contact_fname = dataPath + f'movesByContact.csv'
  addContactToMoveDict(contact_fname, moveDict)

  effect_fname = dataPath + f'movesByEffect.csv'
  addEffectToMoveDict(effect_fname, moveDict)

  status_fname = dataPath + f'movesByStatus.csv'
  addStatusToMoveDict(status_fname, moveDict)

  target_fname = dataPath + f'movesByTarget.csv'
  addTargetToMoveDict(target_fname, moveDict)

  statMod_fname = dataPath + 'movesModifyStat.csv'
  addStatModToMoveDict(statMod_fname, moveDict)

  updateMoveCategory(moveDict)
  
  removedFromGen8_fname = dataPath + 'movesRemovedFromGen8.csv'
  removedFromGen8(removedFromGen8_fname, moveDict)

  enforceDataTypes(moveDict)

  requirement_fname = dataPath + 'movesByRequirement.csv'
  addRequirementData(requirement_fname, moveDict)

  maxPower_fname = dataPath + 'movesByMaxPower.csv'
  zPower_fname = dataPath + 'movesByZPower.csv'
  addZPowerMaxPowerData(maxPower_fname, zPower_fname, moveDict)

  interaction_fname = dataPath + 'moveInteractions.csv'
  kings_rock_fname = dataPath + 'movesByKingsRock.csv'
  addInteractionData(interaction_fname, kings_rock_fname, moveDict)

  addFormattedNames(moveDict)

  return moveDict

if __name__ == '__main__':
  moveDict = main()

  # check name consistency in moveDict
  print('Checking for inconsistencies...')
  for moveName in moveDict.keys():
    for inconsistency in [
      checkConsistency(moveDict[moveName]["effects"], 'effect', effectDict, False),
      checkConsistency(moveDict[moveName]["causes_status"], 'status', statusDict, 0.0),
      checkConsistency(moveDict[moveName]["resists_status"], 'status', statusDict, False),
      checkConsistency(moveDict[moveName]["usage_method"], 'usage_method', usageMethodDict, False),
    ]:
      if inconsistency:
        print(f'Inconsistency found for {moveName}: {inconsistency}')

    for stat in moveDict[moveName]["stat_modifications"]:
      if stat not in statList():
        print('Inconsistent stat name', moveName, stat)
  print('Finished.')