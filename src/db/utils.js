const GEN_ARRAY = [
  [1, 'I'],
  [2, 'II'],
  [3, 'III'],
  [4, 'IV'],
  [5, 'V'],
  [6, 'VI'],
  [7, 'VII'],
  [8, 'VIII'],
];
const NUMBER_OF_GENS = GEN_ARRAY.length;

// CREATING AND DROPPING TABLES
// #region

// Drops foreign keys and indices from pokemon_pmove to facilitate deleting data, as pokemon_pmove has the most rows by far.
const prepareForDrop = async (db) => {
  console.log('Dropping foreign keys and indices from pokemon_pmove--if they exist--to improve DELETE performance...');

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
          return db.promise().query(`ALTER TABLE pokemon_pmove DROP FOREIGN KEY ${result.CONSTRAINT_NAME}`);
        })
      )
    })
    .then( () => console.log('Foreign keys deleted from pokemon_pmove.'))
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
  .then( () => console.log('Indices deleted from pokemon_pmove.'));

  return;
}

// Drops all tables, if they exist.
const dropTables = async (db, tableStatements) => {
  // Drop junction tables.
  await Promise.all(
    Object.keys(tableStatements)
      .filter(tableGroup => tableGroup != 'entityTables')
      .map(tableGroup => {
        return Promise.all(
          Object.keys(tableStatements[tableGroup]).map(tableName=> {
            const statement = tableStatements[tableGroup][tableName].drop;
            
            return db.promise().query(statement).then( () => console.log(`${tableName} dropped.`));
          })
        );
      })
    )
    .then( () => console.log('\nJunction tables dropped.\n'))
    .catch(console.log);

  // Drop basic entity tables.
  await Promise.all(Object.keys(tableStatements.entityTables)
    .filter(tableName => tableName !== 'generation').map(tableName => {
      const statement = tableStatements.entityTables[tableName].drop;

      return db.promise().query(statement)
        .then( () => console.log(`${tableName} dropped.`));
    }))
    .then( () => console.log(`\nEntity tables dropped.\n`))
    .catch(console.log);

  // Finally, drop generation table.
  return await db.promise().query(tableStatements.entityTables.generation.drop)
    .then( () => console.log('\ngeneration table dropped.\n'))
    .catch(console.log);
}

// Creates all tables, if they don't already exist.
const createTables = async (db, tableStatements) => {
  // Create generation table, which most other tables reference.
  await db.promise().query(tableStatements.entityTables.generation.create)
    .then( () => console.log('\ngeneration table created.\n'))
    .catch(console.log);

  // Create basic entity tables, e.g. stat, pokemon, pmove, which the junction tables reference.
  await Promise.all(Object.keys(tableStatements.entityTables)
    .filter(tableName => tableName !== 'generation').map(tableName => {
      const statement = tableStatements.entityTables[tableName].create;

      return db.promise().query(statement)
        .then( () => console.log(`${tableName} created.`));
    }))
    .then( () => console.log(`\nEntity tables created.\n`))
    .catch(console.log);
  
  // Create junction tables.
  return await Promise.all(
    Object.keys(tableStatements)
      .filter(tableGroup => tableGroup != 'entityTables')
      .map(tableGroup => {
        return Promise.all(
          Object.keys(tableStatements[tableGroup]).map(tableName=> {
            const statement = tableStatements[tableGroup][tableName].create;
            
            return db.promise().query(statement).then( () => console.log(`${tableName} created.`));
          })
        );
      })
  )
  .then( () => console.log('\nJunction tables created.\n'))
  .catch(console.log);
};

// #endregion

// INSERTING DATA
// #region

// #endregion

module.exports = {
  NUMBER_OF_GENS,
  GEN_ARRAY,
  prepareForDrop,
  dropTables,
  createTables,
}