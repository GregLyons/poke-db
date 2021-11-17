require('dotenv').config();
const mysql = require('mysql2');
const sqlStatements = require('./sql/index.js');

const db = mysql.createPool({
  host: process.env.DB_HOST,
  user: process.env.DB_USERNAME,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME,
  connectionLimit: 10,
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

// initializes tables
const createTables = () => {
  Object.keys(sqlStatements.createTableStatements).map(tableGroupKey => {
    sqlStatements.createTableStatements[tableGroupKey].split(';').map(statement => {
      db.execute(statement, (err, results, fields) => {
        if (err && err.errno != 1065) {
          console.log(err);
        }
      });
    });
  });
}
