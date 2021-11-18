import csv
from utils import genSymbolToNumber, getCSVDataPath, versionGroupDictionary, getVersionGroupsInGen

def makeDescriptionDict(dataPath):
  descriptionDict = {}

  for category in ['Ability', 'Berry', 'Gen2Berry', 'Item', 'Move']:
    with open(dataPath + f'{category.lower()}Descriptions.csv', 'r', encoding='utf-8') as descriptionCSV, open(dataPath + f'{category.lower()}DescriptionsKeys.csv', 'r', encoding='utf-8') as keysCSV:
      descriptionReader, keysReader = csv.DictReader(descriptionCSV), csv.DictReader(keysCSV)

      for row in descriptionReader:
        entityName, entityGen = row[f"{category} Name"], int(row["Gen"])
        descriptionDict[entityName] = {
          "gen": entityGen,
          "description_type": category.lower()
        }

        for descriptionIndex in [key for key in row.keys() if key.isnumeric()]:
          if row[descriptionIndex] != '':
            descriptionDict[entityName][int(descriptionIndex)] = [row[descriptionIndex]]

      for row in keysReader:
        entityName = row[f"{category} Name"]
        
        versionGroups = [key for key in row.keys() if key != f"{category} Name"]
        for versionGroup in versionGroups:
          if row[versionGroup] != '':
            descriptionIndex = int(row[versionGroup])
            descriptionDict[entityName][descriptionIndex].append(versionGroup)
        
        for descriptionIndex in [key for key in descriptionDict[entityName].keys() if isinstance(key, int)]:
          descriptionDict[entityName][descriptionIndex] = [descriptionDict[entityName][descriptionIndex][0], descriptionDict[entityName][descriptionIndex][1:]]

        for descriptionIndex in range(len([key for key in descriptionDict[entityName].keys() if isinstance(key, int)]) - 1, 0, -1):
          if descriptionDict[entityName][descriptionIndex][0] == '':
            del descriptionDict[entityName][descriptionIndex]
          else:
            break

  return descriptionDict

def main():
  dataPath = getCSVDataPath() + '/descriptions/'
  descriptionDict = makeDescriptionDict(dataPath)

  return descriptionDict

if __name__ == '__main__':
  descriptionDict = main()