import csv
from functools import cmp_to_key

# Used for a few calculations--need to alter when gen 9 comes
def numberOfGens():
  return 8

# converts roman numeral for to arabic numeral
def genSymbolToNumber(roman):
  if roman == 'I':
    return 1
  elif roman == 'II':
    return 2
  elif roman == 'III':
    return 3
  elif roman == 'IV':
    return 4
  elif roman == 'V':
    return 5
  elif roman == 'VI':
    return 6
  elif roman == 'VII':
    return 7
  elif roman == 'VIII':
    return 8
  elif roman == 'IX':
    return 9
  else:
    raise ValueError('Not a valid gen.')

# get value(s) and generation(s) from description
# Flag OHKO moves
# Flag fixed damage moves
# Flag LGPE: if 'in LGPE'; refers to move damage/accuracy/type and it takes a specific value; if 'LGPE only' refers to presence of move itself and doesn't take specific value; if 'and LGPE', refers to move value present in LGPE and multiple generations prior to VII
# For most changes, it'll just be the value and the latest generation for that value (e.g. 40 Power before and in Generation V would be [40, 5])
def parseMoveListNote(note):
  moveID = note[0]
  header = note[1]
  description = note[2]

  # Notes about type change are actually given in the 'Name' column
  if header == 'Name':
    header = 'Type'

  # "Success is calculated using a custom formula" for OHKO moves
  # the success of the OHKO move depends on mechanics which are hard to capture in a list--since there are only four, and they're hardly used, we ignore them
  if 'custom' in description:
    return [moveID, header, ['OHKO', None]]

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
  # except-clause for debugging
  except:
    print('Something went wrong when handling this description:')
    print(description)
    return None

# a patch is of the form [value, gen], where gen is either 1-8 or "LGPE"
def comparePatches(patch1, patch2):
  # make LGPE last, otherwise sort by gen
  if patch1[1] == "LGPE" or patch1[1] == "LGPE Only":
    return 1
  elif patch2[1] == "LGPE" or patch2[1] == "LGPE Only":
    return -1
  else:
    if patch1[1] > patch2[1]:
      return 1
    else:
      return -1

