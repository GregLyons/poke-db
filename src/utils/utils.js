// EXTENDING PATCH LISTS OF OBJECTS
// #region
const NUMBER_OF_GENS = 8;


// given a list of patches of the form [[..., gen_a], [..., gen_b], ...], fill in the gaps between and to the NUMBER_OF_GENS to get a complete list of values
// [[30, 3], [60, 6]] --> [[30, 3], [30, 4], [30, 5], [60, 6], [60, 7], [60, 8]]
const extendPatches = patches => {
  // patches is always an array of arrays, with the inner arrays having a number as their last entry, the gen number; ignore arrays which are not of this form
  if (typeof patches[0].slice(-1)[0] !== 'number') {
    return patches;
  }
  
  // dummy value added to the end to allow extending to the latest gen
  const [initialPatch, laterPatches] = [patches[0], patches.slice(1).concat([[null, NUMBER_OF_GENS + 1]])];

  return laterPatches.reduce((acc, curr) => {
    // find the latest previous patch (each pass can potentially add more than one patch) and get info on it
    const previousPatch = acc.slice(-1)[0];
    const [previousValues, previousGen] = [previousPatch.slice(0, -1), previousPatch.slice(-1)[0]];
    const currentGen = curr.slice(-1)[0];
    
    // fill in gap between previousGen and currentGen with previousValues
    for (let gen = previousGen + 1; gen < currentGen; gen++) {
      acc.push([...previousValues, gen]);
    }

    // add on currentPatch to be previousPatch in next iteration
    acc.push(curr);
    return acc;
  }, [initialPatch])
  // remove dummy value
  .slice(0, -1);
};

// given an entity dict, extend the patch lists for each of its entries; do so recursively when the entry is itself a dict containing patch lists
const extendPatchesOfDict = dict => {
  const extendedDict = {};
  for (let key of Object.keys(dict)) {
    if (Array.isArray(dict[key]) && Array.isArray(dict[key][0])) {
      extendedDict[key] = extendPatches(dict[key]);
    } else if (typeof dict[key] === 'object') {
      extendedDict[key] = extendPatchesOfDict(dict[key]);
    } else extendedDict[key] = dict[key];
  }
  return extendedDict;
};

// given an entity dict from one of the .json files, convert to an array of objects where each key in the dict gives 
export const serializeDict = dict => {
  return Object.keys(dict).reduce((acc, curr) => {
    acc.push({
      name: curr,
      ...extendPatchesOfDict(dict[curr]),
    });
    return acc;
  }, []);
};

//#endregion

// MOVE CLASSIFICATIONS
// #region

const getZMoves = moveArr => moveArr.filter(move => move.z_move).map(move => move.name);

const getStatusZMoves = moveArr => moveArr.filter(move => move.category[0][0] == 'status' && move.name.includes('z_')).map(move => move.name);

const getMaxMoves = moveArr => moveArr.filter(move => move.max_move).map(move => move.name);

const getGMaxMoves = moveArr => moveArr.filter(move => move.g_max_move).map(move => move.name);

export const getMovesOfClass = (moveArr, className) => {
  switch (className) {
    case 'z':
      return getZMoves(moveArr);
    case 'zstatus': 
      return getStatusZMoves(moveArr);
    case 'max':
      return getMaxMoves(moveArr);
    case 'gmax':
      return getGMaxMoves(moveArr);
    default:
      throw 'Not a valid move class!';
  }
}

// #endregion

