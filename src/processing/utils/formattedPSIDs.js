const { NUMBER_OF_GENS } = require("./helpers");

const toPSID = str => {
  return str.toLowerCase().replace(/[^a-z0-9]+/g, '')
}

// Abilities 
// #region

const addPSIDs_ability = (splitAbilityArr, formattedPSIDs) => {
  const formattedPSIDMap = new Map();
  for (let formattedPSID of formattedPSIDs) {
    formattedPSIDMap.set(toPSID(formattedPSID), formattedPSID);
  }

  for (let ability of splitAbilityArr) {
    const abilityPSID = toPSID(ability.name);
    ability.ps_id = abilityPSID;
    if (formattedPSIDMap.get(abilityPSID) !== undefined) {
      ability.formatted_ps_id = formattedPSIDMap.get(abilityPSID);
    }
    else console.log(abilityPSID);
  }
}

// #endregion

// Items 
// #region

const addPSIDs_item = (splitItemArr, formattedPSIDs) => {
  const formattedPSIDMap = new Map();
  for (let formattedPSID of formattedPSIDs) {
    formattedPSIDMap.set(toPSID(formattedPSID), formattedPSID);
  }

  for (let item of splitItemArr) {
    let itemPSID = toPSID(item.name);
    if (itemPSID === 'metronomeitem') {
      itemPSID = 'metronome';
    }

    item.ps_id = itemPSID;
    if (formattedPSIDMap.get(itemPSID) !== undefined) {
      item.formatted_ps_id = formattedPSIDMap.get(itemPSID);
    }
    else console.log(itemPSID);
  }
}

// #endregion

// Moves
// #region

// 'patchPSIDObj' is an object whose keys are generations (1, 2, ... 'NUMBER_OF_GENS'), and whose values are arrays of move names
const addPSIDs_move = (splitMoveArr, patchPSIDObj) => {
  const genToMap = new Map();
  // Blank slot makes indices line up with gen number
  let formattedPSIDMapArr = [{}, ];
  let previousGenFormattedPSIDs = [];
  for (let i = 1; i <= NUMBER_OF_GENS; i++) {
    const formattedPSIDs = previousGenFormattedPSIDs.concat(patchPSIDObj[i]);
    genToMap.set(i, formattedPSIDs);

    // Keep track of previous gen psIDs
    previousGenFormattedPSIDs = previousGenFormattedPSIDs.concat(patchPSIDObj[i]);

    // Set up new Map for given gen
    const formattedPSIDMap = new Map();
    for (let formattedPSID of formattedPSIDs) {
      formattedPSIDMap.set(toPSID(formattedPSID), formattedPSID);
    }

    // Add Map
    formattedPSIDMapArr.push(formattedPSIDMap);
  }

  for (let move of splitMoveArr) {
    const moveGen = move.gen;
    const movePSID = toPSID(move.name);
    move.ps_id = movePSID;

    const formattedPSIDMap = formattedPSIDMapArr[moveGen];
    if (formattedPSIDMap.get(movePSID) !== undefined) {
      move.formatted_ps_id = formattedPSIDMap.get(movePSID);
    }
    // Status Z-moves aren't included in data set
    else if (move.z_move === true && movePSID.charAt(0) === 'z') {
      move.formatted_ps_id = 'Z-' + formattedPSIDMap.get(movePSID.slice(1));
    }
    else console.log(movePSID);
  }
}

// #endregion

// Pokemon
// #region

// 'patchPSIDObj' is an object whose keys are generations (1, 2, ... 'NUMBER_OF_GENS'), and whose values are arrays of pokemon names
const addPSIDs_pokemon = (splitPokemonArr, patchPSIDObj) => {
  const genToMap = new Map();
  // Blank slot makes indices line up with gen number
  let formattedPSIDMapArr = [{}, ];
  let previousGenFormattedPSIDs = [];
  for (let i = 1; i <= NUMBER_OF_GENS; i++) {
    const formattedPSIDs = previousGenFormattedPSIDs.concat(patchPSIDObj[i]);
    genToMap.set(i, formattedPSIDs);

    // Keep track of previous gen psIDs
    previousGenFormattedPSIDs = previousGenFormattedPSIDs.concat(patchPSIDObj[i]);

    // Set up new Map for given gen
    const formattedPSIDMap = new Map();
    for (let formattedPSID of formattedPSIDs) {
      formattedPSIDMap.set(toPSID(formattedPSID), formattedPSID);
    }

    // Add Map
    formattedPSIDMapArr.push(formattedPSIDMap);
  }

  for (let pokemon of splitPokemonArr) {
    const pokemonGen = pokemon.gen;
    const pokemonPSID = pokemon.ps_id;

    const formattedPSIDMap = formattedPSIDMapArr[pokemonGen];
    if (formattedPSIDMap.get(pokemonPSID) !== undefined) {
      pokemon.formatted_ps_id = formattedPSIDMap.get(pokemonPSID);
    }
    // Pokemon who are only identified by their species
    else if (
      pokemonPSID.includes('unown')
      ||pokemonPSID.includes('burmy')
      ||pokemonPSID.includes('shellos')
      ||pokemonPSID.includes('gastrodon')
      ||pokemonPSID.includes('deerling')
      ||pokemonPSID.includes('sawsbuck')
      ||pokemonPSID.includes('flabebe')
      ||pokemonPSID.includes('floette')
      ||pokemonPSID.includes('florges')
      ||pokemonPSID.includes('furfrou')
      ||pokemonPSID.includes('xerneas')
      ||pokemonPSID.includes('spewpa')
      ||pokemonPSID.includes('scatterbug')
      ||pokemonPSID.includes('vivillon')
      ||pokemonPSID.includes('minior')
    ) {
      pokemon.formatted_ps_id = pokemon.species.charAt(0) + pokemon.species.slice(1);
    }
    // Pikachu-World in gen 7
    else if (pokemonPSID === 'pikachuworld') {
      pokemon.formatted_ps_id = 'Pikachu-World';
    }
    // Magearna-Original in gen 7
    else if (pokemonPSID === 'magearnaoriginal') {
      pokemon.formatted_ps_id = 'Magearna-Original';
    }
    // Aegislash-Shield
    else if (pokemonPSID === 'aegislash') {
      pokemon.formatted_ps_id = 'Aegislash-Shield';
    }
    else console.log(pokemonPSID);
  }
}

// #endregion

module.exports = {
  addPSIDs_ability,
  addPSIDs_item,
  addPSIDs_move,
  addPSIDs_pokemon,
}