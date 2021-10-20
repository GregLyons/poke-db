import csv
from functools import cmp_to_key
from utils import getBulbapediaDataPath, genSymbolToNumber, getSerebiiDataPath

# TODO defog only removes terrain in gen8
# TODO 

# Create move .json file with the following data:
# name, description, power, PP, accuracy, category, priority, contact, target, type, gen introduced, where it affects item
# also include whether the move affects stats, and whose stats it affects
# also include whether the move inflicts status, and the probability of inflicting status
# also include any effects the move has
# also include any usage methods the move has


# Used for a few calculations--need to alter when gen 9 comes
def numberOfGens():
  return 8

# get value(s) and generation(s) from description
def parseMoveListNote(note):
  moveID = note[0]
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
        moveID = int(row["Move ID"])

        isMax = row["Move Name"][:3] == "max"
        isGMax = row["Move Name"][:5] == "g_max"
        # the extra checks are for the attacking Z_moves, e.g. 'Breakneck Blitz'
        isZMove = row["Move Name"][:2] == "z_" or (row["PP"] == '1' and row["Accuracy"] == '' and genSymbolToNumber(row["Gen"]) == 7)

        # Many values are lists since they can potentially change across generations--Bulbapedia lists the latest values for each field, with the past values in notes
        moveDict[moveID] = {
          "move_name": row["Move Name"],
          "move_description": "",
          "type": [[row["Type"], 8]],
          "category": [[row["Category"], 8]],
          "pp": [[row["PP"], 8]],
          "power": [[row["Power"], 8]],
          "accuracy": [[row["Accuracy"].rstrip('%'), 8]],
          "gen": genSymbolToNumber(row["Gen"]),
          "removed_from_gen8": False,
          "fixed_damage": None,
          "z_move": isZMove,
          "lgpe_only": False,
          "max_move": isMax,
          "g_max_move": isGMax,
          "effects": {},
          "status": {},
          "stat_modifications": {},
          "usage_method": {},
          "contact": [],
          "priority": [],
          "target": [],
        }

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
      moveDict[int(moveID)]["category"] = [['physical', 6], ['special', 8]]
      continue

    moveID = change[0]
    # type data is under 'move name' header
    header = change[1]
    if header == 'move name':
      header = 'type'
      change[2][0] = change[2][0].lower()
    valueAndGen = change[2]
    
    moveDict[int(moveID)][header].append(valueAndGen)

  # ohko moves [moveID, header, ['ohko', None]]
  ohkoMoves = [note for note in parsedNotes if note[2][0] == 'ohko']
  for ohkoMove in ohkoMoves:
    moveID = int(ohkoMove[0])
    gen = moveDict[moveID]["gen"]
    moveDict[moveID]["effects"]["ohko"] = [[True, gen]]

  # Fixed damage moves [moveID, header, [value + "fixed", Gen]]
  fixedDamageMoves = [note for note in parsedNotes if note[2][0] != None and 'fixed' in note[2][0]]
  for fixedDamageMove in fixedDamageMoves:
    moveID = fixedDamageMove[0]
    moveDict[int(moveID)]["fixed_damage"] = fixedDamageMove[2][0].rstrip('fixed')

  # Value for move in LGPE [moveID, header, [value, "LGPE"]]
  LGPEMoveValues = [note for note in parsedNotes if note[2][1] == 'LGPE']
  for LGPEMoveValue in LGPEMoveValues:
    moveID = LGPEMoveValue[0]
    header = LGPEMoveValue[1]
    moveDict[int(moveID)][header].append(LGPEMoveValue[2])

  # LGPE exclusive move [moveID, header, [None, "LGPE only"]]
  LGPEExclusives = [note for note in parsedNotes if note[2][1] == 'LGPE only']
  for LGPEExclusive in LGPEExclusives:
    moveID = LGPEExclusive[0]
    header = LGPEExclusive[1]
    moveDict[int(moveID)]["lgpe_only"] = True
    for header in ['type', 'pp', 'power', 'accuracy']:
      moveDict[int(moveID)][header][0][1] = "lgpe_only"

  # Value for move which holds in LGPE and in other gens [moveID, header, [value, gen, "LGPE"]]
  # only includes Mega Drain 
  LGPEandGenMoves = [note for note in parsedNotes if len(note[2]) == 3 and note[2][2] == 'LGPE']
  for LGPEandGenMove in LGPEandGenMoves:
    moveID = LGPEandGenMove[0]
    header = LGPEandGenMove[1]
    valueAndGen = [LGPEandGenMove[2][0], LGPEandGenMove[2][1]]
    valueAndLGPE = [LGPEandGenMove[2][0], LGPEandGenMove[2][2]]
    moveDict[int(moveID)][header].append(valueAndGen)
    moveDict[int(moveID)][header].append(valueAndLGPE)

  # For each move in initialMoveDict, sort the "Type", "PP", "Power", and "Accuracy" fields by generation
  for key in moveDict:
    for innerKey in ['type', 'pp', 'power', 'accuracy']:
      if len(moveDict[key][innerKey]) > 1:
        moveDict[key][innerKey].sort(key = cmp_to_key(comparePatches))

  # For each move in initialMoveDict, rewrite the patches in "Type", "PP", "Power", and "Accuracy" fields so that the generation represents the starting gen rather than the ending gen of that value
  for key in moveDict:
    for innerKey in ['type', 'pp', 'power', 'accuracy', 'category']:
      # Split up patch into LGPE_only and other
      LGPEOnlyPatch = [patch for patch in moveDict[key][innerKey] if patch[1] == 'lgpe_only']
      noLGPEOnlyPatches = [patch for patch in moveDict[key][innerKey] if patch[1] != 'lgpe_only']

      # If the move is LGPE_only, no change required
      if LGPEOnlyPatch == moveDict[key][innerKey]:
        continue
      # If the move is not LGPE_only, change the non_LGPE_only patches
      else:
        # If only one non_LGPE_only patch, set gen equal to when move was introduced
        if len(noLGPEOnlyPatches) == 1:
          patch = moveDict[key][innerKey][0]
          value = patch[0]
          moveDict[key][innerKey] = [[value, moveDict[key]["gen"]]]
        # Otherwise, need to determine when the starting gens from the list of ending gens
        else:
          modifiedPatchList = []
          for i in range(len(moveDict[key][innerKey])):
            # first 'patch' applied in gen the move was introduced
            if i == 0:
              modifiedPatchList.append([moveDict[key][innerKey][0][0], moveDict[key]["gen"]])
            # send [value, endGen] to [value, oldEndGen + 1]
            else:
              oldValueEndGen = moveDict[key][innerKey][i - 1][1]
              value = moveDict[key][innerKey][i][0]
              modifiedPatchList.append([value, oldValueEndGen + 1])

          moveDict[key][innerKey] = modifiedPatchList
      if LGPEOnlyPatch:
        moveDict[key][innerKey].append(LGPEOnlyPatch[0])

  # hard code water shuriken type
  moveDict[594]['category'] = [['physical', 6], ['special', 8]]
  moveDict[594]['type'] = [['water', 6]]

  return moveDict

