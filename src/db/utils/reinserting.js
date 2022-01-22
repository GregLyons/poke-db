/*
  RESETTING TABLES/RE-INSERTING DATA
*/

const { PROCESSED_DATA_PATH } = require('./helpers.js');
const { getForeignKeyMaps } = require('./foreignKeyMaps.js'); 
const { getValuesForTable } = require('./values.js');

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
    'field_state',
    'item',
    'pokemon',
    'pmove',
    'pstatus',
    'ptype',
    'nature',
    'stat',
    'usage_method',
    'version_group'
  ].filter(tableName => !ignoreTables.includes(tableName));

  return reinsertDataForTableGroup(
    db,
    tableStatements,
    entityTableNames,
    'entityTables',
    undefined
  );
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
      'ability_creates_field_state',
      'ability_removes_field_state',
      'ability_prevents_field_state',
      'ability_suppresses_field_state',
      'ability_ignores_field_state',
      'ability_prevents_usage_method',
    ]
  */
  const abilityJunctionTableNames = Object.keys(tableStatements.abilityJunctionTables);

  // Since Promise.all() preserves order, foreignKeyMaps unpacks alphabetically.
  const foreignKeyTables = [
    'ability',
    'effect',
    'field_state',
    'pstatus',
    'ptype',
    'stat',
    'usage_method',
  ];
  const foreignKeyMaps = await getForeignKeyMaps(db, tableStatements, foreignKeyTables);
  
  const abilityData = require(PROCESSED_DATA_PATH + 'abilities.json');

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
  DELETE FROM field state junction tables, then INSERT INTO those tables.
*/
const reinsertFieldStateJunctionData = async(db, tableStatements) => {
  /*
    [
      'field_state_modifies_stat',
      'field_state_effect',
      'field_state_causes_pstatus',
      'field_state_prevents_pstatus',
      'weather_ball',
      'field_state_boosts_ptype',
      'field_state_resists_ptype',
      'field_state_activates_ability',
      'field_state_activates_item',
      'field_state_enhances_pmove',
      'field_state_hinders_pmove',
    ]
  */
  const fieldStateJunctionTableNames = Object.keys(tableStatements.fieldStateJunctionTables);

  // Since Promise.all() preserves order, foreignKeyMaps unpacks alphabetically.
  const foreignKeyTables = [
    'ability',
    'effect',
    'field_state',
    'item',
    'pmove',
    'pstatus',
    'ptype',
    'stat',
  ];
  const foreignKeyMaps = await getForeignKeyMaps(db, tableStatements, foreignKeyTables);
  
  const fieldStateData = require(PROCESSED_DATA_PATH + 'fieldStates.json');

  return await reinsertDataForTableGroup(
    db,
    tableStatements,
    fieldStateJunctionTableNames,
    'fieldStateJunctionTables',
    fieldStateData,
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
      'item_extends_field_state',
      'item_resists_field_state',
      'item_ignores_field_state',
      'item_confuses_nature'
    ]
  */
  const itemJunctionTableNames = Object.keys(tableStatements.itemJunctionTables)
    // Currently no items boost usage methods; remove if a new game adds it.
    .filter(tableName => tableName != 'item_boosts_usage_method');

  // Since Promise.all() preserves order, foreignKeyMaps unpacks alphabetically.
  const foreignKeyTables = [
    'effect',
    'field_state',
    'item',
    'nature',
    'pokemon',
    'pstatus',
    'ptype',
    'stat',
    'usage_method',
  ];
  const foreignKeyMaps = await getForeignKeyMaps(db, tableStatements, foreignKeyTables);
  
  const itemData = require(PROCESSED_DATA_PATH + 'items.json');

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
      'pmove_ptype',
      'pmove_requires_ptype',
      'pmove_requires_pmove',
      'pmove_requires_pokemon',
      'pmove_requires_item',
      'pmove_usage_method',
      'pmove_modifies_stat',
      'pmove_effect',
      'pmove_causes_pstatus',
      'pmove_resists_pstatus',
      'move_creates_field_state',
      'move_removes_field_state',
      'move_prevents_field_state',
      'move_suppresses_field_state',
      'move_prevents_usage_method',
    ]
  */
  const moveJunctionTableNames = Object.keys(tableStatements.moveJunctionTables);

  // Since Promise.all() preserves order, foreignKeyMaps unpacks alphabetically.
  const foreignKeyTables = [
    'effect',
    'field_state',
    'item',
    'pmove',
    'pokemon',
    'pstatus',
    'ptype',
    'stat',
    'usage_method',
  ];
  const foreignKeyMaps = await getForeignKeyMaps(db, tableStatements, foreignKeyTables);
  
  const itemData = require(PROCESSED_DATA_PATH + 'moves.json');

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
  DELETE FROM nature junction tables, then INSERT INTO those tables.
