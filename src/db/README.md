# General structure

The `sql` folder contains all the necessary MySQL statements for creating and inserting into the tables of the database. `sql/index.js` exports the `tableStatements` object, which contains these statements. This gives a pseudo-ORM. 

The `utils` folder consists of functions which compose the various SQL statements into scripts. These functions are combined further in `index.js` into functions which can be run for various database operations. These functions are at the bottom of `index.js`, commented out. The user can uncomment the desired function to run it. Perhaps a CLI interface would be less crude, but I have found these statements quite helpful for automating the various database tasks.

For example, running `node src/db/index.js` with `resetEverything()` un-commented will delete all the data from the database and drop all the tables, then create all the tables and re-insert the data again. On the other hand, the `reset ... JunctionTables` functions allow re-inserting data for specific classes of junction tables. The user can comment and uncomment the appropriate functions for desired database operations. For example, if they're debugging data in an ability junction table, they can comment out all the functions by `resetAbilityJunctionTables` at the bottom and run that.

# Extended example: Adding Natures

A few lines of code need to be written in several spots in both the `sql` folders and `utils` folders, so refer to the `README.md` files in those folders. 

Once that is done correctly, running `node src/db/index.js` with only `resetEverything()` un-commented at the bottom (in the 'Joint database statements' region) will insert all of the data, including the Nature data, into the database.