# creates dictionary for moves in csv located at fname
# contains moveID, name, type, category, contest type, PP, power, accuracy, gen introduced, whether move is OHKO, whether move is fixed damage/its fixed damage value, whether the move is LGPE exclusive
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
        isGMax = row["Name"][:5] == "G-Max"

        moveDict[int(row["Move ID"])] = {
          "Name": row["Name"],
          "Type": [[row["Type"], 8]],
          "Category": [row["Category"], 8],
          "Contest": row["Contest"],
          "PP": [[row["PP"], 8]],
          "Power": [[row["Power"], 8]],
          "Accuracy": [[row["Accuracy"].rstrip('%'), 8]],
          "Gen": genSymbolToNumber(row["Gen"]),
          "OHKO": False,
          "Fixed Damage": None,
          "LGPE Only": False,
          "Max Move": isMax,
          "G-Max Move": isGMax,
          "Priority": [],
          "Effect": {},
          "Status": {},
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

  # OHKO moves [moveID, header, ['OHKO', None]]
  OHKOMoves = [note for note in parsedNotes if note[2][0] == 'OHKO']
  for OHKOMove in OHKOMoves:
    moveID = OHKOMove[0]
    moveDict[int(moveID)]["OHKO"] = True

  # Fixed damage moves [moveID, header, [value + "fixed", Gen]]
  fixedDamageMoves = [note for note in parsedNotes if note[2][0] != None and 'fixed' in note[2][0]]
  for fixedDamageMove in fixedDamageMoves:
    moveID = fixedDamageMove[0]
    moveDict[int(moveID)]["Fixed Damage"] = fixedDamageMove[2][0].rstrip('fixed')

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
    moveDict[int(moveID)]["LGPE Only"] = True
    for header in ['Type', 'PP', 'Power', 'Accuracy']:
      moveDict[int(moveID)][header][0][1] = "LGPE Only"

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
    for innerKey in ['Type', 'PP', 'Power', 'Accuracy']:
      if len(moveDict[key][innerKey]) > 1:
        moveDict[key][innerKey].sort(key = cmp_to_key(comparePatches))

  # For each move in initialMoveDict, rewrite the patches in "Type", "PP", "Power", and "Accuracy" fields so that the generation represents the starting gen rather than the ending gen of that value
  for key in moveDict:
    for innerKey in ['Type', 'PP', 'Power', 'Accuracy']:
      # Split up patch into LGPE-only and other
      LGPEOnlyPatch = [patch for patch in moveDict[key][innerKey] if patch[1] == 'LGPE Only']
      noLGPEOnlyPatches = [patch for patch in moveDict[key][innerKey] if patch[1] != 'LGPE Only']

      # If the move is LGPE-only, no change required
      if LGPEOnlyPatch == moveDict[key][innerKey]:
        continue
      # If the move is not LGPE-only, change the non-LGPE-only patches
      else:
        # If only one non-LGPE-only patch, set gen equal to when move was introduced
        if len(noLGPEOnlyPatches) == 1:
          patch = moveDict[key][innerKey][0]
          value = patch[0]
          moveDict[key][innerKey] = [[value, moveDict[key]["Gen"]]]
        # Otherwise, need to determine when the starting gens from the list of ending gens
        else:
          modifiedPatchList = []
          for i in range(len(moveDict[key][innerKey])):
            # first 'patch' applied in gen the move was introduced
            if i == 0:
              modifiedPatchList.append([moveDict[key][innerKey][0][0], moveDict[key]["Gen"]])
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
      if row["Move Name"] != 'None' and row["Move Name"] != 'fleeing':
        moveID = inverseDict[row["Move Name"]]
        # we add duplicate entries for when moves maintain the same priority across generations--we will handle this in the next loop to account for zero-priority moves
        moveDict[int(moveID)]["Priority"].append([int(row["Priority"]), int(row["Generation"])])

  # handle priority zero moves
  for key in moveDict.keys():
    numGensPresent = numberOfGens() - moveDict[key]["Gen"] + 1

    # indicates that either the move had zero priority in some gens, or it was removed in gen 8
    # we will account for the moves removed from gen 8 later--for now, give them 0 priority
    if len(moveDict[key]["Priority"]) != numGensPresent:
      gensAccountedFor = [entry[1] for entry in moveDict[key]["Priority"]]
      for gen in range(moveDict[key]["Gen"], moveDict[key]["Gen"] + numGensPresent):
        if gen not in gensAccountedFor:
          moveDict[key]["Priority"].append([0, gen])

    # sort the patches by gen
    if len(moveDict[key]["Priority"]) > 1:
      moveDict[key]["Priority"].sort(key = cmp_to_key(comparePatches))

    # remove duplicates
    priorities_noDuplicates = []
    for patch in moveDict[key]["Priority"]:
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

    moveDict[key]["Priority"] = priorities_noDuplicates
  
  # lastly, we add Teleport, ID 100 with -6 priority in LGPE
  moveDict[100]["Priority"].append([-6, 'LGPE Only'])

  return

# read contact data and update moveDict
def addContactToMoveDict(fname, moveDict, inverseDict):
  # initially, no moves make contact
  for key in moveDict.keys():
    moveDict[key]["Contact"] = [[False, max(moveDict[key]["Gen"], 3)]]

  with open(fname, encoding='utf-8') as contactCSV:
    reader = csv.DictReader(contactCSV)
    for row in reader:
      moveName = row["Move Name"]
      note = row["Note"]
      genOfMoveName = moveDict[inverseDict[moveName]]["Gen"]

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
      if effect not in moveDict[1]["Effect"]:
        for key in moveDict.keys():
          moveDict[key]["Effect"][effect] = [[False, moveDict[key]["Gen"]]]
      
      key = inverseDict[moveName]
      moveDict[key]["Effect"][effect] = [[True, moveDict[key]["Gen"]]]
  
  # EXCEPTIONS SECTION
  # not covered in the above .csv
  exceptions = [
    ['suppressesAbility', ['CoreEnforcer', 'GastroAcid']],
    ['useDifferentStat', ['BodyPress', 'Psyshock', 'Psystrike', 'SecretSword']],
    ['canCrash', ['HighJumpKick', 'JumpKick']],
    ['changesDamageCategory', ['LightThatBurnstheSky', 'PhotonGeyser', 'ShellSideArm']],
  ]
  for exception in exceptions:
    effect = exception[0]
    
    # add effect to moveDict
    for key in moveDict.keys():
      moveDict[key][effect] = [[False, moveDict[key]["Gen"]]]

    # go through exceptions
    moveNames = exception[1]
    for moveName in moveNames:
      key = inverseDict[moveName]
      moveDict[key][effect] = [[True, moveDict[key]["Gen"]]]

  # still more exceptions
  moveDict[inverseDict['Astonish']]["Effect"]['antiMini'] = [[True, 3], [False, 4]]
  moveDict[inverseDict['Dig']]["Effect"]['hitsSemiInvulnerable'] = [[False, 1], [True, 2]]

  # cannotCrit effect
  for key in moveDict.keys():
    moveDict[key]["Effect"]["cannotCrit"] = [[False, moveDict[key]["Gen"]]]

  moveDict[inverseDict['Flail']]["Effect"]['cannotCrit'] = [[True, 2], [False, 3]]
  moveDict[inverseDict['FutureSight']]["Effect"]['cannotCrit'] = [[True, 2], [False, 5]]
  moveDict[inverseDict['Reversal']]["Effect"]['cannotCrit'] = [[True, 2], [False, 3]]
  moveDict[inverseDict['DoomDesire']]["Effect"]['cannotCrit'] = [[True, 3], [False, 5]]
  moveDict[inverseDict['SpitUp']]["Effect"]['cannotCrit'] = [[True, 3], [False, 4]]

  # high crit ratio
  moveDict[inverseDict['RazorWind']]['Effect']['hasHighCritChance'] = [[False, 1], [True, 2]]
  moveDict[inverseDict['SkyAttack']]['Effect']['hasHighCritChance'] = [[False, 1], [True, 3]]

  return

# read status data and update moveDict
def addStatusToMoveDict(fname, moveDict, inverseDict):
  with open(fname, encoding='utf-8') as csvFile:
    reader = csv.DictReader(csvFile)

    for row in reader:
      status = row["Status Caused"]
      moveName = row["Move Name"]
      probability = float(row["Probability"])

      if status not in moveDict[1]["Status"]:
        for key in moveDict.keys():
          moveDict[key]["Status"][status] = [0, moveDict[key]["Gen"]]
      
      key = inverseDict[moveName]
      moveDict[key]["Status"][status] = [[probability, moveDict[key]["Gen"]]]

  # EXCEPTIONS SECTION
  # Fire Blast had 30% to burn in Gen 1
  print(moveDict[inverseDict["FireBlast"]]["Status"]["Burn"])
  moveDict[inverseDict["FireBlast"]]["Status"]["Burn"] = [
    [30.0, 1], 
    [10.0, 2]
  ]
  print(moveDict[inverseDict["FireBlast"]]["Status"]["Burn"])

  # Tri Attack only applied statuses from Gen 2 on
  for status in ['Burn', 'Freeze', 'Paralysis']:
    moveDict[inverseDict["TriAttack"]]["Status"][status] = [
      [0.0, 1],
      [6.67, 2]
    ]

  # Thunder had 10% change to paralyze in Gen 1
  moveDict[inverseDict["Thunder"]]["Status"]["Paralysis"] = [
    [10.0, 1], 
    [30.0, 2]
  ]

  # Poison Sting had 20% chance to poison in Gen 1
  moveDict[inverseDict["PoisonSting"]]["Status"]["Poison"] = [
    [20.0, 1], 
    [30.0, 2]
  ]
  moveDict[inverseDict["Sludge"]]["Status"]["Poison"] = [
    [40.0, 1], 
    [30.0, 2]
  ]

  # Chatter has variable chance to confuse in Gens 4 and 5--we choose the highest value in each gen
  moveDict[inverseDict["Chatter"]]["Status"]["Confusion"] = [
    [31, 4],
    [10, 5],
    [100, 6]
  ]

  # Sky Attack only causes Flinch starting in Gen 3
  moveDict[inverseDict["SkyAttack"]]["Status"]["Flinch"] = [
    [0, 1],
    [30, 3]
  ]

  # Other notes in movesThatCauseStatusNotes.csv don't apply to status

  return

# holds moveID, Name, Type, Category, Contest, PP, Power, Accuracy, Gen
moveList_fname = f'src\data\movesList.csv'
moveDict = makeInitialMoveDict(moveList_fname)

# for reverse lookup of Move ID by Move Name
inverseDict = makeInverseDict(moveList_fname)

priority_fname = f'src\data\movesByPriority.csv'
addPriorityToMoveDict(priority_fname, moveDict, inverseDict)

contact_fname = f'src\data\movesByContact.csv'
addContactToMoveDict(contact_fname, moveDict, inverseDict)

effect_fname = f'src\data\movesByEffect.csv'
addEffectToMoveDict(effect_fname, moveDict, inverseDict)

status_fname = f'src\data\movesThatCauseStatus.csv'
addStatusToMoveDict(status_fname, moveDict, inverseDict)

