import csv
import re
from utils import openLink, getCSVDataPath, parseName, versionGroupDictionary, genSymbolToNumber

# keeps track of version groups and corresponding gens
versionDict = versionGroupDictionary()

# given category, e.g. move or ability, return the relevant Bulbapedia table/list for that category, along with column indices for the desired data
# all but the non-berry held items lie in tables; non-berry held item links are spread across multiple <ul>'s
def getDataList(category):
  if category == 'move':
    bs = openLink('https://bulbapedia.bulbagarden.net/wiki/List_of_moves', 0, 10)
    moveRows = bs.find(id='List_of_moves').find_next('table').find('table').find_all('tr')[1:] + bs.find(id='List_of_G-Max_Moves').find_next('table').find('table').find_all('tr')[1:]
 
    dataRows, nameSlot, genSlot, ignoreSlot, ignoreCode, placeholderGen = moveRows, 1, -1, 0, '???', 8

  elif category == 'ability':
    bs = openLink('https://bulbapedia.bulbagarden.net/wiki/Ability#List_of_Abilities', 0, 10)
    abilityRows = bs.find(id='List_of_Abilities').find_next('table').find('table').find_all('tr')[1:]

    dataRows, nameSlot, genSlot, ignoreSlot, ignoreCode, placeholderGen = abilityRows, 1, -1, 0, '—', 8

  elif category == 'item':
    bs = openLink('https://bulbapedia.bulbagarden.net/wiki/Category:In-battle_effect_items', 0, 10)
    itemGroups = bs.find(id='mw-pages').find_all('div', {'class': 'mw-category-group'})

    dataRows, nameSlot, genSlot, ignoreSlot, ignoreCode, placeholderGen = itemGroups, None, None, None, None, None

  elif category == 'berry':
    bs = openLink('https://bulbapedia.bulbagarden.net/wiki/Berry', 0, 10)
    berryRows = bs.find(id='Generation_III_onwards').find_next('p').find_next('table').find_all('tr')[1:]

    dataRows, nameSlot, genSlot, ignoreSlot, ignoreCode, placeholderGen = berryRows, 3, 0, None, None, None

  elif category == 'gen2berry':
    bs = openLink('https://bulbapedia.bulbagarden.net/wiki/Berry', 0, 10)
    berryRows = bs.find(id='Generation_II').find_next('table').find_all('tr')[1:]

    dataRows, nameSlot, genSlot, ignoreSlot, ignoreCode, placeholderGen = berryRows, 0, None, None, None, 2

  # dataRows: actual data
  # nameSlot: index for cell with name
  # genSlot: index for gen, if any
  # ignoreCode and ignoreSlot: string indicating special case where move doesn't have description (e.g. moveID = '???' for stone_axe) and the cell where that would occur, respectively
  # placeholderGen: what to use for gen if gen not found; e.g. for g_max move table, gen is always 8, so the table doesn't have gen

  return dataRows, nameSlot, genSlot, ignoreSlot, ignoreCode, placeholderGen

