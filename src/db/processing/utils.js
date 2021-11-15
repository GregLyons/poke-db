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

// export const getMovesOfClass = (moveArr, className) => {
//   switch (className) {
//     case 'z':
//       return getZMoves(moveArr);
//     case 'zstatus': 
//       return getStatusZMoves(moveArr);
//     case 'max':
//       return getMaxMoves(moveArr);
//     case 'gmax':
//       return getGMaxMoves(moveArr);
//     default:
//       throw 'Not a valid move class!';
//   }
// }

// #endregion

// ADD LEARNSET DATA
// #region

// pokemonName --> corresponding Pokemon in learnset with learnset data
// e.g. deoxysattack doesn't have learnset data, so deoxys_attack is mapped to deoxys instead
const computePokemonLearnsetName = pokemonName => {
  // certain groups of Pokemon, like Deoxys and its forms, have their learnsets given only to the base form, but the other forms still have entries, e.g. deoxysattack, deoxysdefense, deoxysspeed are present, but have no learnsets
  // in this case, we assign them the learnset of their species/base form
  const formHasMissingLearnset = (pokemonName.includes('hoopa') || pokemonName.includes('deoxys') || pokemonName.includes('giratina') || pokemonName.includes('shaymin') || pokemonName.includes('tornadus') || pokemonName.includes('landorus') || pokemonName.includes('thundurus') || pokemonName.includes('keldeo') || pokemonName.includes('arceus') || pokemonName.includes('silvally'));

  if (pokemonName.includes('_mega') || pokemonName.includes('_primal') || formHasMissingLearnset) 
  // primals, megas, and pokemon whose forms have missing learnsets
  {
    return pokemonName.split('_')[0];

  } 
  // gmax pokemon
  else if (pokemonName.includes('_gmax')) {
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

  // lycanroc midday taken as default form in PS data
  else if (pokemonName === 'lycanroc_midday') {
    return 'lycanroc';
  }

  else return pokemonName.replaceAll('_', '')
}

// return pokemonMap, which sends Pokemon names to the corresponding name in learnsets, and inversePokemonMap, which sends a name in learnsets to all Pokemon names which are mapped to it
// inversePokemonMap thus returns an array, e.g. inversePokemonMap('deoxys') = ['deoxys_normal', 'deoxys_attack', 'deoxys_defense', 'deoxys_speed'] since only deoxys has a learnset in learnsets
const getPokemonLearnsetMaps = (learnsets, pokemon) => {
  const pokemonMap = new Map(), inversePokemonMap = new Map();

  for (let pokemonName of Object.keys(pokemon)) {
    // ignore cosmetic forms
    if (pokemon[pokemonName].cosmetic) {
      continue;
    }

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

// adds Z-moves, max moves, etc. to learnsets and returns updatedLearnsets
// also returns moveMap and inverseMoveMap for going between moveNames and move names in the learnsets
const getUpdatedLearnsets = (learnsets, moves, pokemon) => {
  // learnsets shouldn't have dates, functions, undefined, regexp, or infinity 
  let updatedLearnsets = JSON.parse(JSON.stringify(learnsets));
  
  // moveMap: moveName --> learnsetMoveName
  // inverseMoveMap: learnsetMoveName --> moveName
  const moveMap = new Map(), inverseMoveMap = new Map();

  // keep track of moves and learnset moves handled
  let moveNameSet = new Set(), learnsetMoveNameSet = new Set();
  // do a pass through the learnset data to add all the learnset move names to learnsetMoveNameSet

  // pokemonWhoLearnMoveMap: learnsetMoveName --> learnsetPokemonName[]
  const pokemonWhoLearnMoveMap = new Map();
  for (let learnsetPokemonName of Object.keys(updatedLearnsets)) {
    // for many Pokemon forms, the learnset data omits the learnset
    if (!updatedLearnsets[learnsetPokemonName].learnset) {
      continue
    }
    for (let learnsetMoveName of Object.keys(updatedLearnsets[learnsetPokemonName].learnset)) {

      // if learnsetMoveName has not been seen before, learnsetPokemonName is the first Pokemon to learn this move
      if (!pokemonWhoLearnMoveMap.has(learnsetMoveName)) {
        pokemonWhoLearnMoveMap.set(learnsetMoveName, [learnsetPokemonName]);
      } 
      // learnsetMoveName has been seen before on another Pokemon; add learnsetPokemonName to the list
      else {
        pokemonWhoLearnMoveMap.set(learnsetMoveName, pokemonWhoLearnMoveMap.get(learnsetMoveName).concat(learnsetPokemonName));
      }
      learnsetMoveNameSet.add(learnsetMoveName)
    }
  }
  // add all the moves which are already in learnsetMoveNameSet upon removing the underscores
  for (let moveName of Object.keys(moves)) {
    if (learnsetMoveNameSet.has(moveName.replaceAll('_' ,''))) {
      moveNameSet.add(moveName);
      // add moveName to moveMap and add its inverse to inverseMoveMap
      moveMap.set(moveName, moveName.replaceAll('_', ''));
      inverseMoveMap.set(moveName.replaceAll('_', ''), moveName);
    }
  }

  // pokemonMap: pokemonName --> learnsetPokemonName 
  // inversePokemonMap: learnsetPokemonName --> pokemkonName[] (recall that multiple Pokemon forms may be mapped to the same learnset Pokemon)
  const {pokemonMap, inversePokemonMap} = getPokemonLearnsetMaps(updatedLearnsets, pokemon)
  // need to convert moves to an array to use getStatusZMoves
  const moveArr = serializeDict(moves);

  // handle status Z-moves 
  for (let moveName of getStatusZMoves(moveArr)) {
    // for potential debugging
    if (moveMap.has(moveName.replaceAll('_', ''))) {
      console.log(`WARNING: moveMap already has ${moveName}, moving on...`);
    }

    // add data to moveMap and inverseMoveMap
    // update learnsets with status Z-move for Pokemon who learn the base move
    else {
      moveNameSet.add(moveName);

      const learnsetMoveName = moveName.replaceAll('_', '');
      moveMap.set(moveName, learnsetMoveName);
      inverseMoveMap.set(learnsetMoveName, moveName);
      
      // update learnsets so that Pokemon who learn the base move can also learn the corresponding Z-move
      // get base move for moveName 
      const learnsetBaseMoveName = moveMap.get(moves[moveName].requirements.move);
      for (let learnsetPokemonName of pokemonWhoLearnMoveMap
        .get(learnsetBaseMoveName)
        // filter out Pokemon introduced after gen 7, or who did not learn the base move in gen 7
        .filter(learnsetPokemonName => {
          // pokemon introduced after gen 7
          if (!inversePokemonMap.get(learnsetPokemonName) || inversePokemonMap.get(learnsetPokemonName)[0].gen > 7) {
            return false;
          } 
          // didn't learn base move in gen 7
          else {
            // learnData is a string containing the gen number and learn method for the move, one string per generation of move's presence 
            for (let learnData of updatedLearnsets[learnsetPokemonName].learnset[learnsetBaseMoveName]) {
              // gen number is first character of learnData
              if (learnData[0] == 7) {
                // Pokemon learned move in gen 7
                return true;
              }
            }
            // Pokemon didn't learn move in gen 7
            return false;
          }
        })
      ) {
        // the learnData for the Z-move is the same as for the base move; extract the Gen 7 learn data for that move/pokemon
        updatedLearnsets[learnsetPokemonName].learnset[learnsetMoveName] = ['7B'];
      }
    }
  }

  // handle generic and Pokemon specific Z-moves, Max moves, and G-Max moves
  for (let moveName of getZMoves(moveArr).concat(getMaxMoves(moveArr).concat(getGMaxMoves(moveArr)))) {
    // Z-status moves have already been handled
    if (moveNameSet.has(moveName)) {
      continue;
    }
    
    // add data to the move maps
    moveNameSet.add(moveName);
    
    // when moveName was introduced
    const moveGen = moves[moveName].gen;
    
    const learnsetMoveName = moveName.replaceAll('_', '');
    moveMap.set(moveName, learnsetMoveName);
    inverseMoveMap.set(learnsetMoveName, moveName);
    
    // indicates move is Pokemon specific; in this case, it definitely learns the move
    if (moves[moveName].requirements.hasOwnProperty('pokemon')) {
      for (let pokemonName of moves[moveName].requirements.pokemon) {
        let learnsetPokemonName = pokemonMap.get(pokemonName);
        // Z-moves or max moves are exclusive to their generation
        // learnData is the gen + 'S' for 'Special'
        updatedLearnsets[learnsetPokemonName].learnset[learnsetMoveName] = [moveGen + 'B'];
      }
    } 
    // indicates move depends on the type of the base move; non-Pokemon specific Z-moves, max moves, and gmax moves
    else if (moves[moveName].requirements.hasOwnProperty('type')) {
      const elType = moves[moveName].type[0][0];

      // if a Pokemon learns a damaging move of type elType in moveGen, then it knows the corresponding Z-move
      for (let moveOfElType of moveArr
        // get moves whose type in gen moveGen was elType; will exclude moves later than moveGen
        .filter(move => {
          const moveType = (move.type.filter(patch => patch[1] === moveGen));
          return moveType.length && (moveType[0][0] === elType);
        })
        // get moves which are damaging, i.e. not status
        .filter(move => {
          const moveCategory = (move.category.filter(patch => patch[1] === moveGen));
          return moveCategory.length && (moveCategory[0][0] !== 'status');
        })
      )
      {
        const moveOfElTypeName = moveOfElType.name;
        const learnsetMoveOfElTypeName = moveMap.get(moveOfElTypeName);
        if (!learnsetMoveOfElTypeName) {
          continue;
        }

        const learnsetPokemonNames = pokemonWhoLearnMoveMap.get(learnsetMoveOfElTypeName);

        if (!learnsetPokemonNames) {
          continue;
        }

        for (let learnsetPokemonName of learnsetPokemonNames) {
          if (!updatedLearnsets[learnsetPokemonName].learnset[learnsetMoveName]) {
            updatedLearnsets[learnsetPokemonName].learnset[learnsetMoveName] = [moveGen + 'B'];
          } else {
            continue;
          }
        }
      }
    // every Pokemon can learn max guard since every Pokemon can learn a status move
    } else if (moveName == 'max_guard') {
      for (let learnsetPokemonName of Object.keys(updatedLearnsets)) {
        // for many Pokemon forms, the learnset data omits the learnset
        if (!updatedLearnsets[learnsetPokemonName].learnset) {
          continue
        }
        else {
          updatedLearnsets[learnsetPokemonName].learnset['maxguard'] = [8 + 'B'];
        }
      }
    }
    else {
      console.log(`Move name ${moveName} unhandled.`);
    }
  }

  for (let moveName of Object.keys(moves)) {
    // ignore struggle, since Pokemon don't literally 'learn' struggle
    if (!moveNameSet.has(moveName) && moveName !== 'struggle') {
      console.log(`Move name ${moveName} unhandled`);
    }
  }

  return {updatedLearnsets, moveMap, inverseMoveMap};
}

// adds learnset data to pokemonArr
export const addLearnsetsToPokemonArr = (learnsets, moves, pokemon, pokemonArr) => {
  // pokemonMap: pokemonName --> learnsetPokemonName
  // inversePokemonName: learnsetPokemonName --> pokemonName[]
  // the latter returns an array since for some Pokemon with multiple forms, learnsets puts the learnset on only one of the forms; e.g.inversePokemonName('deoxys') returns the names for all of Deoxys's forms
  const {pokemonMap, inversePokemonMap} = getPokemonLearnsetMaps(learnsets, pokemon);
  
  const {updatedLearnsets, moveMap, inverseMoveMap} = getUpdatedLearnsets(learnsets, moves, pokemon);
  
  for (let pokemonEntry of pokemonArr) {
    // ignore cosmetic forms
    if (pokemonEntry.cosmetic) {
      continue;
    }

    const pokemonName = pokemonEntry.name;
    
    pokemonEntry['learnset'] = {};

    // add learnset data
    for (let learnsetMoveName of Object.keys(updatedLearnsets[pokemonMap.get(pokemonName)].learnset)) {
      const moveName = inverseMoveMap.get(learnsetMoveName);
      pokemonEntry.learnset[moveName] = updatedLearnsets[pokemonMap.get(pokemonName)].learnset[learnsetMoveName];
    }

    // add event data
    let pokemonEventData = [];
    if (updatedLearnsets[pokemonMap.get(pokemonName)].eventData) {
      for (let eventDatum of updatedLearnsets[pokemonMap.get(pokemonName)].eventData) {
        const {generation, level, gender, nature, shiny, isHidden, perfectIVs, moves: learnsetMoveNames, pokeball} = eventDatum;
        let moveNames = [];
        for (let learnsetMoveName of learnsetMoveNames) {
          moveNames.push(inverseMoveMap.get(learnsetMoveName));
        }
        pokemonEventData.push({generation, level, gender, nature, shiny, isHidden, moveNames, perfectIVs, pokeball});
      }
    }
    pokemonEntry['eventData'] = pokemonEventData;
  }
}
// #endregion