# Uses move list located at fname to make inverse lookup of moveID from moveName possible
def makeInverseDict(fname):
  inverseDict = {}

  with open(fname, encoding='utf-8') as movesCSV:
    reader = csv.DictReader(movesCSV)
    for row in reader:
      if row["Move ID"] != "???":
        inverseDict[row["Move Name"]] = int(row["Move ID"])

  return inverseDict

# read priority data and update moveDict
def addPriorityToMoveDict(fname, moveDict, inverseDict):
  with open(fname, encoding='utf-8') as priorityCSV:
    reader = csv.DictReader(priorityCSV)

    for row in reader:
      if row["Move Name"] != 'none' and row["Move Name"] != 'fleeing':
        moveID = inverseDict[row["Move Name"]]
        # we add duplicate entries for when moves maintain the same priority across generations--we will handle this in the next loop to account for zero_priority moves
        moveDict[int(moveID)]["priority"].append([int(row["Priority"]), int(row["Gen"])])

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
  moveDict[100]["priority"].append([-6, 'lgpe_only'])

  return

# read contact data and update moveDict
def addContactToMoveDict(fname, moveDict, inverseDict):
  # initially, no moves make contact
  for key in moveDict.keys():
    moveDict[key]["contact"] = [[False, max(moveDict[key]["gen"], 3)]]

  with open(fname, encoding='utf-8') as contactCSV:
    reader = csv.DictReader(contactCSV)
    for row in reader:
      moveName = row["Move Name"]
      note = row["Note"]
      genOfMoveName = moveDict[inverseDict[moveName]]["gen"]

      if note == '--':
        # contact as a mechanic was introduced in Gen 3
        moveDict[inverseDict[moveName]]["Contact"] = [[True, max(genOfMoveName, 3)]]
      else:
        if note == 'Gen IV onward':
          moveDict[inverseDict[moveName]]["Contact"].append([True, 4])
        elif note == 'Only Gen III':
          moveDict[inverseDict[moveName]]["Contact"] = [[True, 3], [False, 4]]

  return

