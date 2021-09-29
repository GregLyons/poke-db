import fetch from "cross-fetch";

const POKEAPI_BASE_URL = 'https://pokeapi.co/api/v2/';

function genStringToNumber(genString) {
  switch(genString) {
    case "generation-i":
      return 1;
    case "generation-ii":
      return 2;
    case "generation-iii":
      return 3;
    case "generation-iv":
      return 4;
    case "generation-v":
      return 5;
    case "generation-vi":
      return 6;
    case "generation-vii":
      return 7;
    case "generation-viii":
      return 8;
    default:
      return 0;
  }
}

function varietyNameToGen(variantName, speciesGen) {
  const maxRegex = /[ga]max/;
  if (variantName.includes('-mega') || variantName.includes('-primal')) {
    return 6;
  } else if (variantName.includes('-alola')) {
    return 7;
  }
  else if (maxRegex.test(variantName) || variantName.includes('galar')) {
    return 8;
  } else if(variantName.includes('pikachu') && variantName.includes('-')) {
    return 7;
  } else {
    return speciesGen;
  }
}

async function fetchPokemonSpeciesNames() {
  const response = await fetch(`${POKEAPI_BASE_URL}/pokemon-species?limit=max`)
  const json = await response.json();

  const speciesNames = json.results.map(d => d.name);
  return speciesNames;
}

async function fetchPokemonDataFromSpeciesName(pokemonSpeciesName) {
  const response = await fetch(`${POKEAPI_BASE_URL}/pokemon-species/${pokemonSpeciesName}`);
  const json = await response.json();

  const dexNumber = json.id;
  const speciesGen = genStringToNumber(json.generation.name);

  const varieties = json.varieties.map(d => d.pokemon.name);
  const varietiesGen = varieties.map(d => varietyNameToGen(d, speciesGen));

  // console.log(dexNumber);
  // console.log(speciesGen);
  console.log(varieties);
  console.log(varietiesGen);

  return {dexNumber, speciesGen, varieties, varietiesGen};
}

async function fetchPokemonDataFromVarietyName(pokemonVarietyName) {
  const response = await fetch(`${POKEAPI_BASE_URL}/pokemon/${pokemonVarietyName}`);
  const json = await response.json();

  const abilities = json.abilities.map(d => d.ability.name);
  const typing = json.types.map(d => d.type.name);
  const pastTyping = json.past_types.map(d => {
    return {
      gen: genStringToNumber(d.generation.name),
      typing: d.types.map(t => t.type.name),
    }
  });
  const baseStats = json.stats.map(d => {
    let statObj = {};
    statObj[d.stat.name] = d.base_stat;
    return statObj;
  });
  const weight = json.weight;

  // console.log(abilities);
  // console.log(typing);
  // console.log(pastTyping);
  // console.log(baseStats);
  // console.log(weight);
  return {abilities, typing, pastTyping, baseStats, weight};
}
