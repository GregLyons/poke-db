/*
  Process the .json files the raw_data directory into a form more amenable for inserting into the database, then save to the processed_data directory.
  
  This processing includes extending patch lists to cover all generations, changing the objects to arrays, and splitting entries according to generation as necessary (e.g. 'bulbasaur' had one entry in pokemon.json before; now it will have an entry for each generation with the appropriate data).

  The comment below gives a more detailed description of these steps.
*/

/* 
1. Take the .json files in the raw_data directory, extend the patch notes so that each gen has a patch in every relevant field, and then change each object to an array. This is done via serializeDict.

  E.g. for the pokemon.json, update the 'hp' field from something like 
    [[50, 1], [60, 4]] 
  to 
    [[50, 1], [50, 2], [50, 3], [60, 4], [60, 5], ... [60, <number of gens>]].
  
  Then, transform the entire pokemon.json into an array, pokemonArr, whose entry at index 0 is the original value whose key in pokemon.json is "bulbasaur", together with an extra entry, "name: 'bulbasaur'". So each key becomes another field in the corresponding array entry.

Note that, due to the complicated structure of the evolution data, the 'evolves_to' and 'evolves_from' properties for Pokemon are not extended in this way. We handle them separately in step 4.

2. Pokemon Showdown splits the learnsets between generation 2 and below and after generation 2. We merge them into a single collection of learnsets.

3. Add learnset and event data from Pokemon Showdown's learnsets.js to pokemonArr. Thus, pokemonArr[0], corresponding to "bulbasaur", will have added fields "learnset" and "event_data" with the relevant information. This is done via addLearnsetsToPokemonArr.

In this step, we also add the names used in the learnset as 'ps_id', since they are used throughout Pokemon Showdown's code/packages.

4. For each entry in an entity array, split the entry into multiple copies according to generation. For example, "bulbasaur" in pokemonArr will be split into 8 entries, one for each gen, with the data appropriate to that gen.

5. Import descriptions.json, effects.json, stats.json, statuses.json, usageMethods.json, and versionGroups.json, and serialize them. Aside from descriptions.json, these objects are much simpler in that they don't change across games (at least, the data--name and debut gen--we're tracking for them doesn't change), so we use a simplified version of serializeDict.

6. Write arrays to .json files.

7. Valid data for insertion (e.g. check for numbers in numeric fields, defined values in non-nullable fields, etc.).
*/

/* 1. Extend patch notes and serialize. */
// #region

const { RAW_JSON_DATA_PATH } = require('./utils/index.js');
const abilities = require(RAW_JSON_DATA_PATH + 'abilities.json');
const pTypes = require(RAW_JSON_DATA_PATH + 'elementalTypes.json');
const items = require(RAW_JSON_DATA_PATH + 'items.json');
const moves = require(RAW_JSON_DATA_PATH + 'moves.json');
const pokemon = require(RAW_JSON_DATA_PATH + 'pokemon.json');


const effects = require(RAW_JSON_DATA_PATH + 'effects.json');
const fieldStates = require(RAW_JSON_DATA_PATH + 'fieldStates.json');
const natures = require(RAW_JSON_DATA_PATH + 'natures.json');
const usageMethods = require(RAW_JSON_DATA_PATH + 'usageMethods.json');
const stats= require(RAW_JSON_DATA_PATH + 'stats.json');
const statuses = require(RAW_JSON_DATA_PATH + 'statuses.json');



const { serializeDict } = require('./utils/index.js');

// these entities depend on generation, and so will be split later
const abilityArr = serializeDict(abilities);
const itemArr = serializeDict(items);
// We'll filter out LGPE Pokemon and moves once we calculate the learnsets
let moveArr = serializeDict(moves);
let pokemonArr = serializeDict(pokemon);

const pTypeArr = serializeDict(pTypes);


const effectArr = serializeDict(effects);
const fieldStateArr = serializeDict(fieldStates);
const natureArr = serializeDict(natures);
const statArr = serializeDict(stats);
const statusArr = serializeDict(statuses);
const usageMethodArr = serializeDict(usageMethods);

