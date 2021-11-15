const fs = require('fs');

const tablePath = './src/db/sql/tables/';

/* 
Functions for creating tables
*/ 

// Entity tables, e.g. generation, pokemon, move, etc.
const entityTablesSQL = fs.readFileSync(tablePath + 'entities.sql').toString();

// Relationship tables involving abilities
const abilityTablesSQL = fs.readFileSync(tablePath + 'abilities.sql').toString();

// Relationship tables involving elemental types
const typeTablesSQL = fs.readFileSync(tablePath + 'elementalTypes.sql').toString();

// Relationship tables involving items
const itemTablesSQL = fs.readFileSync(tablePath + 'items.sql').toString();

// Relationship tables involving moves
const moveTablesSQL = fs.readFileSync(tablePath + 'moves.sql').toString();

// Relationship tables involving pokemon
const pokemonTablesSQL = fs.readFileSync(tablePath + 'pokemon.sql').toString();

// Relationship tables involving version groups--includes sprite data and description data
const versionGroupTablesSQL = fs.readFileSync(tablePath + 'versionGroups.sql').toString();