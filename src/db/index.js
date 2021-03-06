require('dotenv').config();
const mysql = require('mysql2');
const tableStatements = require('./sql/index.js');

/*
  The learnset data may be too large to insert into the database. If an ECONNRESET error comes up on inserting the learnset data, you may need to change the MySQL max_allowed_packet to 16M/1024*1024*16 (or to any number greater than the size of the learnset data). 
*/
const db = mysql.createPool({
  host: process.env.DB_HOST,
  user: process.env.DB_USERNAME,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME,
  connectionLimit: 30,
  connectTimeout: 20000,
});

const {
  recreateAllTables,

  resetBasicEntityTables,

  resetGenDependentEntityTables,

  resetAbilityJunctionTables,
  resetFieldStateJunctionTables,
  resetItemJunctionTables,
  resetMoveJunctionTables,
  resetNatureJunctionTables,
  resetPokemonJunctionTables,
  resetTypeJunctionTables,
  resetUsageMethodJunctionTables,
  resetVersionGroupJunctionTables,

  resetLearnsetTable,
} = require('./utils/jointStatements.js');

const { reinsertBasicEntityData } = require('./utils/reinserting.js');

// Resets the gen-dependent entity tables, with the option to ignore 'pokemon' and 'pmove', on which the learnset table depends.
const resetEntityTables = async (ignoreLearnsetTable = true) => {
  if (ignoreLearnsetTable) {
    console.log(`\nResetting entity tables except those which influence learnset data, i.e. except for 'generation', 'pokemon', and 'pmove'.\n`);

    console.log(`NOTE: This will drop all junction tables as well, except 'pokemon_pmove' (the other junction tables involving 'pokemon' and 'pmove' will be dropped).\n`);

  } else {
    console.log(`\nResetting all entity tables.\n`);

    console.log(`NOTE: This will drop all junction tables as well.\n`);

    // Drop indices and foreign key constraints from 'pokemon_pmove' to facilitate deleting from the junction tables.
    const { prepareLearnsetTableForDrop } = require('./utils/dropping.js');
    await prepareLearnsetTableForDrop(db);
  }

  const ignoreTables = ignoreLearnsetTable 
    ? ['generation', 'pokemon', 'pmove', 'pokemon_pmove']
    : [];

  await resetBasicEntityTables(db, tableStatements, ignoreTables);

  return resetGenDependentEntityTables(db, tableStatements, ignoreTables);
}

// Resets all junction tables, with the option to ignore the learnset table.
const resetJunctionTables = async (ignoreLearnsetTable = true) => {
  ignoreLearnsetTable 
    ? console.log(`\nResetting junction tables except learnset table...\n`)
    : console.log(`\nResetting all junction tables...\n`);
  
  let resetFunctions = [
    resetAbilityJunctionTables,
    resetFieldStateJunctionTables,
    resetMoveJunctionTables,
    resetItemJunctionTables,
    resetNatureJunctionTables,
    resetPokemonJunctionTables,
    resetTypeJunctionTables,
    resetUsageMethodJunctionTables,
    resetVersionGroupJunctionTables,
  ]

  if (!ignoreLearnsetTable) resetFunctions = resetFunctions.concat(resetLearnsetTable);

  return Promise.all(
    resetFunctions.map(resetFunction => {
      return resetFunction(db, tableStatements);
    })
  )
  .then( () => console.log('\nFinished resetting junction tables.\n'))
  .catch(console.log);
}

// Deletes everything, recreates all the tables, and re-inserts all the data.
// The timer at the end shows how long the entire operation took. The other timers come from the various functions called from ./utils/jointStatements.js.
// As of Generation 8, takes about 15-20 minutes.
const resetEverything = async () => {
  console.log('\nResetting all data and tables...\n')
  const { timeElapsed } = require('./utils/helpers.js');

  let timer = new Date().getTime();

  await recreateAllTables(db, tableStatements);

  await resetBasicEntityTables(db, tableStatements);

  await resetGenDependentEntityTables(db, tableStatements);

  return resetJunctionTables(false)
    .then( () => {

      timer = timeElapsed(timer);

      console.log('\nAll tables created and all data inserted!\n');
    })
    .catch();
}

// JOINT DATABASE STATEMENTS
/*
  Only uncomment functions out in one region at a time. Otherwise, table lock is likely to result. For example, only run functions in the 'RESET SPECIFIC CLASSES OF JUNCTION TABLES' region, or in the 'RESET ENTITY TABLES' region, but not functions from both.
*/ 
//#region

// RESET ENTIRE DATABASE
//#region

resetEverything();

//#endregion

// RESET ALL JUNCTION TABLES
//#region

// resetJunctionTables()
// resetLearnsetTable(db, tableStatements);

//#endregion

// RECREATE ALL TABLES
//#region

// recreateAllTables(db, tableStatements);

//#endregion

// RESET ENTITY TABLES
//#region

// resetBasicEntityTables(db, tableStatements);
// resetGenDependentEntityTables(db, tableStatements);

//#endregion

// RESET SPECIFIC CLASSES OF JUNCTION TABLES
//#region

// resetAbilityJunctionTables(db, tableStatements);
// resetFieldStateJunctionTables(db, tableStatements);
// resetMoveJunctionTables(db, tableStatements);
// resetNatureJunctionTables(db, tableStatements);
// resetItemJunctionTables(db, tableStatements);
// resetPokemonJunctionTables(db, tableStatements);
// resetTypeJunctionTables(db, tableStatements);
// resetUsageMethodJunctionTables(db, tableStatements);
// resetVersionGroupJunctionTables(db, tableStatements);

// resetLearnsetTable(db, tableStatements);

//#endregion

//#endregion