# General structure

All of the `.sql` files here are for inserting data into MySQL tables. INSERT INTO statements for all the entity classes are in `entities.sql`. INSERT INTO statements for the junction tables are in other files such as `abilities.sql`, according to the subject-object/owner-owned relationship described previously. For example, the junction table between Pokemon and Abilities is in `pokemon.sql`, since Pokemon is the subject in the 'Pokemon has Ability' relationship.

These MySQL statements are gathered in `index.js`, stored in a single object, and then exported.

All statements are of the form:

    INSERT INTO <table name> (
      ...
      <column names>
      ...
    ) VALUES ?;

This statement includes all the columns for the relevant tables, except the `AUTO_INCREMENT` column, which is not necessary. The `?` is a placeholder for the `mysql2` package to fill in the actual data values.

See `../tables/README.md` for naming conventions of the tables.

# Extended example: Adding Natures

From the discussion in `../README.md`, we know we need to insert data into three tables. These are simple statements, which you can find as follows:

- `nature` in `entities.sql`
- `nature_modifies_stat` in `natures.sql`
- `item_confuses_nature` in `items.sql`

Don't forget to add `['natures.sql', 'natureJunctionTables']` to `FILENAMES_AND_KEYS` in `index.js`.