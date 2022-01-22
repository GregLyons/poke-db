/*
Gather together all the CREATE TABLE statements in this folder. We combine them all into several objects: statements for entities, and then several objects of statements for junction tables of various types.

The keys of each object are the table names, and each value is another object with keys:

  create: Statement for creating the table.

  select: A function which takes in a column selection (e.g. 'generation_id', 'pmove_id, pmove_name') and returns a statement for selecting those columns.

  truncate: Statement for truncating the table.

  foreign_keys: Array consisting of table names which are foreign key references for the given table.

These will be combined one level up with the objects created in ../inserting/index.js for INSERT INTO functionality.
*/

const fs = require('fs');

const TABLE_PATH = './src/db/sql/tables/';
const FILENAMES_AND_KEYS = [
  ['entities.sql', 'entityTables'],
  ['abilities.sql', 'abilityJunctionTables'],
  ['fieldStates.sql', 'fieldStateJunctionTables'],
  ['pTypes.sql', 'typeJunctionTables'],
  ['items.sql', 'itemJunctionTables'],
  ['moves.sql', 'moveJunctionTables'],
  ['natures.sql', 'natureJunctionTables'],
  ['pokemon.sql', 'pokemonJunctionTables'],
  ['usageMethods.sql', 'usageMethodJunctionTables'],
  ['versionGroups.sql', 'versionGroupJunctionTables'],
]

const tableStatements = FILENAMES_AND_KEYS.reduce((acc, curr) => {
  const [fname, keyName] = curr;
  return {
    ...acc,
    [keyName]: getStatementObj(fname),
  };
}, {});

function getStatementObj(fname) {
  return fs.readFileSync(TABLE_PATH + fname)
  .toString()
  .split(';')
  .reduce((acc, curr) => {
    if (curr) {
      const tableRegex = /CREATE TABLE IF NOT EXISTS ([a-z_]+) \(/;
      const createMatch = curr.match(tableRegex);
      const [tableName, createStatement] = [createMatch[1], createMatch.input];
      const truncateStatement = `TRUNCATE TABLE ${tableName}`;
      
      // For each table, identify the foreign key dependencies
      const dependencyRegex = /REFERENCES ([a-z_]+)\(/g;
      const matches = curr.matchAll(dependencyRegex);
      let dependencies = [];
      for (let dependency of matches) {
        dependencies.push(dependency[1]);
      }

      const selectColumns = columnSelection => `SELECT ${columnSelection} FROM ${tableName}`;

      // delete data from a table 
      const deleteStatement = `DELETE FROM ${tableName}`;
      // DROP TABLE
      const dropStatement = `DROP TABLE IF EXISTS ${tableName}`;
      // reset auto_increment
      const resetStatement = `ALTER TABLE ${tableName} AUTO_INCREMENT = 1`;

      return {
        ...acc,
        [tableName]: {
          "create": createStatement,
          "truncate": truncateStatement,
          "select": selectColumns,
          "delete": deleteStatement,
          "drop": dropStatement,
          "reset_auto_inc": resetStatement,
          "foreign_keys": dependencies,
        }
      };
    }
    else return acc;
  }, {});
}

module.exports = tableStatements;