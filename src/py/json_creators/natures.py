import csv
from utils import getCSVDataPath
from tests import checkGenConsistency, natureTests

def makeNatureDict(fname): 
  natureDict = {}

  with open(fname, 'r', encoding='utf-8') as natureCSV:
    reader = csv.DictReader(natureCSV)

    for row in reader:
      natureName = row["Nature Name"]

      # .csv uses e.g. 'sp_attack' instead of 'special_attack'.
      increasedStat = correctStatName(row["Increased Stat"])
      decreasedStat = correctStatName(row["Decreased Stat"])

      favoriteFlavor = row["Favorite Flavor"]
      dislikedFlavor = row["Disliked Flavor"]
      natureGen = 3

      natureDict[natureName] = {
        # All natures introduced in Gen 3
        "gen": natureGen,
        "stat_modifications": {},
        "formatted_name": natureName.title(),
        # If no favorite or disliked flavors, use 'False' for filtering later
        "favorite_flavors": [[False, natureGen]], 
        "disliked_flavors": [[False, natureGen]], 
      }

      if len(increasedStat) > 0:
        natureDict[natureName]["stat_modifications"][increasedStat] = [[1.1, natureGen]]
      if len(decreasedStat) > 0:
        natureDict[natureName]["stat_modifications"][decreasedStat] = [[0.9, natureGen]]
      if len(favoriteFlavor) > 0:
        natureDict[natureName]["favorite_flavors"] = [[favoriteFlavor, natureGen]]
      if len(dislikedFlavor) > 0:
        natureDict[natureName]["disliked_flavors"] = [[dislikedFlavor, natureGen]]

  return natureDict

def correctStatName(statName):
  return statName.replace('sp_', 'special_')

def main():
  dataPath = getCSVDataPath() + '\\natures\\'
  fname = dataPath + 'natureList.csv'
  natureDict = makeNatureDict(fname)

  checkGenConsistency(natureDict)
  natureTests(natureDict)

  return natureDict

if __name__ == '__main__':
  main()