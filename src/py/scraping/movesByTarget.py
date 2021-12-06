import csv
import re
from utils import openLink, getCSVDataPath, parseName, isShadowMove

# given an <a> element for a move category, parse the text to determine the target category, and find all moves therein
def handleCategoryLink(link, writer):
  categoryLink = 'https://bulbapedia.bulbagarden.net' + link['href']
  linkText = link.get_text()


  targetCategory = parseName(re.search(r'Moves that [can ]*target (.*)', linkText).group(1).rstrip(' Pokémon'))

  # remove extraneous words
  targetCategory = targetCategory.replace('the_', '').replace('an_', '').replace('one_', '').replace('any_', '')

  # this is the majority of moves--we'll use at as the default for moveDict, for no further processing necessary; this way, we avoid having to navigate multiple pages
  if targetCategory == 'adjacent':
    return
  # this category just contains links to one of the other categories
  elif targetCategory == 'non_adjacent':
    return
  
  # now find specific move
  bs = openLink(categoryLink, 0, 10)
  moveLists = bs.find(id='mw-pages').find_all('ul')

  try:
    for moveList in moveLists:
      for move in moveList.find_all('li'):
        moveName = parseName(move.get_text().removesuffix(' (move)'))
        
        # ignore shadow moves; check for prefix so we don't have to search the shadow move list for every move
        if 'shadow_' in moveName:
          if isShadowMove(moveName):
            continue

        writer.writerow([moveName, targetCategory])
  except Exception as e:
    print(e)
    print('something went wrong with', targetCategory)
    print()

  return

# Columns are Targets, Move Name
def makeCSV(fname):
  with open(fname, 'w', newline='', encoding='utf-8') as targetCSV:
    writer = csv.writer(targetCSV)
    writer.writerow(['Move Name', 'Targets'])
    
    bs = openLink('https://bulbapedia.bulbagarden.net/wiki/Category:Moves_by_targeting', 0, 10)

    categoryList = bs.find('div', {'class': 'mw-category'}).find('ul').find_all('li')
    for categoryLink in categoryList:
      handleCategoryLink(categoryLink.find('a'), writer)

  return

def main():
  dataPath = getCSVDataPath() + '\\moves\\'
  fname = dataPath + 'movesByTarget.csv'
  makeCSV(fname)

  return

if __name__ == '__main__':
  main()