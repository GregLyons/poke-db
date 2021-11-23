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

const timeElapsed = timer => {
  let now = new Date().getTime();
  console.log('Took', Math.floor((now - timer) / 1000), 'seconds.\n');
  timer = now;
  return timer;
}

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


/* 
  DELETE FROM tables for generation-independent entities, then INSERT INTO those tables. 
  
  WARNING: Will cause data in most other tables, which depend on generation, to be deleted as well. 
*/
const resetGenDependentEntityTables = async(db, tableStatements) => {
  const entityTableNames = [
    'ability',
    'effect',
    'item',
    'pokemon',
    'pmove',
    'ptype',
    'usage_method',
    'version_group'
  ];
  return resetTableGroup(db, tableStatements, entityTableNames)
}

/*
  DELETE FROM tables for generation-dependent entities, then INSERT INTO those tables.

  WARNING: Will cause data in the junction tables to be deleted.
*/
const resetBasicEntityTables = async(db, tableStatements) => {
  // TODO add sprites
  const basicEntityTableNames = [
    'generation',
    'pdescription',
    'pstatus',
    'stat',
  ];
  return await resetTableGroup(db, tableStatements, basicEntityTableNames)
}

const resetTableGroup = async(
  db,
  tableStatements,
  tableNameArr,
) => {
  /*
    1. DELETE FROM tableName.
    2. Reset AUTO_INCREMENT counter for tableName.
    3. INSERT INTO tableName.
  */
  return await Promise.all(
    tableNameArr.map(async (tableName) => {
      // DELETE FROM tableName.
      await deleteTableRows(db, tableStatements, tableName);

      // Reset AUTO_INCREMENT counter for tableName.
      await resetAutoIncrement(db, tableStatements, tableName);

      // INSERT INTO tableName.
      const values = getValuesForTable(db, tableName);
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

// #endregion


// DASDSADSADSA
// #region
const deleteTableRows = async(db, tableStatements, tableName) => {
  return db.promise().query(tableStatements.entityTables[tableName].delete)
    .then( () => console.log(`${tableName} table deleted.`))
    .catch(console.log);
}

const resetAutoIncrement = async(db, tableStatements, tableName) => {
  return db.promise().query(tableStatements.entityTables[tableName].reset_auto_inc)
    .then( () => console.log(`Reset AUTO_INCREMENT counter for ${tableName} table.`))
    .catch(console.log)
}

const getValuesForTable = (db, tableName) => {
  let values;
  switch(tableName) {
    /*
      BASIC ENTITIES
    */
    case 'generation':
      /*
        Need (
          generation_id,
          generation_code
        )
      */
      values = GEN_ARRAY;
      break;
    
    case 'pdescription':
      /*
        Need (
          pdescription_text,
          pdescription_index,
          pdescription_type,
          entity_name
        )
      */
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
      /*
        Need (
          pstatus_name,
          pstatus_formatted_name
        )
      */
      values = require('./processing/processed_data/statuses.json').map(data => [data.name, data.formatted_name]);
      break;
    
    case 'stat':
      /*
        Need (
          stat_name,
          stat_formatted_name
        )
      */
      values = require('./processing/processed_data/stats.json').map(data => [data.name, data.formatted_name]);
      break;

    /*
      GENERATION-DEPENDENT ENTITIES
    */
    case 'ability':
      /*
        Need (
          generation_id,
          ability_name,
          ability_formatted_name,
          introduced
        )
      */
      values = require('./processing/processed_data/abilities.json')
        .map(data => [data.gen, data.name, data.formatted_name, data.introduced]);
      break;

    case 'effect':
      /* 
        Need (
          effect_name,
          effect_formatted_name,
          introduced
        )
      */
      values = require('./processing/processed_data/effects.json')
        .map(data => [data.name, data.formatted_name, data.introduced]);
      break;

    case 'item':
      /* 
        Need (
          generation_id,
          item_name,
          item_formatted_name,
          introduced,
          item_class
        ) 
      */
      values = require('./processing/processed_data/items.json')
        .map(data => [data.gen, data.name, data.formatted_name, data.introduced, data.item_type]);
      break;

    case 'pokemon':
      /* 
        Need (
          generation_id,
          pokemon_name,
          pokemon_formatted_name,
          pokemon_species,
          pokemon_dex,
          pokemon_height,
          pokemon_weight,
          introduced,
          pokemon_hp,
          pokemon_attack,
          pokemon_defense,
          pokemon_special_defense,
          pokemon_special_attack,
          pokemon_speed
        )
      */
      values = require('./processing/processed_data/pokemon.json')
        // filter out cosmetic forms and lgpe_only pokemon
        .filter(data => !data.cosmetic && !(data.gen == 'lgpe_only'))
        .map(data => [
          data.gen,
          data.name,
          data.formatted_name,
          data.species,
          data.dex_number,
          data.height,
          data.weight,
          data.introduced,
          data.hp,
          data.attack,
          data.defense,
          data.special_defense,
          data.special_attack,
          data.speed,
        ]);
      break;
    
    case 'pmove':
      /*
        Need (
          generation_id,
          pmove_name,
          pmove_formatted_name,
          introduced,
          pmove_power,
          pmove_pp,
          pmove_accuracy,
          pmove_category,
          pmove_priority,
          pmove_contact,
          pmove_target
        )
      */
      values = require('./processing/processed_data/moves.json')
        .map(data => [
          data.gen,
          data.name,
          data.formatted_name,
          data.introduced,
          data.power,
          data.pp,
          data.accuracy,
          data.category,
          data.priority,
          data.contact,
          data.target
        ]);
      break;

    case 'ptype':
      /*
        Need (
          generation_id,
          ptype_name,
          ptype_formatted_name,
          introduced
        )
      */
      values = require('./processing/processed_data/pTypes.json')
        .map(data => [data.gen, data.name, data.formatted_name, data.introduced]);
      break;

    case 'usage_method':
      /*
        Need (
          usage_method_name
          usage_method_formatted_name
          introduced
        )
      */
      values = require('./processing/processed_data/usageMethods.json')
        .map(data => [data.name, data.formatted_name, data.introduced]);
      break;

    case 'version_group':
      /*
        Need (
          version_group_code,
          version_group_formatted_name
          introduced
        )
      */
      values = require('./processing/processed_data/versionGroups.json').map(data => [data.name, data.formatted_name, data.introduced]);
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
  timeElapsed,
  prepareLearnsetTableForDrop,
  dropTables,
  createTables,
  resetBasicEntityTables,
  resetGenDependentEntityTables,
}