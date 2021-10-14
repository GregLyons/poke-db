def getDataPath():
  return '..\data\\'

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