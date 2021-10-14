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
  roman = roman.rstrip('\n')
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
  shadowMoves = ['shadow_' + move for move in shadowMoves]

  with open(fname, 'r', encoding='utf-8') as oldFile, open(fname.replace('WithShadowMoves', ''), 'w', newline='', encoding='utf-8') as newFile:
    reader = csv.DictReader(oldFile)
    writer = csv.writer(newFile, csv.QUOTE_MINIMAL)
    writer.writerow([firstHeader, 'Move Name'])
    for row in reader:
      if row["Move Name"] not in shadowMoves:
        writer.writerow([row[firstHeader], row['Move Name']])

def getDataBasePath():
  return '..\\data\\bulbapedia_data\\'

# parse names in different forms from Bulbapedia and Smogon API to a common, snake_case form
def parseName(text, mode='normal'):
  text = text.rstrip('\n')
  if mode == 'normal':
    # hyphens to underscores
    text = text.replace('-', '_')

    # remove commas, apostrophes, periods, colons
    text = re.sub(r'[,\'\.:]', '', text)

    # separate lowercase followed by uppercase, e.g. 'ExtremeSpeed' to 'Extreme Speed'--for Bulbapedia typos
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
    
    # replace spaces with underscores and convert to lowercase
    return text.replace(' ', '_').lower()

  elif mode == 'pokemon':
    # extract species and form data (latter in parentheses, if present)
    if '(' in text:
      speciesAndForm = [part.strip().strip(')') for part in text.split('(')]
      speciesName = speciesAndForm[0]
      form = speciesAndForm[1].replace('(', '').replace(')', '')

      # remove 'Form' and 'Forme'
      form = re.sub(r'Forme*', '', form)

      # various cases to 
      if speciesName == 'Wormadam':
        form = form.replace('Cloak', '')
      elif speciesName == 'Darmanitan':
        form = form.replace('Mode', '')
        # switch order 'Galarian Standard' to 'Standard Galarian'
        form = re.sub(r'Galarian (Standard|Zen)', r'\1 Galarian', form)
      elif speciesName == 'Urshifu':
        #  preserve 'Rapid Strike' to match with Smogon API
        form = form.replace('Single Strike Style', '')
        form = form.replace('Rapid Strike Style', 'Rapid Strike')
      elif speciesName in ['Zacian', 'Zamazenta']:
        # Bulbapedia adds 'Hero of Many Battles', but Smogon does not
        form = form.replace('Hero of Many Battles', '')
        # Zacian and Zamazenta, remove noun in 'Crowned [noun]'
        form = form.replace('Sword', '')
        form = form.replace('Shield', '')
      elif speciesName in ['Pumpkaboo', 'Gourgeist']:
        form = form.replace('Size', '')
      elif speciesName == 'Indeedee':
        form = form.replace('Female', 'f').replace('Male', 'm')
      elif speciesName == 'Calyrex':
        form = form.replace('Rider', '')
      elif speciesName == 'Nidoran':
        # sometimes Nidoran will have the gender symbol (Bulbapedia)
        form = form.replace('♀', ' Female').replace('Female', 'f')
        form = form.replace('♂', ' Male').replace('Male', 'f')

      # sometimes on Bulbapedia the form has the species name again
      form = form.replace(speciesName, '')

      # change regional names
      form = form.replace('Alolan', 'Alola')
      form = form.replace('Galarian', 'Galar')
    else:
      speciesName = text
      form = ''

    # combine species and form name after parsing
    text = (speciesName + ' ' + form).strip().replace('  ', ' ')

    # hyphens to undescores
    text = text.replace('-', '_')

    # remove commas, apostophes, periods, colons, percent signs
    text = re.sub(r'[,\'\.:\%]', '', text)

    # separate lowercase followed by uppercase, e.g. 'ExtremeSpeed' to 'Extreme Speed'--for Bulbapedia typos
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
    
    # replace spaces with underscores, convert to lowercase, and strip any underscores on the ends (e.g. from Ash-Greninja')
    return text.replace(' ', '_').lower().strip('_')
  else:
    return
  
