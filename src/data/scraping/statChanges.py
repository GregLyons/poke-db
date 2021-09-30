from bs4 import BeautifulSoup
import re

class StatChange:
  def __init__(self, pokemonName, prevGen, prevGenStats, currentGen, currentGenStats):
    self.pokemonName = pokemonName
    self.prevGen = prevGen
    self.prevGenStats = prevGenStats
    self.currentGen = currentGen
    self.currentGenStats = currentGenStats

  def getChanges(self):
    stats = ['hp', 'attack', 'defense', 'special-attack', 'special-defense', 'speed']

    statChanges = []

    for i in range(len(stats)):
      if self.prevGenStats[i] != self.currentGenStats[i]:
        statChanges.append([stats[i], self.prevGenStats[i], self.currentGenStats[i]])

    return statChanges

def getDataFromRowTriplet(rowPair):  
  
  firstRow, thirdRow = rowPair

  POKEMON_NAME_REGEX = r'/pokedex-(xy|sm)/(\w+).shtml">(\w.+)<br/>'
  ROW_SHORTHEN_REGEX = r'<b>(.+)'
  GEN_REGEX = r'<b>(.+)</b>'
  STAT_REGEX = r'>(\d+)<'

  # get rid of line breaks to search across multiple lines
  firstRow = firstRow.replace('\n', ' ')
  thirdRow = thirdRow.replace('\n', ' ')

  # get name
  pokemonName = re.search(POKEMON_NAME_REGEX, firstRow).group()
  pokemonName = re.search(r'>([\w\'*\s*]+)<', pokemonName).group()
  pokemonName = pokemonName[1:len(pokemonName) - 1]

  firstRow = re.search(ROW_SHORTHEN_REGEX, firstRow).group()
  thirdRow = re.search(ROW_SHORTHEN_REGEX, thirdRow).group()

  # get generation info
  currentGen = re.search(GEN_REGEX, firstRow).group()
  currentGen = currentGen[3:len(currentGen) - 4]
  prevGen = re.search(GEN_REGEX, thirdRow).group()
  prevGen = prevGen[3:len(prevGen) - 4]

  # get stat info
  prevGenStats_matches = re.findall(STAT_REGEX, firstRow)
  currentGenStats_matches = re.findall(STAT_REGEX, thirdRow)

  prevGenStats = []
  for match in prevGenStats_matches:
    prevGenStats.append(int(match))
  
  currentGenStats = []
  for match in currentGenStats_matches:
    currentGenStats.append(int(match))

  return pokemonName, prevGen, prevGenStats, currentGen, currentGenStats

# get stat change data for gens 6 and 7
statLinks = [r"src\data\scraping\gen6\updatedStats.html", r"src\data\scraping\gen7\updatedStats.html"]

allStatChanges = []

for link in statLinks:
  with open(link) as fp:
    soup = BeautifulSoup(fp, 'html.parser')
    rows = soup.find_all("tr")

    for i in range(0, len(rows), 3):
      rowPair = (str(rows[i]), str(rows[i+2]))
      pokemonName, prevGen, prevGenStats, currentGen, currentGenStats = getDataFromRowTriplet(rowPair)
      statChanges = StatChange(pokemonName, prevGen, prevGenStats, currentGen, currentGenStats)
      allStatChanges.append(statChanges)

# the regexes for gens 6 and 7 dont work for gen 8; only aegislash's stats were changed in gen 8, so we add that manually
aegisSlashBlade_StatChanges = StatChange("aegislash-blade", "S/M", [60, 50, 150, 50, 150, 60], "SW/SH", [60, 50, 140, 50, 140, 60])
aegisSlashShield_StatChanges = StatChange("aegislash-shield", "S/M", [60, 150, 50, 150, 50, 60], "SW/SH", [60, 140, 50, 140, 50, 60])
allStatChanges.append(aegisSlashBlade_StatChanges)
allStatChanges.append(aegisSlashShield_StatChanges)

for changes in allStatChanges:
  print(changes.pokemonName, changes.getChanges())