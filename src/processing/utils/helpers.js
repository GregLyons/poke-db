
// VARIOUS CONSTANTS 
// #region

const NUMBER_OF_GENS = 8

// Filepath prefixes
const RAW_DATA_PATH = './../data/raw_data/'
const RAW_JSON_DATA_PATH = RAW_DATA_PATH + 'json/';
const PROCESSED_DATA_PATH = './../data/processed_data/';

// #endregion

// MOVE CLASSIFICATIONS
// #region

const getZMoves = moveArr => moveArr.filter(move => move.z_move).map(move => move.name);

const getStatusZMoves = moveArr => moveArr.filter(move => move.category[0][0] == 'status' && move.name.includes('z_')).map(move => move.name);

const getMaxMoves = moveArr => moveArr.filter(move => move.max_move).map(move => move.name);

const getGMaxMoves = moveArr => moveArr.filter(move => move.g_max_move).map(move => move.name);

// Pokemon who cannot Dynamax, hence who can't use Max moves
const noMax = ['zacian', 'zacian_crowned', 'zamazenta', 'zamazenta_crowned', 'eternatus'];

// const getMovesOfClass = (moveArr, className) => {
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

// From Sean Bright's answer on SO: https://stackoverflow.com/questions/1144783/how-to-replace-all-occurrences-of-a-string-in-javascript
function escapeRegExp(string) {
  return string.replace(/[.*+\-?^${}()|[\]\\]/g, '\\$&'); // $& means the whole matched string
}

function replaceAll(str, find, replace) {
  return str.replace(new RegExp(escapeRegExp(find), 'g'), replace);
}

module.exports = {
  NUMBER_OF_GENS,
  RAW_DATA_PATH,
  RAW_JSON_DATA_PATH,
  PROCESSED_DATA_PATH,
  getZMoves,
  getStatusZMoves,
  getMaxMoves,
  getGMaxMoves,
  noMax,
  replaceAll,
}