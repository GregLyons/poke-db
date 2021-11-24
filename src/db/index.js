require('dotenv').config();
const mysql = require('mysql2');
const tableStatements = require('./sql/index.js');


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

const {
  recreateAllTables,
  resetBasicEntityTables,
  resetGenDependentEntityTables,
  resetAbilityJunctionTables,
  resetMoveJunctionTables,
  resetItemJunctionTables,
  resetPokemonJunctionTables,
  resetTypeJunctionTables,
  resetVersionGroupJunctionTables,
  resetLearnsetTable,
} = require('./utils/jointStatements.js');

// recreateAllTables(db, tableStatements);
// resetBasicEntityTables(db, tableStatements);
// resetGenDependentEntityTables(db, tableStatements);
// resetAbilityJunctionTables(db, tableStatements);
// resetMoveJunctionTables(db, tableStatements);
// resetItemJunctionTables(db, tableStatements);
// resetPokemonJunctionTables(db, tableStatements);
// resetTypeJunctionTables(db, tableStatements);
// resetVersionGroupJunctionTables(db, tableStatements);
// resetLearnsetTable(db, tableStatements);