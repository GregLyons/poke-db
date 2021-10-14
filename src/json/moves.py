import csv
from functools import cmp_to_key
from utils import getDataPath, genSymbolToNumber

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
        # "Type", "Power", and "Accuracy" are lists since those can potentially change across generations--Bulbapedia lists the latest values for each field, with the past values in notes
        isMax = row["Name"][:3] == "Max"
        isGMax = row["Name"][:5] == "G_Max"

        moveDict[int(row["Move ID"])] = {
          "name": row["Name"],
          "type": [[row["Type"], 8]],
          "category": [row["Category"], 8],
          "contest": row["Contest"],
          "pp": [[row["PP"], 8]],
          "power": [[row["Power"], 8]],
          "accuracy": [[row["Accuracy"].rstrip('%'), 8]],
          "gen": genSymbolToNumber(row["Gen"]),
          "ohko": False,
          "fixed_damage": None,
          "lgpe_only": False,
          "max_move": isMax,
          "g_max_move": isGMax,
          "priority": [],
          "effect": {},
          "status": {},
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
      moveDict[int(moveID)]['Category'] = [['Physical', 6], ['Special', 8]]
      continue

    moveID = change[0]
    header = change[1]
    valueAndGen = change[2]
    moveDict[int(moveID)][header].append(valueAndGen)

  # ohko moves [moveID, header, ['ohko', None]]
  ohkoMoves = [note for note in parsedNotes if note[2][0] == 'ohko']
  for ohkoMove in ohkoMoves:
    moveID = ohkoMove[0]
    moveDict[int(moveID)]["ohko"] = True

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
    for innerKey in ['type', 'pp', 'power', 'accuracy']:
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
     
  return moveDict

# Uses move list located at fname to make inverse lookup of moveID from moveName possible
def makeInverseDict(fname):
  inverseDict = {}

  with open(fname, encoding='utf-8') as movesCSV:
    reader = csv.DictReader(movesCSV)
    for row in reader:
      if row["Move ID"] != "???":
        inverseDict[row["Name"]] = int(row["Move ID"])

  return inverseDict

# read priority data and update moveDict
def addPriorityToMoveDict(fname, moveDict, inverseDict):
  with open(fname, encoding='utf-8') as priorityCSV:
    reader = csv.DictReader(priorityCSV)

    for row in reader:
      if row["Move Name"] != 'none' and row["Move Name"] != 'fleeing':
        moveID = inverseDict[row["Move Name"]]
        # we add duplicate entries for when moves maintain the same priority across generations--we will handle this in the next loop to account for zero_priority moves
        moveDict[int(moveID)]["priority"].append([int(row["Priority"]), int(row["Generation"])])

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
      effect = row["Effect"]
      moveName = row["Move Name"]

      # if effect isn't in moveDict, add it and initialize as False
      if effect not in moveDict[1]["effect"]:
        for key in moveDict.keys():
          moveDict[key]["effect"][effect] = [[False, moveDict[key]["gen"]]]
      
      key = inverseDict[moveName]
      moveDict[key]["effect"][effect] = [[True, moveDict[key]["gen"]]]
  
  # EXCEPTIONS SECTION
  # not covered in the above .csv
  exceptions = [
    ['suppresses_ability', ['core_enforcer', 'gastro_acid']],
    ['use_different_stat', ['body_press', 'psyshock', 'psystrike', 'secret_sword']],
    ['can_crash', ['high_jump_kick', 'jump_kick']],
    ['changes_damage_category', ['light_that_burns_the_sky', 'photon_geyser', 'shell_side_arm']],
  ]
  for exception in exceptions:
    effect = exception[0]
    
    # add effect to moveDict
    for key in moveDict.keys():
      moveDict[key][effect] = [[False, moveDict[key]["gen"]]]

    # go through exceptions
    moveNames = exception[1]
    for moveName in moveNames:
      key = inverseDict[moveName]
      moveDict[key][effect] = [[True, moveDict[key]["gen"]]]

  # still more exceptions
  moveDict[inverseDict['astonish']]["effect"]['anti_mini'] = [[True, 3], [False, 4]]
  moveDict[inverseDict['dig']]["effect"]['hits_semi_invulnerable'] = [[False, 1], [True, 2]]

  # cannot_crit effect
  for key in moveDict.keys():
    moveDict[key]["effect"]["cannot_crit"] = [[False, moveDict[key]["gen"]]]

  moveDict[inverseDict['flail']]["effect"]['cannot_crit'] = [[True, 2], [False, 3]]
  moveDict[inverseDict['future_sight']]["effect"]['cannot_crit'] = [[True, 2], [False, 5]]
  moveDict[inverseDict['reversal']]["effect"]['cannot_crit'] = [[True, 2], [False, 3]]
  moveDict[inverseDict['doom_desire']]["effect"]['cannot_crit'] = [[True, 3], [False, 5]]
  moveDict[inverseDict['spit_up']]["effect"]['cannot_crit'] = [[True, 3], [False, 4]]

  # high crit ratio
  moveDict[inverseDict['razor_wind']]["effect"]['high_crit_chance'] = [[False, 1], [True, 2]]
  moveDict[inverseDict['sky_attack']]["effect"]['high_crit_chance'] = [[False, 1], [True, 3]]

  return

# read status data and update moveDict
def addStatusToMoveDict(fname, moveDict, inverseDict):
  with open(fname, encoding='utf-8') as csvFile:
    reader = csv.DictReader(csvFile)

    for row in reader:
      status = row["Status Caused"]
      moveName = row["Move Name"]
      probability = float(row["Probability"])

      if status not in moveDict[1]["status"]:
        for key in moveDict.keys():
          moveDict[key]["status"][status] = [[0, moveDict[key]["gen"]]]
      
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
    [31, 4],
    [10, 5],
    [100, 6]
  ]

  # Sky Attack only causes Flinch starting in Gen 3
  moveDict[inverseDict["sky_attack"]]["status"]["flinch"] = [
    [0, 1],
    [30, 3]
  ]

  # Other notes in movesThatCauseStatusNotes.csv don't apply to status

  return