# scrapes descriptions for specific category from Bulbapedia, storing in descriptionDict, then write to two .csv's: one with the list of descriptions, the other with the version groups and their corresponding description keys 
# e.g. if a description has index 1 in abilityDescriptions, then in abilityDescriptionsKeys, all version groups with a value of 1 have that description
# columns of description .csv are name of entity, gen of that entity, followed by indices; rows consist of all the descriptions for a given entity, with the index columns serving as keys for the descriptions
# columns of keys .csv are name of entity, followed by version groups; rows consist of keys referring to the description .csv
def scrapeDescriptions(fnamePrefix, category, descriptionDict):
  fnamePrefix = fnamePrefix.replace('___', category)

  # for move and ability, dataList will be a table with links to the move/ability, as well as other data; for item, it will be a list of html elements containing <ul> elements, each of which has items
  # in the latter case, everything after dataRows is None
  dataList, nameSlot, genSlot, ignoreSlot, ignoreCode, placeholderGen= getDataList(category)
  
  # in most cases, dataList is a table containing links to the relevant data
  # in the non-berry held item case, it is a list of sections, each of which contains a <ul> whose <li>'s contain links to the relevant data
  for entry in dataList:
    try:
      # in this case, entry is a <tr> in a <table>
      if category != 'item':
        cells = entry.find_all(['td', 'th'])

        # check whether move has been released yet
        if ignoreSlot != None and cells[ignoreSlot].get_text().rstrip('\n') == ignoreCode:
          continue

        entityLink = cells[nameSlot].find('a')

        # some tables, e.g. gMax moves table, don't have gen; in this case, use placeholderGen
        try:
          entityGen = genSymbolToNumber(cells[genSlot].get_text().rstrip('*'))
        except:
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

      # if a version group doesn't have a description, assign it the description of another version group from the same gen
      for leftover in unhandledVersionGroups:
        leftoverGen = versionDict[leftover][-1]
        assigned = False

        for descriptionIndex in [index for index in descriptionDict[entityKey].keys() if isinstance(index, int)]:
          if not assigned:
            for versionGroup in descriptionDict[entityKey][descriptionIndex]:
              versionGroupGen = versionDict[versionGroup][-1]

              if versionGroupGen == leftoverGen and not assigned:
                descriptionDict[entityKey][descriptionIndex].append(leftover)
                assigned = True
              else:
                continue
    else:
      continue

  print('descriptionDict cleaned.')

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
        # remove new lines from description and remove accents from 'Pokémon'.
        description = description.replace('\n', '').replace('Pok\u00e9mon', 'Pokemon').replace('Pokémon', 'Pokemon')
        csvRow.append(description)
      
      # make length of rows consistent
      while len(csvRow) < len(headers):
        csvRow.append('')

      writer.writerow(csvRow)

  print(f'Writing {category} description indices for each version group to .csv\'s.')

  with open(fnamePrefix + 'Keys.csv', 'w', newline='', encoding='utf-8') as entityDescription_versionGroupCSV:
    writer = csv.writer(entityDescription_versionGroupCSV)

    # write header
    headers = [f'{category.title()} Name']
    for versionGroup in versionDict.keys():
      headers.append(versionGroup)
    writer.writerow(headers)

    # write move descriptions for current gen, filtering out descriptions which haven't been released yet, or which aren't about moves
    for entityKey in [key for key in descriptionDict.keys() if descriptionDict[key]["description_type"] == category]:
      # start .csv row with name of move
      csvRow = [entityKey]

      for versionGroup in versionDict.keys():
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

# figure out which method to use for updating descriptionDict based on category
# passes in link for entity, descriptionDict, gen to the aforementioned link-handling method
def handleLink(link, descriptionDict, gen, category):
  if category == 'move':
    return handleMoveLink(link, descriptionDict, gen)
  elif category == 'ability':
    return handleAbilityLink(link, descriptionDict, gen)
  elif category == 'item':
    # need to find gen in the item page
    return handleItemLink(link, descriptionDict)
  elif category == 'berry':
    return handleBerryLink(link, descriptionDict, gen)
  elif category == 'gen2berry':
    return handleGen2BerryLink(link, descriptionDict)
  else:
    return

# in each link-handling method, we end up with an array, descriptions_groups, which matches descriptions to the corresponding version groups. this method adds that data to descriptionDict so as to avoid multiple instances of the same exact description
def addDataToDescriptionDict(entityName, descriptions_groups, descriptionDict):
  entityDescriptionArray = []
  descriptionIndex = -1
  oldEntityDescription = ''
  descriptionDict[entityName]["descriptions"] = entityDescriptionArray

  for description_group in descriptions_groups:
    entityDescription, versionGroups = description_group

    # only add new description if it's not blank (e.g. from Gen 7 to Gen 8, the ability descriptions for PE will be blank)
    if entityDescription and entityDescription != oldEntityDescription:
      entityDescriptionArray.append(entityDescription)
      descriptionIndex += 1
      descriptionDict[entityName][descriptionIndex] = []

    for versionGroup in versionGroups:
      descriptionDict[entityName][descriptionIndex].append(versionGroup)

    oldEntityDescription = entityDescription

  return entityName

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

  # match descriptions with version groups
  descriptions_groups = []
  for row in descriptionRows: 
    cells = row.find_all('td')

    # the version groups are blold-faced
    groups = cells[0].find_all('b')

    # sometimes the descriptions are different within version groups between move and TM/HM description; the first one is the move description
    moveDescription = cells[1].get_text().rstrip('\n').split('*')[0]

    # Sometimes Bulbapedia forgets to put an asterisk for the non-TM/HM description, so the above will not detect it. In this case, the two descriptions will be glued togehter, indicated by a period followed immediately by a non-space character; we extract the first description using a regex
    match = re.search(r'\.[A-Z]', moveDescription)
    if match:
      moveDescription = moveDescription[:match.start() + 1]
      
    
    versionGroupCodes = []

    for group in groups:
      for versionGroupCode in group.find_all('a'):
        # sometimes 'Colo.', sometimes 'Colo'--standardize
        versionGroupCodes.append(versionGroupCode.get_text().replace('Colo.', 'Colo'))

    descriptions_groups.append([moveDescription, versionGroupCodes])

  addDataToDescriptionDict(moveName, descriptions_groups, descriptionDict)
  
  return moveName

