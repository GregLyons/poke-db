require('dotenv').config();
const mysql = require('mysql2');
const sqlStatements = require('./sql/index.js');

const db = mysql.createConnection({
  host: process.env.DB_HOST,
  user: process.env.DB_USERNAME,
  password: process.env.DB_PASSWORD,
});

db.connect(function(err) {
  if (err) throw err;
  console.log('Connected!');
})