# read effect data and update moveDict
def addEffectToMoveDict(fname, moveDict, inverseDict):

  with open(fname, encoding='utf-8') as effectCSV:
    reader = csv.DictReader(effectCSV)

    # get effects and add them to moveDict with initial value False
    for row in reader:
      effect = row["Effect Name"]
      moveName = row["Move Name"]
      
      currentKey = inverseDict[moveName]

      # distinguish between usage method and other effects
      if effect in ['pulse', 'ball', 'bite', 'dance', 'explosive', 'mouth', 'powder', 'punch', 'sound']:
        # # if usage_method isn't in moveDict, add it and initialize as False
        # if effect not in moveDict[1]["usage_method"]:
        #   for key in moveDict.keys():
        #     moveDict[key]["usage_method"][effect] = [[False, moveDict[key]["gen"]]]
        moveDict[currentKey]["usage_method"][effect] = [[True, moveDict[currentKey]["gen"]]]
      else:
      # # if effect isn't in moveDict, add it and initialize as False
      #   if effect not in moveDict[1]["effects"] :
      #       for key in moveDict.keys():
      #         moveDict[key]["effects"][effect] = [[False, moveDict[key]["gen"]]]

        moveDict[currentKey]["effects"][effect] = [[True, moveDict[currentKey]["gen"]]]
      

  # EXCEPTIONS SECTION
  # not covered in the above .csv
  exceptions = [
    ['suppresses_ability', ['core_enforcer', 'gastro_acid']],
    ['use_different_stat', ['body_press', 'psyshock', 'psystrike', 'secret_sword']],
    ['can_crash', ['high_jump_kick', 'jump_kick']],
    ['changes_damage_category', ['light_that_burns_the_sky', 'photon_geyser', 'shell_side_arm']],
    ['punishes_contact', ['baneful_bunker', 'beak_blast', 'kings_shield', 'obstruct', 'spiky_shield']],
    ['affects_weight', ['autotomize']]
  ]
  for exception in exceptions:
    effect = exception[0]
    # go through exceptions
    moveNames = exception[1]
    for moveName in moveNames:
      key = inverseDict[moveName]
      moveDict[key][effect] = [[True, moveDict[key]["gen"]]]

  # still more exceptions
  moveDict[inverseDict["astonish"]]["effects"]['anti_mini'] = [[True, 3], [False, 4]]
  moveDict[inverseDict["earthquake"]]["effects"]['hits_semi_invulnerable'] = [[False, 1], [True, 2]]

  # cannot_crit effect
  for key in moveDict.keys():
    moveDict[key]["effects"]["cannot_crit"] = [[False, moveDict[key]["gen"]]]

  moveDict[inverseDict['flail']]["effects"]['cannot_crit'] = [[True, 2], [False, 3]]
  moveDict[inverseDict['future_sight']]["effects"]['cannot_crit'] = [[True, 2], [False, 5]]
  moveDict[inverseDict['reversal']]["effects"]['cannot_crit'] = [[True, 2], [False, 3]]
  moveDict[inverseDict['doom_desire']]["effects"]['cannot_crit'] = [[True, 3], [False, 5]]
  moveDict[inverseDict['spit_up']]["effects"]['cannot_crit'] = [[True, 3], [False, 4]]

  # high crit ratio
  moveDict[inverseDict['razor_wind']]["effects"]['high_crit_chance'] = [[False, 1], [True, 2]]
  moveDict[inverseDict['sky_attack']]["effects"]['high_crit_chance'] = [[False, 1], [True, 3]]

  # haze
  moveDict[inverseDict['haze']]["effects"]['resets_stats'] = [[True, 1]]
  moveDict[inverseDict['haze']]["effects"]['removes_screens'] = [[True, 1], [False, 2]]

  return

