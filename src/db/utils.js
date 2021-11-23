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
const prepareLearnsetTableForDrop = async (db) => {
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

const insertBasicEntities = async(db, tableStatements) => {
  // TODO add sprites
  const basicEntityTableNames = [
    'generation',
    'pdescription',
    'pstatus',
    'stat',
  ];

  /*
    1. DELETE FROM tableName.
    2. Reset AUTO_INCREMENT counter for tableName.
    3. INSERT INTO tableName.
  */
  return await Promise.all(
    basicEntityTableNames.map(async (tableName) => {
      // DELETE FROM tableName.
      await db.promise().query(tableStatements.entityTables[tableName].delete)
        .then( () => console.log(`${tableName} table deleted.`))
        .catch(console.log);

      // Reset AUTO_INCREMENT counter for tableName.
      await db.promise().query(tableStatements.entityTables[tableName].reset_auto_inc)
        .then( () => console.log(`Reset AUTO_INCREMENT counter for ${tableName} table.`))
        .catch(console.log)

      // INSERT INTO tableName.
      const values = getValuesForBasicEntities(tableName);
      return db.promise()
        .query(tableStatements.entityTables[tableName].insert, [values])
        .then( ([results, fields]) => {
          console.log(`${tableName} data inserted: ${results.affectedRows} rows.`);
        })
        .catch(console.log);
    })
  )
  .then( () => console.log('Inserted basic entity data.'))
  .catch(console.log);
}

const getValuesForBasicEntities = (tableName) => {
  let values;
  switch(tableName) {
    case 'generation':
      values = GEN_ARRAY;
      break;
    
    case 'pdescription':
      const descriptions = require('./processing/processed_data/descriptions.json');
      values = descriptions.reduce((acc, descriptionObj) => {
        // extract entityName and description type
        const { entity_name: entityName, description_type: descriptionType } = descriptionObj;
        
        // descriptionObj contains all the descriptions for entity name, so we need to split them up. The unique descriptions are indexed by numeric keys.
        return acc.concat(Object.keys(descriptionObj)
          // numeric keys contain description info
          .filter(key => !isNaN(key))
          .map(descriptionIndex => {
            // descriptionObj[descriptionIndex] is a two-element array, whose first element is the description itself, and whose second element is another array containing version group codes; we don't need the latter at this moment
            const description = descriptionObj[descriptionIndex][0];
            
            return [description, descriptionIndex, descriptionType, entityName];
          }));
      }, []);
      break;
    
    case 'pstatus':
      values = require('./processing/processed_data/statuses.json').map(data => [data.name, data.formatted_name]);
      break;
    
    case 'stat':
      values = require('./processing/processed_data/stats.json').map(data => [data.name, data.formatted_name]);
      break;
    
      default:
        console.log(`${tableName} unhandled.`);
  }
  return values;
}

// #endregion

module.exports = {
  NUMBER_OF_GENS,
  GEN_ARRAY,
  prepareForDrop: prepareLearnsetTableForDrop,
  dropTables,
  createTables,
  insertBasicEntities,
}