/* 
Gather SQL statements and export them.
*/ 

const createTableStatements = require('./tables/index.js');
const insertStatements = require('./inserting/index.js');

module.exports = {
  ...createTableStatements,
  ...insertStatements,
};