// 
export const computePokemonLearnsetName = pokemonName => {
  // certain groups of Pokemon, like Deoxys and its forms, have their learnsets given only to the base form, but the other forms still have entries, e.g. deoxysattack, deoxysdefense, deoxysspeed are present, but have no learnsets
  // in this case, we assign them the learnset of their species/base form
  const formHasMissingLearnset = (pokemonName.includes('hoopa') || pokemonName.includes('deoxys') || pokemonName.includes('giratina') || pokemonName.includes('shaymin') || pokemonName.includes('tornadus') || pokemonName.includes('landorus') || pokemonName.includes('thundurus') || pokemonName.includes('keldeo') || pokemonName.includes('arceus') || pokemonName.includes('silvally'));

  if (pokemonName.includes('_mega') || pokemonName.includes('_primal')|| formHasMissingLearnset) 
  // primals, megas, and pokemon whose forms have missing learnsets
  {
    return pokemonName.split('_')[0];

  } 
  // gmax pokemon
  else if (pokemonName.includes('g_max_')) {
    // toxtricity amped
    if (pokemonName.includes('amped')) {
      return 'toxtricity';
    } else return pokemonName.split('_').slice(2).join('');

  } 
  // darmanitan 
  else if (pokemonName.includes('darmanitan')) {
    switch (pokemonName) {
      case 'darmanitan_standard':
      case 'darmanitan_zen':
        return 'darmanitan';
      case 'darmanitan_standard_galar':
      case 'darmanitan_zen_galar':
        return 'darmanitangalar';

      }

  } 
  // in PS, 'eeveestarter', not 'eeveepartner'
  else if (pokemonName === 'eevee_partner') {
    return 'eeveestarter';
  } 
  else return pokemonName.replaceAll('_', '')
}

// return pokemonMap, which sends Pokemon names to the corresponding name in learnsets, and inversePokemonMap, which sends a name in learnsets to all Pokemon names which are mapped to it
// inversePokemonMap thus returns an array, e.g. inversePokemonMap('deoxys') = ['deoxys_normal', 'deoxys_attack', 'deoxys_defense', 'deoxys_speed'] since only deoxys has a learnset in learnsets
export const getPokemonLearnsetMaps = (learnsets, pokemon) => {
  const pokemonMap = new Map(), inversePokemonMap = new Map();

  for (let pokemonName of Object.keys(pokemon)) {
    // make pokemonName match its entry in learnsets
    let learnsetPokemonName;
    if (!learnsets.hasOwnProperty(computePokemonLearnsetName(pokemonName))) {
      learnsetPokemonName = pokemonName.split('_')[0]
    } else {
      learnsetPokemonName = computePokemonLearnsetName(pokemonName);
    }

    // help debugging
    if (!learnsets.hasOwnProperty(learnsetPokemonName)) {
      throw `Name not found in learnsets: ${pokemonName}, ${learnsetPokemonName}.`
    }

    if (!pokemonMap.get(pokemonName)) {
      pokemonMap.set(pokemonName, learnsetPokemonName);
    } else {
      console.log(`${pokemonName} already in map.`)
    }
    if (!inversePokemonMap.get(learnsetPokemonName)) {
      inversePokemonMap.set(learnsetPokemonName, [pokemonName]);
    } else {
      inversePokemonMap.set(learnsetPokemonName, inversePokemonMap.get(learnsetPokemonName).concat(pokemonName));
    }

    // for debugging; checks whether we have pokemon without learnsets
    if (!learnsets[learnsetPokemonName].learnset) {
      console.log(`${pokemonName}, ${learnsetPokemonName} has no learnset.`);
    }
  }

  return {pokemonMap, inversePokemonMap};
}

export const getMoveLearnsetMaps = (learnsets, moves) => {
  const moveMap = new Map(), inverseMoveMap = new Map();

  let learnsetMoveNameSet = new Set(); 
  for (let learnsetPokemonName of Object.keys(learnsets)) {
    if (learnsets[learnsetPokemonName].learnset) {
      for (let learnsetMoveName of Object.keys(learnsets[learnsetPokemonName].learnset)) {
        learnsetMoveNameSet.add(learnsetMoveName);
      }
    }
  }

  for (let moveName of Object.keys(moves)) {
    let learnsetMoveName;
    if (!learnsetMoveNameSet.has(moveName.replaceAll('_', ''))) {
      if (moveName.includes('z_')) {
        learnsetMoveName = moveName.split('_').slice(1).join('');
      }
    } else {
      learnsetMoveName = moveName.replaceAll('_', '');
    }
  
    if (!learnsetMoveNameSet.has(learnsetMoveName)) {
      console.log(`${moveName} unhandled.`);
    }
  }

  return learnsetMoveNameSet;
}