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

/* 1. Reset tables. ~3 min without learnset data. */
// #region
const { dropAllTables, createAllTables } = require('./utils.js');

// Drop tables if they exist, then recreate them.
const resetAllTables = async () => {
  console.log('Resetting tables...\n');
  let timer = new Date().getTime();
  let now;

  return dropAllTables(db)
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

      console.log('\nFinished resetting tables!\n');
    })
    .catch(console.log);
}

// resetAllTables();

// #endregion

/* 2. Insert data for basic entities. */ 
// #region
const { resetBasicEntityTables } = require('./utils.js');

const reinsertBasicEntityTables = async () => {
  console.log('Re-inserting data for basic entities...\n');
  let timer = new Date().getTime();

  return resetBasicEntityTables(db, tableStatements)
    .then( () => {
      timer = timeElapsed(timer);
    })
    .then ( () => {
      console.log('\nFinished inserting data for basic entities!\n');
    })
    .catch(console.log);
}

// reinsertBasicEntityTables();

// #endregion

/* 3. Insert data for gen-dependent entities. */
// #region
const { resetGenDependentEntityTables } = require('./utils.js');

const reinsertGenDependentEntityTables = async () => {
  console.log('Re-inserting data for gen-dependent entities...\n');
  let timer = new Date().getTime();

  return resetGenDependentEntityTables(db, tableStatements)
    .then( () => {
      timer = timeElapsed(timer);
    })
    .then ( () => {
      console.log('\nFinished inserting data for gen-dependent entities!\n');
    })
    .catch(console.log);
}

// reinsertGenDependentEntityTables();

// #endregion

/* 4. Insert data for ability junction tables. */
// #region
const { resetAbilityJunctionTables } = require('./utils.js');

const reinsertAbilityJunctionTables = async () => {
  console.log('Re-inserting data for ability junction tables...\n');
  let timer = new Date().getTime();

  return resetAbilityJunctionTables(db, tableStatements)
    .then( () => {
      timer = timeElapsed(timer);
    })
    .then ( () => {
      console.log('\nFinished inserting data for ability junction tables!\n');
    })
    .catch(console.log);
}

// reinsertAbilityJunctionTables();

// #endregion

/* 5. Insert data for item junction tables. */
// #region
const { resetItemJunctionTables } = require('./utils.js');

const reinsertItemJunctionTables = async () => {
  console.log('Re-inserting data for item junction tables...\n');
  let timer = new Date().getTime();

  return resetItemJunctionTables(db, tableStatements)
    .then( () => {
      timer = timeElapsed(timer);
    })
    .then ( () => {
      console.log('\nFinished inserting data for item junction tables!\n');
    })
    .catch(console.log);
}

// reinsertItemJunctionTables();

// #endregion

/* 6. Insert data for move junction tables. */
// #region
const { resetMoveJunctionTables } = require('./utils.js');

const reinsertMoveJunctionTables = async () => {
  console.log('Re-inserting data for move junction tables...\n');
  let timer = new Date().getTime();

  return resetMoveJunctionTables(db, tableStatements)
    .then( () => {
      timer = timeElapsed(timer);
    })
    .then ( () => {
      console.log('\nFinished inserting data for move junction tables!\n');
    })
    .catch(console.log);
}

// reinsertMoveJunctionTables();
// #endregion

/* 7. Insert data for type junction tables. */
// #region
const { resetTypeJunctionTables } = require('./utils.js');

const reinsertTypeJunctionTables = async () => {
  console.log('Re-inserting data for type junction tables...\n');
  let timer = new Date().getTime();

  return resetTypeJunctionTables(db, tableStatements)
    .then( () => {
      timer = timeElapsed(timer);
    })
    .then ( () => {
      console.log('\nFinished inserting data for type junction tables!\n');
    })
    .catch(console.log);
}

// reinsertTypeJunctionTables();

// #endregion

/* 8. Insert data for Pokemon junction tables. */
// #region
const { resetPokemonJunctionTables } = require('./utils.js');

const reinsertPokemonJunctionTables = async () => {
  console.log('Re-inserting data for Pokemon junction tables...\n');
  let timer = new Date().getTime();

  return resetPokemonJunctionTables(db, tableStatements)
    .then( () => {
      timer = timeElapsed(timer);
    })
    .then ( () => {
      console.log('\nFinished inserting data for Pokemon junction tables!\n');
    })
    .catch(console.log);
}

// reinsertPokemonJunctionTables();

// #endregion

/* 9. Insert data for version group junction tables. */
// #region
const { resetVersionGroupJunctionTables } = require('./utils.js');

const reinsertVersionGroupJunctionTables = async () => {
  console.log('Re-inserting data for version group junction tables...\n');
  let timer = new Date().getTime();

  return resetVersionGroupJunctionTables(db, tableStatements)
    .then( () => {
      timer = timeElapsed(timer);
    })
    .then ( () => {
      console.log('\nFinished inserting data for version group junction tables!\n');
    })
    .catch(console.log);
}

// reinsertVersionGroupJunctionTables();

// #endregion

/* 10. Insert data for Pokemon learnset table. */
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

// reinsertPokemonJunctionTables();

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
