import abilities from '../src/data/json/abilities.json';
import effects from '../src/data/json/effects.json';
import elementalTypes from '../src/data/json/elementalTypes.json';
import items from '../src/data/json/items.json'
import moves from '../src/data/json/moves.json';
import pokemon from '../src/data/json/pokemon.json';
import statuses from '../src/data/json/statuses.json';
import usageMethods from '../src/data/json/usageMethods.json';

const NUMBER_OF_GENS = 8;
const patches = [[80, 1], [90, 6]]

const extendPatches = patches => {
  let extendedPatchList = [];
  for (let patch of patches) {
    const patchGen = patch[-1];

    while (extendPatchList.length > 1 && extendedPatchList[-1][-1] < patchGen) {
      console.log(patchGen);
      patchGen++;
    }

    extendedPatchList.push(patch);
  }
  return extendedPatchList
}
console.log(extendPatches(patches));