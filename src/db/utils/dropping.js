/*
  DROPPING TABLES
*/

/*
  Throughout, db refers to the MySQL database, and tableStatements refers to the object of MySQL statements created in the ./sql folder. 
  
  tableGroup will refer to keys of this object, and tableName will refer to keys of nested object tableStatements[tableGroup].
*/

// Drops all tables.
const dropAllTables = async (db, tableStatements) => {
  console.log('\nDropping all tables...\n')

  // Drop junction tables.
  await dropAllJunctionTables(db, tableStatements);

  // Drop entity tables except for generation.
  await dropTablesInGroup(db, tableStatements, 'entityTables', ['generation']);

  // Finally, drop generation table.
  return dropSingleTableInGroup(db, tableStatements, 'entityTables', 'generation')
  .then( () => console.log('\nDropped all tables.\n'))
  .catch(console.log);
}

// Drops junction tables and entity tables that aren't relevant to 'pokemon_pmove', which is where learnset data is stored. 
const dropTablesNotRelevantToLearnsets = async (
  db,
  tableStatements
) => {
  console.log(`\nDropping all tables not relevant to 'pokemon_pmove'...\n
  `)
  await dropAllJunctionTables(db, tableStatements, ['pokemon_pmove']);
  
  return dropTablesInGroup(db, tableStatements, ['pokemon', 'pmove'])
  .then( () => console.log(`\nDropped all tables not relevant to 'pokemon_pmove'.`))
  .catch(console.log);
}

// Drops junction tables that aren't listed in ignoreTables.
const dropAllJunctionTables = async (
  db,
  tableStatements,
  ignoreTables = []
) => {
  console.log(`\nDropping all junction tables...\n`)

  return Promise.all(
    Object.keys(tableStatements)
      .filter(tableGroup => tableGroup != 'entityTables')
      .map(tableGroup => {
        return dropTablesInGroup(db, tableStatements, tableGroup, ignoreTables);
      })
  )
  .then( () => console.log(`\nDropped junction tables.\n`))
  .catch(console.log);
}

// Drops tables in a given tableGroup that aren't listed in ignoreTables.
const dropTablesInGroup = async (
  db,
  tableStatements,
  tableGroup,
  ignoreTables = []
) => {
  console.log(`\nDropping tables in '${tableGroup}'...\n`);

  return Promise.all(
    Object.keys(tableStatements[tableGroup])
      .map(async (tableName) => {
        if (ignoreTables.includes(tableName)) {
          return Promise.resolve()
            .then( () => { console.log(`Skipping over '${tableName}' table.`) });
        }

        return dropSingleTableInGroup(db, tableStatements, tableGroup, tableName);
      })
  )
  .then( () => console.log(`\nDropped all tables in '${tableGroup}'.\n`))
  .catch(console.log);
}

// Drops the table named tableName, and which is part of tableGroup. If the table is the learnset table, removes the indices and foreign keys before dropping.
const dropSingleTableInGroup = async (
  db,
  tableStatements,
  tableGroup,
  tableName
) => {
  // If asked to drop learnset table, delete keys and indices first to make it drop more quickly.
  if (tableName == 'pokemon_pmove') {
    await prepareLearnsetTableForDrop(db);
  }

  const dropStatement = tableStatements[tableGroup][tableName].drop

  return db.promise().query(dropStatement)
    .then( () => console.log(`'${tableName}' table dropped.`))
    .catch(console.log);
}

// Drops foreign keys and indices from pokemon_pmove to facilitate deleting data, as pokemon_pmove has the most rows by far.
const prepareLearnsetTableForDrop = async (db) => {
  console.log(`\nDropping foreign keys and indices from 'pokemon_pmove'--if they exist--to improve performance...\n`);

  // Delete foreign keys, if they exist; the index opposite_pokemon_pmove references them, so we must delete them first.
  await db.promise()
    // Selects foreign keys
    .query(`
      SELECT * FROM information_schema.TABLE_CONSTRAINTS 
      WHERE information_schema.TABLE_CONSTRAINTS.CONSTRAINT_TYPE = 'FOREIGN KEY' 
      AND information_schema.TABLE_CONSTRAINTS.TABLE_SCHEMA = '${process.env.DB_NAME}'
      AND information_schema.TABLE_CONSTRAINTS.TABLE_NAME = 'pokemon_pmove'
    `)
    .then( ([results, fields]) => {
      if (results.length == 0) { return; }
      
      // Deletes each returned foreign key.
      return Promise.all(
        results.map(result => {
          return db.promise().query(`
            ALTER TABLE pokemon_pmove DROP FOREIGN KEY ${result.CONSTRAINT_NAME}
          `);
        })
      )
    })
    .then( () => console.log(`Foreign keys deleted from 'pokemon_pmove'.`))
    .catch(console.log)

  // Deletes the indices.
  await Promise.all([
    db.promise().query(`DROP INDEX opposite_pokemon_pmove ON pokemon_pmove`)
      .then()
      .catch( err => {
        // Index doesn't exist.
        if (err.errno == 1091) console.log('Index doesn\'t exist. Moving on...');
        // Table doesn't exist.
        else if (err.errno == 1146) console.log('Table doesn\'t exist. Moving on...');
        else console.log(err);
      }),
    db.promise().query(`ALTER TABLE pokemon_pmove DROP PRIMARY KEY`)
      .then()
      .catch( err => {
        // Index doesn't exist.
        if (err.errno == 1091) console.log('Primary key index doesn\'t exist. Moving on...');
        // Table doesn't exist.
        else if (err.errno == 1146) console.log('Table doesn\'t exist. Moving on...');
        else console.log(err);
      })
  ])
  .then( () => console.log(`Indices deleted from 'pokemon_pmove'.`));

  return Promise.resolve().then( () => console.log(`\n'pokemon_pmove' prepared for dropping.\n`));
}

module.exports = {
  dropSingleTableInGroup,
  dropTablesInGroup,
  dropAllJunctionTables,
  dropTablesNotRelevantToLearnsets,
  dropAllTables,
}