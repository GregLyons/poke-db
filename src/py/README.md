# The concerns of each folder

- `fetching` is where relevant PokeAPI data (e.g. the ID number of each Pokemon) is fetched, generating a couple `.csv` files.
- `json_creators` is where the `.csv` data generated in the other folders is processed into Python `dict`s, e.g. `abilityDict`, `itemDict`, etc. These `dict`
- `scraping` is where data from Bulbapedia (or occasionally Serebii) is scraped, generating `.csv` files.

# Extended example: Adding Natures

To add the Nature entity class, one would first need to add the data for it. [This Bulbapedia page](https://bulbapedia.bulbagarden.net/wiki/Nature) has a table listing the relevant data, so we write the code to scrape it in `scraping/natures.py`. 

Then, in `json_creators/natures.py`, we process this scraped data into a `dict`, `natureDict`. Once `../data/raw_data/json/natures.json` is created, we're ready to process it. 

For more details, check the `scraping` and `json_creators` folders.