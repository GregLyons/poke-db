/*
Process the .json files in the raw_data/json folder into a form more amenable for inserting into a database. This includes extending patch lists to cover all generations, changing the objects to arrays, and splitting entries according to generation as necessary (e.g. 'bulbasaur' had one entry in pokemon.json before; now it will have an entry for each generation with the appropriate data).
*/

/* 
1. Take the .json files in the raw_data folder, extend the patch notes so that each gen has a patch in every relevant field, and then change each object to an array. This is done via serializeDict.

  E.g. for the pokemon.json, update the 'hp' field from something like 
    [[50, 1], [60, 4]] 
  to 
    [[50, 1], [50, 2], [50, 3], [60, 4], [60, 5], ... [60, <number of gens>]].
  
  Then, transform the entire pokemon.json into an array, pokemonArr, whose entry at index 0 is the original value whose key in pokemon.json is "bulbasaur", together with an extra entry, "name: 'bulbasaur'". So each key becomes another field in the corresponding array entry.

Note that, due to the complicated structure of the evolution data, the 'evolves_to' and 'evolves_from' properties for Pokemon are not extended in this way. We handle them separately in step 4.

2. Pokemon Showdown splits the learnsets between generation 2 and below and after generation 2. We merge them into a single collection of learnsets.

3. Add learnset and event data from Pokemon Showdown's learnsets.js to pokemonArr. Thus, pokemonArr[0], corresponding to "bulbasaur", will have added fields "learnset" and "event_data" with the relevant information. This is done via addLearnsetsToPokemonArr.

4. For each entry in an entity array, split the entry into multiple copies according to generation. For example, "bulbasaur" in pokemonArr will be split into 8 entries, one for each gen, with the data appropriate to that gen.

5. Import descriptions.json, effects.json, stats.json, statuses.json, usageMethods.json, and versionGroups.json, and serialize them. Aside from descriptions.json, these objects are much simpler in that they don't change across games (at least, the data--name and debut gen--we're tracking for them doesn't change), so we use a simplified version of serializeDict.

6. Write arrays to .json files.
*/

/* 1. Extend patch notes and serialize. */
// #region
const abilities = require('../../raw_data/json/abilities.json');
const pTypes = require('../../raw_data/json/elementalTypes.json');
const items = require('../../raw_data/json/items.json');
const moves = require('../../raw_data/json/moves.json');
const pokemon = require('../../raw_data/json/pokemon.json');



const { serializeDict } = require('./utils.js');

// these entities depend on generation, and so will be split later
const abilityArr = serializeDict(abilities);
const itemArr = serializeDict(items);
const moveArr = serializeDict(moves);
// We'll filter out LGPE Pokemon once we calculate the learnsets
let pokemonArr = serializeDict(pokemon);
const pTypeArr = serializeDict(pTypes);

// #endregion

/* 2. Merge learnset data. */
// #region
const { mergeLearnsets } = require('./utils.js');
const gen2Learnsets = require('../../raw_data/gen2learnsets.js');
const laterLearnsets = require('../../raw_data/learnsets.js');
const learnsets = mergeLearnsets(gen2Learnsets, laterLearnsets);

// #endregion

/* 3. Add merged learnset data. */
// #region
const { addLearnsetsToPokemonArr } = require('./utils.js');
addLearnsetsToPokemonArr(learnsets, moves, pokemon, pokemonArr);

// Separate out LGPE only Pokemon
const lgpeOnlyPokemon = pokemonArr.filter(data => data.gen == 'lgpe_only');
pokemonArr = pokemonArr.filter(data => data.gen !== 'lgpe_only');

// #endregion

/* 4. Split entities by generation. */
// #region
const { splitArr } = require('./utils.js');
const splitAbilityArr = splitArr(abilityArr);
const splitItemArr = splitArr(itemArr);
const splitMoveArr = splitArr(moveArr);
const splitPokemonArr = splitArr(pokemonArr);
const splitPTypeArr = splitArr(pTypeArr);

// #endregion

/* 5. Serialize descriptions and other simple objects. */
// #region
/*
Entries in descriptionArr are objects of the form:
  {
    entity_name: Name of ability, item, etc. to which the description applies, e.g. 'inner_focus'.

    description_type: Type of entity_name, e.g. 'inner_focus' has description_type 'ability'.

    gen: The generation in which the entity was introduced.

    '0': An array of the form
      [
        <Description text>,
        [<Version group codes>]
      ],
    e.g. 
      [
        'Prevents flinching.',
        ['RS', 'E', 'Colo', 'XD', 'FRLG']
      ]
    
    ...: Possibly additional integers, one for each unique description, with similar structure to the value for '0', e.g.
      '1': [...]
      '2': [...]
  }
*/
const descriptions = require('../../raw_data/json/descriptions.json');
const { serializeDescriptions } = require('./utils.js');
const descriptionArr = serializeDescriptions(descriptions);

// Serialize simpler objects.

const effects = require('../../raw_data/json/effects.json');
const usageMethods = require('../../raw_data/json/usageMethods.json');
const stats= require('../../raw_data/json/stats.json');
const statuses = require('../../raw_data/json/statuses.json');
const versionGroups = require('../../raw_data/json/versionGroups.json');

const { serializeSimpleDict } = require('./utils.js');

const effectArr = serializeSimpleDict(effects);
const statArr = serializeSimpleDict(stats);
const statusArr = serializeSimpleDict(statuses);
const usageMethodArr = serializeSimpleDict(usageMethods);
const versionGroupArr = serializeSimpleDict(versionGroups);

// #endregion

/* 6. Write arrays to .json files. */
// #region
const fs = require('fs');

// We get list of stats as well

const PROCESSED_DATA_PATH = './src/db/processing/processed_data/';
const FILENAMES_AND_ARRAYS = [
  ['abilities.json', splitAbilityArr],
  ['items.json', splitItemArr],
  ['moves.json', splitMoveArr],
  ['pokemon.json', splitPokemonArr],
  ['pTypes.json', splitPTypeArr],
  ['descriptions.json', descriptionArr],
  ['effects.json', effectArr],
  ['stats.json', statArr],
  ['statuses.json', statusArr],
  ['usageMethods.json', usageMethodArr],
  ['versionGroups.json', versionGroupArr],
];

FILENAMES_AND_ARRAYS.map(pair => {
  const [fname, arr] = pair;

  fs.writeFileSync(PROCESSED_DATA_PATH + fname, JSON.stringify(arr), (err) => {
    if (err) {
      throw err;
    }
  });

  console.log(`Saved ${fname}.`);
})

// #endregion

module.exports = {
  splitAbilityArr,
  splitItemArr,
  splitMoveArr,
  splitPokemonArr,
  splitPTypeArr,
  descriptionArr,
  effectArr,
  statusArr,
  usageMethodArr,
};

