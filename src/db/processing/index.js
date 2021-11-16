/* 
1. Take the .json files in the raw_data folder, extend the patch notes so that each gen has a patch in every relevant field, and then change each object to an array. This is done via serializeDict.

  E.g. for the pokemon.json, update the 'hp' field from something like 
    [[50, 1], [60, 4]] 
  to 
    [[50, 1], [50, 2], [50, 3], [60, 4], [60, 5], ... [60, <number of gens>]].
  
  Then, transform the entire pokemon.json into an array, pokemonArr, whose entry at index 0 is the original value whose key in pokemon.json is "bulbasaur", together with an extra entry, "name: 'bulbasaur'". So each key becomes another field in the corresponding array entry.

2. Add learnset and event data from Pokemon Showdown's learnsets.js to pokemonArr. Thus, pokemonArr[0], corresponding to "bulbasaur", will have added fields "learnset" and "event_data" with the relevant information. This is done via addLearnsetsToPokemonArr.
*/

/* 1 */
const abilities = require('../../raw_data/json/abilities.json');
const effects = require('../../raw_data/json/effects.json');
const pTypes = require('../../raw_data/json/elementalTypes.json');
const items = require('../../raw_data/json/items.json');
const moves = require('../../raw_data/json/moves.json');
const pokemon = require('../../raw_data/json/pokemon.json');
const statuses = require('../../raw_data/json/statuses.json');
const usageMethods = require('../../raw_data/json/usageMethods.json');
const learnsets = require('../../raw_data/learnsets.js');

const { serializeDict } = require('./utils.js');

const abilityArr = serializeDict(abilities);
const effectArr = serializeDict(effects);
const itemArr = serializeDict(items);
const moveArr = serializeDict(moves);
const pokemonArr = serializeDict(pokemon);
const pTypeArr = serializeDict(pTypes);
const statusArr = serializeDict(statuses);
const usageMethodArr = serializeDict(usageMethods);

/* 2 */
const { addLearnsetsToPokemonArr } = require('./utils.js');
addLearnsetsToPokemonArr(learnsets, moves, pokemon, pokemonArr);

module.exports = {
  abilityArr,
  effectArr,
  itemArr,
  moveArr,
  pokemonArr,
  pTypeArr,
  statusArr,
  usageMethodArr,
};
