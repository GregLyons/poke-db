# General structure

The folders herein consist of `.sql` files containing all the necessarily MySQL statements for inserting data into the database. These statements are stored in an object, `tableStatements`, created and exported in `index.js`.

- `tables`
  - Contains all CREATE TABLE statements.
  - Also adds DELETE statements, UPDATE statements, etc.

# Extended example: Adding Natures

We need to add a few MySQL tables for Nature data. Specifically, we need three tables:
  
- `nature`: an entity table containing basic data about Natures
- `nature_modifies_stat`: a junction table between `nature` and `stat`
- `item_confuses_nature`: a junction table between `item` and `nature`.

We need to write statements in both the `tables` folder and the `inserting` folder. We'll need to create a `natures.sql` file and add to the `entities.sql` and `items.sql` files in each of the two folders. For organization, we keep the filenames between the two folders matched.