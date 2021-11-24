// MISCELLANEOUS HELPERS 
// #region

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

const getGenOfVersionGroup = (versionGroupCode) => {
  switch(versionGroupCode) {
    case 'Stad':
      return 1;
    case 'GS':
    case 'C':
    case 'Stad2':
      return 2;
    case 'RS':
    case 'E':
    case 'Colo':
    case 'XD':
    case 'FRLG':
      return 3;
    case 'DP':
    case 'Pt':
    case 'HGSS':
    case 'PBR':
      return 4;
    case 'BW':
    case 'B2W2':
      return 5;
    case 'XY':
    case 'ORAS':
      return 6;
    case 'SM':
    case 'USUM':
    case 'PE':
      return 7;
    case 'SwSh':
      return 8;
    default:
      throw `Invalid version group code: ${versionGroupCode}.`
  }
}

const timeElapsed = timer => {
  let now = new Date().getTime();
  console.log('Took', Math.floor((now - timer) / 1000), 'seconds.\n');
  timer = now;
  return timer;
}

// #endregion

// DROPPING TABLES
// #region

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

// #endregion

// CREATING TABLES
// #region

/*
  Throughout, db refers to the MySQL database, and tableStatements refers to the object of MySQL statements created in the ./sql folder. 
  
  tableGroup will refer to keys of this object, and tableName will refer to keys of nested object tableStatements[tableGroup].

  If a given table already exists, then this code will do nothing to that table, since the MySQL statements are of the form 'CREATE TABLE IF NOT EXISTS...'
*/

// Creates all tables.
const createAllTables = async (db, tableStatements) => {
  // Create generation table, which most other tables reference.
  await createSingleTableInGroup(db, tableStatements, 'entityTables', 'generation');

  // Create basic entity tables, e.g. stat, pokemon, pmove, which the junction tables reference.
  await createTablesInGroup(db, tableStatements, 'entityTables');
  
  // Create junction tables.
  return createAllJunctionTables(db, tableStatements);
};

// Creates all junction tables.
const createAllJunctionTables = async (
  db,
  tableStatements
) => {
  console.log(`\nCreating all junction tables...\n`)

  return Promise.all(
    Object.keys(tableStatements)
      .filter(tableGroup => tableGroup != 'entityTables')
      .map(tableGroup => {
        return createTablesInGroup(db, tableStatements, tableGroup);
      })
  )
  .then( () => console.log(`\nCreated all junction tables.\n`))
  .catch(console.log);
}

// Creates all tables in tableGroup.
const createTablesInGroup = async (
  db,
  tableStatements,
  tableGroup
) => {
  console.log(`\nCreating tables in '${tableGroup}'...\n`);
  return Promise.all(
    Object.keys(tableStatements[tableGroup])
      .map(tableName => {
        return createSingleTableInGroup(db, tableStatements, tableGroup, tableName);
      })
  )
  .then( () => console.log(`\nCreated all tables in '${tableGroup}'.\n`))
  .catch(console.log);
}

// Creates tableName in tableGroup.
const createSingleTableInGroup = async (
  db,
  tableStatements,
  tableGroup,
  tableName
) => {
  return db.promise().query(tableStatements[tableGroup][tableName].create)
    .then( () => console.log(`'${tableName}' table created if it didn't already exist.`))
    .catch(console.log);
}

// #endregion

// RESETTING TABLES/INSERTING DATA
// #region

/*
  Each function in this section:
    
    1. Performs DELETE FROM on the relevant tables. (This will cascade.)
    2. Resets the AUTO_INCREMENT counter on those same tables.
    3. Performs INSERT INTO of all relevant data into those same tables.

  Most of these operations each take less than a minute. Moreover, because of how the data is gathered and processed in previous steps, an error in one data point can affect multiple different tables. Also, this is not sensitive data, and can easily be recovered. Finally, we want to overwrite any incorrect data with the correct data. Taking all of this into account, I have judged it best to focus on bulk inserts rather than writing ON DUPLICATE KEY behavior. 

  The one exception to this is the learnset junction table, 'pokemon_pmove'. The bulk insert function for that table has been isolated from the rest, and 'resetPokemonJunctionTables' does not affect 'pokemon_pmove'. Resetting the entity tables WILL affect it, however, so there are ignoreTables arguments in those functions to allow the user to specify which tables to avoid. They would be 'generation' (basic entity), and 'pokemon' and 'pmove' (gen-dependent entities). 
*/

/* 
  DELETE FROM tables for generation-independent entities, then INSERT INTO those tables. 
  
  WARNING: Will cause data in most other tables, which depend on generation, to be deleted as well. 
*/
const reinsertBasicEntityData = async(db, tableStatements, ignoreTables = []) => {
  // TODO add sprites
  const basicEntityTableNames = [
    'generation',
    'pdescription',
    'pstatus',
    'stat',
  ].filter(tableName => !ignoreTables.includes(tableName));;

  return reinsertDataForTableGroup(
    db,
    tableStatements,
    basicEntityTableNames,
    'entityTables',
    undefined
  );
}

/*
  DELETE FROM tables for generation-dependent entities, then INSERT INTO those tables.

  WARNING: Will cause data in the junction tables to be deleted.
*/
const reinsertGenDependentEntityData = async(db, tableStatements, ignoreTables = []) => {
  const entityTableNames = [
    'ability',
    'effect',
    'item',
    'pokemon',
    'pmove',
    'ptype',
    'usage_method',
    'version_group'
  ].filter(tableName => !ignoreTables.includes(tableName));

  return reinsertDataForTableGroup(
    db,
    tableStatements,
    entityTableNames,
    'entityTables',
    undefined
  )
}

/*
  DELETE FROM ability junction tables, then INSERT INTO those tables.
*/
const reinsertAbilityJunctionData = async(db, tableStatements) => {
  /*
    [
      'ability_boosts_ptype',
      'ability_resists_ptype',
      'ability_boosts_usage_method',
      'ability_resists_usage_method',
      'ability_modifies_stat',
      'ability_effect',
      'ability_causes_pstatus',
      'ability_resists_pstatus',
    ]
  */
  const abilityJunctionTableNames = Object.keys(tableStatements.abilityJunctionTables);

  /* 
    Since Promise.all() preserves order, foreignKeyMaps unpacks as:

      [ability_FKM, pType_FKM, usageMethod_FKM, stat_FKM, pstatus_FKM, effect_FKM]

  */ 
  const foreignKeyMaps = await Promise.all(
    // Array of relevant entity tableNames.
    ['ability', 'ptype', 'usage_method', 'stat', 'pstatus', 'effect']
    .map(async (tableName) => {
        console.log(`Getting foreign key map for ${tableName}...`)
        return await getForeignKeyMap(db, tableStatements, tableName);
      })
  );
  
  const abilityData = require('./processing/processed_data/abilities.json');

  return await reinsertDataForTableGroup(
    db,
    tableStatements,
    abilityJunctionTableNames,
    'abilityJunctionTables',
    abilityData,
    foreignKeyMaps
  );
}

