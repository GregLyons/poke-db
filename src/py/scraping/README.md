# General structure

Most of the `.py` files herein are for scraping one or more tables and storing the data in `.csv` files. Some `.py` files may make multiple `.csv` files. Aside from these files, we have the following:

- `makeAll.py`
  - Gathers together all the scraping scripts and runs them. This takes several minutes, as the time necessary for each script varies from seconds to a few minutes. 
  - In general, I recommend not running this except when you need to add multiple different types of data (e.g. when a new generation is released, or multiple `.csv`s are corrupted for whatever reason).
- `utils.py`
  - Provides several utility functions to facilitate scraping. We list the two most common ones here.
  - `openLink` returns a `BeautifulSoup` object of the given link, after which one can navigate throughout the page as desired.
  - `parseName` takes in the name of an entity on Bulbapedia (e.g. 'Pikachu', 'RKS System', 'Leppa Berry') and converts it to `snake_case`. Since we're scraping from tables all over Bulbapedia, the formats of the names aren't already consistent. In particular, for Pokemon we need to consider a lot of exceptions. 

# Extended example: Adding Natures

Scraping the Nature table from [the page on Bulbapedia](https://bulbapedia.bulbagarden.net/wiki/Nature) is simple, since the data is encapsulated in a single table. We create a new folder, `../../data/raw_data/csv/natures` to store `natureList.csv`, which we will create. 

We use the `openLink` function provided in `utils.py` to get a `BeautifulSoup` object, then we navigate to the table and add the data. For the names of the Natures and of the Stats, we use the `parseName` function, also provided in `utils.py`, to ensure that all entity names are of the same `snake_case` style.

Now, we need to go to `../json_creators` to process this data.