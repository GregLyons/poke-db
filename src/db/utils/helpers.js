/*
  MISCELLANEOUS CONSTANTS AND HELPER FUNCTIONS
*/

const GEN_ARRAY = [
  [1, 'I'],
  [2, 'II'],
  [3, 'III'],
  [4, 'IV'],
  [5, 'V'],
  [6, 'VI'],
  [7, 'VII'],
  [8, 'VIII'],
];

const NUMBER_OF_GENS = GEN_ARRAY.length;

const PROCESSED_DATA_PATH = './../../data/processed_data/';

// Given a version group code, return the generation of that version group. E.g. 'GS' -> 2, 'BW' -> 5.
const getGenOfVersionGroup = (versionGroupCode) => {
  switch(versionGroupCode) {
    case 'RB':
    case 'Y':
    case 'Stad':
      return 1;
    case 'GS':
    case 'C':
    case 'Stad2':
      return 2;
    case 'RS':
    case 'E':
    case 'Colo':
    case 'XD':
    case 'FRLG':
      return 3;
    case 'DP':
    case 'Pt':
    case 'HGSS':
    case 'PBR':
      return 4;
    case 'BW':
    case 'B2W2':
      return 5;
    case 'XY':
    case 'ORAS':
      return 6;
    case 'SM':
    case 'USUM':
    case 'PE':
      return 7;
    case 'SwSh':
    case 'BDSP':
      return 8;
    default:
      throw `Invalid version group code: ${versionGroupCode}.`
  }
}

const timeElapsed = timer => {
  let now = new Date().getTime();
  console.log('Took', Math.floor((now - timer) / 1000), 'seconds.\n');
  timer = now;
  return timer;
}

module.exports = {
  GEN_ARRAY,
  NUMBER_OF_GENS,
  PROCESSED_DATA_PATH,
  getGenOfVersionGroup,
  timeElapsed,
}