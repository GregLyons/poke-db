const { replaceAll } = require('./helpers.js');

// MERGE GEN 2 LEARNSETS WITH LATER LEARNSETS
// #region

// Given learnset objects from separate periods, combine them into a single learnset object
const mergeLearnsets = (gen2Learnsets, gen3OnwardsLearnsets) => {
  let mergedLearnsets = {};
  let earlierLearnsets = JSON.parse(JSON.stringify(gen2Learnsets));
  let laterLearnsets = JSON.parse(JSON.stringify(gen3OnwardsLearnsets));

  // add data from earlierLearnsets 
  for (let learnsetPokemonName of Object.keys(earlierLearnsets)) {
    mergedLearnsets[learnsetPokemonName] = {};
    mergedLearnsets[learnsetPokemonName].learnset = earlierLearnsets[learnsetPokemonName].learnset;
    mergedLearnsets[learnsetPokemonName].event_data = earlierLearnsets[learnsetPokemonName].eventData;
  }
  
  // add data from laterLearnsets
  for (let learnsetPokemonName of Object.keys(laterLearnsets)) {
    // if learnsetPokemonName is in earlierLearnset, we need to append new data to old data
    if (mergedLearnsets[learnsetPokemonName]) {
      // concatenate learnset data
      for (let learnsetMoveName of Object.keys(laterLearnsets[learnsetPokemonName].learnset)) {
        // if move has data from gen 2, concatenate with new data
        if (mergedLearnsets[learnsetPokemonName].learnset[learnsetMoveName]) {
          mergedLearnsets[learnsetPokemonName].learnset[learnsetMoveName] = mergedLearnsets[learnsetPokemonName].learnset[learnsetMoveName].concat(laterLearnsets[learnsetPokemonName].learnset[learnsetMoveName]); 
        }
        // otherwise, no gen 2 data to conatenate
        else {
          mergedLearnsets[learnsetPokemonName].learnset[learnsetMoveName] = laterLearnsets[learnsetPokemonName].learnset[learnsetMoveName]; 
        }
      }
      // concatenate event data
      // event data present from earlier period AND in later period (Fearow only has event data in earlier period)
      if (mergedLearnsets[learnsetPokemonName].event_data && laterLearnsets[learnsetPokemonName].eventData) {
        mergedLearnsets[learnsetPokemonName].event_data = mergedLearnsets[learnsetPokemonName].event_data.concat(laterLearnsets[learnsetPokemonName].eventData); 
      }
      // event data from later period, but not earlier period
      else if (laterLearnsets[learnsetPokemonName].eventData) {
        mergedLearnsets[learnsetPokemonName].event_data = laterLearnsets[learnsetPokemonName].eventData;
      }
      // case of event data only in earlier period needs no treatment, since that data is already in mergedLearnsets
    }
    // Pokemon is not present in earlierLearnset, so no need to merge data
    else {
      mergedLearnsets[learnsetPokemonName] = {};
      mergedLearnsets[learnsetPokemonName].learnset = laterLearnsets[learnsetPokemonName].learnset;
      mergedLearnsets[learnsetPokemonName].event_data = laterLearnsets[learnsetPokemonName].eventData;
    }
  }

  return mergedLearnsets;
}
// #endregion

// ADD LEARNSET AND EVENT DATA
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

  else return replaceAll(pokemonName, '_', '')
}

// return pokemonMap, which sends Pokemon names to the corresponding name in learnsets, and inversePokemonMap, which sends a name in learnsets to all Pokemon names which are mapped to it
// inversePokemonMap thus returns an array, e.g. inversePokemonMap('deoxys') = ['deoxys_normal', 'deoxys_attack', 'deoxys_defense', 'deoxys_speed'] since only deoxys has a learnset in learnsets
const getPokemonLearnsetMaps = (learnsets, pokemon) => {
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

    // Some forms aren't represented in learnset, e.g. genesect_douse; match them with their base forms
    if (!learnsets[learnsetPokemonName].learnset && pokemon[pokemonName].form_data) {
      // Get baseFormName from form_data
      let baseFormName;
      for (let formKey of Object.keys(pokemon[pokemonName].form_data)) {
        if (pokemon[pokemonName].form_data[formKey][0][0] === 'base_form') {
          baseFormName = formKey;
          break;
        }
      }
      
      if (!baseFormName) {
        console.log(learnsetPokemonName, 'has no base form.');
      }

      const learnsetBaseFormName = pokemonMap.get(baseFormName)

      pokemonMap.set(pokemonName, learnsetBaseFormName);
      inversePokemonMap.set(learnsetBaseFormName, inversePokemonMap.get(learnsetBaseFormName).concat(pokemonName));
    }
    // for debugging; checks whether we have pokemon without learnsets
    else if (!learnsets[learnsetPokemonName].learnset) {
      console.log(`${pokemonName}, ${learnsetPokemonName} has no learnset.`);
    }
  }

  return {pokemonMap, inversePokemonMap};
}


