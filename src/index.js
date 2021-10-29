import abilities from '../src/data/json/abilities.json';
import effects from '../src/data/json/effects.json';
import elementalTypes from '../src/data/json/elementalTypes.json';
import items from '../src/data/json/items.json'
import moves from '../src/data/json/moves.json';
import pokemon from '../src/data/json/pokemon.json';
import statuses from '../src/data/json/statuses.json';
import usageMethods from '../src/data/json/usageMethods.json';
import learnsets from '../src/data/learnsets.js';
import { serializeDict, getMovesOfClass, computePokemonLearnsetName, getPokemonLearnsetMaps, getMoveLearnsetMaps } from './utils/utils.js';

const abilityArr = serializeDict(abilities);
const effectArr = serializeDict(effects);
const elTypeArr = serializeDict(elementalTypes);
const itemArr = serializeDict(items);
const moveArr = serializeDict(moves);
const pokemonArr = serializeDict(pokemon);
const statusArr = serializeDict(statuses);
const usageMethodArr = serializeDict(usageMethods);

const {pokemonMap, inversePokemonMap} = getPokemonLearnsetMaps(learnsets, pokemon);

getMoveLearnsetMaps(learnsets, moves);

// console.log(pokemonMap.get('deoxys_attack'));
// console.log(inversePokemonMap.get('deoxys'));



// console.log(moveSet);