# read target data and update moveDict
def addTargetToMoveDict(fname, moveDict, inverseDict):
  with open(fname, encoding='utf-8') as targetCSV:
    reader = csv.DictReader(targetCSV)

    # get effects and add them to moveDict with initial value False
    for row in reader:
      target = row["Target"]
      moveName = row["Move Name"]

      # if effect isn't in moveDict, add it and initialize as False
      if target not in moveDict[1]["target"]:
        for key in moveDict.keys():
          moveDict[key]["target"] = [['any_adjacent', moveDict[key]["gen"]]]
      
      key = inverseDict[moveName]
      moveDict[key]["target"] = [[True, moveDict[key]["gen"]]]

# holds moveID, Name, Type, Category, Contest, PP, Power, Accuracy, Gen
moveList_fname = getDataPath() + f'moveList.csv'
moveDict = makeInitialMoveDict(moveList_fname)

# for reverse lookup of Move ID by Move Name
inverseDict = makeInverseDict(moveList_fname)

priority_fname = getDataPath() + f'movesByPriority.csv'
addPriorityToMoveDict(priority_fname, moveDict, inverseDict)

contact_fname = getDataPath() + f'movesByContact.csv'
addContactToMoveDict(contact_fname, moveDict, inverseDict)

effect_fname = getDataPath() + f'movesByEffect.csv'
addEffectToMoveDict(effect_fname, moveDict, inverseDict)

status_fname = getDataPath() + f'movesByStatus.csv'
addStatusToMoveDict(status_fname, moveDict, inverseDict)

target_fname = getDataPath() + f'movesByTarget.csv'
addTargetToMoveDict(target_fname, moveDict, inverseDict)

print(moveDict[12])