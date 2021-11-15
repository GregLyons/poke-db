import abilities from '../../raw_data/json/abilities.json';
import effects from '../../raw_data/json/effects.json';
import elementalTypes from '../../raw_data/json/elementalTypes.json';
import items from '../../raw_data/json/items.json'
import moves from '../../raw_data/json/moves.json';
import pokemon from '../../raw_data/json/pokemon.json';
import statuses from '../../raw_data/json/statuses.json';
import usageMethods from '../../raw_data/json/usageMethods.json';
import learnsets from '../../raw_data/learnsets.js';
import { serializeDict, addLearnsetsToPokemonArr} from './utils.js';

const abilityArr = serializeDict(abilities);
const effectArr = serializeDict(effects);
const elTypeArr = serializeDict(elementalTypes);
const itemArr = serializeDict(items);
const moveArr = serializeDict(moves);
const pokemonArr = serializeDict(pokemon);
const statusArr = serializeDict(statuses);
const usageMethodArr = serializeDict(usageMethods);

addLearnsetsToPokemonArr(learnsets, moves, pokemon, pokemonArr);
