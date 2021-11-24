// SPLIT ARRAYS 
// #region

const { NUMBER_OF_GENS } = require('./helpers.js');


const splitArr = arr => {
  return arr.reduce((acc, curr) => {
    return acc.concat(splitEntity(curr, curr.gen));
  }, []);
};


const splitEntity = (entity, initialGen) => {
  // the keys of splitObject will be gen numbers
  let splitObject = {}

  for (let gen = initialGen; gen <= NUMBER_OF_GENS; gen++) {
    // in splitObject, 'gen' refers to the gen for which the values hold, rather than when the entity was introduced
    splitObject[gen] = {
      "gen": gen,
    };

    for (let key of Object.keys(entity)) {
      const value = entity[key];

      // special case for Pokemon eventData
      if (key === 'event_data') {
        const eventDatumForGen = entity[key].filter(eventDatum => eventDatum.generation === gen);

        if (eventDatumForGen.length > 0) {
          splitObject[gen][key] = eventDatumForGen;
        }

        // no further processing necessary
        continue;
      }
      
      // indicates patch list
      if (Array.isArray(value) && Array.isArray(value[0])) {
        for (let patch of value) {
          if (patch.slice(-1)[0] == gen && !splitObject[gen][key]) {
            // indicates patch consists of a single value, followed by gen
            if (patch.length === 2) {
              splitObject[gen][key] = patch.slice(0, -1)[0];
            }
            // indicates patch consists of multiple values in addition to gen, leave as array
            else {
              splitObject[gen][key] = patch.slice(0, -1);
            }
          } 
          // for some attributes, e.g. power, we need to have only one value per gen, so this catches that 
          // for other attributes, e.g. 'evolves_to' for eevee, which evolves to multiple Pokemon in Gen 1, we can have multiple values per gen. Also true for move requirements.
          else if (patch.slice(-1)[0] == gen && key != 'evolves_to' && key != 'evolves_from' && key != 'requirements') {
            throw `${entity.formatted_name} has duplicate gen in ${key}, ${value}.`;
          }
        }
        // // need to check specifically that it's undefined, since 0 is a valid value
        // if (splitObject[gen][key] === undefined) {
        //   console.log(`${entity.formatted_name} does not have a patch for ${gen}: ${key}, ${value}.`);
        // }
        
      } 
      // indicates nested object; there may be a patch list within, but there won't be another object within aside from requirement data
      else if (typeof value === 'object') {
        splitObject[gen][key] = {};
        
        for (let innerKey of Object.keys(value)) {
          const innerValue = value[innerKey];
          
          // special case for Pokemon learnsets; in this case, innerKey is a move name, and innerValue is of the form, e.g. ["7M", "7V", "6M", "5M", "4M", "3M"]
          if (key === 'learnset') {
            // learnDatum[0] is a single character repsenting the gen
            const learnDatumForGen = innerValue.filter(learnDatum => learnDatum[0] == gen).map(learnDatum => learnDatum.slice(1));
            
            // if Pokemon doesn't learn move in gen, then learnDatumForGen will be empty
            if (learnDatumForGen.length > 0) {
              splitObject[gen][key][innerKey] = learnDatumForGen;
            }

            // no further processing required for innerKey
            continue;
          } 

          // indicates patch list
          if (Array.isArray(innerValue) && Array.isArray(innerValue[0])) {
            for (let patch of innerValue) {
              // console.log(patch, gen, patch.slice(-1)[0]);
              if (patch.slice(-1)[0] == gen && !splitObject[gen][key][innerKey]) {
                // indicates patch consists of a single value, followed by gen
                if (patch.length === 2) {
                  splitObject[gen][key][innerKey] = patch.slice(0, -1)[0];
                }
                // indicates patch consists of multiple values in addition to gen, leave as array
                else {
                  splitObject[gen][key][innerKey] = patch.slice(0, -1);
                }
              } 
              // Move requirements can have multiple Pokemon.
              else if (patch.slice(-1)[0] == gen && key != 'requirements') {
                throw `${entity.formatted_name} has duplicate gen in ${key}, ${innerValue}.`;
              }
            }
            // // need to check specifically that it's undefined, since 0 is a valid value
            // if (splitObject[gen][key][innerKey] === undefined) {
            //   console.log(`${entity.formatted_name} does not have a patch for ${gen}: ${innerKey}, ${innerValue}.`);
            // }
          }
          // Special case for move requirements; the reason we have it so nested is that the extendPatch algorithm works; otherwise, we'd need to handle an exception there instead.
          else if (key == 'requirements') {
            // innerValue is an object whose keys are requirement names (e.g. 'electric', 'fairy', 'orbeetle', 'alcremie'), and whose values are patch lists
            splitObject[gen][key][innerKey] = [];
            for (let reqName of Object.keys(innerValue)) {
              innerValue[reqName].map(patch => {
                // patch[0] is true if patch applies for gen, false otherwise.
                if (patch[1] === gen && patch[0]) {
                  splitObject[gen][key][innerKey] = splitObject[gen][key][innerKey].concat(reqName);
                }
              });
            }
          }
          // indicates simple field that doesn't depend on gen
          else {
            splitObject[gen][key][innerKey] = innerValue;
          }
        }
      }
      // indicates simple field that doesn't depend on gen
      else {
        // change key 'gen' to 'introduced'
        if (key === 'gen') {
          key = 'introduced';
        }
        splitObject[gen][key] = value;
      }
    }
  };

  // returns an array of objects, split according to generation
  return Object.keys(splitObject).map(gen => splitObject[gen]);
};  
// #endregion

module.exports = {
  splitArr,
}