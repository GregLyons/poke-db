import abilities from '../src/data/json/abilities.json';
import effects from '../src/data/json/effects.json';
import elementalTypes from '../src/data/json/elementalTypes.json';
import items from '../src/data/json/items.json'
import moves from '../src/data/json/moves.json';
import pokemon from '../src/data/json/pokemon.json';
import statuses from '../src/data/json/statuses.json';
import usageMethods from '../src/data/json/usageMethods.json';
import learnsets from '../src/data/learnsets.js';
import { serializeDict, getMovesOfClass, computePokemonLearnsetName, getPokemonLearnsetMaps, getParsedLearnsets } from './utils/utils.js';

const abilityArr = serializeDict(abilities);
const effectArr = serializeDict(effects);
const elTypeArr = serializeDict(elementalTypes);
const itemArr = serializeDict(items);
const moveArr = serializeDict(moves);
const pokemonArr = serializeDict(pokemon);
const statusArr = serializeDict(statuses);
const usageMethodArr = serializeDict(usageMethods);


const {parsedLearnsets, moveMap, inverseMoveMap} = getParsedLearnsets(learnsets, moves, pokemon);



// console.log(pokemonMap.get('deoxys_attack'));
// console.log(inversePokemonMap.get('deoxys'));


// console.log(moveMap.get('tearful_look'));
// console.log(moveMap.get('z_tearful_look'));
// console.log(inverseMoveMap.get('tearfullook'));



// console.log(moveSet);