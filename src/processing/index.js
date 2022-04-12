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

5. Add 'formattedPSIDs': these are names of the entities in PokemonShowdown, which are necessary for using, e.g. @smogon/calc ('ps_id' doesn't suffice).

6. Import descriptions.json, effects.json, stats.json, statuses.json, usageMethods.json, and versionGroups.json, and serialize them. Aside from descriptions.json, these objects are much simpler in that they don't change across games (at least, the data--name and debut gen--we're tracking for them doesn't change), so we use a simplified version of serializeDict.

7. Write arrays to .json files.

8. Valid data for insertion (e.g. check for numbers in numeric fields, defined values in non-nullable fields, etc.).
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
const { mergeGen2Learnsets } = require('./utils/index.js');
const { mergeBDSPLearnsets } = require('./utils/index.js');
const gen2Learnsets = require(RAW_DATA_PATH + 'learnsets/gen2learnsets.js');
const laterLearnsets = require(RAW_DATA_PATH + 'learnsets/learnsets.js');
const bdspLearnsets = require(RAW_DATA_PATH + 'learnsets/bdsplearnsets.js');
const swshLearnsets = mergeGen2Learnsets(gen2Learnsets, laterLearnsets);
const learnsets = mergeBDSPLearnsets(swshLearnsets, bdspLearnsets);

// for (let [pokemonName, learnData] of Object.entries(learnsets)) {
//   if (!learnData.learnset) {
//     console.log(pokemonName);
//     console.log('No learn data');
//   }
//   else if (Object.keys(learnData.learnset).length < 5) {
//     console.log(pokemonName);
//   }
// }

// weedle
// ditto
// unown
// pikachurockstar
// pikachubelle
// pikachupopstar
// pikachuphd
// pikachulibre
// deoxysattack
// No learn data
// deoxysdefense
// No learn data
// deoxysspeed
// No learn data
// gastrodoneast
// rotomheat
// rotomwash
// rotomfrost
// rotomfan
// rotommow
// giratinaorigin
// No learn data
// shayminsky
// No learn data
// arceusbug
// No learn data
// arceusdark
// No learn data
// arceusdragon
// No learn data
// arceuselectric
// No learn data
// arceusfairy
// No learn data
// arceusfighting
// No learn data
// arceusfire
// No learn data
// arceusflying
// No learn data
// arceusghost
// No learn data
// arceusgrass
// No learn data
// arceusground
// No learn data
// arceusice
// No learn data
// arceuspoison
// No learn data
// arceuspsychic
// No learn data
// arceusrock
// No learn data
// arceussteel
// No learn data
// arceuswater
// No learn data
// tornadustherian
// No learn data
// thundurustherian
// No learn data
// landorustherian
// No learn data
// keldeoresolute
// No learn data
// genesectburn
// No learn data
// genesectchill
// No learn data
// genesectdouse
// No learn data
// genesectshock
// No learn data
// pumpkaboosuper
// hoopaunbound
// No learn data
// cosmog
// cosmoem
// necrozmaduskmane
// necrozmadawnwings
// necrozmaultra
// zaciancrowned
// zamazentacrowned
// flarelm
// rebble
// tactite
// privatyke
// monohm
// duohm
// protowatt

// #endregion

/* 3. Add merged learnset data. Separate out LGPE-only Pokemon. Also adds Pokemon Showdown IDs, 'ps_id'. */
// #region

const { pokemon: psIDs, } = require(RAW_DATA_PATH + 'ps-img.json');
const { addLearnsetsToPokemonArr, addLearnDataToEvolutions, addPokemonShowdownIDToPokemonArr, } = require('./utils/index.js');
const evolutionLearnsetMap = addLearnsetsToPokemonArr(learnsets, moves, pokemon, pokemonArr);
// In the PS learnset data, some evolutions are listed as not being able to learn moves, even when their prevolutions can learn those moves. In such a case, we add an 'EV' flag to the move in question for the evolution's learnset data. 
// To improve performance and reduce space in the database, we do not add an 'EV' flag to every move learned by a prevolution in an evolution's learnset data, as this would nearly double the learnset data in the database, which already comprises the bulk of the data stored.
addLearnDataToEvolutions(evolutionLearnsetMap, pokemonArr);
addPokemonShowdownIDToPokemonArr(psIDs, pokemonArr);

for (let pokemon of pokemonArr) {
  const { gen, name, learnset } = pokemon;

  if (name.includes('unown')) continue;
  else if (['cosmog', 'cosmoem', 'ditto', 'blipbug'].includes(name)) continue;

  if (Object.keys(learnset).length < 10) {
    console.log(gen, name);
  }
}


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

// For moves which cannot miss, replace accuracy with "null"; same with moves whose power varies
for (let move of splitMoveArr) {
  if (move.effects.cannot_miss) {
    move.accuracy = null;
  }
  if (move.effects.variable_power || move.effects.deals_direct_damage) {
    move.power = null;
  }
}

const splitEffectArr = splitArr(effectArr);
const splitFieldStateArr = splitArr(fieldStateArr);
const splitNatureArr = splitArr(natureArr);
const splitStatArr = splitArr(statArr);
const splitStatusArr = splitArr(statusArr);
const splitUsageMethodArr = splitArr(usageMethodArr);

// #endregion

/* 5. Add formatted psIDs to Pokemon, and add psIDs to other entities (abilities, items, moves). */
// #region

const {
  addPSIDs_ability,
  addPSIDs_item,
  addPSIDs_move,
  addPSIDs_pokemon,
} = require('./utils/index.js');

// Abilities 
// #region

const { SS_ability, } = require('../data/raw_data/formatted-psids/abilities.js');
addPSIDs_ability(splitAbilityArr, SS_ability);

// #endregion

// Items 
// #region

const { GSC_ONLY_item, MEGA_STONES_item, SS_item, } = require('../data/raw_data/formatted-psids/items.js');
addPSIDs_item(splitItemArr, [...GSC_ONLY_item, ...Object.keys(MEGA_STONES_item), ...SS_item]);

// #endregion

// Moves
// #region

const { 
  RBY_move, 
  GSC_PATCH_move,
  ADV_PATCH_move,
  DPP_PATCH_move,
  BW_PATCH_move,
  XY_PATCH_move,
  SM_PATCH_move,
  SS_PATCH_move,
} = require('../data/raw_data/formatted-psids/moves.js');

addPSIDs_move(splitMoveArr, {
  1: Object.keys(RBY_move),
  2: Object.keys(GSC_PATCH_move),
  3: Object.keys(ADV_PATCH_move),
  4: Object.keys(DPP_PATCH_move),
  5: Object.keys(BW_PATCH_move),
  6: Object.keys(XY_PATCH_move),
  7: Object.keys(SM_PATCH_move),
  8: Object.keys(SS_PATCH_move),
});

// #endregion

// Pokemon
// #region

const { 
  RBY_pokemon, 
  GSC_PATCH_pokemon,
  ADV_PATCH_pokemon,
  DPP_PATCH_pokemon,
  BW_PATCH_pokemon,
  XY_PATCH_pokemon,
  SM_PATCH_pokemon,
  SS_PATCH_pokemon,
} = require('../data/raw_data/formatted-psids/pokemon.js');

addPSIDs_pokemon(splitPokemonArr, {
  1: Object.keys(RBY_pokemon),
  2: Object.keys(GSC_PATCH_pokemon),
  3: Object.keys(ADV_PATCH_pokemon),
  4: Object.keys(DPP_PATCH_pokemon),
  5: Object.keys(BW_PATCH_pokemon),
  6: Object.keys(XY_PATCH_pokemon),
  7: Object.keys(SM_PATCH_pokemon),
  8: Object.keys(SS_PATCH_pokemon),
});


// #endregion

// #endregion

/* 6. Serialize descriptions and other simple objects. */
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

/* 7. Validate data. */
// #region

console.log('\nValidating data...\n');

console.log('Checking abilities...');
splitAbilityArr.map(data => {
  if (!data.name) console.log('Doesn\'t have a name!');

  if (isNaN(data.introduced)) console.log(`${data.name}: Debut gen ${data.introduced} is not a number.`);

  if (!data.ps_id) console.log(`${data.name}: Doesn't have a Pokemon Showdown ID.`);

  if (!data.formatted_ps_id) console.log(`${data.name}: Doesn't have a formatted Pokemon Showdown ID.`);
});

console.log('Checking items...');
splitItemArr.map(data => {
  if (!data.name) console.log('Doesn\'t have a name!');

  if (isNaN(data.introduced)) console.log(`${data.name}: Debut gen ${data.introduced} is not a number.`);

  if (!data.ps_id) console.log(`${data.name}: Doesn't have a Pokemon Showdown ID.`);

  if (!data.formatted_ps_id) console.log(`${data.name}: Doesn't have a formatted Pokemon Showdown ID.`);
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

  if (!data.ps_id) console.log(`${data.name}: Doesn't have a Pokemon Showdown ID.`);

  if (!data.formatted_ps_id) console.log(`${data.name}: Doesn't have a formatted Pokemon Showdown ID.`);
});

console.log('Checking Pokemon...');
splitPokemonArr.map(data => {
  if (!data.name) console.log('Doesn\'t have a name!');

  if (isNaN(data.introduced)) console.log(`${data.name}: Debut gen ${data.introduced} is not a number.`);

  if (isNaN(data.dex_number)) console.log(`${data.name}: Dex number ${data.dexNumber} is not a number.`);
  
  if (!data.species) console.log(`${data.name}: Doesn't have a species name.`);

  if (!data.form_class) console.log(`${data.name}: Doesn't have a form class.`);

  if (!data.ps_id) console.log(`${data.name}: Doesn't have a Pokemon Showdown ID.`);

  if (!data.formatted_ps_id) console.log(`${data.name}: Doesn't have a formatted Pokemon Showdown ID.`);
  
  if (isNaN(data.height)) console.log(`${data.name}: Height ${data.weight} is not a number.`);

  if (isNaN(data.weight)) console.log(`${data.name}: Weight ${data.weight} is not a number.`);

  if (isNaN(data.hp)) console.log(`${data.name}: HP ${data.hp} is not a number.`);

  if (isNaN(data.attack)) console.log(`${data.name}: Attack ${data.attack} is not a number.`);

  if (isNaN(data.defense)) console.log(`${data.name}: Defense ${data.defense} is not a number.`);

  if (isNaN(data.special_attack)) console.log(`${data.name}: Special attack ${data.special_attack} is not a number.`);

  if (isNaN(data.special_defense)) console.log(`${data.name}: Special defense ${data.special_defense} is not a number.`);

  if (isNaN(data.speed)) console.log(`${data.name}: Speed ${data.speed} is not a number.`);

  if (isNaN(data.male_rate)) console.log(`${data.name}: Male rate ${data.male_rate} is not a number.`);

  if (isNaN(data.female_rate)) console.log(`${data.name}: Female rate ${data.female_rate} is not a number.`);

  if (!data.hasOwnProperty('genderless')) console.log(`${data.name}: Missing 'genderless' flag.`)
});

console.log('Checking types...');
splitPTypeArr.map(data => {
  if (!data.name) console.log('Doesn\'t have a name!');

  if (isNaN(data.introduced)) console.log(`${data.name}: Debut gen ${data.introduced} is not a number.`);
});

// #endregion

/* 8. Write arrays to .json files. */
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

  // console.log(`Saved ${fname}.`);
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

