/*
Gather together all the INSERT INTO statements in this folder. We combine them all into several objects: statements for entities, and then several objects of statements for junction tables of various types.

The keys of each object are the table names, and each value is another object with an "insert" key consisting of the actual INSERT INTO statement.

These will be combined one level up with the objects created in ../tables/index.js for CREATE TABLE, TRUNCATE TABLE, and SELECT functionality, as well as foreign key dependency data.
*/

const fs = require('fs');

const INSERT_PATH = './src/db/sql/inserting/';
const FILENAMES_AND_KEYS = [
  ['entities.sql', 'entityTables'],
  ['abilities.sql', 'abilityJunctionTables'],
  ['fieldStates.sql', 'fieldStateJunctionTables'],
  ['pTypes.sql', 'typeJunctionTables'],
  ['items.sql', 'itemJunctionTables'],
  ['moves.sql', 'moveJunctionTables'],
  ['natures.sql', 'natureJunctionTables'],
  ['pokemon.sql', 'pokemonJunctionTables'],
  ['versionGroups.sql', 'versionGroupJunctionTables'],
];

const insertStatements = FILENAMES_AND_KEYS.reduce((acc, curr) => {
  const [fname, keyName] = curr;
  return {
    ...acc,
    [keyName]: getStatementObj(fname),
  };
}, {});

function getStatementObj(fname) {
  return fs.readFileSync(INSERT_PATH + fname)
  .toString()
  .split(';')
  .reduce((acc, curr) => {
    if (curr) {
      const tableRegex = /INSERT INTO ([a-z_]+) \(/;
      const match = curr.match(tableRegex);
      const [tableName, insertStatement] = [match[1], match.input];

      return {
        ...acc,
        [tableName]: {
          "insert": insertStatement,
        }
      };
    }
    else return acc;
  }, {});
}

module.exports = insertStatements;