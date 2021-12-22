# General structure

All of the `.sql` files here are for creating MySQL tables. CREATE TABLE statements for all the entity classes are in `entities.sql`. CREATE TABLE statements for the junction tables are in other files such as `abilities.sql`, according to the subject-object/owner-owned relationship described previously. For example, the junction table between Pokemon and Abilities is in `pokemon.sql`, since Pokemon is the subject in the 'Pokemon has Ability' relationship.

These MySQL statements are gathered in `index.js`, where, for each table, a few other statements (e.g. `DELETE FROM`, `DROP TABLE`) are added, and then the resulting object is exported.

- Most table attributes are name-spaced, e.g. `ability_name` versus `pokemon_name`, the exception being `generation_id` and `introduced`. 
- Most entity tables have `generation_id` and `introduced` as foreign keys, referring to the `generation` table. 
- The primary keys for most entity tables consist of two parts: the foreign key `generation_id`, and an `AUTO_INCREMENT` field, called e.g. `ability_id`, `item_id`, `stat_id`. 
- With the exception of `generation_id`, these should be `SMALLINT`s (keep in mind we have a row per entity, *per generation*, so 255 rows is often not enough, and eventually won't be enough as more generations are added).
- `generation_id` is just the number of the generation, and is a `TINYINT`. Since almost all tables will have a `generation_id` column (or two, for junction tables), this is significant for reducing storage requirements. One caveat is that LGPE data, if it is to be added, becomes a bit complicated to add. Perhaps one could use a big number like '200' to represent it as a separate 'Generation'.
- We use names like `pmove`, `pdescription`, and `pstatus` to avoid reserved keywords. 

# Extended example: Adding Natures

From the discussion in `../README.md`, we know we need to add three tables:

- `nature` in `entities.sql`
  - Consists of non-relational data about Natures, e.g. their names, and their flavor preferences.
  - Even though there are only 25 natures, we use a `SMALLINT` rather than a `TINYINT` for the `AUTO_INCREMENT` ID; keep in mind that each entity is split into multiple instances for each generation. Thus, there are actually 150 rows in the `nature` table, and after Gen 11 we'd need a `SMALLINT` anyway (25 * 9 = 275 > 255). 
- `nature_modifies_stat` in `natures.sql`
  - We already have junction tables of this form, e.g. `ability_modifies_stat` in `abilities.sql`, so one could just copy/paste that table into `natures.sql` and replace `ability` with `nature`.
  - Note that we've added additional columns, `chance` and `recipient`. This is more relevant for Stat modifications for Abilities, Items, and Moves, but for the `..._modifies_stat` junction tables, we use one single form to add consistency to the GraphQL API.
- `item_confuses_nature` in `items.sql`
  - This is a simple junction table, whose columns are simply the primary keys of the two entity tables. 

Finally, don't forget to add `['natures.sql', 'natureJunctionTables']` to `FILENAMES_AND_KEYS` in `index.js`.
