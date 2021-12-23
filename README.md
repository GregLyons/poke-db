# Purpose

The goal of this code is to set up a MySQL backend for a [GraphQL API](https://github.com/GregLyons/poke-gql), to be used in Pokemon apps. The data herein is focused around competitive Pokemon, and is mostly scraped from Bulbapedia, among other sources. 

I have provided `README.md` files in most of the other directories explaining the role of each folder in achieving this goal. If you want to add data to this project, I have written out a detailed example on doing so across these `README.md` files. I have organized my code so as to facilitate inserting new data, and several of the conventions I have employed in processing the data are to this end. These are described in the appropriate `README.md` file.

The `README.md` file in the `src` folder describes the overall structure of this repository.

# Quick setup

Currently I do not have the funds or expertise to host this database, or the API. I have tried to make setting up the necessary MySQL database from scratch as simple as possible, but it does take some work if one doesn't already have MySQL installed. Once you have an empty MySQL database to insert the tables into, do the following:

1. Write a `.env` file in this directory with the database credentials.
2. Go to `src/index.js` and go to the 'JOINT DATABASE STATEMENTS' region. In that region, make sure everything but `resetEverything()` is commented out. 
3. Run `node src/db/index.js`. The `resetEverything()` function will create all the necessary tables in your database, and insert all the data. There will be a lot of messages as tables are created and data is inserted, which should take about 15-20 minutes (on my machine). The last thing to finish will almost certainly be inserting data into `pokemon_pmove` (the learnset tables). Once that has been inserted (a message will come up), everything should be ready.

Your `.env` file should look like:

    DB_HOST=<your database server name>
    DB_USERNAME=<your database username>
    DB_PASSWORD=<your database password>
    DB_NAME=<your database name>