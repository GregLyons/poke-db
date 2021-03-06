import csv
import requests
from utils import parseName, getCSVDataPath

# columns are name, ID, species name; all from PokeAPI
def makeIDcsv(fname): 
  with open(fname, 'w', newline='', encoding='utf-8') as idCSV:
    writer = csv.writer(idCSV)
    writer.writerow(['PokeAPI Name', 'PokeAPI ID'])
    
    response = requests.get('https://pokeapi.co/api/v2/pokemon?limit=1200').json()
    for result in response["results"]:
      pokemonName = result["name"]
      url = result["url"]
      pokemonID = url.removesuffix('/').split('/')[-1]

      writer.writerow([pokemonName, pokemonID])
  return

def makeFormIDcsv(fname):
  with open(fname, 'w', newline='', encoding='utf-8') as idCSV:
    writer = csv.writer(idCSV)
    writer.writerow(['PokeAPI Form Name', 'PokeAPI ID'])
    
    response = requests.get('https://pokeapi.co/api/v2/pokemon-form?limit=1300').json()
    for result in response["results"]:
      pokemonFormName = result["name"]
      url = result["url"]
      pokemonFormID = url.removesuffix('/').split('/')[-1]

      writer.writerow([pokemonFormName, pokemonFormID])
  return

def getSpecies(url):
  species = requests.get(url).json()["species"]["name"]
  return species

def main():
  dataPath = getCSVDataPath() + '/pokemon/'
  fname = dataPath + 'pokemonByID.csv'
  # makeIDcsv(fname)

  form_fname = dataPath + 'pokemonFormByID.csv'
  makeFormIDcsv(form_fname)

  return

if __name__ == '__main__':
  main()