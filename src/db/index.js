require('dotenv').config();
const mysql = require('mysql2');
const tableStatements = require('./sql/index.js');

const db = mysql.createPool({
  host: process.env.DB_HOST,
  user: process.env.DB_USERNAME,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME,
  connectionLimit: 20,
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

// creates any missing tables
const createTables = () => {
  // Create entity tables first for foreign keys
  Object.keys(tableStatements.entityTables).map(tableName => {
    const statement = tableStatements.entityTables[tableName].create;

    db.execute(statement, (err, results, fields) => {
      if (err && err.errno != 1065) {
        console.log(err);
      }
    });
  });

  // Create the junction tables
  Object.keys(tableStatements).map(tableGroup => {
    // We've already handled entity tables
    if (tableGroup === 'entityTables') return;

    Object.keys(tableStatements[tableGroup]).map(tableName=> {
      const statement = tableStatements[tableGroup][tableName].create;

      db.execute(statement, (err, results, fields) => {
        if (err && err.errno != 1065) {
          console.log(err);
        }
      });
    });
  });

  return;
};