# read status data and update moveDict
def addStatusToMoveDict(fname, moveDict, inverseDict):
  with open(fname, encoding='utf-8') as csvFile:
    reader = csv.DictReader(csvFile)

    for row in reader:
      status = row["Status Caused"]
      moveName = row["Move Name"]
      probability = float(row["Probability"])

      # if status not in moveDict[1]["status"]:
      #   for key in moveDict.keys():
      #     moveDict[key]["status"][status] = [[0, moveDict[key]["gen"]]]
      
      key = inverseDict[moveName]
      moveDict[key]["status"][status] = [[probability, moveDict[key]["gen"]]]

  # EXCEPTIONS SECTION
  # Fire Blast had 30% to burn in Gen 1
  moveDict[inverseDict["fire_blast"]]["status"]["burn"] = [
    [30.0, 1], 
    [10.0, 2]
  ]

  # Tri Attack only applied statuses from Gen 2 on
  for status in ['burn', 'freeze', 'paralysis']:
    moveDict[inverseDict["tri_attack"]]["status"][status] = [
      [0.0, 1],
      [6.67, 2]
    ]

  # Thunder had 10% change to paralyze in Gen 1
  moveDict[inverseDict["thunder"]]["status"]["paralysis"] = [
    [10.0, 1], 
    [30.0, 2]
  ]

  # Poison Sting had 20% chance to poison in Gen 1
  moveDict[inverseDict["poison_sting"]]["status"]["poison"] = [
    [20.0, 1], 
    [30.0, 2]
  ]
  moveDict[inverseDict["sludge"]]["status"]["poison"] = [
    [40.0, 1], 
    [30.0, 2]
  ]

  # Chatter has variable chance to confuse in Gens 4 and 5--we choose the highest value in each gen
  moveDict[inverseDict["chatter"]]["status"]["confusion"] = [
    [31.0, 4],
    [10.0, 5],
    [100.0, 6]
  ]

  # Sky Attack only causes Flinch starting in Gen 3
  moveDict[inverseDict["sky_attack"]]["status"]["flinch"] = [
    [0.0, 1],
    [30.0, 3]
  ]

  # Other notes in movesThatCauseStatusNotes.csv don't apply to status

  return

# read target data and update moveDict
def addTargetToMoveDict(fname, moveDict, inverseDict):
  with open(fname, encoding='utf-8') as targetCSV:
    reader = csv.DictReader(targetCSV)

    # 'any_adjacent' is the most common targetting class
    for key in moveDict.keys():
      moveDict[key]["target"] = [['any_adjacent', moveDict[key]["gen"]]]

    for row in reader:
      target = row["Targets"]
      moveName = row["Move Name"]
      
      key = inverseDict[moveName]
      moveDict[key]["target"] = [[target, moveDict[key]["gen"]]]

    # hard code exceptions
    #region
    # helping_hand
    helpingHandKey = inverseDict["helping_hand"]
    moveDict[helpingHandKey]["target"] = [["self", 3], ["adjacent_ally", 4]]

    # surf
    surfKey = inverseDict["surf"]
    moveDict[surfKey]["target"] = [["all_foes", 3], ["all_adjacent"], 4]

    # conversion_2
    conversion2Key = inverseDict["conversion_2"]
    moveDict[conversion2Key]["target"] = [["user", 2], ["any_adjacent", 5]]

    # poison_gas
    poisonGasKey = inverseDict["poison_gas"]
    moveDict[poisonGasKey]["target"] = [["any_adjacent", 1], ["all_adjacent_foes", 5]]

    # cotton_spore
    cottonSporeKey = inverseDict["cotton_spore"]
    moveDict[cottonSporeKey]["target"] = [["adjacent", 2], ["all_adjacent_foes", 6]]

    # nature_power
    naturePowerKey = inverseDict["nature_power"]
    moveDict[naturePowerKey]["target"] = [["user", 5], ["adjacent", 6]]

    # howl
    howlKey = inverseDict["howl"]
    moveDict[howlKey]["target"] = [["user", 3], ["user_and_all_allies", 8]]
    #endregion
  return

# read description data and update moveDict
def addDescriptionToMoveDict(fname, moveDict, inverseDict):
  with open(fname, encoding='utf-8') as descriptionCSV:
    reader = csv.DictReader(descriptionCSV)
    
    for row in reader:
      moveName, moveDescription = row["Move Name"], row["Move Description"]
      key = inverseDict[moveName]
      moveDict[key]["move_description"] = moveDescription
  return

