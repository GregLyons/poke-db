import csv
import re
from utils import openLink, getBulbapediaDataPath, parseName, versionDictionary, genSymbolToNumber, numberOfGens, getVersionGroupsInGen

# exceptions:

# abilities: as_one, cacophony

versionDict = versionDictionary()

# category describes the type of description being considered
def getDataList(category):
  if category == 'move':
    bs = openLink('https://bulbapedia.bulbagarden.net/wiki/List_of_moves', 0, 10)
    moveRows = bs.find(id='List_of_moves').find_next('table').find('table').find_all('tr')[82:84] + bs.find(id='List_of_moves').find_next('table').find('table').find_all('tr')[294:296]
    # bs.find(id='List_of_G-Max_Moves').find_next('table').find('table').find_all('tr')[1:2]
 
    dataRows, nameSlot, genSlot, ignoreSlot, ignoreCode, placeholderGen = moveRows, 1, -1, 0, '???', 8

  elif category == 'ability':
    bs = openLink('https://bulbapedia.bulbagarden.net/wiki/Ability#List_of_Abilities', 0, 10)
    abilityRows = bs.find(id='List_of_Abilities').find_next('table').find('table').find_all('tr')[1:]

    dataRows, nameSlot, genSlot, ignoreSlot, ignoreCode, placeholderGen = abilityRows, 1, -1, 0, '—', 8

  elif category == 'item':
    bs = openLink('https://bulbapedia.bulbagarden.net/wiki/Category:In-battle_effect_items', 0, 10)
    itemGroups = bs.find(id='mw-pages').find_all('div', {'class': 'mw-category-group'})

    dataRows, nameSlot, genSlot, ignoreSlot, ignoreCode, placeholderGen = itemGroups, None, None, None, None, None

  # dataRows: actual data
  # nameSlot: index for cell with name
  # genSlot: index for gen, if any
  # ignoreCode and ignoreSlot: string indicating special case where move doesn't have description (e.g. moveID = '???' for stone_axe) and the cell where that would occur, respectively
  # placeholderGen: what to use for gen if gen not found; e.g. for g_max move table, gen is always 8, so the table doesn't have gen
  return dataRows, nameSlot, genSlot, ignoreSlot, ignoreCode, placeholderGen

# figure out which method to use for updating descriptionDict based on category
# passes link, descriptionDict, gen to the aforementioned method
def handleLink(link, descriptionDict, gen, category):
  if category == 'move':
    return handleMoveLink(link, descriptionDict, gen)
  elif category == 'ability':
    return handleAbilityLink(link, descriptionDict, gen)
  elif category == 'item':
    # need to find gen in the item page
    return handleItemLink(link, descriptionDict)
  else:
    return

# find descriptions for move referenced by given link and add to descriptionDict
def handleMoveLink(link, descriptionDict, moveGen):
  moveName, linkURL = parseName(link.get_text().rstrip('*')), 'https://bulbapedia.bulbagarden.net/' + link['href']

  # checking for duplicate names, if any
  if moveName in descriptionDict:
    print(f'{moveName} is already in descriptionDict!')

  # initialize entry for moveName
  descriptionDict[moveName] = {
    "gen": moveGen,
    "description_type": "move",
  }

  bs = openLink(linkURL, 0, 10)

  # description table is in a section labeled by id; each description is in a row of that table
  try:
    descriptionRows = bs.find(id='Description').find_next('table').find('table').find_all('tr')[1:]

  except Exception as e:
    print('Error finding description table for', moveName, '.')
    print(e)
    print()
    return moveName

  # keep track of how when the description changes
  descriptionIndex = -1
  oldMoveDescription = ''
  moveDescriptionArray = []
  descriptionDict[moveName]["descriptions"] = moveDescriptionArray

  # second column is description, first column is list of version groups corresponding to that description
  for row in descriptionRows: 
    try: 
      cells = row.find_all('td')

      #make sure that all version groups in this generation are matched with a description
      
      # sometimes the descriptions are different within version groups between item and TM description; the first one is the item description
      groups, moveDescription = cells[0].find_all('b'), cells[1].get_text().rstrip('\n').split('*')[0]

      if moveDescription != oldMoveDescription:
        moveDescriptionArray.append(moveDescription)
        descriptionIndex += 1
        descriptionDict[moveName][descriptionIndex] = []
      
      for group in groups:
        versionGroups = group.find_all('a')
        for versionGroup in versionGroups:
          # sometimes typo
          descriptionDict[moveName][descriptionIndex].append(versionGroup.get_text().replace('Colo.', 'Colo'))

      oldMoveDescription = moveDescription
    except Exception as e:
      print('Error handling the description table for', moveName, '.')
      print(e)
      print()
      return moveName
  
  return moveName