// #endregion

/* 2. Merge learnset data. */
// #region
const { RAW_DATA_PATH } = require('./utils/index.js');
const { mergeLearnsets } = require('./utils/index.js');
const gen2Learnsets = require(RAW_DATA_PATH + 'gen2learnsets.js');
const laterLearnsets = require(RAW_DATA_PATH + 'learnsets.js');
const learnsets = mergeLearnsets(gen2Learnsets, laterLearnsets);

// #endregion

/* 3. Add merged learnset data. Also adds Pokemon Showdown IDs, 'ps_id'. */
// #region
const { addLearnsetsToPokemonArr } = require('./utils/index.js');
addLearnsetsToPokemonArr(learnsets, moves, pokemon, pokemonArr);

// Separate out LGPE only Pokemon
const lgpeOnlyPokemon = ['pikachu_partner', 'eevee_partner'];
const lgpeOnlyMoves = moveArr.filter(data => data.gen == 7 && Object.keys(data.lgpe_exclusive_values).length == 5);

pokemonArr = pokemonArr.filter(data => !lgpeOnlyPokemon.includes(data.name));
moveArr = moveArr.filter(data => !(data.gen == 7 && Object.keys(data.lgpe_exclusive_values).length == 5));

// #endregion

/* 4. Split entities by generation. */
// #region
const { splitArr } = require('./utils/index.js');
const splitAbilityArr = splitArr(abilityArr);
const splitItemArr = splitArr(itemArr);
const splitMoveArr = splitArr(moveArr);
const splitPokemonArr = splitArr(pokemonArr);
const splitPTypeArr = splitArr(pTypeArr);


const splitEffectArr = splitArr(effectArr);
const splitFieldStateArr = splitArr(fieldStateArr);
const splitNatureArr = splitArr(natureArr);
const splitStatArr = splitArr(statArr);
const splitStatusArr = splitArr(statusArr);
const splitUsageMethodArr = splitArr(usageMethodArr);

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
const descriptions = require(RAW_JSON_DATA_PATH + 'descriptions.json');
const { serializeDescriptions } = require('./utils/index.js');
let descriptionArr = serializeDescriptions(descriptions);
const lgpeOnlyMoveNames = lgpeOnlyMoves.map(data => data.name);
descriptionArr = descriptionArr.filter(data => data.description_class != 'move' || !lgpeOnlyMoveNames.includes(data.entity_name));


// Serialize simpler objects.
const versionGroups = require(RAW_JSON_DATA_PATH + 'versionGroups.json');

const { serializeVersionGroupDict } = require('./utils/index.js');

const versionGroupArr = serializeVersionGroupDict(versionGroups);

// #endregion

/* 6. Validate data. */
// #region

console.log('\nValidating data...\n');

console.log('Checking abilities...');
splitAbilityArr.map(data => {
  if (!data.name) console.log('Doesn\'t have a name!');

  if (isNaN(data.introduced)) console.log(`${data.name}: Debut gen ${data.introduced} is not a number.`);
});

console.log('Checking items...');
splitItemArr.map(data => {
  if (!data.name) console.log('Doesn\'t have a name!');

  if (isNaN(data.introduced)) console.log(`${data.name}: Debut gen ${data.introduced} is not a number.`);
});

