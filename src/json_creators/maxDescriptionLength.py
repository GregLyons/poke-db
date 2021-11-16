# For tracking length of descriptions in order to ensure that we can store in MySQL as VARCHAR(255).
import csv
from utils import getCSVDataPath

maxLength = 0
maxDescription = ''
maxEntityName = ''

dataPath = getCSVDataPath() + '/descriptions/'
for descriptionFname in ['abilityDescriptions.csv', 'berryDescriptions.csv', 'gen2berryDescriptions.csv', 'itemDescriptions.csv', 'moveDescriptions.csv']:
  with open(dataPath + descriptionFname, 'r', encoding='utf-8') as descriptionCSV:
    reader = csv.reader(descriptionCSV)

    # skip header row
    next(reader, None)

    # iterate through rows and see if description length is greater than maxLength
    for row in reader:
      # first two columns are entity name and debut gen
      descriptions = row[2:]
      for description in descriptions:
        if len(description) > maxLength:
          maxEntityName = row[0]
          maxLength, maxDescription, maxEntityName = len(description), description, maxEntityName

print(maxLength, maxDescription, maxEntityName)