*/
const reinsertNatureJunctionData = async(db, tableStatements) => {
  /*
    [
      'nature_modifies_stat'
    ]
  */
  const natureJunctionTableNames = Object.keys(tableStatements.natureJunctionTables)

  // Since Promise.all() preserves order, foreignKeyMaps unpacks alphabetically.
  const foreignKeyTables = [
    'nature',
    'stat'
  ];
  const foreignKeyMaps = await getForeignKeyMaps(db, tableStatements, foreignKeyTables);
  
  const natureData = require(PROCESSED_DATA_PATH + 'natures.json');

  return await reinsertDataForTableGroup(
    db,
    tableStatements,
    natureJunctionTableNames,
    'natureJunctionTables',
    natureData,
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
      'ptype_resists_field_state',
      'ptype_removes_field_state',
      'ptype_ignores_field_state',
    ]
  */
  const typeJunctionTableNames = Object.keys(tableStatements.typeJunctionTables);

  // Since Promise.all() preserves order, foreignKeyMaps unpacks alphabetically.
  const foreignKeyTables = [
    'field_state',
    'ptype',
  ];
  const foreignKeyMaps = await getForeignKeyMaps(db, tableStatements, foreignKeyTables);
  
  const pTypeData = require(PROCESSED_DATA_PATH + 'pTypes.json');

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
      'pokemon_requires_item',
    ]
  */
  const pokemonJunctionTableNames = Object.keys(tableStatements.pokemonJunctionTables)
    // Due to the size of the learnset data, we handle that separately.
    .filter(tableName => tableName != 'pokemon_pmove');

  // Since Promise.all() preserves order, foreignKeyMaps unpacks alphabetically.
  const foreignKeyTables = [
    'ability',
    'item',
    'pokemon',
    'ptype',
  ];
  const foreignKeyMaps = await getForeignKeyMaps(db, tableStatements, foreignKeyTables);
  
  const pokemonData = require(PROCESSED_DATA_PATH + 'pokemon.json');

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
  DELETE FROM usage method junction tables, then INSERT INTO those tables.
*/
const reinsertUsageMethodJunctionData = async(db, tableStatements) => {
  /*
    [
      'usage_method_activates_ability',
      'usage_method_activates_item',
    ]
  */
  const usageMethodJunctionTableNames = Object.keys(tableStatements.usageMethodJunctionTables);

  // Since Promise.all() preserves order, foreignKeyMaps unpacks alphabetically.
  const foreignKeyTables = [
    'ability',
    'item',
  ];
  const foreignKeyMaps = await getForeignKeyMaps(db, tableStatements, foreignKeyTables);
  
  const uasgeMethodData = require(PROCESSED_DATA_PATH + 'usageMethods.json');

  return await reinsertDataForTableGroup(
    db,
    tableStatements,
    usageMethodJunctionTableNames,
    'usageMethodJunctionTables',
    uasgeMethodData,
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
    .filter(tableName => tableName.split('_').includes('pdescription'));
    
  // Since Promise.all() preserves order, foreignKeyMaps unpacks alphabetically.
  const foreignKeyTables = [
    'ability',
    'pdescription',
    'item',
    'pmove',
    'version_group'
  ];
  const foreignKeyMaps = await getForeignKeyMaps(db, tableStatements, foreignKeyTables);
  
  const descriptionData = require(PROCESSED_DATA_PATH + 'descriptions.json');

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

  WARNING: Takes a long time, about 485 seconds (okay, long compared to everything else).

  To perform, need to have max_allowed_packet size be around 16M.
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
  const foreignKeyTables = [
    'pokemon',
    'pmove'
  ];
  const foreignKeyMaps = await getForeignKeyMaps(db, tableStatements, foreignKeyTables);
  
  const pokemonData = require(PROCESSED_DATA_PATH + 'pokemon.json');

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
    // .then( () => console.log(`${tableName} table deleted.`))
    .catch(console.log);
}

// Reset AUTO_INCREMENT counter for tableName.
const resetAutoIncrement = async(db, tableStatements, tableGroup, tableName) => {
  return db.promise().query(tableStatements[tableGroup][tableName].reset_auto_inc)
    // .then( () => console.log(`Reset AUTO_INCREMENT counter for ${tableName} table.`))
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

module.exports = {
  // Entity tables
  reinsertBasicEntityData,
  reinsertGenDependentEntityData,

  // Junction tables
  reinsertAbilityJunctionData,
  reinsertFieldStateJunctionData,
  reinsertItemJunctionData,
  reinsertMoveJunctionData,
  reinsertNatureJunctionData,
  reinsertTypeJunctionData,
  reinsertPokemonJunctionData,
  reinsertUsageMethodJunctionData,
  reinsertVersionGroupJunctionData,
  reinsertLearnsetData,
}