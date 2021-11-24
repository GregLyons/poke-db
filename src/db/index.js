require('dotenv').config();
const mysql = require('mysql2');
const tableStatements = require('./sql/index.js');
const { timeElapsed } = require('./utils.js');


const db = mysql.createPool({
  host: process.env.DB_HOST,
  user: process.env.DB_USERNAME,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME,
  connectionLimit: 30,
  connectTimeout: 20000,
});

// initializes database
const createDB = () => {
  db.execute(`CREATE DATABASE IF NOT EXISTS ${process.env.DB_NAME}`, (err, results, fields) => {
    console.log(err);
    console.log(results);
    console.log(fields);
  });

  console.log('Database created.');
} 

/* 1. Recreate all tables. */
// #region
const { dropAllTables, createAllTables } = require('./utils.js');

// Drop tables if they exist, then recreate them.
const recreateAllTables = async () => {
  console.log('Resetting tables...\n');
  let timer = new Date().getTime();
  let now;

  return dropAllTables(db, tableStatements)
    .then( () => {

      now = new Date().getTime();
      console.log('Took', Math.floor((now - timer) / 1000), 'seconds.\n');
      timer = now;

      console.log('\nCreating tables...\n')
      return createAllTables(db, tableStatements);
    })
    .then( () => {

      now = new Date().getTime();
      console.log('Took', Math.floor((now - timer) / 1000), 'seconds.\n');
      timer = now;

      console.log('\nFinished recreating all tables!\n');
    })
    .catch(console.log);
}

// recreateAllTables();

// #endregion

/* 2. Re-insert data for basic entities. */ 
// #region
const { reinsertBasicEntityData } = require('./utils.js');

const resetBasicEntityTables = async () => {
  console.log('Re-inserting data for basic entities...\n');
  let timer = new Date().getTime();

  return reinsertBasicEntityData(db, tableStatements)
    .then( () => {
      timer = timeElapsed(timer);
    })
    .then ( () => {
      console.log('\nFinished inserting data for basic entities!\n');
    })
    .catch(console.log);
}

// resetBasicEntityTables();

// #endregion

/* 3. Re-insert data for gen-dependent entities. */
// #region
const { reinsertGenDependentEntityData } = require('./utils.js');

const resetGenDependentEntityTables = async () => {
  console.log('Re-inserting data for gen-dependent entities...\n');
  let timer = new Date().getTime();

  return reinsertGenDependentEntityData(db, tableStatements)
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
const { reinsertAbilityJunctionData } = require('./utils.js');

const resetAbilityJunctionTables = async () => {
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

/* 5. Re-insert data for item junction tables. */
// #region
const { reinsertItemJunctionData } = require('./utils.js');

const resetItemJunctionTables = async () => {
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

/* 6. Re-insert data for move junction tables. */
// #region
const { reinsertMoveJunctionData } = require('./utils.js');

const resetMoveJunctionTables = async () => {
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

/* 7. Re-insert data for type junction tables. */
// #region
const { reinsertTypeJunctionData } = require('./utils.js');

const resetTypeJunctionTables = async () => {
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

/* 8. Re-insert data for Pokemon junction tables. */
// #region
const { reinsertPokemonJunctionData } = require('./utils.js');

const resetPokemonJunctionTables = async () => {
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

/* 9. Re-insert data for version group junction tables. */
// #region
const { reinsertVersionGroupJunctionData } = require('./utils.js');

const resetVersionGroupJunctionTables = async () => {
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

/* 10. Re-insert data for Pokemon learnset table. */
// #region
const { resetPokemonLearnsetTable } = require('./utils.js');

const reinsertLearnsetJunctionTable = async () => {
  console.log('Re-inserting data for Pokemon learnset table...\n');
  let timer = new Date().getTime();

  return resetLearnsetJunctionTable(db, tableStatements)
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


// dropAllTables();
// createAllTables();
// insertBasicEntities();
// insertGenDependentEntities();
// insertAbilityJunctionData();
// insertItemJunctionData();
// insertMoveJunctionData();
// insertPokemonJunctionData();
// insertPokemonLearnsetData();