# read stat modification data and update moveDict
def addStatModToMoveDict(fname, moveDict, inverseDict):
  with open(fname, encoding='utf-8') as statModCSV:
    reader = csv.reader(statModCSV)
    next(reader)

    for row in reader:
      moveName, gen, stat, modifier, sign, recipient, probability = row
      moveKey = inverseDict[moveName]

      # for belly drum--it always sets attack stage to +6, even if it's negative beforehand
      if modifier == 'max':
        modifier = 12
      gen, modifier, probability = int(gen), int(modifier), float(probability)

      if sign == '-':
        modifier = -modifier

      # if stat not in moveDict[1]["stat_modifications"]:
      #   for key in moveDict:
      #     moveDict[key]["stat_modifications"][stat] = [[0, '', moveDict[key], 0.0, ["gen"]]]
      
      # indicates move has always modified that stat as described
      if gen == moveDict[moveKey]["gen"]:
        moveDict[moveKey]["stat_modifications"][stat] = [[modifier, recipient, probability, gen]]
      # indicate move's stat modification was introduced in a later gen
      else:
        if stat not in moveDict[moveKey]["stat_modifications"]:
          moveDict[moveKey]["stat_modifications"][stat] = []

        moveDict[moveKey]["stat_modifications"][stat].append([modifier, recipient, probability, gen])
  
  # hard code exceptions
  #region
  # acid
  acidKey = inverseDict["acid"]
  moveDict[acidKey]["stat_modifications"]["defense"] = [[-1, 'target', 33.2, 1], [-1, 'target', 10.0, 2], [0, 'target', 0.0, 4]]
  moveDict[acidKey]["stat_modifications"]["special_defense"] = [[0, 'target', 0.0, 1], [-1, 'target', 10.0, 4]]

  # aurora beam
  auroraBeamKey = inverseDict["aurora_beam"]
  moveDict[auroraBeamKey]["attack"] = [[-1, 'target', 33.2, 1], [-1, 'target', 10.0, 2]]

  # bubble
  bubbleKey = inverseDict["bubble"]
  moveDict[bubbleKey]["speed"] = [[-1, 'target', 33.2, 1], [-1, 'target', 10.0, 2]]
  
  # bubble beam
  bubbleBeamKey = inverseDict["bubble_beam"]
  moveDict[bubbleBeamKey]["speed"] = [[-1, 'target', 33.2, 1], [-1, 'target', 10.0, 2]]

  # constrict
  constrictKey = inverseDict["constrict"]
  moveDict[constrictKey]["speed"] = [[-1, 'target', 33.2, 1], [-1, 'target', 10.0, 2]]

  # psychic
  psychicKey = inverseDict["psychic"]
  moveDict[psychicKey]["special_attack"] = [[-1, 'target', 33.2, 1], [0, 'target', 0.0, 2]]
  moveDict[psychicKey]["special_defense"] = [[-1, 'target', 33.2, 1], [-1, 'target', 10.0, 2]]

  # amnesia
  amnesiaKey = inverseDict["amnesia"]
  moveDict[amnesiaKey]["special_attack"] = [[2, 'user', 100.0, 1], [0, 'user', 0.0, 2]]
  moveDict[amnesiaKey]["special_defense"] = [[2, 'user', 100.0, 1], [2, 'user', 100.0, 2]]

  # crunch
  crunchKey = inverseDict["crunch"]
  moveDict[crunchKey]["stat_modifications"]["defense"] = [[-1, 'target', 20.0, 2], [0, 'target', 0.0, 4]]
  moveDict[crunchKey]["stat_modifications"]["special_defense"] = [[0, 'target', 0.0, 2], [-1, 'target', 20.0, 4]]

  # diamond_storm
  diamondStormKey = inverseDict["diamond_storm"]
  moveDict[diamondStormKey]["stat_modifications"]["defense"] = [[1, 'user', 50.0, 6], [2, 'user', 50.0, 7]]

  # fell_stinger
  fellStingerKey = inverseDict["fell_stinger"]
  moveDict[fellStingerKey]["stat_modifications"]["attack"] = [[2, 'user', 100.0, 6], [3, 'user', 100.0, 7]]

  # focus_energy
  focusEnergyKey = inverseDict["focus_energy"]
  moveDict[focusEnergyKey]["stat_modifications"]["critical_hit_ratio"] = [[1, 'user', 100.0, 2], [2, 'user', 100.0, 3]]

  #endregion

  return
  # EXCEPTIONS: ['secret_power', 'crunch', 'diamond_storm', 'acid', 'psychic', 'amnesia', 'shadow_down', 'focus_energy', 'aurora_beam', 'bubble', 'bubble_beam', 'constrict']
  # Secret Power has a complicated Bulbapedia description to parse, with tables
  # Crunch, Acid, Focus Energy, and Diamond Storm have changed their stat modifications between generations
  # Psychic and Amnesia have also changed their stat modifications if you count the Special split
  # Shadow Down doesn't exist

