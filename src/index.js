import abilities from '../src/data/json/abilities.json';
import effects from '../src/data/json/effects.json';
import elementalTypes from '../src/data/json/elementalTypes.json';
import items from '../src/data/json/items.json'
import moves from '../src/data/json/moves.json';
import pokemon from '../src/data/json/pokemon.json';
import statuses from '../src/data/json/statuses.json';
import usageMethods from '../src/data/json/usageMethods.json';
import learnsets from '../src/data/learnsets.js';
import { serializeDict, getMovesOfClass, computePokemonLearnsetName, getPokemonLearnsetMaps, getUpdatedLearnsets} from './utils/utils.js';

const abilityArr = serializeDict(abilities);
const effectArr = serializeDict(effects);
const elTypeArr = serializeDict(elementalTypes);
const itemArr = serializeDict(items);
const moveArr = serializeDict(moves);
const pokemonArr = serializeDict(pokemon);
const statusArr = serializeDict(statuses);
const usageMethodArr = serializeDict(usageMethods);

const addLearnsetsToPokemonArr = (pokemonArr) => {
  // pokemonMap: pokemonName --> learnsetPokemonName
  // inversePokemonName: learnsetPokemonName --> pokemonName[]
  // the latter returns an array since for some Pokemon with multiple forms, learnsets puts the learnset on only one of the forms; e.g.inversePokemonName('deoxys') returns the names for all of Deoxys's forms
  const {pokemonMap, inversePokemonMap} = getPokemonLearnsetMaps(learnsets, pokemon);
  
  const {updatedLearnsets, moveMap, inverseMoveMap} = getUpdatedLearnsets(learnsets, moves, pokemon);
  
  
  for (let pokemonEntry of pokemonArr) {
    const pokemonName = pokemonEntry.name;
    
    // each deoxys form receives the learnset for 'deoxys'
    const pokemonForms = inversePokemonMap.get(pokemonMap.get(pokemonName));
    for (let formName of pokemonForms) {
      pokemonEntry['learnset'] = updatedLearnsets[pokemonMap.get(formName)].learnset;
    }
  }
}

addLearnsetsToPokemonArr(pokemonArr);
console.log(pokemon['bulbasaur']);
console.log(pokemonArr[1]);

// console.log(pokemonMap.get('deoxys_attack'));
// console.log(inversePokemonMap.get('deoxys'));


// console.log(moveMap.get('tearful_look'));
// console.log(moveMap.get('z_tearful_look'));
// console.log(inverseMoveMap.get('tearfullook'));



// console.log(moveSet);