# find descriptions for ability referenced by given link and add to descriptionDict
def handleAbilityLink(link, descriptionDict, abilityGen):
  abilityName, linkURL = parseName(link.get_text().rstrip('*')), 'https://bulbapedia.bulbagarden.net/' + link['href']

  # as_one depends on which of Glastrier or Spectrier is merged with Calyrex, and Bulbapedia treats it as one ability (though with two different ability indices)
  if abilityName == 'as_one':
    descriptionDict["as_one_glastrier"] = {
      "gen": 8,
      "description_type": "ability",
      "descriptions": ["This Ability combines the effects of both Calyrex's Unnerve Ability and Glastrier's Chilling Neigh Ability."],
      0: ['SwSh'],
    }
    descriptionDict["as_one_spectrier"] = {
      "gen": 8,
      "description_type": "ability",
      "descriptions": ["This Ability combines the effects of both Calyrex's Unnerve Ability and Spectrier's Grim Neigh Ability."],
      0: ['SwSh'],
    }

    return 'as_one'
  else:
    descriptionDict[abilityName] = {
      "gen": abilityGen,
      "description_type": "ability",
    }

  # description table is at top of page, and each description has its own <table> within the description table
  bs = openLink(linkURL, 0, 10)
  try:
    descriptionTable = bs.find(id="mw-content-text").find_next('table')

    # the "This may be in need of research" and "This article is incomplete" boxes at the top of the page are actually tables; they're center-aligned, whereas the table we're interested in is not
    while descriptionTable.has_attr('align'):
      descriptionTable = descriptionTable.find_next('table')

    # if and ability was released in, say, gen VI, then there will still be entries for that ability in gens III-V with dummy text; such entries will have the 'display:none' in their style attribute
    descriptionEntryTables = [table for table in descriptionTable.find('tr').find_next_siblings('tr')[-1].find_all('table') if 'display:none;' not in table["style"]]
  except Exception as e:
    print(f'Error finding description table for {abilityName}.')
    print(e)
    print()
    return abilityName

  # in contrast to the case of move descriptions, if a generation has multiple different ability descriptions, then the different descriptions belong to the same cell as their version groups, and they are only separated by a <br>
  # we match descriptions with version groups in a list, then we iterate through that list in a manner similar to the case of move descriptions to avoid duplicates
  descriptions_groups = []
  for table in descriptionEntryTables:
    try: 
      descriptionGen = genSymbolToNumber(table.find('small').get_text().strip('\n').replace('Generation ', ''))

      abilityDescriptionCell = table.find_all('tr')[-1].find('td')

      if abilityDescriptionCell.find('sup'):
        for child in abilityDescriptionCell.children:
          if child.name:
            if child.find('a'):
              versionGroupCodes = []
              for versionGroupLink in child.find_all('a'):
                # sometimes typo
                versionGroup = versionGroupLink.get_text().replace('Colo.', 'Colo')
                versionGroupCodes.append(versionGroup)

              descriptions_groups.append([abilityDescription, versionGroupCodes])
          else:
            abilityDescription = child.get_text().strip('\n')
      else: 
        abilityDescription = abilityDescriptionCell.get_text().strip('\n')
        versionGroupCodes = []

        for versionGroup in versionDict.keys():
          versionGroupGen = versionDict[versionGroup][-1]

          # abilities aren't present in Let's Go Pikachu/Let's Go Eevee
          # generations prior to gen 3 won't be included, since all the descriptions start at gen 3 at the earliest
          if versionGroup == 'PE':
            continue
          elif versionGroupGen == descriptionGen:
            versionGroupCodes.append(versionGroup)
        
        descriptions_groups.append([abilityDescription, versionGroupCodes])
      
    except Exception as e:
      print(f'Error handling the description table for {abilityName}.')
      print(e)
      print()
      return abilityName
  
  abilityDescriptionArray = []
  descriptionIndex = -1
  oldAbilityDescription = ''
  descriptionDict[abilityName]["descriptions"] = abilityDescriptionArray

  for description_group in descriptions_groups:
    abilityDescription, versionGroups = description_group

    if abilityDescription != oldAbilityDescription:
      abilityDescriptionArray.append(abilityDescription)
      descriptionIndex += 1
      descriptionDict[abilityName][descriptionIndex] = []

    for versionGroup in versionGroups:
      descriptionDict[abilityName][descriptionIndex].append(versionGroup)

    oldAbilityDescription = abilityDescription

  return abilityName

