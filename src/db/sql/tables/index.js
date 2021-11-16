/*
Gather together all the CREATE TABLE statements in this folder and export them.
*/

const fs = require('fs');

const tablePath = './src/db/sql/tables/';

// Entity tables, e.g. generation, pokemon, move, etc.
const createEntityTables = fs.readFileSync(tablePath + 'entities.sql').toString();

// Relationship tables involving abilities
const createAbilityJunctionTables = fs.readFileSync(tablePath + 'abilities.sql').toString();

// Relationship tables involving elemental types
const createTypeJunctionTables = fs.readFileSync(tablePath + 'pTypes.sql').toString();

// Relationship tables involving items
const createItemJunctionTables = fs.readFileSync(tablePath + 'items.sql').toString();

// Relationship tables involving moves
const createMoveJunctionTables = fs.readFileSync(tablePath + 'moves.sql').toString();

// Relationship tables involving pokemon
const createPokemonJunctionTables = fs.readFileSync(tablePath + 'pokemon.sql').toString();

// Relationship tables involving version groups--includes sprite data and description data
const createVersionGroupJunctionTables = fs.readFileSync(tablePath + 'versionGroups.sql').toString();

module.exports = {
  createEntityTables, 
  createAbilityJunctionTables,
  createTypeJunctionTables,
  createItemJunctionTables,
  createMoveJunctionTables,
  createPokemonJunctionTables,
  createVersionGroupJunctionTables,
};