import abilities from '../../data/json/abilities.json';
import effects from '../../data/json/effects.json';
import elementalTypes from '../../data/json/elementalTypes.json';
import items from '../../data/json/items.json'
import moves from '../../data/json/moves.json';
import pokemon from '../../data/json/pokemon.json';
import statuses from '../../data/json/statuses.json';
import usageMethods from '../../data/json/usageMethods.json';
import learnsets from '../../data/learnsets.js';
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