/*
  Various joint database operations with timers attached. 

  'recreate' means to DROP and then CREATE a table.

  'reset' and 'reinsert' mean to DELETE FROM a table, reset its AUTO_INCREMENT counter if applicable, and INSERT INTO the appropriate data.
*/

const { timeElapsed } = require('./helpers.js');

/* 1. Recreate all tables. */

const { dropAllTables } = require('./dropping.js');
const { createAllTables } = require('./creating.js');
// Drop tables if they exist, then recreate them.
const recreateAllTables = async (db, tableStatements) => {
  console.log('Resetting tables...\n');
  let timer = new Date().getTime();

  return dropAllTables(db, tableStatements)
    .then( () => {

      timer = timeElapsed(timer);

      console.log('\nCreating tables...\n')
      return createAllTables(db, tableStatements);
    })
    .then( () => {

      timer = timeElapsed(timer);

      console.log('\nFinished recreating all tables!\n');
    })
    .catch(console.log);
}

// #endregion

/* 2. Re-insert data for basic entities. */ 
// #region
const { reinsertBasicEntityData } = require('./reinserting.js');

const resetBasicEntityTables = async (db, tableStatements, ignoreTables) => {
  console.log('Re-inserting data for basic entities...\n');
  let timer = new Date().getTime();

  return reinsertBasicEntityData(db, tableStatements, ignoreTables)
    .then( () => {
      timer = timeElapsed(timer);
    })
    .then ( () => {
      console.log('\nFinished inserting data for basic entities!\n');
    })
    .catch(console.log);
}

// #endregion

/* 3. Re-insert data for gen-dependent entities. */
// #region
const { reinsertGenDependentEntityData } = require('./reinserting.js');

const resetGenDependentEntityTables = async (db, tableStatements, ignoreTables) => {
  console.log('Re-inserting data for gen-dependent entities...\n');
  let timer = new Date().getTime();

  return reinsertGenDependentEntityData(db, tableStatements, ignoreTables)
    .then( () => {
      timer = timeElapsed(timer);
    })
    .then ( () => {
      console.log('\nFinished inserting data for gen-dependent entities!\n');
    })
    .catch(console.log);
}

// resetGenDependentEntityTables();

// #endregion

/* 4. Re-insert data for ability junction tables. */
// #region
const { reinsertAbilityJunctionData } = require('./reinserting.js');

const resetAbilityJunctionTables = async (db, tableStatements) => {
  console.log('Re-inserting data for ability junction tables...\n');
  let timer = new Date().getTime();

  return reinsertAbilityJunctionData(db, tableStatements)
    .then( () => {
      timer = timeElapsed(timer);
    })
    .then ( () => {
      console.log('\nFinished inserting data for ability junction tables!\n');
    })
    .catch(console.log);
}

// resetAbilityJunctionTables();

// #endregion

/* 5. Re-insert data for field state junction tables. */
// #region
const { reinsertFieldStateJunctionData } = require('./reinserting.js');

const resetFieldStateJunctionTables = async (db, tableStatements) => {
  console.log('Re-inserting data for field state junction tables...\n');
  let timer = new Date().getTime();

  return reinsertFieldStateJunctionData(db, tableStatements)
    .then( () => {
      timer = timeElapsed(timer);
    })
    .then ( () => {
      console.log('\nFinished inserting data for field state junction tables!\n');
    })
    .catch(console.log);
}

// resetFieldStateJunctionTables();

// #endregion

/* 6. Re-insert data for nature junction tables. */
// #region
const { reinsertNatureJunctionData } = require('./reinserting.js');

const resetNatureJunctionTables = async (db, tableStatements) => {
  console.log('Re-inserting data for nature junction tables...\n');
  let timer = new Date().getTime();

  return reinsertNatureJunctionData(db, tableStatements)
    .then( () => {
      timer = timeElapsed(timer);
    })
    .then ( () => {
      console.log('\nFinished inserting data for nature junction tables!\n');
    })
    .catch(console.log);
}