/*
  DELETE FROM item junction tables, then INSERT INTO those tables.
*/
const reinsertItemJunctionData = async(db, tableStatements) => {
  /*
    [
      'natural_gift',
      'item_boosts_ptype',
      'item_resists_ptype',
      'item_boosts_usage_method',
      'item_resists_usage_method',
      'item_modifies_stat',
      'item_effect',
      'item_causes_pstatus',
      'item_resists_pstatus',
      'item_requires_pokemon',
    ]
  */
  const itemJunctionTableNames = Object.keys(tableStatements.itemJunctionTables)
    // Currently no items boost usage methods; remove if a new game adds it.
    .filter(tableName => tableName != 'item_boosts_usage_method');

  /* 
    Since Promise.all() preserves order, foreignKeyMaps unpacks as:

      [item_FKM, pType_FKM, usageMethod_FKM, stat_FKM, pstatus_FKM, effect_FKM, pokemon_FKM]

  */ 
  const foreignKeyMaps = await Promise.all(
    // Array of relevant entity tableNames.
    ['item', 'ptype', 'usage_method', 'stat', 'pstatus', 'effect', 'pokemon']
    .map(async (tableName) => {
        console.log(`Getting foreign key map for ${tableName}...`)
        return await getForeignKeyMap(db, tableStatements, tableName);
      })
  );
  
  const itemData = require('./processing/processed_data/items.json');

  return await reinsertDataForTableGroup(
    db,
    tableStatements,
    itemJunctionTableNames,
    'itemJunctionTables',
    itemData,
    foreignKeyMaps
  );
}

/*
  DELETE FROM move junction tables, then INSERT INTO those tables.
*/
const reinsertMoveJunctionData = async(db, tableStatements) => {
  /*
    [
      'pmove_has_ptype',
      'pmove_requires_ptype',
      'pmove_requires_pmove',
      'pmove_requires_pokemon',
      'pmove_requires_item',
      'pmove_usage_method',
      'pmove_modifies_stat',
      'pmove_effect',
      'pmove_causes_pstatus',
      'pmove_resists_pstatus',
    ]
  */
  const moveJunctionTableNames = Object.keys(tableStatements.moveJunctionTables);

  /* 
    Since Promise.all() preserves order, foreignKeyMaps unpacks as:

      [move_FKM, pokemon_FKM, pType_FKM, item_FKM, usageMethod_FKM, stat_FKM, pstatus_FKM, effect_FKM]

  */ 
  const foreignKeyMaps = await Promise.all(
    // Array of relevant entity tableNames.
    ['pmove', 'pokemon', 'ptype', 'item', 'usage_method', 'stat', 'pstatus', 'effect']
    .map(async (tableName) => {
        console.log(`Getting foreign key map for ${tableName}...`)
        return await getForeignKeyMap(db, tableStatements, tableName);
      })
  );
  
  const itemData = require('./processing/processed_data/moves.json');

  return await reinsertDataForTableGroup(
    db,
    tableStatements,
    moveJunctionTableNames,
    'moveJunctionTables',
    itemData,
    foreignKeyMaps
  );
}

/*
  DELETE FROM type junction tables, then INSERT INTO those tables.
*/
const reinsertTypeJunctionData = async(db, tableStatements) => {
  /*
    [
      'ptype_matchup',
    ]
  */
  const typeJunctionTableNames = Object.keys(tableStatements.typeJunctionTables);

  /* 
    Since Promise.all() preserves order, foreignKeyMaps unpacks as:

      [pType_FKM]

  */ 
  const foreignKeyMaps = await Promise.all(
    // Array of relevant entity tableNames.
    ['ptype']
    .map(async (tableName) => {
        console.log(`Getting foreign key map for ${tableName}...`)
        return await getForeignKeyMap(db, tableStatements, tableName);
      })
  );
  
  const pTypeData = require('./processing/processed_data/pTypes.json');

  return await reinsertDataForTableGroup(
    db,
    tableStatements,
    typeJunctionTableNames,
    'typeJunctionTables',
    pTypeData,
    foreignKeyMaps);
}

/*
  DELETE FROM pokemon junction tables (except learnset table, 'pokemon_pmove'), then INSERT INTO those tables.
*/
const reinsertPokemonJunctionData = async(db, tableStatements) => {
  /*
    [
      'pokemon_evolution',
      'pokemon_form',
      'pokemon_ptype',
      'pokemon_ability',
    ]
  */
  const pokemonJunctionTableNames = Object.keys(tableStatements.pokemonJunctionTables)
    // Due to the size of the learnset data, we handle that separately.
    .filter(tableName => tableName != 'pokemon_pmove');

  /* 
    Since Promise.all() preserves order, foreignKeyMaps unpacks as:

      [pokemon_FKM, pType_FKM, ability_FKM]

  */ 
  const foreignKeyMaps = await Promise.all(
    // Array of relevant entity tableNames.
    ['pokemon', 'ptype', 'ability']
    .map(async (tableName) => {
        console.log(`Getting foreign key map for ${tableName}...`)
        return await getForeignKeyMap(db, tableStatements, tableName);
      })
  );
  
  const pokemonData = require('./processing/processed_data/pokemon.json');

  return await reinsertDataForTableGroup(
    db,
    tableStatements,
    pokemonJunctionTableNames,
    'pokemonJunctionTables',
    pokemonData,
    foreignKeyMaps
  );
}

/*
  DELETE FROM version group junction tables, then INSERT INTO those tables.
*/
const reinsertVersionGroupJunctionData = async(db, tableStatements) => {
  /*
    [
      'version_group_pdescription',
      'version_group_sprite',
      'pdescription_ability',
      'pdescription_pmove',
      'pdescription_item',
      'sprite_pokemon',
      'sprite_item'
    ]
  */
 const versionGroupJunctionTableNames = Object.keys(tableStatements.versionGroupJunctionTables)
    // TODO handle sprite tables
    .filter(tableName => tableName.split('_')[0] == 'pdescription');
    

  /* 
    Since Promise.all() preserves order, foreignKeyMaps unpacks as:

      [description_FKM, ability_FKM, move_FKM, item_FKM, versionGroup_FKM]

  */ 
  const foreignKeyMaps = await Promise.all(
    // Array of relevant entity tableNames.
    ['pdescription', 'ability', 'pmove', 'item', 'version_group']
    .map(async (tableName) => {
        console.log(`Getting foreign key map for ${tableName}...`)
        return await getForeignKeyMap(db, tableStatements, tableName);
      })
  );

  const descriptionData = require('./processing/processed_data/descriptions.json');

  return await reinsertDataForTableGroup(
    db,
    tableStatements,
    versionGroupJunctionTableNames,
    'versionGroupJunctionTables',
    descriptionData,
    foreignKeyMaps
  );
}

/*
  DELETE FROM learnset table, then INSERT INTO that table.

  WARNING: Takes a long time.
*/
const reinsertLearnsetData = async(db, tableStatements) => {
  /*
    [
      'pokemon_pmove'
    ]
  */
  const pokemonJunctionTableNames = Object.keys(tableStatements.pokemonJunctionTables)
    // Due to the size of the learnset data, we handle that separately.
    .filter(tableName => tableName == 'pokemon_pmove');

  /* 
    Since Promise.all() preserves order, foreignKeyMaps unpacks as:

      [pokemon_FKM, move_FKM]

  */ 
  const foreignKeyMaps = await Promise.all(
    // Array of relevant entity tableNames.
    ['pokemon', 'pmove']
    .map(async (tableName) => {
        console.log(`Getting foreign key map for ${tableName}...`)
        return await getForeignKeyMap(db, tableStatements, tableName);
      })
  );
  
  const pokemonData = require('./processing/processed_data/pokemon.json');

  return await reinsertDataForTableGroup(
    db,
    tableStatements,
    pokemonJunctionTableNames,
    'pokemonJunctionTables',
    pokemonData,
    foreignKeyMaps
  );
}

