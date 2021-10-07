import urllib.request
from bs4 import BeautifulSoup
import csv
import re

# Returns BeautifulSoup object given Bulbapedia link
def openBulbapediaLink(url, retryCount, retryMax):
  try:
    req = urllib.request.Request(url, headers={'User-Agent' : "Magic Browser"}) 
    html = urllib.request.urlopen( req )
    bs = BeautifulSoup(html.read(), 'html.parser')
    return bs
  except urllib.error.HTTPError:
    if retryCount < retryMax:
      openBulbapediaLink(url, retryCount + 1, retryMax)
  else:
    return None

# converts roman numeral for gen to arabic numeral
def genSymbolToNumber(roman):
  if roman.upper() == 'I':
    return 1
  elif roman.upper() == 'II':
    return 2
  elif roman.upper() == 'III':
    return 3
  elif roman.upper() == 'IV':
    return 4
  elif roman.upper() == 'V':
    return 5
  elif roman.upper() == 'VI':
    return 6
  elif roman.upper() == 'VII':
    return 7
  elif roman.upper() == 'VIII':
    return 8
  elif roman.upper() == 'IX':
    return 9
  else:
    raise ValueError('Not a valid gen.')

# converts dex number to gen
def dexNumberToGen(dexNumber):
  dexNumber = int(dexNumber)
  if dexNumber <= 151:
    return 1
  elif dexNumber <= 251:
    return 2
  elif dexNumber <= 386:
    return 3
  elif dexNumber <= 493: 
    return 4
  elif dexNumber <= 649:
    return 5
  elif dexNumber <= 721:
    return 6
  elif dexNumber <= 809:
    return 7
  else:
    return 8

# remove Shadow Moves, which are listed on Bulbapedia
def removeShadowMoves(fname, firstHeader):
  shadowMoves = ['blitz', 'rush', 'break', 'end', 'wave', 'rave', 'storm', 'fire', 'bolt', 'chill', 'blast', 'sky', 'hold', 'mist', 'panic', 'down', 'shed', 'half']
  shadowMoves = ['shadow-' + move for move in shadowMoves]

  with open(fname, 'r', encoding='utf-8') as oldFile, open(fname.replace('WithShadowMoves', ''), 'w', newline='', encoding='utf-8') as newFile:
    reader = csv.DictReader(oldFile)
    writer = csv.writer(newFile, csv.QUOTE_MINIMAL)
    writer.writerow([firstHeader, 'Move Name'])
    for row in reader:
      if row["Move Name"] not in shadowMoves:
        writer.writerow([row[firstHeader], row['Move Name']])

def getDataPath():
  return 'src\data\\'

# adapted top answer at https://stackoverflow.com/questions/1175208/elegant-python-function-to-convert-camelcase-to-snake-case
def titleOrPascalToKebab(text):
  # handles Will-O-Wisp, U-turn, King's Shield
  text = text.replace('-', ' ').replace('\'', '').title()
  text = re.sub(r'[\s,.()]', '', text)
  text = re.sub('(.)([A-Z][a-z]+)', r'\1-\2', text)
  return re.sub('([a-z0-9])([A-Z])', r'\1-\2', text).lower()