console.log('Checking moves...');
splitMoveArr.map(data => {
  if (!data.name) console.log('Doesn\'t have a name!');

  if (isNaN(data.introduced)) console.log(`${data.name}: Debut gen ${data.introduced} is not a number.`);

  if (isNaN(data.power)) console.log(`${data.name}: Power ${data.power} is not a number.`);

  if (isNaN(data.pp)) console.log(`${data.name}: PP ${data.pp} is not a number.`);

  if (isNaN(data.accuracy)) console.log(`${data.name}: Accuracy ${data.accuracy} is not a number.`);

  if (['physical', 'special', 'status', 'varies'].indexOf(data.category) < 0) console.log(`${data.name}: ${data.category} is not a valid move category.`);

  if (['adjacent_ally', 'adjacent_foe', 'all_adjacent','all_adjacent_foes', 'all', 'all_allies', 'all_foes', 'any', 'any_adjacent', 'user', 'user_and_all_allies', 'user_or_adjacent_ally'].indexOf(data.target) < 0) console.log(`${data.name}: ${data.target} is not a valid move target class.`);

  if (!data.hasOwnProperty('removed_from_swsh')) console.log(`${data.name}: Doesn't have an removed_from_swsh flag.`);

  if (!data.hasOwnProperty('removed_from_bdsp')) console.log(`${data.name}: Doesn't have an removed_from_bdsp flag.`);
});

console.log('Checking Pokemon...');
splitPokemonArr.map(data => {
  if (!data.name) console.log('Doesn\'t have a name!');

  if (isNaN(data.introduced)) console.log(`${data.name}: Debut gen ${data.introduced} is not a number.`);

  if (isNaN(data.dex_number)) console.log(`${data.name}: Dex number ${data.dexNumber} is not a number.`);
  
  if (!data.species) console.log(`${data.name}: Doesn't have a species name.`);

  if (!data.form_class) console.log(`${data.name}: Doesn't have a form class.`);

  if (!data.ps_id) console.log(`${data.name}: Doesn't have a Pokemon Showdown ID.`)
  
  if (isNaN(data.height)) console.log(`${data.name}: Height ${data.weight} is not a number.`);

  if (isNaN(data.weight)) console.log(`${data.name}: Weight ${data.weight} is not a number.`);

  if (isNaN(data.hp)) console.log(`${data.name}: HP ${data.hp} is not a number.`);

  if (isNaN(data.attack)) console.log(`${data.name}: Attack ${data.attack} is not a number.`);

  if (isNaN(data.defense)) console.log(`${data.name}: Defense ${data.defense} is not a number.`);

  if (isNaN(data.special_attack)) console.log(`${data.name}: Special attack ${data.special_attack} is not a number.`);

  if (isNaN(data.special_defense)) console.log(`${data.name}: Special defense ${data.special_defense} is not a number.`);

  if (isNaN(data.speed)) console.log(`${data.name}: Speed ${data.speed} is not a number.`);
});

console.log('Checking types...');
splitPTypeArr.map(data => {
  if (!data.name) console.log('Doesn\'t have a name!');

  if (isNaN(data.introduced)) console.log(`${data.name}: Debut gen ${data.introduced} is not a number.`);
});

// #endregion

/* 7. Write arrays to .json files. */
// #region

const fs = require('fs');

// We get list of stats as well

console.log('\nSaving data...\n')

const { PROCESSED_DATA_PATH } = require('./utils/index.js');
const FILENAMES_AND_ARRAYS = [
  ['abilities.json', splitAbilityArr],
  ['items.json', splitItemArr],
  ['moves.json', splitMoveArr],
  ['pokemon.json', splitPokemonArr],
  ['pTypes.json', splitPTypeArr],
  ['descriptions.json', descriptionArr],
  ['effects.json', splitEffectArr],
  ['fieldStates.json', splitFieldStateArr],
  ['natures.json', splitNatureArr],
  ['stats.json', splitStatArr],
  ['statuses.json', splitStatusArr],
  ['usageMethods.json', splitUsageMethodArr],
  ['versionGroups.json', versionGroupArr],
];

FILENAMES_AND_ARRAYS.map(pair => {
  const [fname, arr] = pair;

  fs.writeFileSync(__dirname + PROCESSED_DATA_PATH + fname, JSON.stringify(arr), (err) => {
    if (err) {
      throw err;
    }
  });

  console.log(`Saved ${fname}.`);
});

// #endregion

module.exports = {
  splitAbilityArr,
  splitItemArr,
  splitMoveArr,
  splitPokemonArr,
  splitPTypeArr,
  descriptionArr,
  splitEffectArr,
  splitStatusArr,
  splitUsageMethodArr,
};