// resetNatureJunctionTables();

// #endregion

/* 7. Re-insert data for item junction tables. */
// #region
const { reinsertItemJunctionData } = require('./reinserting.js');

const resetItemJunctionTables = async (db, tableStatements) => {
  console.log('Re-inserting data for item junction tables...\n');
  let timer = new Date().getTime();

  return reinsertItemJunctionData(db, tableStatements)
    .then( () => {
      timer = timeElapsed(timer);
    })
    .then ( () => {
      console.log('\nFinished inserting data for item junction tables!\n');
    })
    .catch(console.log);
}

// resetItemJunctionTables();

// #endregion

/* 8. Re-insert data for move junction tables. */
// #region
const { reinsertMoveJunctionData } = require('./reinserting.js');

const resetMoveJunctionTables = async (db, tableStatements) => {
  console.log('Re-inserting data for move junction tables...\n');
  let timer = new Date().getTime();

  return reinsertMoveJunctionData(db, tableStatements)
    .then( () => {
      timer = timeElapsed(timer);
    })
    .then ( () => {
      console.log('\nFinished inserting data for move junction tables!\n');
    })
    .catch(console.log);
}

// resetMoveJunctionTables();

// #endregion

/* 9. Re-insert data for type junction tables. */
// #region
const { reinsertTypeJunctionData } = require('./reinserting.js');

const resetTypeJunctionTables = async (db, tableStatements) => {
  console.log('Re-inserting data for type junction tables...\n');
  let timer = new Date().getTime();

  return reinsertTypeJunctionData(db, tableStatements)
    .then( () => {
      timer = timeElapsed(timer);
    })
    .then ( () => {
      console.log('\nFinished inserting data for type junction tables!\n');
    })
    .catch(console.log);
}

// resetTypeJunctionTables();

// #endregion

/* 10. Re-insert data for Pokemon junction tables. Doesn't include learnset data. */
// #region
const { reinsertPokemonJunctionData } = require('./reinserting.js');

const resetPokemonJunctionTables = async (db, tableStatements) => {
  console.log('Re-inserting data for Pokemon junction tables...\n');
  let timer = new Date().getTime();

  return reinsertPokemonJunctionData(db, tableStatements)
    .then( () => {
      timer = timeElapsed(timer);
    })
    .then ( () => {
      console.log('\nFinished inserting data for Pokemon junction tables!\n');
    })
    .catch(console.log);
}

// resetPokemonJunctionTables();

// #endregion

/* 11. Re-insert data for version group junction tables. */
// #region
const { reinsertVersionGroupJunctionData } = require('./reinserting.js');

const resetVersionGroupJunctionTables = async (db, tableStatements) => {
  console.log('Re-inserting data for version group junction tables...\n');
  let timer = new Date().getTime();

  return reinsertVersionGroupJunctionData(db, tableStatements)
    .then( () => {
      timer = timeElapsed(timer);
    })
    .then ( () => {
      console.log('\nFinished inserting data for version group junction tables!\n');
    })
    .catch(console.log);
}

// resetVersionGroupJunctionTables();

// #endregion

/* 12. Re-insert data for Pokemon learnset table. */
// #region
const { reinsertLearnsetData} = require('./reinserting.js');

const resetLearnsetTable = async (db, tableStatements) => {
  console.log('Re-inserting data for Pokemon learnset table...\n');
  let timer = new Date().getTime();

  return reinsertLearnsetData(db, tableStatements)
    .then( () => {
      timer = timeElapsed(timer);
    })
    .then ( () => {
      console.log('\nFinished inserting data for Pokemon learnset table!\n');
    })
    .catch(console.log);
}

// resetPokemonJunctionTables();

// #endregion

module.exports = {
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
  resetVersionGroupJunctionTables,
  
  resetLearnsetTable,
}