# find descriptions for ability referenced by given link and add to descriptionDict
# in contrast with handleMoveLink, the description table is in a different part of the page, and the formatting of the cells is more complicated
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

          if versionGroupGen == descriptionGen:
            versionGroupCodes.append(versionGroup)
        
        descriptions_groups.append([abilityDescription, versionGroupCodes])
      
    except Exception as e:
      print(f'Error handling the description table for {abilityName}.')
      print(e)
      print()
      return abilityName
  
  addDataToDescriptionDict(abilityName, descriptions_groups, descriptionDict)

  return abilityName

# find descriptions for item referenced by given link and add to descriptionDict
# very similar to handleMoveLink, but we need to find the generation from the item link as well, as the item link doesn't come from a table which has the generation
def handleItemLink(link, descriptionDict):
  # metronome has '(item)' appended to avoid confusion with the move--remove parentheses
  itemName, linkURL = parseName(link.get_text().rstrip('*')).replace('(item)', 'item'), 'https://bulbapedia.bulbagarden.net/' + link['href']

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

  # match descriptions with version groups
  descriptions_groups = []
  for row in descriptionRows: 
    cells = row.find_all('td')

    # the version groups are blold-faced
    groups = cells[0].find_all('b')

    # sometimes the descriptions are different within version groups; get the first one
    itemDescription = cells[1].get_text().rstrip('\n').split('*')[0]
    
    # extract version group codes from groups
    versionGroupCodes = []
    for group in groups:
      for versionGroupCode in group.find_all('a'):
        # sometimes 'Colo.', sometimes 'Colo'--standardize
        versionGroupCodes.append(versionGroupCode.get_text().replace('Colo.', 'Colo'))
    descriptions_groups.append([itemDescription, versionGroupCodes])

  addDataToDescriptionDict(itemName, descriptions_groups, descriptionDict)

  return itemName

# find descriptions for berry referenced by given link and add to descriptionDict
# similar to handleAbilityLink, as the description table is in a similar part of the page and formatted similarly, though there are a few exceptions to consider
def handleBerryLink(link, descriptionDict, berryGen):
  berryName, linkURL = parseName(link.get_text().rstrip('*')), 'https://bulbapedia.bulbagarden.net/' + link['href']

  descriptionDict[berryName] = {
    "description_type": "berry",
    "gen": berryGen,
  }

  bs = openLink(linkURL, 0, 10)
  try:
    # table with bag descriptions is at top of screen inside a table with style including float:right
    containerTable = bs.find('table', style=lambda value: value and 'float:right' in value).find('table', style=lambda value: value and 'text-align:center' in value)

    # if berry released in a later gen, previous gens take have <tr>'s but are not displayed
    descriptionRows = containerTable.find_all('tr', style=lambda value: not value or 'display:none;' not in value)[1:]

  except Exception as e:
    print(f'Error finding description table for {berryName}.')
    print(e)
    print()
    return berryName
  
  # in contrast to the case of move descriptions, if a generation has multiple different berry descriptions, then the different descriptions belong to the same cell as their version groups, and they are only separated by a <br>
  # we match descriptions with version groups in a list
  descriptions_groups = []
  for row in descriptionRows:
    try: 
      descriptionGen = genSymbolToNumber(row.find('th').get_text().strip('\n').replace('Generation ', ''))

      berryDescriptionCell = row.find('td')

      # sometimes the description has a span with "Pokemon" in small caps because that is how it appears in-game; replace it with a string so that the code below works properly
      for s in berryDescriptionCell.find_all('span', {'class': 'sc'}):
        s.replaceWith(f"{s.string}")

      # even after replacing the <span> with its string, the deleted <span> still shows up as a child (in some sense...) for berryDescriptionCell (see nested 'else' below)
      berryDescription = ''

      if berryDescriptionCell.find('sup'):
        for child in berryDescriptionCell.children:
          if child.name:
            if child.find('a'):
              versionGroupCodes = []
              for versionGroupLink in child.find_all('a'):
                # sometimes typo
                versionGroup = versionGroupLink.get_text().replace('Colo.', 'Colo')
                versionGroupCodes.append(versionGroup)

              descriptions_groups.append([berryDescription, versionGroupCodes])
            else:
              berryDescription = ''
          else:
            # since the deleted <span> (which is replaced with text) still shows up as a child for some reason, if we merely assign child.get_text() to berryDescription like in the handleAbilityLink method, then only the part of the description after the <span> will be read; thus, we need to add on the text instead
            berryDescription += child.get_text().strip('\n')
      else: 
        # get description from cell; gen 8 descriptions have a 'Curry Ingredient' section which we remove
        berryDescription = re.sub(r'Curry Ingredient:.*', '', berryDescriptionCell.get_text().strip('\n')).replace('Held Item: ', '')
        versionGroupCodes = []
        
        # for some reason rows with no display are still sometimes selected, so we skip them.
        if '—' in berryDescription or 'Unknown' in berryDescription:
          continue

        for versionGroup in versionDict.keys():
          versionGroupGen = versionDict[versionGroup][-1]

          if versionGroupGen == descriptionGen:
            versionGroupCodes.append(versionGroup)
        
        descriptions_groups.append([berryDescription, versionGroupCodes])
      
    except Exception as e:
      print(f'Error handling the description table for {berryName}.')
      print(e)
      print()
      return berryName
  
  addDataToDescriptionDict(berryName, descriptions_groups, descriptionDict)

  return berryName

