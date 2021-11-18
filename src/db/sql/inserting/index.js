/*
Gather together all the INSERT INTO statements in this folder. We combine them all into several objects: statements for entities, and then several objects of statements for junction tables of various types.

The keys of each object are the table names, and each value is another object with an "insert" key consisting of the actual INSERT INTO statement.

These will be combined one level up with the objects created in ../tables/index.js for CREATE TABLE and TRUNCATE TABLE functionality, as well as foreign key dependency data.
*/

const fs = require('fs');

const insertPath = './src/db/sql/inserting/';

// Object containing table names and their corresponding insert statements
/* 
Need to INSERT INTO generation first.
Need to INSERT INTO ptype before INSERT INTO pmove, the latter of which uses ptype as a foreign key.
Otherwise, order doesn't matter.
*/
const insertEntities = fs.readFileSync(insertPath + 'entities.sql')
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