# find descriptions for item referenced by given link and add to descriptionDict
# very similar to handleMoveLink, but we need to find the generation from the link as well, as the item link doesn't come from a table which has the generation
def handleItemLink(link, descriptionDict):
  itemName, linkURL = parseName(link.get_text().rstrip('*')), 'https://bulbapedia.bulbagarden.net/' + link['href']

  # checking for duplicate names, if any
  if itemName in descriptionDict:
    print(f'{itemName} is already in descriptionDict!')

  bs = openLink(linkURL, 0, 10)

  try:
    introduction = bs.find(id='mw-content-text').find_next('p').get_text()
    itemGenSearch = re.search(r'introduced in Generation ([IVX]*).', introduction)
    if itemGenSearch:
      itemGen = genSymbolToNumber(itemGenSearch.group(1))
    else: 
      if re.search(r'Omega Ruby and Alpha Sapphire', introduction):
        itemGen = 6
      elif re.search(r'exclusive to the Generation II games', introduction):
        itemGen = 2
      else:
        raise Exception("Could not find item gen from introduction:", introduction)

  except Exception as e:
    print(f'Error finding generation for {itemName}.')
    print(e)
    print()
    return itemName

  # initialize entry for itemName
  descriptionDict[itemName] = {
    "gen": itemGen,
    "description_type": "item",
  }

  # description table is in a section labeled by id; each description is in a row of that table
  try:
    descriptionRows = bs.find(id='Description').find_next('table').find('table').find_all('tr')[1:]

  except Exception as e:
    print('Error finding description table for', itemName, '.')
    print(e)
    print()
    return itemName

  # keep track of when the description changes
  descriptionIndex = -1
  oldItemDescription = ''
  itemDescriptionArray = []
  descriptionDict[itemName]["descriptions"] = itemDescriptionArray

  # second column is description, first column is list of version groups corresponding to that description
  for row in descriptionRows: 
    try: 
      cells = row.find_all('td')

      # sometimes the descriptions are different within version groups between item and TM description; the first one is the item description
      groups, itemDescription = cells[0].find_all('b'), cells[1].get_text().rstrip('\n').split('*')[0]

      if itemDescription != oldItemDescription:
        itemDescriptionArray.append(itemDescription)
        descriptionIndex += 1
        descriptionDict[itemName][descriptionIndex] = []
      
      for group in groups:
        versionGroups = group.find_all('a')
        for versionGroup in versionGroups:
          # sometimes typo
          descriptionDict[itemName][descriptionIndex].append(versionGroup.get_text().replace('Colo.', 'Colo'))

      oldItemDescription = itemDescription
    except Exception as e:
      print('Error handling the description table for', itemName, '.')
      print(e)
      print()
      return itemName

  return itemName