# find descriptions for gen 2-exclusive berry referenced by given link and add to descriptionDict
# similar to handleMoveLink, where the description table is easier to parse
def handleGen2BerryLink(link, descriptionDict):
  berryName, linkURL = parseName(link.get_text().rstrip('*')), 'https://bulbapedia.bulbagarden.net/' + link['href']

  if berryName in ['psncure_berry', 'przcure_berry']:
    berryName = berryName[0:3] + '_' + berryName[3:]


  # checking for duplicate names, if any
  if berryName in descriptionDict:
    print(f'{berryName} is already in descriptionDict!')

  # initialize entry for moveName
  descriptionDict[berryName] = {
    "gen": 2,
    "description_type": "gen2berry",
  }

  bs = openLink(linkURL, 0, 10)

  # description table is in a section labeled by id; each description is in a row of that table
  try:
    descriptionRows = bs.find(id='Description').find_next('table').find('table').find_all('tr')[1:]

  except Exception as e:
    print('Error finding description table for', berryName, '.')
    print(e)
    print()
    return berryName

  # match descriptions with version groups
  descriptions_groups = []
  for row in descriptionRows: 
    cells = row.find_all('td')

    # the version groups are bold-faced
    groups = cells[0].find_all('b')

    # sometimes the descriptions are different within version groups; get the first one
    berryDescription = cells[1].get_text().rstrip('\n').split('*')[0]
    
    # go through groups and extract version codes corresponding to berryDescription
    versionGroupCodes = []
    for group in groups:
      for versionGroupCode in group.find_all('a'):
        # sometimes 'Colo.', sometimes 'Colo'--standardize
        versionGroupCodes.append(versionGroupCode.get_text().replace('Colo.', 'Colo'))
    descriptions_groups.append([berryDescription, versionGroupCodes])

  addDataToDescriptionDict(berryName, descriptions_groups, descriptionDict)
  
  return berryName

# Scrapes descriptions for moves, abilities, non-berry held-items, berries, and gen 2-exclusive berries
def main():
  dataPath = getCSVDataPath() + '\\descriptions\\'
  # we'll replace '___' depending on category
  fnamePrefix = dataPath + '___Descriptions'
  descriptionDict = {}

  print('Scraping ability descriptions...')
  scrapeDescriptions(fnamePrefix, 'ability', descriptionDict)
  print()

  print('Scraping berry descriptions...')
  scrapeDescriptions(fnamePrefix, 'berry', descriptionDict)
  print()

  print('Scraping gen 2 berry descriptions...')
  scrapeDescriptions(fnamePrefix, 'gen2berry', descriptionDict)
  print()

  print('Scraping item descriptions...')
  scrapeDescriptions(fnamePrefix, 'item', descriptionDict)
  print()

  print('Scraping move descriptions...')
  scrapeDescriptions(fnamePrefix, 'move', descriptionDict)
  print()

  return

if __name__ == '__main__':
  main()