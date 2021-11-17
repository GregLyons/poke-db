/* 
1. Take the .json files in the raw_data folder, extend the patch notes so that each gen has a patch in every relevant field, and then change each object to an array. This is done via serializeDict.

  E.g. for the pokemon.json, update the 'hp' field from something like 
    [[50, 1], [60, 4]] 
  to 
    [[50, 1], [50, 2], [50, 3], [60, 4], [60, 5], ... [60, <number of gens>]].
  
  Then, transform the entire pokemon.json into an array, pokemonArr, whose entry at index 0 is the original value whose key in pokemon.json is "bulbasaur", together with an extra entry, "name: 'bulbasaur'". So each key becomes another field in the corresponding array entry.

Note that, due to the complicated structure of the evolution data, the 'evolves_to' and 'evolves_from' properties for Pokemon are not extended in this way. We handle them separately in step 4.

2. Pokemon Showdown splits the learnsets between gen 2 and below and after gen 2. We merge them into a single collection of learnsets.

3. Add learnset and event data from Pokemon Showdown's learnsets.js to pokemonArr. Thus, pokemonArr[0], corresponding to "bulbasaur", will have added fields "learnset" and "event_data" with the relevant information. This is done via addLearnsetsToPokemonArr.

4. For each entry in an entity array, split the entry into multiple copies according to generation. For example, "bulbasaur" in pokemonArr will be split into 8 entries, one for each gen, with the data appropriate to that gen.
*/

/* 1. Extend patch notes and serialize. */
const abilities = require('../../raw_data/json/abilities.json');
const effects = require('../../raw_data/json/effects.json');
const pTypes = require('../../raw_data/json/elementalTypes.json');
const items = require('../../raw_data/json/items.json');
const moves = require('../../raw_data/json/moves.json');
const pokemon = require('../../raw_data/json/pokemon.json');
const statuses = require('../../raw_data/json/statuses.json');
const usageMethods = require('../../raw_data/json/usageMethods.json');

const { serializeDict } = require('./utils.js');

// these entities depend on generation, and so will be split later
const abilityArr = serializeDict(abilities);
const itemArr = serializeDict(items);
const moveArr = serializeDict(moves);
const pokemonArr = serializeDict(pokemon);
const pTypeArr = serializeDict(pTypes);

// these entities do not depend on generation, and so will not be split later
const effectArr = serializeDict(effects);
const statusArr = serializeDict(statuses);
const usageMethodArr = serializeDict(usageMethods);



/* 2. Merge learnset data. */
const { mergeLearnsets } = require('./utils.js');
const gen2Learnsets = require('../../raw_data/gen2learnsets.js');
const laterLearnsets = require('../../raw_data/learnsets.js');
const learnsets = mergeLearnsets(gen2Learnsets, laterLearnsets);



/* 3. Add merged learnset data. */
const { addLearnsetsToPokemonArr } = require('./utils.js');
addLearnsetsToPokemonArr(learnsets, moves, pokemon, pokemonArr);



/* 4. Split entities by generation. */
const { splitArr } = require('./utils.js');
const splitAbilityArr = splitArr(abilityArr);
const splitItemArr = splitArr(itemArr);
const splitMoveArr = splitArr(moveArr);
const splitPokemonArr = splitArr(pokemonArr);
const splitPTypeArr = splitArr(pTypeArr);

module.exports = {
  splitAbilityArr,
  splitItemArr,
  splitMoveArr,
  splitPokemonArr,
  splitPTypeArr,
  effectArr,
  statusArr,
  usageMethodArr,
};