/*
  Invoked by all the above statements to reset data for the appropriate tables.

    Refer to the creating/dropping sections for what db, tableSDtatements, and tableGroup are.

    tableNameArr is a subset of tableGroup consisting of the tables to be reset.

    entityData is an array of objects for data used to compute the values to be inserted. This is used mainly for junction tables. E.g. for ability junction tables, this is abilities.json.

    foreignKeyMaps is an array of Maps, each of which takes identifying information from an entry in entityData and maps it to the primary key for that entity in the database. We unpack it when computing the actual values to be inserted. Refer to the foreign key map section for more.
*/
const reinsertDataForTableGroup = async(
  db,
  tableStatements,
  tableNameArr,
  tableGroup,
  entityData,
  foreignKeyMaps,
) => {
  /*
    For each tableName in tableNameArr:

      1. DELETE FROM tableName.
      2. Reset AUTO_INCREMENT counter for tableName.
      3. INSERT INTO tableName.

  */

  return await Promise.all(
    tableNameArr.map(async (tableName) => {
      // DELETE FROM tableName.
      await deleteTableRows(db, tableStatements, tableGroup, tableName);

      // Reset AUTO_INCREMENT counter for tableName.
      await resetAutoIncrement(db, tableStatements, tableGroup, tableName);

      // Get the values to be inserted using entityData and foreignKeyMaps.
      const values = getValuesForTable(
        tableName,
        tableGroup,
        entityData,
        foreignKeyMaps
      );
        
      // INSERT INTO tableName.
      return insertIntoTable(db, tableStatements, tableGroup, tableName, values);
    })
  )
  .then( () => console.log(`\nReset the following tables:\n\n[\n  ${tableNameArr.join(',\n  ')}\n].\n`))
  .catch(console.log);
}

// DELETE FROM tableName.
const deleteTableRows = async(db, tableStatements, tableGroup, tableName) => {
  return db.promise().query(tableStatements[tableGroup][tableName].delete)
    .then( () => console.log(`${tableName} table deleted.`))
    .catch(console.log);
}

// Reset AUTO_INCREMENT counter for tableName.
const resetAutoIncrement = async(db, tableStatements, tableGroup, tableName) => {
  return db.promise().query(tableStatements[tableGroup][tableName].reset_auto_inc)
    .then( () => console.log(`Reset AUTO_INCREMENT counter for ${tableName} table.`))
    .catch(console.log)
}

// INSERT INTO tableName the array, values.
const insertIntoTable = async(
  db,
  tableStatements,
  tableGroup,
  tableName, 
  values
) => {
  return await db.promise().query(tableStatements[tableGroup][tableName].insert, [values])
    .then( ([results, fields]) => {
      console.log(`Inserted data for ${tableName}: ${results.affectedRows} rows.`);
    })
    .catch(console.log);
}

// #endregion

// COMPUTING VALUES TO BE INSERTED FOR A GIVEN TABLE
// #region