# Columns are Move Name, Description
def scrapeDescriptions(fnamePrefix, category, descriptionDict):
  fnamePrefix = fnamePrefix.replace('___', category)

  # for move and ability, dataList will be a table with links to the move/ability, as well as other data; for item, it will be a list of html elements containing <ul> elements, each of which has items
  # in the latter case, everything after dataRows is None
  dataList, nameSlot, genSlot, ignoreSlot, ignoreCode, placeholderGen= getDataList(category)
  
  for entry in dataList:
    try:
      # in this case, entry is a <tr> in a <table>
      if category != 'item':
        cells = entry.find_all(['td', 'th'])

        # check whether move has been released yet
        if cells[ignoreSlot].get_text().rstrip('\n') == ignoreCode:
          continue

        entityLink = cells[nameSlot].find('a')

        # some tables, e.g. gMax moves table, don't have gen; in this case, use placeholderGen
        try:
          entityGen = genSymbolToNumber(cells[genSlot].get_text().rstrip('*'))
        except ValueError:
          entityGen = placeholderGen

        entityName = handleLink(entityLink, descriptionDict, entityGen, category)
      # in this case, entry is a <div> containing a <ul>
      else:
        entityLinks = entry.find('ul').find_all('a')
        for entityLink in entityLinks:
          entityName = handleLink(entityLink, descriptionDict, None, category)

    except Exception as e:
      print(f'Error handling link {entityLink}. Previous {category} was {entityName}.')
      print(e)
      continue
  
  print(f'Finished extracting {category} descriptions. Removing duplicates and filling in missing entries...')

  for entityKey in descriptionDict:
    if descriptionDict[entityKey]["description_type"] == category:
      unhandledVersionGroups = set(versionDict.keys())
      # if a version group shows up twice for different description indices, de-assign all but the latest description index from that version group
      for descriptionIndex in [index for index in descriptionDict[entityKey].keys() if isinstance(index, int)]:
        for versionGroup in descriptionDict[entityKey][descriptionIndex]:
          if versionGroup in unhandledVersionGroups:
            unhandledVersionGroups.remove(versionGroup)
            oldDescriptionIndex = descriptionIndex
          else:
            descriptionDict[entityKey][oldDescriptionIndex].remove(versionGroup)
            oldDescriptionIndex = descriptionIndex
      
      print(unhandledVersionGroups)

      # if a version group doesn't have a description, assign it the description of another version group from the same gen
      for leftover in unhandledVersionGroups:
        leftoverGen = versionDict[leftover][-1]
        assigned = False

        for descriptionIndex in [index for index in descriptionDict[entityKey].keys() if isinstance(index, int)]:
          if not assigned:
            for versionGroup in descriptionDict[entityKey][descriptionIndex]:
              if versionDict[versionGroup][-1] == leftoverGen and not assigned:
                descriptionDict[entityKey][descriptionIndex].append(leftover)
                assigned = True
              else:
                continue
        print(leftover)

    else:
      continue


  print(f'Writing {category} descriptions to .csv.')
  # Write move descriptions to .csv
  # First column is Move Name, followed by the description index
  # The rows are the name of the move, followed by the description corresponding to that description index
  with open(fnamePrefix + '.csv', 'w', newline='', encoding='utf-8') as entityDescriptionCSV:
    writer = csv.writer(entityDescriptionCSV)
    headers = [f"{category.title()} Name", "Gen"]

    # there can be a maximum of one description for each version group
    for i in range(len(versionDict.keys())):
      headers.append(i)
    writer.writerow(headers)

    for entityKey in [key for key in descriptionDict.keys() if descriptionDict[key]["description_type"] == category]:
      csvRow = [entityKey, descriptionDict[entityKey]["gen"]]

      for description in descriptionDict[entityKey]["descriptions"]:
        csvRow.append(description)
      
      # make length of rows consistent
      while len(csvRow) < len(headers):
        csvRow.append('')

      writer.writerow(csvRow)

  print(f'Writing {category} description indices for each version group to .csv\'s.')
  # Write version groups and description indices to .csv's for each gen 
  # The first column is Move Name, followed by Gen, followed by a column for each version group in that gen
  # The rows are the name of the move, its gen, followed by the description indices to which each version group corresponds
  fnames_gens = []
  for i in range(numberOfGens()):
    # ignore gens which didn't have the mechanic, e.g. gen 2 didn't have abilities
    if category == 'ability' and i < 2:
      continue
    elif category == 'item' and i < 1:
      continue

    fnames_gens.append([i + 1, fnamePrefix + f'Gen{i + 1}.csv'])
  

  for fname_gen in fnames_gens:
    entityGen, fname = fname_gen
    print('Writing for Gen', entityGen, '...')

    with open(fname, 'w', newline='', encoding='utf-8') as entityDescription_versionGroupCSV:
      writer = csv.writer(entityDescription_versionGroupCSV)
      versionGroupsOfGen = [versionGroup for versionGroup in versionDict.keys() if versionDict[versionGroup][-1] == entityGen]

      # write header
      headers = [f'{category.title()} Name']
      for versionGroup in versionGroupsOfGen:
        groupName = versionGroup

        headers.append(groupName)
      writer.writerow(headers)

      # write move descriptions for current gen, filtering out descriptions which haven't been released yet, or which aren't about moves
      for entityKey in [key for key in descriptionDict.keys() if descriptionDict[key]["gen"] <= entityGen and descriptionDict[key]["description_type"] == category]:
        # start .csv row with name of move
        csvRow = [entityKey]

        for versionGroup in versionGroupsOfGen:
          if versionGroup == 'Colo.':
            versionGroup = 'Colo'
          
          # in some cases, the version group does not contain the entity, e.g. PE does not contain abilities, or held items other than mega stones
          addedEntry = False

          for descriptionIndex in descriptionDict[entityKey].keys():
            # check if descriptionIndex is actually an int; there are keys of descriptionDict which aren't int
            if isinstance(descriptionIndex, int) and versionGroup in descriptionDict[entityKey][descriptionIndex] and not addedEntry:
              csvRow.append(descriptionIndex)
              addedEntry = True
              continue
            else:
              continue
          
          # if entry wasn't added, add a placeholder
          if not addedEntry:
            csvRow.append('')
        
        writer.writerow(csvRow)


  print(f'Finished writing {category} descriptions.')

  return

def main():
  dataPath = getBulbapediaDataPath() + '\\descriptions\\'
  # we'll replace '___' depending on category
  fnamePrefix = dataPath + '___Descriptions'
  descriptionDict = {}

  print('Scraping move descriptions...')
  scrapeDescriptions(fnamePrefix, 'move', descriptionDict)

  # print('Scraping ability descriptions...')
  # scrapeDescriptions(fnamePrefix, 'ability', descriptionDict)

  # print('Scraping item descriptions...')
  # scrapeDescriptions(fnamePrefix, 'item', descriptionDict)

  print(descriptionDict.keys())

  return

if __name__ == '__main__':
  main()