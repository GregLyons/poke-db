# General structure

The files herein compose all the MySQL statements in `../sql` in different ways to perform operations on the database using Node's `mysql2` module. 

- `creating.js`
  - Combines statements for creating all the tables. 
- `dropping.js` 
  - Combines statements for dropping all the tables. - `prepareLearnsetTableForDrop` removes foreign keys and indices from the learnset junction table, `pokemon_pmove`. This is the largest table by far in the database, so we do this to help speed up the `DROP TABLE pokemon_pmove` operation.
- `foreignKeyMaps.js` 
  - Creates Javascript `Map` objects which map entity name/generation pairs to primary key pairs for entities. 
  - Recall that the primary key for entities consists of a synthetic `AUTO_INCREMENT` column. For inserting into junction tables, which consists of foreign keys to the appropriate entity tables, we need to know the foreign keys of the two entities in question. Foreign key maps allow us to determine this from the names of the entities.
  - Since the name of each entity is unique (somewhere in `py` we've changed the name of the Item `metronome` to `metronome_item` so as not to conflict with the Move `metronome`), we could've used the entity name as the primary key. Using a synthetic primary key helps speed up queries, however. Hence, we need these foreign key `Map`s.
- `jointStatements.js` 
  - Gathers statements from the other files and composes them further. Then exports them.
  - For example, to re-insert data into junction tables, we first delete the data from them, then re-insert the data (two separate MySQL statements).
  - As another example, to re-insert data into entity tables, we first delete the data from them, then reset the `AUTO_INCREMENT` counter, then re-insert the data (three separate MySQL statements).
- `reinserting.js`
  - Contains functions for executing `DELETE FROM` and `INSERT INTO` queries.
- `values.js`
  - Contains the code for actually inserting the processed data according to the table name.
  - The `foreignKeyMaps` array passed into `getValuesForTable` should unpack alphabetically.
  - Descriptions and Sprites (Sprites not yet added) are referred to as 'meta entities', which represent other entities, such as Pokemon.

# Extended example: Adding Natures

We need to add a few lines of code in several places:

- `creating.js` and `dropping.js`
  - No code necessary.
- `foreignKeyMaps.js`
  - In `getIdentifyingColumnNames`, add `case 'nature'` to the `switch` statement. Here we're saying that we'll use the name of the Nature to find its foreign key.
- `jointStatements.js`
  - Add a region for inserting data for nature junction tables. Here we can simply copy/paste from another region and change a few words (we should probably extract this to a single function).
  - See Region 6 for the code.
- `reinserting.js`
  - In `reinsertGenDependentEntityData` add `'nature'` to `entityTableNames`.
  - Write `reinsertNatureJunctionData` like the other `reinset ... JunctionData` functions. Note the following:
    - We get the names of the Nature junction tables from `tableStatements`.
    - `foreignKeyTables` lists the tables from which we need the foreign keys. Since `nature_modifies_stat` is a relationship between Natures and Stats, the foreign keys will refer to each of those tables. *Important: organize the table names alphabetically to help remember the order in which to unpack the foreign key maps stored in `foreignKeyMaps`.* 
    - Import the Nature data from `../../data/processed_data/natures.json` and store it in `natureData`. 
    - Call `reinsertDataForTableGroup` with the appropriate arguments.
- `values.js`
  - In the 'UNPACK `foreignKeyMaps`' region, write a case for the `natureJunctionTables` `tableGroup`.
  - In the 'COMPUTE `values`' region, write three cases, corresponding to the relevant table names:
    - `case 'nature'` in the 'GENERATION-DEPENDENT ENTITIES' region for the entity data. Follows the pattern of the other cases in this region.
    - `case 'item_confuses_nature'` in the 'ITEM JUNCTION TABLES' region for the relational data between Items and Natures. Follows the pattern of the `item_effect` case in this region.
    - `case 'nature_modifies_stat'` in the 'NATURE JUNCTION TABLES' region (add that) for the relational data between Natures and Stats. Follows the pattern of the `item_modifies_stat` case. Note that we use default values for the chance and target data.

This is a tricky part. When you run `resetEverything()` in `../index.js`, you may find that you've made some bugs. Once you've created the tables and inserted the basic Nature data, you can use `resetItemJunctionTables()` and `resetNatureJunctionTables()` (be sure to import that and write it in the appropriate region) to debug the junction tables, instead of resetting the entire database each time.