// Use entityData and foreignKeyMaps to determine the array, values, which will be inserted into tableName.
const getValuesForTable = (
  tableName, 
  tableGroup, 
  entityData, 
  foreignKeyMaps
) => {

  // UNPACK foreignKeyMaps AND ASSIGN entityData BASED ON tableGroup
  // #region

  // Declarations for foreign key maps.
  let ability_FKM, item_FKM, move_FKM, pokemon_FKM, pType_FKM, usageMethod_FKM, stat_FKM, pstatus_FKM, effect_FKM, description_FKM, sprite_FKM, versionGroup_FKM;
  // Declarations for entity data.
  let abilityData, metaEntityData, itemData, moveData, pokemonData, pTypeData;
  switch(tableGroup) {
    case 'abilityJunctionTables':
      [ability_FKM, pType_FKM, usageMethod_FKM, stat_FKM, pstatus_FKM, effect_FKM] = foreignKeyMaps;
      abilityData = entityData;
      break;

    case 'itemJunctionTables':
      [item_FKM, pType_FKM, usageMethod_FKM, stat_FKM, pstatus_FKM, effect_FKM, pokemon_FKM] = foreignKeyMaps;
      itemData = entityData;
      break;

    case 'moveJunctionTables':
      [move_FKM, pokemon_FKM, pType_FKM, item_FKM, usageMethod_FKM, stat_FKM, pstatus_FKM, effect_FKM] = foreignKeyMaps;
      moveData = entityData;
      break;
    
    case 'typeJunctionTables':
      [pType_FKM] = foreignKeyMaps;
      pTypeData = entityData;
      break;

    case 'pokemonJunctionTables':
      // We handle pokemon_pmove separately since it is so large.
      if (tableName == 'pokemon_pmove') {
        [pokemon_FKM, move_FKM] = foreignKeyMaps;
      } else {
        [pokemon_FKM, pType_FKM, ability_FKM] = foreignKeyMaps;
      }
      pokemonData = entityData;
      break;
    case 'versionGroupJunctionTables':
      if (tableName.split('_')[0] == 'pdescription') {
        [description_FKM, ability_FKM, move_FKM, item_FKM, versionGroup_FKM] = foreignKeyMaps;
        metaEntityData = entityData;
      } else {
        throw `Sprites not handled yet! ${tableName}`;
      }
      break;
    default: 
      console.log('No foreign key maps necessary for this table group.')
  }

  // #endregion

  // This is where we will store the array representing the data to be inserted.
  let values;

  // COMPUTE values BASED ON tableName
  // #region

  // Calculating values is very similar for, e.g. '<entity class>_boosts_ptype' and '<entity_class>_resists_ptype'. We declare these variables for use in multiple places in the following switch-statement.
  let boostOrResist, boostOrResistKey, causeOrResist, causeOrResistKey;

  // Assign values based on tableName
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
          pdescription_class,
          entity_name
        )
      */
      const descriptions = require('./processing/processed_data/descriptions.json');
      values = descriptions.reduce((acc, descriptionObj) => {
        // extract entityName and description type
        const { entity_name: entityName, description_class: descriptionClass } = descriptionObj;
        
        // descriptionObj contains all the descriptions for entity name, so we need to split them up. The unique descriptions are indexed by numeric keys.
        return acc.concat(Object.keys(descriptionObj)
          // numeric keys contain description info
          .filter(key => !isNaN(key))
          .map(descriptionIndex => {
            // descriptionObj[descriptionIndex] is a two-element array, whose first element is the description itself, and whose second element is another array containing version group codes; we don't need the latter at this moment
            const description = descriptionObj[descriptionIndex][0];
            
            return [description, descriptionIndex, descriptionClass, entityName];
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

    /*
      ABILITY JUNCTION TABLES
    */
    case 'ability_boosts_ptype':
    case 'ability_resists_ptype':
      /*
        Need (
          ability_generation_id,
          ability_id,
          ptype_generation_id,
          ptype_id,
          multiplier
        )
      */
      boostOrResist = tableName.split('_')[1];
      boostOrResistKey = boostOrResist + '_type';
      values = abilityData.reduce((acc, curr) => {
        // Get ability data from curr.
        const { gen: gen, name: abilityName, [boostOrResistKey]: typeData } = curr;
        const { ability_id: abilityID } = ability_FKM.get(makeMapKey([abilityName, gen]));
        
        return acc.concat(
          Object.keys(typeData).map(pTypeName => {
            // We always compare entities of the same generation.
            const { ptype_id: pTypeID } = pType_FKM.get(makeMapKey([gen, pTypeName]));
            const multiplier = typeData[pTypeName];

            return multiplier != 1 
              ? [gen, abilityID, gen, pTypeID, multiplier]
              : [];
          })
        )
      }, [])
      // Filter out empty entries
      .filter(data => data.length > 0);
      break;

    case 'ability_boosts_usage_method':
    case 'ability_resists_usage_method':
      /* 
        Need (
          ability_generation_id,
          ability_id,
          usage_method_id,
          multiplier
        ) 
      */
      boostOrResist = tableName.split('_')[1];
      boostOrResistKey = boostOrResist + '_usage_method';

      values = abilityData.reduce((acc, curr) => {
        // Get ability data from curr.
        const { gen: gen, name: abilityName, [boostOrResistKey]: usageMethodData } = curr;
        const { ability_id: abilityID } = ability_FKM.get(makeMapKey([abilityName, gen]));
        
        return acc.concat(
          Object.keys(usageMethodData).map(usageMethodName => {
            // We always compare entities of the same generation.
            const { usage_method_id: usageMethodID } = usageMethod_FKM.get(makeMapKey([usageMethodName]));
            const multiplier = usageMethodData[usageMethodName];

            return multiplier != 1 
            ? [gen, abilityID, usageMethodID, multiplier]
            : [];
          })
        )
      }, [])
      // Filter out empty entries
      .filter(data => data.length > 0);
      break;

    case 'ability_modifies_stat':
      /* 
        Need (
          ability_generation_id,
          ability_id,
          state_id,
          stage,
          multiplier,
          chance,
          recipient
        )
      */
      values = abilityData.reduce((acc, curr) => {
        // Get ability data from curr.
        const { gen: gen, name: abilityName, stat_modifications: statModData } = curr;
        const { ability_id: abilityID } = ability_FKM.get(makeMapKey([abilityName, gen]));

        return acc.concat(
          Object.keys(statModData).map(statName => {
            // We always compare entities of the same generation.
            const { stat_id: statID } = stat_FKM.get(makeMapKey([statName]));
            let [modifier, recipient] = statModData[statName]

            // True if stage modification, False if multiplier.
            const stageOrMultiplier = typeof modifier == 'string';

            // stage
            if (stageOrMultiplier) {
              modifier = parseInt(modifier.slice(1), 0);
              return modifier != 0 
              ? [gen, abilityID, statID, modifier, 1.0, 100.00, recipient]
              : [];
            }
            // multiplier
            else {
              return modifier != 1.0
              ? [gen, abilityID, statID, 0, modifier, 100.00, recipient]
              : [];
            }
          })
        )
      }, [])
      // Filter out empty entries
      .filter(data => data.length > 0);
      break;
    
    case 'ability_effect':
      /*
        Need (
          ability_generation_id,
          ability_id,
          effect_id
        )
      */
      values = abilityData.reduce((acc, curr) => {
        // Get ability data from curr.
        const { gen: gen, name: abilityName, effects: effectData } = curr;
        const { ability_id: abilityID } = ability_FKM.get(makeMapKey([abilityName, gen]));
        return acc.concat(
          Object.keys(effectData).map(effectName => {
            // We always compare entities of the same generation.
            const { effect_id: effectID } = effect_FKM.get(makeMapKey([effectName]));

            // True if effect is present, False otherwise.
            return effectData[effectName]
            ? [gen, abilityID, effectID]
            : [];
          })
        )
      }, [])
      // Filter out empty entries
      .filter(data => data.length > 0);
      break;

    case 'ability_causes_pstatus':
    case 'ability_resists_pstatus':
      /*
        Need (
          ability_generation_id,
          ability_id,
          pstatus_id,
          chance
        ) or (
          ability_generation_id,
          ability_id,
          pstatus_id
        )
      */
      causeOrResist = tableName.split('_')[1];
      causeOrResistKey = causeOrResist + '_status';

      values = abilityData.reduce((acc, curr) => {
        // Get ability data from curr.
        const { gen: gen, name: abilityName, [causeOrResistKey]: statusData } = curr;
        const { ability_id: abilityID } = ability_FKM.get(makeMapKey([abilityName, gen]));
        
        return acc.concat(
          Object.keys(statusData).map(statusName => {
            // We always compare entities of the same generation.
            const { pstatus_id: statusID } = pstatus_FKM.get(makeMapKey([statusName]));
            if (causeOrResist === 'causes') {
              // In case of causes, statusData[statusName] is probability of causing status.
              const chance = statusData[statusName];

              return chance != 0.0 
              ? [gen, abilityID, statusID, chance]
              : [];
            } else {
              // In case of resists, statusData[statusName] is either True or False.
              return statusData[statusName] 
              ? [gen, abilityID, statusID]
              : [];
            }
          })
        )
      }, [])
      // Filter out empty entries
      .filter(data => data.length > 0);
      break;

    /*
      ITEM JUNCTION TABLES
    */
    case 'natural_gift':
      /*
        Need (
          item_generation_id,
          item_id
          ptype_generation_id,
          ptype_id,
          item_power
        )
      */
      
      values = itemData.reduce((acc, curr) => {
        // Get item data from curr.
        const { gen: gen, name: itemName, natural_gift: naturalGiftData } = curr;

        if (!naturalGiftData) return acc;

        const { item_id: itemID } = item_FKM.get(makeMapKey([gen, itemName]));
        
        // Only berries have data for Natural Gift.
        const [pTypeName, power] = naturalGiftData;
        const { ptype_id: pTypeID } = pType_FKM.get(makeMapKey([gen, pTypeName]));

        return acc.concat([
          [gen, itemID, gen, pTypeID, power]
        ]);
      }, [])
      // Filter out empty entries
      .filter(data => data.length > 0);
      break;

    case 'item_boosts_ptype':
    case 'item_resists_ptype':
      /*
        Need (
          item_generation_id,
          item_id,
          ptype_generation_id,
          ptype_id,
          multiplier
        )
      */
      boostOrResist = tableName.split('_')[1];
      boostOrResistKey = boostOrResist + '_type';

      values = itemData.reduce((acc, curr) => {
        // Get item data from curr.
        const { gen: gen, name: itemName, [boostOrResistKey]: typeData } = curr;
        const { item_id: itemID } = item_FKM.get(makeMapKey([gen, itemName]));
        
        return acc.concat(
          Object.keys(typeData).map(pTypeName => {
            // We always compare entities of the same generation.
            const { ptype_id: pTypeID } = pType_FKM.get(makeMapKey([gen, pTypeName]));
            const multiplier = typeData[pTypeName];

            return multiplier != 1 
              ? [gen, itemID, gen, pTypeID, multiplier]
              : [];
          })
        )
      }, [])
      // Filter out empty entries
      .filter(data => data.length > 0);
      break;

      
    // No items boost usage methods yet, but the code is there. Uncomment if any items are introduced which boost usage methods.
    // case 'item_boosts_usage_method':
    case 'item_resists_usage_method':
      /* 
        Need (
          item_generation_id,
          item_id,
          usage_method_id,
          multiplier
        ) 
      */
      boostOrResist = tableName.split('_')[1];
      boostOrResistKey = boostOrResist + '_usage_method';

      values = itemData.reduce((acc, curr) => {
        // Get item data from curr.
        const { gen: gen, name: itemName, [boostOrResistKey]: usageMethodData } = curr;
        const { item_id: itemID } = item_FKM.get(makeMapKey([gen, itemName]));
        
        return acc.concat(
          Object.keys(usageMethodData).map(usageMethodName => {
            // We always compare entities of the same generation.
            const { usage_method_id: usageMethodID } = usageMethod_FKM.get(makeMapKey([usageMethodName]));
            const multiplier = usageMethodData[usageMethodName];

            return multiplier != 1 
            ? [gen, itemID, usageMethodID, multiplier]
            : [];
          })
        )
      }, [])
      // Filter out empty entries
      .filter(data => data.length > 0);
      break;

    case 'item_modifies_stat':
      /* 
        Need (
          item_generation_id,
          item_id,
          state_id,
          stage,
          multiplier,
          chance,
          recipient
        )
      */
      values = itemData.reduce((acc, curr) => {
        // Get item data from curr.
        const { gen: gen, name: itemName, stat_modifications: statModData } = curr;
        const { item_id: itemID } = item_FKM.get(makeMapKey([gen, itemName]));

        return acc.concat(
          Object.keys(statModData).map(statName => {
            // We always compare entities of the same generation.
            const { stat_id: statID } = stat_FKM.get(makeMapKey([statName]));
            let [modifier, recipient] = statModData[statName]

            // True if stage modification, False if multiplier.
            const stageOrMultiplier = typeof modifier == 'string';

            // stage
            if (stageOrMultiplier) {
              modifier = parseInt(modifier.slice(1), 10);
              return modifier != 0 
              ? [gen, itemID, statID, modifier, 1.0, 100.00, recipient]
              : [];
            }
            // multiplier
            else {
              return modifier != 1.0
              ? [gen, itemID, statID, 0, modifier, 100.00, recipient]
              : [];
            }
          })
        )
      }, [])
      // Filter out empty entries
      .filter(data => data.length > 0);
      break;
    
    case 'item_effect':
      /*
        Need (
          item_generation_id,
          item_id,
          effect_id
        )
      */
      values = itemData.reduce((acc, curr) => {
        // Get item data from curr.
        const { gen: gen, name: itemName, effects: effectData } = curr;
        const { item_id: itemID } = item_FKM.get(makeMapKey([gen, itemName]));
        return acc.concat(
          Object.keys(effectData).map(effectName => {
            // We always compare entities of the same generation.
            const { effect_id: effectID } = effect_FKM.get(makeMapKey([effectName]));

            // True if effect is present, False otherwise.
            return effectData[effectName]
            ? [gen, itemID, effectID]
            : [];
          })
        )
      }, [])
      // Filter out empty entries
      .filter(data => data.length > 0);
      break;

    case 'item_causes_pstatus':
    case 'item_resists_pstatus':
      /*
        Need (
          item_generation_id,
          item_id,
          pstatus_id
        ) or (
          item_generation_id,
          item_id,
          pstatus_id
        )
      */
      causeOrResist = tableName.split('_')[1];
      causeOrResistKey = causeOrResist + '_status';

      values = itemData.reduce((acc, curr) => {
        // Get item data from curr.
        const { gen: gen, name: itemName, [causeOrResistKey]: statusData } = curr;
        const { item_id: itemID } = item_FKM.get(makeMapKey([gen, itemName]));
        
        return acc.concat(
          Object.keys(statusData).map(statusName => {
            // We always compare entities of the same generation.
            const { pstatus_id: statusID } = pstatus_FKM.get(makeMapKey([statusName]));

            return statusData[statusName] 
            ? [gen, itemID, statusID]
            : [];
          })
        )
      }, [])
      // Filter out empty entries
      .filter(data => data.length > 0);
      break;
    
    case 'item_requires_pokemon':
      /*
        Need (
          item_generation_id,
          item_id,
          pokemon_generation_id,
          pokemon_id
        )
      */
      
      values = itemData.reduce((acc, curr) => {
        // Get item data from curr.
        const { gen: gen, name: itemName, pokemon_specific: pokemonData } = curr;
        const { item_id: itemID } = item_FKM.get(makeMapKey([gen, itemName]));

        
        // If item is not Pokemon-specific
        if (!pokemonData) { return acc; }
        
        return acc.concat(
          Object.keys(pokemonData).map(pokemonName => {
            // We always compare entities of the same generation.
            const { pokemon_id: pokemonID } = pokemon_FKM.get(makeMapKey([gen, pokemonName]));

            return pokemonData[pokemonName] 
            ? [gen, itemID, gen, pokemonID]
            : [];
          })
        )
      }, [])
      // Filter out empty entries
      .filter(data => data.length > 0);
      break;
    
    /*
      MOVE JUNCTION TABLES
    */
    case 'pmove_has_ptype':
      /*
        Need (
          pmove_generation_id,
          pmove_id
          ptype_generation_id,
          ptype_id
        )
      */
      
      values = moveData.reduce((acc, curr) => {
        const { gen: gen, name: moveName, type: pTypeName } = curr;

        const { pmove_id: moveID } = move_FKM.get(makeMapKey([gen, moveName]));
        
        const { ptype_id: pTypeID } = pType_FKM.get(makeMapKey([gen, pTypeName]));

        return acc.concat([
          [gen, moveID, gen, pTypeID]
        ]);
      }, [])
      // Filter out empty entries
      .filter(data => data.length > 0);
      break;

    case 'pmove_requires_ptype':
    case 'pmove_requires_pmove':
    case 'pmove_requires_pokemon':
    case 'pmove_requires_item':
      /*
        Need (
          pmove_generation_id,
          pmove_id,
          <entity>_generation_id,
          <entity>_id,
          multiplier
        ), where <entity> is ptype, pmove, pokemon, or item.
      */

      // Whether the requirement is a type, move, Pokemon, or item. Choose the foreign key map accordingly.
      // dictKey refers to how the data is stored in moves.json; we need the key to extract the requirement data from moveData.
      const entityClass = tableName.split('_')[2];
      const entity_id = entityClass + '_id';
      let entity_FKM, dictKey;
      switch (entityClass) {
        case 'ptype':
          entity_FKM = pType_FKM;
          dictKey = 'type';
          break;
        case 'pmove':
          entity_FKM = move_FKM;
          dictKey = 'move';
          break;
        case 'pokemon':
          entity_FKM = pokemon_FKM;
          dictKey = 'pokemon';
          break;
        case 'item':
          entity_FKM = item_FKM;
          dictKey = 'item'
          break;
        default:
          throw 'Invalid entity class, ' + entityClass;
      }

      values = moveData.reduce((acc, curr) => {
        // Get item data from curr.
        const { gen: gen, name: moveName, requirements: requirementData } = curr;
        const { pmove_id: moveID } = move_FKM.get(makeMapKey([gen, moveName]));

        // Check whether requirementData exists AND has the relevant entity, dictKey. If not, return.
        if (!requirementData || !requirementData[dictKey]) return acc;
        
        return acc.concat(
          requirementData[dictKey].map(entityName => {
            // All the possible entity classes come alphabetically before 'generation_id', so the order [gen, entityName] is correct.
            if (entity_FKM.get(makeMapKey([gen, entityName])) == undefined) {
              console.log(requirementData, entityName);
            }
            const { [entity_id]: entityID } = entity_FKM.get(makeMapKey([gen, entityName]));

            return [gen, moveID, gen, entityID]
          })
        )
      }, [])
      // Filter out empty entries
      .filter(data => data.length > 0);
      break;

    case 'pmove_usage_method':
      /* 
        Need (
          pmove_generation_id,
          pmove_id,
          usage_method_id
        ) 
      */
      values = moveData.reduce((acc, curr) => {
        // Get entity data from curr.
        const { gen: gen, name: moveName, usage_method: usageMethodData } = curr;
        const { pmove_id: moveID } = move_FKM.get(makeMapKey([gen, moveName]));

        // Move has no usage method.
        if (!usageMethodData) { return acc; }
        
        return acc.concat(
          Object.keys(usageMethodData).map(usageMethodName => {
            // We always compare entities of the same generation.
            const { usage_method_id: usageMethodID } = usageMethod_FKM.get(makeMapKey([usageMethodName]));
            
            // A move may lose a usage method. 
            const present = usageMethodData[usageMethodName];

            return present
            ? [gen, moveID, usageMethodID]
            : [];
          })
        )
      }, [])
      // Filter out empty entries
      .filter(data => data.length > 0);
      break;

    case 'pmove_modifies_stat':
      /* 
        Need (
          pmove_generation_id,
          pmove_id,
          state_id,
          stage,
          multiplier,
          chance,
          recipient
        )
      */
      values = moveData.reduce((acc, curr) => {
        // Get move data from curr.
        const { gen: gen, name: moveName, stat_modifications: statModData } = curr;
        const { pmove_id: moveID } = move_FKM.get(makeMapKey([gen, moveName]));

        return acc.concat(
          Object.keys(statModData).map(statName => {
            // We always compare entities of the same generation.
            const { stat_id: statID } = stat_FKM.get(makeMapKey([statName]));
            let [modifier, recipient, chance] = statModData[statName]

            // True if stage modification, False if multiplier.
            const stageOrMultiplier = typeof modifier == 'string';
            
            // stage
            if (stageOrMultiplier) {
              modifier = parseInt(modifier.slice(1), 10);
              return modifier != 0 
              ? [gen, moveID, statID, modifier, 1.0, chance, recipient]
              : [];
            }
            // multiplier
            else {
              return modifier != 1.0
              ? [gen, moveID, statID, 0, modifier, chance, recipient]
              : [];
            }
          })
        )
      }, [])
      // Filter out empty entries
      .filter(data => data.length > 0);
      break;
    
    case 'pmove_effect':
      /*
        Need (
          pmove_generation_id,
          pmove_id,
          effect_id
        )
      */
      values = moveData.reduce((acc, curr) => {
        // Get move data from curr.
        const { gen: gen, name: moveName, effects: effectData } = curr;
        const { pmove_id: moveID } = move_FKM.get(makeMapKey([gen, moveName]));
        return acc.concat(
          Object.keys(effectData).map(effectName => {
            // We always compare entities of the same generation.
            const { effect_id: effectID } = effect_FKM.get(makeMapKey([effectName]));

            // True if effect is present, False otherwise.
            return effectData[effectName]
            ? [gen, moveID, effectID]
            : [];
          })
        )
      }, [])
      // Filter out empty entries
      .filter(data => data.length > 0);
      break;

    case 'pmove_causes_pstatus':
    case 'pmove_resists_pstatus':
      /*
        Need (
          pmove_generation_id,
          pmove_id,
          pstatus_id,
          chance
        ) or (
          pmove_generation_id,
          pmove_id,
          pstatus_id
        )
      */
      causeOrResist = tableName.split('_')[1];
      causeOrResistKey = causeOrResist + '_status';

      values = moveData.reduce((acc, curr) => {
        // Get move data from curr.
        const { gen: gen, name: moveName, [causeOrResistKey]: statusData } = curr;
        const { pmove_id: moveID } = move_FKM.get(makeMapKey([gen, moveName]));
        
        return acc.concat(
          Object.keys(statusData).map(statusName => {
            // We always compare entities of the same generation.
            const { pstatus_id: statusID } = pstatus_FKM.get(makeMapKey([statusName]));
            if (causeOrResist === 'causes') {
              // In case of causes, statusData[statusName] is probability of causing status.
              const chance = statusData[statusName];

              return chance != 0.0 
              ? [gen, moveID, statusID, chance]
              : [];
            } else {
              // In case of resists, statusData[statusName] is either True or False.
              return statusData[statusName] 
              ? [gen, moveID, statusID]
              : [];
            }
          })
        )
      }, [])
      // Filter out empty entries
      .filter(data => data.length > 0);
      break;
    
    /*
      TYPE JUNCTION TABLES
    */
    case 'ptype_matchup':
      /*
        Need (
          attacking_ptype_generation_id,
          attacking_ptype_id,
          defending_ptype_generation_id,
          defending_ptype_id,
          multiplier          
        )
      */ 
      values = pTypeData.reduce((acc, curr) => {
        // Get offensive type data from curr.
        const { gen: gen, name: pTypeName_att, damage_to: matchupData } = curr;
        const { ptype_id: pTypeID_att } = pType_FKM.get(makeMapKey([gen, pTypeName_att]));
        
        return acc.concat(
          Object.keys(matchupData).map(pTypeName_def => {
            // if (pType_FKM.get(makeMapKey([gen, pTypeName_def])) == undefined) {
            //   console.log(requirementData, pTypeName_def);
            // }
            const { ptype_id: pTypeID_def } = pType_FKM.get(makeMapKey([gen, pTypeName_def]));

            const multiplier = curr.damage_to[pTypeName_def];

            return multiplier != 1
              ? [gen, pTypeID_att, gen, pTypeID_def, multiplier]
              : [];
          })
        )
      }, [])
      // Filter out empty entries
      .filter(data => data.length > 0);
      break;

    /*
      POKEMON JUNCTION TABLES
    */
    case 'pokemon_evolution':
      /*
        Need (
          prevolution_generation_id,
          prevolution_id,
          evolution_generation_id,
          evolution_id,
          evolution_method
        )
      */

      values = pokemonData.reduce((acc, curr) => {
        const { gen: gen, name: pokemonName, evolves_to: evolvesToData } = curr;

        const { pokemon_id: pokemonID } = pokemon_FKM.get(makeMapKey([gen, pokemonName]));
        
        return acc.concat(
          Object.keys(evolvesToData).map(evolutionName => {
            const { pokemon_id: evolutionID } = pokemon_FKM.get(makeMapKey([gen, evolutionName]));
            
            const evolutionMethod = evolvesToData[evolutionName];

            return [gen, pokemonID, gen, evolutionID, evolutionMethod];
          })
        );
      }, [])
      // Filter out empty entries
      .filter(data => data.length > 0);
      break;
    
    case 'pokemon_form':
      /*
        Need (
          base_form_generation_id,
          base_form_id,
          form_generation_id,
          form_id,
          form_class
        )
      */

      values = pokemonData.reduce((acc, curr) => {
        const { gen: gen, name: pokemonName, form_data: formData } = curr;

        const { pokemon_id: pokemonID } = pokemon_FKM.get(makeMapKey([gen, pokemonName]));
        
        return acc.concat(
          Object.keys(formData).map(formName => {
            const { pokemon_id: formID } = pokemon_FKM.get(makeMapKey([gen, formName]));
            
            const formClass = formData[formName];

            return [gen, pokemonID, gen, formID, formClass];
          })
        );
      }, [])
      // Filter out empty entries
      .filter(data => data.length > 0);
      break;

    case 'pokemon_ptype':
      /*
        Need (
          pokemon_generation_id,
          pokemon_id,
          ptype_generation_id,
          ptype_id
        )
      */
      
      values = pokemonData.reduce((acc, curr) => {
        const { gen: gen, name: pokemonName, type_1: pType1Name, type_2: pType2Name } = curr;

        const { pokemon_id: pokemonID } = pokemon_FKM.get(makeMapKey([gen, pokemonName]));
        
        // Filter out empty type name, e.g. for monotype Pokemon.
        return acc.concat(
          [pType1Name, pType2Name]
          .filter(pTypeName => pTypeName.length > 0)
          .map(pTypeName => {
            const { ptype_id: pTypeID } = pType_FKM.get(makeMapKey([gen, pTypeName]));
            
            return [gen, pokemonID, gen, pTypeID];
          })
        );
      }, [])
      // Filter out empty entries
      .filter(data => data.length > 0);
      break;

    case 'pokemon_pmove': 
      /*
        Need (
          pokemon_generation_id,
          pokemon_id,
          pmove_generation_id,
          pmove_id,
          learn_method
        )
      */
      
      values = pokemonData.reduce((acc, curr) => {
        const { gen: gen, name: pokemonName, learnset: learnsetData } = curr;

        const { pokemon_id: pokemonID } = pokemon_FKM.get(makeMapKey([gen, pokemonName]));
        
        return acc.concat(
          Object.keys(learnsetData).reduce((innerAcc, moveName)=> {
            const { pmove_id: moveID } = move_FKM.get(makeMapKey([gen, moveName]));
            
            return innerAcc.concat([
              // We can have multiple different learn methods within the same generation.
              learnsetData[moveName].map(learnMethod => {
                return [gen, pokemonID, gen, moveID, learnMethod];
              })
            ]);
          }, [])
        );
      }, [])
      // Filter out empty entries
      .filter(data => data.length > 0);
      break;

    case 'pokemon_ability':
      /*
        Need (
          pokemon_generation_id,
          pokemon_id,
          ability_generation_id,
          ability_id,
          ability_slot
        )
      */
      
      values = pokemonData.reduce((acc, curr) => {
        const { gen: gen, name: pokemonName, ability_1: ability1Name, ability_2: ability2Name, ability_hidden: abilityHiddenName } = curr;

        // No abilities in Gen 3
        if (gen < 3) { return acc; }

        const { pokemon_id: pokemonID } = pokemon_FKM.get(makeMapKey([gen, pokemonName]));
        
        // Filter out empty ability slots, e.g. for Mimikyu, who only has one ability.
        return acc.concat(
          [ability1Name, ability2Name, abilityHiddenName]
          .filter(abilityName => abilityName && abilityName.length > 0)
          .map(abilityName => {
            const { ability_id: abilityID } = ability_FKM.get(makeMapKey([abilityName, gen]));

            let abilitySlot;
            switch (abilityName) {
              case ability1Name:
                abilitySlot = '1';
                break;
              case ability2Name:
                abilitySlot = '2';
                break;
              case abilityHiddenName:
                abilitySlot = 'hidden';
                break;
            }
            
            return [gen, pokemonID, gen, abilityID, abilitySlot];
          })
        );
      }, [])
      // Filter out empty entries
      .filter(data => data.length > 0);
      break;
    
    /*
      VERSION GROUP JUNCTION TABLES
    */ 
    case 'pdescription_ability':
    case 'pdescription_item':
    case 'pdescription_pmove':
    // case 'sprite_item':
    // case 'sprite_pokemon':
      /*
        Need (
          <base entity>_generation_id
          <base entity>_id
          version_group_id
          <meta entity>_id
        ), where <entity> is an ability, item, pmove, or pokemon, and <meta entity> is a pdescription or sprite.
      */
      
      // 
      // #region

      const metaEntityClass = tableName.split('_')[0];
      const metaEntity_id = metaEntityClass + '_id';
      
      // Whether the pdescription/sprite is of an ability, item, pokemon, or pmove. Choose the foreign key map accordingly.
      // baseEntityDataClass refers to how the data is stored in descriptions.json or sprites.json.
      const baseEntityClass = tableName.split('_')[1];
      const baseEntity_id = baseEntityClass + '_id';

      let baseEntity_FKM, baseEntityDataClass;
      switch (baseEntityClass) {
        case 'ability':
          baseEntity_FKM = ability_FKM;
          baseEntityDataClass = 'ability';
          break;
        case 'item':
          baseEntity_FKM = item_FKM;
          baseEntityDataClass = 'item'
          break;
        case 'pmove':
          baseEntity_FKM = move_FKM;
          baseEntityDataClass = 'move';
          break;
        case 'pokemon':
          baseEntity_FKM = pokemon_FKM;
          baseEntityDataClass = 'pokemon';
          break;
        default:
          throw 'Invalid base entity class, ' + baseEntityClass;
      }

      let metaEntity_FKM, metaEntityKey;
      switch (metaEntityClass) {
        case 'pdescription':
          metaEntity_FKM = description_FKM;
          metaEntityKey = 'description_class'
          break;
        case 'sprite':
          metaEntity_FKM = sprite_FKM;
          metaEntityKey = 'sprite_class';
          break;
        default:
          throw 'Invalid meta entity class, ' + metaEntityClass;
      }

      // #endregion

      values = metaEntityData.filter(data => data[metaEntityKey] == baseEntityDataClass).reduce((acc, curr) => {
        // Get item data from curr.
        const { entity_name: baseEntityName } = curr;
        
        return acc.concat(
          Object.keys(curr)
            .filter(key => !isNaN(key))
            .reduce((innerAcc, metaEntityIndex) => {
              const [metaEntityContent, versionGroups] = curr[metaEntityIndex];

              // 'pdescription_index, pdescription_class, entity_name' sorted alphabetically is 'entity_name, pdescription_index, pdescription_class'
              const { [metaEntity_id]: metaEntityID } = metaEntity_FKM.get(makeMapKey([baseEntityName, baseEntityDataClass, metaEntityIndex]));

              return innerAcc.concat(
                versionGroups.map(versionGroupCode => {

                  const { version_group_id: versionGroupID } = versionGroup_FKM.get(versionGroupCode);

                  const versionGroupGen = getGenOfVersionGroup(versionGroupCode);

                  const { [baseEntity_id]: baseEntityID } = 
                  baseEntityClass == 'ability' 
                    // 'ability_id' comes before 'generation_id' alphabetically.
                    ? baseEntity_FKM.get(makeMapKey([baseEntityName, versionGroupGen]))
                    // Otherwise, 'generation_id' comes first alphabetically.
                    : baseEntity_FKM.get(makeMapKey([versionGroupGen, baseEntityName]));
      
                  // <base entity>_generation_id
                  // <base entity>_id
                  // version_group_id
                  // <meta entity>_id
                  return [versionGroupGen, baseEntityID, versionGroupID, metaEntityID];
                })
              );
            }, [])
        );
      }, [])
      // Filter out empty entries
      .filter(data => data.length > 0);
      break;

    default:
      console.log(`${tableName} unhandled.`);
  }

  // #endregion

  return values;
}

// #endregion

// FOREIGN KEY MAPS AND KEYS
// #region

// Helper function for taking an array of strings and making a key for a foreign key map. We need this since the keys of a Map cannot be an array or an object.
const makeMapKey = arr => arr.join(' ');

/*
  Given a table name, tableName, build a Map, foreignKeyMap, which maps identifying column values to primary key column values. E.g.

    If tableName = 'pokemon', foreignKeyMap maps { generation_id, pokemon_name } to { pokemon_id, generation_id }.

  This will facilitate inserting data into junction tables, indeed into any table with a foreign key.
*/
const getForeignKeyMap = async (db, tableStatements, tableName) => {
  const foreignKeyMap = new Map();
  const results = await queryIdentifyingColumns(db, tableStatements,tableName).then( ([results, fields]) => {
    // Maps values in identifying columns of tableName to values in primary key columns of tableName.

    results.map(row => {
      // Check whether tableName depends on 'generation'.
      const hasGenID = row.generation_id != undefined;

      // Name of the AUTO_INCREMENT column.
      const autoIncColumnName = `${tableName}_id`;
      const autoIncColumnValue = row[autoIncColumnName];

      // Compute the primary key column(s).
      const primaryKeyColumns = { [autoIncColumnName]: autoIncColumnValue }
      if (hasGenID) primaryKeyColumns.generation_id = row.generation_id

      // Get the non-AUTO_INCREMENT columns from the given row.
      const identifyingColumns = Object.keys(row).reduce((acc, curr) => {
        // Ignore AUTO_INCREMENT column.
        if (curr === `${tableName}_id`) return acc;

        return {
          ...acc,
          [curr]: row[curr],
        }
      }, {});

      // We can't use objects or arrays as keys for a Map, so we need to use a string (AGHHHHHHHHHHHHHHHHHHHHHHHHHH). Since we aren't guaranteed the order of the object keys, we sort them alphabetically.
      const identifyingColumnsString = Object.keys(identifyingColumns)
        .sort()
        .reduce((acc, curr) => {
          return acc + identifyingColumns[curr] + ' ';
        }, '')
        // Slice to remove space.
        .slice(0, -1);
      foreignKeyMap.set(identifyingColumnsString, primaryKeyColumns);
    });
  });

  return foreignKeyMap;
}


/* 
  Given a table name, tableName, with an AUTO_INCREMENT column, select the AUTO_INCREMENT column, as well as any other identifying columns for the purpose of data insertion. E.g.

    If tableName = 'pokemon', select 'pokemon_id', the AUTO_INCREMENT column, as well as 'generation_id' and 'pokemon_name'. 
    
  We will use this to build Maps for inserting into junction tables. E.g.
  
    To insert rows into 'pokemon_ability', we use getIdentifyingColumns('pokemon') to (in another function) build a map which sends (pokemon_name, generation_id) to (generation_id, pokemon_id), which is one of the foreign keys for 'pokemon_ability'. 
*/
const queryIdentifyingColumns = async (db, tableStatements, tableName) => {
  // Whether the entity corresponding to tableName is generation-dependent.
  let hasGenID;
  switch (tableName) {
    case 'pdescription':
    case 'sprite':
    case 'version_group':
    case 'stat':
    case 'pstatus':
    case 'usage_method':
    case 'effect':
      hasGenID = false;
      break;
    default:
      hasGenID = true;
  }

  // The column of tableName which AUTO_INCREMENTs.
  const autoIncColumn = `${tableName}_id`;

  // The other columns of tableName which help identify a given row for the purpose of data insertion.
  const identifyingColumns = getIdentifyingColumnNames(tableName);

  return hasGenID 
    ? db.promise().query(tableStatements.entityTables[tableName].select(`generation_id, ${autoIncColumn}, ${identifyingColumns}`))
    : db.promise().query(tableStatements.entityTables[tableName].select(`${autoIncColumn}, ${identifyingColumns}`));
};

/*
  Given a table name, tableName, with an AUTO_INCREMENT column, select identifying columns for the purpose of data insertion. E.g.

    If tableName = 'pokemon', select 'pokemon_id', the AUTO_INCREMENT column, as well as 'generation_id' and 'pokemon_name'. 
*/
const getIdentifyingColumnNames = (tableName) => {
  let identifyingColumns;
  switch(tableName) {
    case 'pdescription':
      identifyingColumns = 'pdescription_index, pdescription_class, entity_name';
      break;
    case 'sprite':
      identifyingColumns = 'sprite_path, entity_name';
      break;
    case 'version_group':
      identifyingColumns = 'version_group_code';
      break;
    case 'ability': 
    case 'effect':
    case 'item':
    case 'pmove':
    case 'pokemon':
    case 'pstatus':
    case 'ptype':
    case 'stat':
    case 'usage_method':
      identifyingColumns = tableName + '_name';
      break;
    default:
      throw `Invalid table name: ${tableName}.`
  } 

  return identifyingColumns;
}

// #endregion


module.exports = {
  // Miscellaneous utilities
  NUMBER_OF_GENS,
  GEN_ARRAY,
  timeElapsed,

  // Drop statements
  dropSingleTableInGroup,
  dropTablesInGroup,
  dropAllJunctionTables,
  dropTablesNotRelevantToLearnsets,
  dropAllTables,

  // Create statements
  createSingleTableInGroup,
  createTablesInGroup,
  createAllJunctionTables,
  createAllTables,

  // Reinserting data

  // Entity tables
  reinsertBasicEntityData,
  reinsertGenDependentEntityData,

  // Junction tables
  reinsertAbilityJunctionData,
  reinsertItemJunctionData,
  reinsertMoveJunctionData,
  reinsertTypeJunctionData,
  reinsertPokemonJunctionData,
  reinsertVersionGroupJunctionData,
  reinsertLearnsetData,
}