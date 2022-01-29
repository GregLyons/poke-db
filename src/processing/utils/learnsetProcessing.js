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
        if (pokemon[pokemonName].form_data[formKey][0][0] === 'base') {
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


// also returns moveMap and inverseMoveMap for going between moveNames and move names in the learnsets
const { getZMoves, getStatusZMoves, getMaxMoves, getGMaxMoves } = require('./helpers.js');
const { serializeDict } = require('./serializing.js');

// adds Z-moves, max moves, etc. to learnsets and returns updatedLearnsets
const getUpdatedLearnsets = (learnsets, moves, pokemon) => {
  // learnsets shouldn't have dates, functions, undefined, regexp, or infinity, so this copies the learnsets
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
// also adds ps_id's to pokemonArr
const addLearnsetsToPokemonArr = (learnsets, moves, pokemon, pokemonArr) => {
  // pokemonMap: pokemonName --> learnsetPokemonName
  // inversePokemonName: learnsetPokemonName --> pokemonName[]
  // the latter returns an array since for some Pokemon with multiple forms, learnsets puts the learnset on only one of the forms; e.g.inversePokemonName('deoxys') returns the names for all of Deoxys's forms
  const {pokemonMap, inversePokemonMap} = getPokemonLearnsetMaps(learnsets, pokemon);
  
  const {updatedLearnsets, moveMap, inverseMoveMap} = getUpdatedLearnsets(learnsets, moves, pokemon);

  // Keys will be names of evolutions (e.g. 'wartortle', 'blastoise', but not 'squirtle'); values will be objects. The keys of these objects will be move names, and the values will be arrays of gens, e.g. { 'absorb': [5, 6, 7, 8] } on 'ivysaur' would signify that 'bulbasaur' learns 'absorb' in gens 5-8, so 'ivysaur' will certainly have access to 'absorb' in gens 5-8
  const evolutionLearnsetMap = new Map();
  
  for (let pokemonEntry of pokemonArr) {

    const pokemonName = pokemonEntry.name;
    const evolutionData = pokemonEntry.evolves_to;

    const evolutionNames = Object.keys(evolutionData);

    // Initialize evolutionLearnsetMap.get(evolutionName)
    for (let evolutionName of evolutionNames) {
      if (!evolutionLearnsetMap.has(evolutionName)) evolutionLearnsetMap.set(evolutionName, {});
    }
    
    pokemonEntry['learnset'] = {};

    // add learnset data
    for (let learnsetMoveName of Object.keys(updatedLearnsets[pokemonMap.get(pokemonName)].learnset)) {
      const moveName = inverseMoveMap.get(learnsetMoveName);
      pokemonEntry.learnset[moveName] = updatedLearnsets[pokemonMap.get(pokemonName)].learnset[learnsetMoveName];

      // Extract gens and remove duplicates, e.g. ['6E', '7E', '7M', '8E', '8M'] => [6, 7, 8].
      const movePresenceInGenArr = [...new Set(updatedLearnsets[pokemonMap.get(pokemonName)].learnset[learnsetMoveName].map(learnDatum => learnDatum[0]))];

      // For each evolution, 
      for (let evolutionName of evolutionNames) {
        evolutionLearnsetMap.set(evolutionName,
          {
            ...evolutionLearnsetMap.get(evolutionName),
            [moveName]: movePresenceInGenArr,
          }
        );
      }
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

  return evolutionLearnsetMap;
}

// For Pokemon which can only learn a move through evolution, add that move to their learnset
const addLearnDataToEvolutions = (evolutionLearnsetMap, pokemonArr) => {
  // evolutionLearnsetMap only carries from one step to the next. So moves from 'oddish' will be passed onto 'gloom' but not to 'vileplume'. 
  const nextEvolutionLearnsetMap = new Map();
  
  // First pass through pokemonArr. This will pick up 1 -> 2 and 2 -> 3 learn methods, but not 1 -> 3. We use this pass to set up nextEvolutionLearnsetMap, which will establish 1 -> 3.
  for (let pokemonEntry of pokemonArr) {
    const pokemonName = pokemonEntry.name;
    const evolutionLearnsetData = evolutionLearnsetMap.get(pokemonName);

    // Check if this is a second-level evolution
    let nextEvolutionData;
    if (Object.keys(pokemonEntry.evolves_from).length > 0) {
      // If a second-level evolution, get third evolution if it exists
      nextEvolutionData = pokemonEntry.evolves_to;
    }
    let nextEvolutionNames = [];
    if (nextEvolutionData) nextEvolutionNames = nextEvolutionNames.concat(Object.keys(nextEvolutionData));

    // Initialize nextEvolutionLearnsetMap.get(nextEvolutionName)
    for (let nextEvolutionName of nextEvolutionNames) {
      if (!nextEvolutionLearnsetMap.has(nextEvolutionName)) nextEvolutionLearnsetMap.set(nextEvolutionName, {});
    }

    // Update current Pokemon's learnset with its prevolution learn data
    if (evolutionLearnsetData) {
      const pokemonLearnset = pokemonEntry.learnset;
      for (let moveName of Object.keys(evolutionLearnsetData)) {
        // If this Pokemon is the second in a three-evolution line, then the final evolution will not be handled by evolutionLearnsetMap. Thus, we need to add this to nextEvolutionLearnsetMap.
        // Update current entry with previous evolution data
        pokemonLearnset[moveName] = (pokemonLearnset[moveName] || []).concat(evolutionLearnsetData[moveName].map(gen => gen + 'EV'));

        // Add moves learned only through evolution to nextEvolutionMap
        for (let nextEvolutionName of nextEvolutionNames) {
          // evolutionLearnsetData[moveName] is a list of gens in which the prevolution of this current Pokemon learns the move. This will be passed onto the third evolution.
          nextEvolutionLearnsetMap.set(nextEvolutionName,
            {
              ...nextEvolutionLearnsetMap.get(nextEvolutionName),
              [moveName]: evolutionLearnsetData[moveName],
            }
          );
        }
      }
    }
  }

  // Handle 1 -> 3 learning
  for (let pokemonEntry of pokemonArr) {
    const pokemonName = pokemonEntry.name;
    const nextEvolutionLearnsetData = nextEvolutionLearnsetMap.get(pokemonName);

    // Update current Pokemon's learnset with 1 -> 3 learn data
    if (nextEvolutionLearnsetData) {
      const pokemonLearnset = pokemonEntry.learnset;
      for (let moveName of Object.keys(nextEvolutionLearnsetData)) {
        // The Pokemon can only learn the move through evolution
        // If this Pokemon is the second in a three-evolution line, then the final evolution will not be handled by evolutionLearnsetMap. Thus, we need to add this to nextEvolutionLearnsetMap.
        // Update current entry with previous evolution data
        pokemonLearnset[moveName] = (pokemonLearnset[moveName] || []).concat(nextEvolutionLearnsetData[moveName].map(gen => gen + 'EV'));
      }
    }
  }

  // Remove 'EV' flags when there are other ways to learn the move in a given generation
  for (let pokemonEntry of pokemonArr) {
    const pokemonName = pokemonEntry.name;

    // Iterate over moves in pokemonName's learnset
    for (let moveName of Object.keys(pokemonEntry.learnset)) {
      let gensWithOtherLearnMethod = [];

      // Get gens with other learn method
      for (let learnMethod of pokemonEntry.learnset[moveName]) {
        if (!learnMethod.includes('EV')) {
          // First character of learnMethod is gen
          gensWithOtherLearnMethod.push(learnMethod.charAt(0));
        }
      }

      // Keep learn method only if it's not , or if 'EV' is the only way to learn that move in that gen.
      pokemonEntry.learnset[moveName] = [...new Set(
        pokemonEntry.learnset[moveName].filter(learnMethod => !learnMethod.includes('EV') || !gensWithOtherLearnMethod.includes(learnMethod.charAt(0)))
      )];
    }
  }
}

const addPokemonShowdownIDToPokemonArr = (psIDs, pokemonArr) => {
  for (let pokemonEntry of pokemonArr) {
    const pokemonName = pokemonEntry.name;

    if (!psIDs[replaceAll(pokemonName, '_', '')]) {
      // Usual case where base form in PS doesn't have suffix
      if ([
        'castform_normal',
        'burmy_plant',
        'wormadam_plant',
        'arceus_normal',
        'meloetta_aria',
        'oricorio_baile',
        'silvally_normal',
        'darmanitan_standard',
        'deoxys_normal',
        'giratina_altered',
        'shaymin_land',
        'tornadus_incarnate',
        'thundurus_incarnate',
        'landorus_incarnate',
        'aegislash_shield',
        'pumpkaboo_average',
        'gourgeist_average',
        'lycanroc_midday',
        'wishiwashi_solo',
        'toxtricity_amped',
        'eiscue_ice',
        'indeedee_m',
        'keldeo_ordinary',
        'shellos_west',
        'gastrodon_west',
        'deerling_spring',
        'sawsbuck_spring',
        'meowstic_m',
        'unown_a',
        'mothim_plant',
        'flabebe_red',
        'floette_red',
        'florges_red',
        'minior_red',
        'zygarde_50',
        'minior_meteor_red',
        'minior_meteor_orange',
        'minior_meteor_yellow',
        'minior_meteor_green',
        'minior_meteor_blue',
        'minior_meteor_indigo',
        'minior_meteor_violet',
        'mothim_sandy',
        'mothim_trash',
        'sinistea_phony',
        'polteageist_phony',
        'xerneaus_active',
        'rockruff_own_tempo',
        'pikachu_partner_cap',
        'cherrim_overcast',
        'basculin_red_striped',
      ].includes(pokemonName)) {
        pokemonEntry['ps_id'] = pokemonName.split('_')[0];
      }
      else if ([
        'spewpa_icy_snow',
        'scatterbug_icy_snow',
        'pikachu_original_cap',
        'pikachu_kalos_cap',
        'pikachu_alola_cap',
        'pikachu_hoenn_cap',
        'pikachu_sinnoh_cap',
        'pikachu_unova_cap',
        'pikachu_world_cap',
      ].includes(pokemonName)) {
        pokemonEntry['ps_id'] = pokemonName.split('_').slice(0, -1).join('');
      }
      else if (pokemonName.includes('spewpa') || pokemonName.includes('scatterbug')) {
          pokemonEntry['ps_id'] = pokemonName.split('_')[0];
      }
      else {
        switch(pokemonName) {
          case 'toxtricity_amped_gmax':
            pokemonEntry['ps_id'] = 'toxtricitygmax';
            break;
          case 'darmanitan_standard_galar':
            pokemonEntry['ps_id'] = 'darmanitangalar';
            break;
          case 'darmanitan_zen_galar':
            pokemonEntry['ps_id'] = 'darmanitangalarzen';
            break;
          case 'eevee_partner':
            pokemonEntry['ps_id'] = 'eeveestarter';
            break;
          case 'necrozma_dusk':
            pokemonEntry['ps_id'] = 'necrozmaduskmane';
            break;
          case 'necrozma_dawn':
            pokemonEntry['ps_id'] = 'necrozmadawnwings';
            break;
          case 'morpeko_full_belly':
            pokemonEntry['ps_id'] = 'morpeko';
            break;
          case 'vivillon_meadow':
            pokemonEntry['ps_id'] = 'vivillon';
            break;
          case 'xerneas_active':
            pokemonEntry['ps_id'] = 'xerneas';
            break;
          default:
            console.log(`${pokemonName} does not have a psID.`);
        }
      }
    }
    else {
      pokemonEntry['ps_id'] = replaceAll(pokemonName, '_', '');
    }
  }
}

// #endregion

module.exports = {
  mergeLearnsets,
  addLearnsetsToPokemonArr,
  addLearnDataToEvolutions: addLearnDataToEvolutions,
  addPokemonShowdownIDToPokemonArr,
}
