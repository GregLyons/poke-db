/*
Gather together all the CREATE TABLE statements in this folder. We combine them all into several objects: statements for entities, and then several objects of statements for junction tables of various types.

The keys of each object are the table names, and each value is another object with keys:

  create: Statement for creating the table.

  truncate: Statement for truncating the table.

  foreign_keys: Array consisting of table names which are foreign key references for the given table.

These will be combined one level up with the objects created in ../inserting/index.js for INSERT INTO functionality.
*/

const fs = require('fs');

const tablePath = './src/db/sql/tables/';

// Object containing entity table names and their corresponding create and truncate statements statements, as well as any foreign key dependencies
const createEntityTables = fs.readFileSync(tablePath + 'entities.sql')
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

      return {
        ...acc,
        [tableName]: {
          "create": createStatement,
          "truncate": truncateStatement,
          "foreign_keys": dependencies,
        }
      };
    }
    else return acc;
  }, {});

// Relationship tables involving abilities
const createAbilityJunctionTables = fs.readFileSync(tablePath + 'abilities.sql')
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

      return {
        ...acc,
        [tableName]: {
          "create": createStatement,
          "truncate": truncateStatement,
          "foreign_keys": dependencies,
        }
      };
    }
    else return acc;
  }, {});

// Relationship tables involving elemental types
const createTypeJunctionTables = fs.readFileSync(tablePath + 'pTypes.sql')
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

      return {
        ...acc,
        [tableName]: {
          "create": createStatement,
          "truncate": truncateStatement,
          "foreign_keys": dependencies,
        }
      };
    }
    else return acc;
  }, {});

// Relationship tables involving items
const createItemJunctionTables = fs.readFileSync(tablePath + 'items.sql')
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

      return {
        ...acc,
        [tableName]: {
          "create": createStatement,
          "truncate": truncateStatement,
          "foreign_keys": dependencies,
        }
      };
    }
    else return acc;
  }, {});

// Relationship tables involving moves
const createMoveJunctionTables = fs.readFileSync(tablePath + 'moves.sql')
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

      return {
        ...acc,
        [tableName]: {
          "create": createStatement,
          "truncate": truncateStatement,
          "foreign_keys": dependencies,
        }
      };
    }
    else return acc;
  }, {});

// Relationship tables involving pokemon
const createPokemonJunctionTables = fs.readFileSync(tablePath + 'pokemon.sql')
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

      return {
        ...acc,
        [tableName]: {
          "create": createStatement,
          "truncate": truncateStatement,
          "foreign_keys": dependencies,
        }
      };
    }
    else return acc;
  }, {});

// Relationship tables involving version groups--includes sprite data and description data
const createVersionGroupJunctionTables = fs.readFileSync(tablePath + 'versionGroups.sql')
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

      return {
        ...acc,
        [tableName]: {
          "create": createStatement,
          "truncate": truncateStatement,
          "foreign_keys": dependencies,
        }
      };
    }
    else return acc;
  }, {});

module.exports = {
  createEntityTables, 
  createAbilityJunctionTables,
  createTypeJunctionTables,
  createItemJunctionTables,
  createMoveJunctionTables,
  createPokemonJunctionTables,
  createVersionGroupJunctionTables,
};