# update types to account for physical/special split, and add other exceptions
def updateMoveCategory(moveDict, inverseDict):
  for key in moveDict.keys():
    # compute type for move to account for physical/special split
    type = moveDict[key]["type"][-1][0]
    gen = moveDict[key]["gen"]
    category = moveDict[key]["category"][0][0]

    if category == 'status':
      moveDict[key]["category"] = [["status", gen]]
      continue
    elif category == '???':
      moveDict[key]["category"] == [["varies", gen]]
    elif gen < 4:
      # special moves which were physical prior to gen 4 due to their type
      if type in ['normal', 'fighting', 'flying', 'poison', 'ground', 'rock', 'bug', 'ghost', 'steel'] and category == 'special':
         moveDict[key]["category"] = [['physical', gen]] + [[category, 4]]
      # physical moves which were special prior to gen 4 due to their type
      elif type in ['fire', 'water', 'grass', 'electric', 'psychic', 'ice', 'dragon', 'dark'] and category == 'physical':
        moveDict[key]["category"] = [['special', gen]] + [[category, 4]]

  # hard-code exceptions; moves whose type varies
  hiddenPowerKey = inverseDict['hidden_power']
  moveDict[hiddenPowerKey]["category"] = [['varies', 3], ['special', 4]]

  weatherBallKey = inverseDict['weather_ball']
  moveDict[weatherBallKey]["category"] = [['varies', 3], ['special', 4]]

  return

# add flag for moves removed from gen 8
def removedFromGen8(fname, moveDict):
  with open(fname, 'r', encoding='utf-8') as removedCSV:
    reader = csv.DictReader(removedCSV)
    for row in reader:
      moveDict[int(row["Move ID"])]["removed_from_gen8"] = True

  return

def main():
  # holds moveID, Name, Type, Category, Contest, PP, Power, Accuracy, Gen
  bulbapediaDataPath = getBulbapediaDataPath() + '/moves/'
  serebiiDataPath = getSerebiiDataPath() + '\\moves\\'

  moveList_fname = bulbapediaDataPath + 'moveList.csv'
  moveDict = makeInitialMoveDict(moveList_fname)

  # for reverse lookup of Move ID by Move Name
  inverseDict = makeInverseDict(moveList_fname)

  priority_fname = bulbapediaDataPath + 'movesByPriority.csv'
  addPriorityToMoveDict(priority_fname, moveDict, inverseDict)

  contact_fname = bulbapediaDataPath + f'movesByContact.csv'
  addContactToMoveDict(contact_fname, moveDict, inverseDict)

  effect_fname = bulbapediaDataPath + f'movesByEffect.csv'
  addEffectToMoveDict(effect_fname, moveDict, inverseDict)

  status_fname = bulbapediaDataPath + f'movesByStatus.csv'
  addStatusToMoveDict(status_fname, moveDict, inverseDict)

  target_fname = bulbapediaDataPath + f'movesByTarget.csv'
  addTargetToMoveDict(target_fname, moveDict, inverseDict)

  descriptions_fname = serebiiDataPath + 'moveDescriptions.csv'
  addDescriptionToMoveDict(descriptions_fname, moveDict, inverseDict)

  statMod_fname = bulbapediaDataPath + 'movesModifyStat.csv'
  addStatModToMoveDict(statMod_fname, moveDict, inverseDict)

  updateMoveCategory(moveDict, inverseDict)

  removedFromGen8_fname = bulbapediaDataPath + 'movesRemovedFromGen8.csv'
  removedFromGen8(removedFromGen8_fname, moveDict)

  return moveDict

if __name__ == '__main__':
  main()