if __name__ == '__main__':
  # Testing Move name parser
  moveTests = [
    ['Karate Chop', 'karate_chop'],
    ['Razor Wind', 'razor_wind'],
    ['Roar of Time', 'roar_of_time'],
    ['All-Out Pummeling', 'all_out_pummeling'],
    ['U-turn', 'u_turn'],
    ['Multi-Attack', 'multi_attack'],
    ['10,000,000 Volt Thunderbolt', '10000000_volt_thunderbolt'],
    ['Light That Burns the Sky', 'light_that_burns_the_sky'],
    ['G-Max Wildfire', 'g_max_wildfire'],
    ['G-Max Stun Shock', 'g_max_stun_shock'],
    ['Will-O-Wisp', 'will_o_wisp'],
    ['ExtremeSpeed', 'extreme_speed'],
    ['Extreme Speed', 'extreme_speed'],
    ['RKS System', 'rks_system'],
    ['Soul-Heart', 'soul_heart']
  ]

  for test in moveTests:
    if (parseName(test[0]) != test[1]):
      print(parseName(test[0]), 'is not', test[1])

  # Testing Pokemon name parser
  pokemonTests = [
    ['Dragapult', 'dragapult'],
    ['Kommo-o', 'kommo_o'],
    ['Tapu Lele', 'tapu_lele'],
    ['Charizard (Mega Charizard X)', 'charizard_mega_x'],
    ['Blastoise (Mega Blastoise)', 'blastoise_mega'],
    ['Raticate (Alolan Raticate)', 'raticate_alola'],
    ['Pikachu (Partner Pikachu)', 'pikachu_partner'],
    ['Meowth (Galarian Meowth)', 'meowth_galar'],
    ['Farfetch\'d', 'farfetchd'],
    ['Farfetch\'d (Galarian Farfetch\'d)', 'farfetchd_galar'],
    ['Groudon (Primal Groudon)', 'groudon_primal'],
    ['Deoxys (Normal Forme)', 'deoxys_normal'],
    ['Wormadam (Plant Cloak)', 'wormadam_plant'],
    ['Rotom (Heat Rotom)', 'rotom_heat'],
    ['Giratina (Altered Forme)', 'giratina_altered'],
    ['Darmanitan (Standard Mode)', 'darmanitan_standard'],
    ['Darmanitan (Galarian Zen Mode)', 'darmanitan_zen_galar'],
    ['Kyurem (Black Kyurem)', 'kyurem_black'],
    ['Greninja (Ash-Greninja)', 'greninja_ash'],
    ['Gourgeist (Small Size)', 'gourgeist_small'],
    ['Zygarde (50% Forme)', 'zygarde_50'],
    ['Zygarde-10%', 'zygarde_10'],
    ['Hoopa (Hoopa Confined)', 'hoopa_confined'],
    ['Wishiwashi (School Form)', 'wishiwashi_school'],
    ['Minior (Meteor Form)', 'minior_meteor'],
    ['Minior (Core)', 'minior_core'],
    ['Necrozma (Dusk Mane Necrozma)', 'necrozma_dusk_mane'],
    ['Toxtricity (Low Key Form)', 'toxtricity_low_key'],
    ['Eternatus (Eternamax Eternatus)', 'eternatus_eternamax'],
    ['Urshifu (Single Strike Style)', 'urshifu'],
    ['Urshifu (Rapid Strike Style)', 'urshifu_rapid_strike'],
    ['Indeedee (Male)', 'indeedee_m'],
    ['Indeedee (Female)', 'indeedee_f'],
    ['Mr. Mime', 'mr_mime'],
    ['Type: Null', 'type_null'],
    ['Zacian (Hero of Many Battles)', 'zacian'],
    ['Zacian (Crowned Sword)', 'zacian_crowned'],
    ['Diancie (Mega Diancie)', 'diancie_mega'],
    ['Calyrex (Ice Rider Calyrex)', 'calyrex_ice']
  ]

  for test in pokemonTests:
    if (parseName(test[0], 'pokemon') != test[1]):
      print(parseName(test[0], 'pokemon'), 'is not', test[1])