// adds Z-moves, max moves, etc. to learnsets and returns updatedLearnsets
// also returns moveMap and inverseMoveMap for going between moveNames and move names in the learnsets
const { getZMoves, getStatusZMoves, getMaxMoves, getGMaxMoves } = require('./helpers.js');
const { serializeDict } = require('./serializing.js');

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
    if (learnsetMoveNameSet.has(replaceAll(moveName, '_', ''))) {
      moveNameSet.add(moveName);
      // add moveName to moveMap and add its inverse to inverseMoveMap
      moveMap.set(moveName, replaceAll(moveName, '_', ''));
      inverseMoveMap.set(replaceAll(moveName, '_', ''), moveName);
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
    if (moveMap.has(replaceAll(moveName, '_', ''))) {
      console.log(`WARNING: moveMap already has ${moveName}, moving on...`);
    }

    // add data to moveMap and inverseMoveMap
    // update learnsets with status Z-move for Pokemon who learn the base move
    else {
      moveNameSet.add(moveName);

      const learnsetMoveName = replaceAll(moveName, '_', '');
      moveMap.set(moveName, learnsetMoveName);
      inverseMoveMap.set(learnsetMoveName, moveName);
      
      // update learnsets so that Pokemon who learn the base move can also learn the corresponding Z-move
      // get base move for moveName 
      // note that Z-moves only have one base move, so we use the index [0].
      const learnsetBaseMoveName = moveMap.get(Object.keys(moves[moveName].requirements["move"])[0]);
      // console.log(learnsetBaseMoveName);
      // console.log(pokemonWhoLearnMoveMap.get(learnsetBaseMoveName));
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
    
    const learnsetMoveName = replaceAll(moveName, '_', '');
    moveMap.set(moveName, learnsetMoveName);
    inverseMoveMap.set(learnsetMoveName, moveName);
    
    // indicates move is Pokemon specific; in this case, it definitely learns the move
    if (moves[moveName].requirements.hasOwnProperty('pokemon')) {
      for (let pokemonName of Object.keys(moves[moveName].requirements.pokemon)) {
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
const addLearnsetsToPokemonArr = (learnsets, moves, pokemon, pokemonArr) => {
  // pokemonMap: pokemonName --> learnsetPokemonName
  // inversePokemonName: learnsetPokemonName --> pokemonName[]
  // the latter returns an array since for some Pokemon with multiple forms, learnsets puts the learnset on only one of the forms; e.g.inversePokemonName('deoxys') returns the names for all of Deoxys's forms
  const {pokemonMap, inversePokemonMap} = getPokemonLearnsetMaps(learnsets, pokemon);
  
  const {updatedLearnsets, moveMap, inverseMoveMap} = getUpdatedLearnsets(learnsets, moves, pokemon);
  
  for (let pokemonEntry of pokemonArr) {

    const pokemonName = pokemonEntry.name;
    
    pokemonEntry['learnset'] = {};

    // add learnset data
    for (let learnsetMoveName of Object.keys(updatedLearnsets[pokemonMap.get(pokemonName)].learnset)) {
      const moveName = inverseMoveMap.get(learnsetMoveName);
      pokemonEntry.learnset[moveName] = updatedLearnsets[pokemonMap.get(pokemonName)].learnset[learnsetMoveName];
    }

    // add event data
    let pokemonEventData = [];
    if (updatedLearnsets[pokemonMap.get(pokemonName)].event_data) {
      for (let eventDatum of updatedLearnsets[pokemonMap.get(pokemonName)].event_data) {
        const {generation, level, gender, nature, shiny, isHidden, perfectIVs, moves: learnsetMoveNames, pokeball} = eventDatum;
        let moveNames = [];
        for (let learnsetMoveName of learnsetMoveNames) {
          moveNames.push(inverseMoveMap.get(learnsetMoveName));
        }
        pokemonEventData.push({generation, level, gender, nature, shiny, isHidden, moveNames, perfectIVs, pokeball});
      }
    }
    pokemonEntry['event_data'] = pokemonEventData;
  }
}
// #endregion

module.exports = {
  mergeLearnsets,
  addLearnsetsToPokemonArr,
}
