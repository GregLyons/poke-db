// EXTENDING PATCH LISTS OF OBJECTS
// #region

const { NUMBER_OF_GENS } = require('./helpers.js');

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

//#endregion

// SERIALIZING
// #region

// given an entity dict from one of the .json files, convert to an array of objects where each key in the dict gives 
const serializeDict = dict => {
  return Object.keys(dict).reduce((acc, curr) => {
    acc.push({
      name: curr,
      ...extendPatchesOfDict(dict[curr]),
    });
    return acc;
  }, []);
};

// Similar to serializeDict, without patch extension
const serializeDescriptions = descriptions => {
  return Object.keys(descriptions).reduce((acc, curr) => {
    return acc.concat({
      "entity_name": curr,
      ...descriptions[curr],
    });
  }, []);
};

// Similar to serializeDict, but for simpler objects such as stats, statuses, effects, etc.
const serializeVersionGroupDict = versionGroupDict => {
  return Object.keys(versionGroupDict).reduce((acc, curr) => {
    return acc.concat({
      "code": curr,
      "name": versionGroupDict[curr].name,
      "formatted_name": versionGroupDict[curr].formatted_name,
      // stats and statuses don't have gens assigned to them
      "introduced": versionGroupDict[curr].gen ? versionGroupDict[curr].gen : undefined
    });
  }, []);
}

// // Similar to splitArr, but with respect to version group rather than generation
// const splitDescriptions = descriptionArr => {
//   let splitArr = [];
//   // entity is a description object
//   for (let entity of descriptionArr) {
//     // numeric keys of entity have description info
//     for (let descriptionIndex of Object.keys(entity).filter(key => !isNaN(key))) {
//       const [description, versionGroups] = entity[descriptionIndex];
//       for (let versionGroup of versionGroups) {
//         splitArr.push({
//           "entity_name": entity.entity_name,
//           "description_type": entity.description_type,
//           "description_index": parseInt(descriptionIndex, 10),
//           "description": description,
//           "version_group": versionGroup,
//         });
//       }
//     }
//   }

//   return splitArr;
// };
// #endregion

module.exports = {
  serializeDict,
  serializeDescriptions,
  serializeVersionGroupDict,
}