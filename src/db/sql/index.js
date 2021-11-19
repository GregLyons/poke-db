/* 
Merge the insert statements with the rest of the table statements, and then export them.
*/ 

const tableStatements = require('./tables/index.js');
const insertStatements = require('./inserting/index.js');

// Merge insert statements with rest of table statements.
for (let tableType of Object.keys(insertStatements)) {
  for (let tableName of Object.keys(insertStatements[tableType])) {
    tableStatements[tableType][tableName] = 
    {
      ...tableStatements[tableType][tableName],
      insert: insertStatements[tableType][tableName].insert,
    }
  }
}

// Ensures that every table has an insert statement.
for (let tableType of Object.keys(tableStatements)) {
  for (let tableName of Object.keys(tableStatements[tableType])) {
    if (!tableStatements[tableType][tableName].insert) {
      throw `${tableType} ${tableName} is missing an insert statement.`
    }
  }
}

module.exports = tableStatements;