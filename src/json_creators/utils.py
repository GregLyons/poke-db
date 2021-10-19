import re

def getBulbapediaDataPath():
  return 'src\\data\\bulbapedia_data\\'

def getSerebiiDataPath():
  return 'src\\data\\serebii_data\\'

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

# parse names in different forms from Bulbapedia and Smogon API to a common, snake_case form
def parseName(text, mode='normal'):
  text = text.strip('\n')
  if mode == 'normal':
    # hyphens to underscores
    text = text.replace('-', '_')

    # remove commas, apostrophes, periods, colons
    text = re.sub(r'[,\'\.:]', '', text)

    # separate lowercase followed by uppercase, e.g. 'ExtremeSpeed' to 'Extreme Speed'--for Bulbapedia typos
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
    
    # replace spaces with underscores and convert to lowercase
    return text.replace(' ', '_').lower().strip('_')

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