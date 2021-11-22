require('dotenv').config();
const mysql = require('mysql2');
const tableStatements = require('./sql/index.js');


const db = mysql.createPool({
  host: process.env.DB_HOST,
  user: process.env.DB_USERNAME,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME,
  connectionLimit: 20,
});

// initializes database
const createDB = () => {
  db.execute(`CREATE DATABASE IF NOT EXISTS ${process.env.DB_NAME}`, (err, results, fields) => {
    console.log(err);
    console.log(results);
    console.log(fields);
  });

  console.log('Database created.');
} 

// Initializes all tables; will only create tables that don't already exist.
const createTables = async () => {
  // Create entity tables first for foreign keys in junction tables.
  console.log('Creating entity tables if they don\'t already exist.');

  // Create generation table before everything else
  db.promise().query(tableStatements.entityTables.generation.create)
    .then(
      () => {
        console.log('generation table created.');
  
        Promise.all(Object.keys(tableStatements.entityTables).filter(tableName => tableName !== 'generation').map(tableName => {
          const statement = tableStatements.entityTables[tableName].create;
      
          console.log(`Creating ${tableName} if it doesn't already exist...`)
          return db.promise().query(statement);
        }))
        // Once the entity tables are complete, we can create the junction tables in any order.
        .then(
          () => {
            console.log('\nEntity tables finished, adding junction tables.\n');
            
            // Create the junction tables
            Object.keys(tableStatements).map(tableGroup => {
              // We've already handled entity tables
              if (tableGroup === 'entityTables') return;
              
              Object.keys(tableStatements[tableGroup]).map(tableName=> {
                const statement = tableStatements[tableGroup][tableName].create;
                
                db.execute(statement, (err, results, fields) => {
                  if (err && err.errno != 1065) {
                    console.log(err);
                  }
                  console.log(`${tableName} created if it didn't already exist.`);
                });
              });
            });
          }
        )
        .catch(console.log);
      }
    ).catch(console.log);
  
  return;
};

// Inserts generation, version group, description, and sprite data; these are entities which don't depend on generation.
// WARNING: most of the data depends on generation, so performing this will cause most of the other data to be deleted.
const insertBasicEntities = async () => {
  // TODO add sprites
  const basicEntityTableNames = [
    'generation',
    'pdescription',
    'pstatus',
    'stat',
  ];
  for (let tableName of basicEntityTableNames) {
    // Delete the tables to overcome foreign key constraints.
    console.log(tableName);
    db.promise().query(tableStatements.entityTables[tableName].delete)
    .then( ([results, fields]) => {

      console.log(`${tableName} table deleted.`);

    })
    .catch(console.log)
    .then( () => {
      db.promise().query(tableStatements.entityTables[tableName].reset_auto_inc)
      .then( ([results, fields]) => {
        
        console.log(`Reset AUTO_INCREMENT index for ${tableName} table.`);
      })
      .catch(console.log)
      .then( () => {
        
        // Determine values to be inserted.
        let values;
        switch (tableName) {
          // gen numbers and codes
          case 'generation':
            const { GEN_ARRAY } = require('./utils.js');
            values = GEN_ARRAY;
            break;

          // the description 
          case 'pdescription':
            const descriptions = require('./processing/processed_data/descriptions.json');
            values = descriptions.reduce((acc, descriptionObj) => {
              // extract entityName and description type
              const { entity_name: entityName, description_type: descriptionType } = descriptionObj;
              
              // descriptionObj contains all the descriptions for entity name, so we need to split them up. The unique descriptions are indexed by numeric keys.
              return acc.concat(Object.keys(descriptionObj)
                // numeric keys contain description info
                .filter(key => !isNaN(key))
                .map(descriptionIndex => {
                  // descriptionObj[descriptionIndex] is a two-element array, whose first element is the description itself, and whose second element is another array containing version group codes; we don't need the latter at this moment
                  const description = descriptionObj[descriptionIndex][0];
                  
                  return [description, descriptionIndex, descriptionType, entityName];
                }));
            }, []);
            break;
          
          // status effects
          case 'pstatus':
            values = require('./processing/processed_data/statuses.json').map(data => [data.name, data.formatted_name]);
            break;
          
          // battle stats
          case 'stat':
            values = require('./processing/processed_data/stats.json').map(data => [data.name, data.formatted_name]);
            break;

          default:
            console.log(`${tableName} unhandled.`);
        }

        db.promise().query(tableStatements.entityTables[tableName].insert, [values])
        .then( ([results, fields]) => {
          console.log(`${tableName} data inserted: ${results.affectedRows} rows.`);
        })
        .catch(console.log);
      });
    });
  }

  return;
}

// Inserts data for entities which depend on generation, either through a composite primary key or through an 'introduced' column. 
// WARNING: the junction tables all depend on one or more tables in here, so performing this will cause those tables to be deleted.
const insertGenDependentEntities = async () => {
  const entityTableNames = [
    'ability',
    'effect',
    'item',
    'pokemon',
    'pmove',
    'ptype',
    'usage_method',
    'version_group'
  ];
  for (let tableName of entityTableNames) {
    // Delete the tables to overcome foreign key constraints.
    console.log(tableName);
    db.promise().query(tableStatements.entityTables[tableName].delete)
    .then( ([results, fields]) => {

      console.log(`${tableName} table deleted.`);

    })
    .catch(console.log)
    .then( () => {
      db.promise().query(tableStatements.entityTables[tableName].reset_auto_inc)
      .then( ([results, fields]) => {
        
        console.log(`Reset AUTO_INCREMENT index for ${tableName} table.`);
      })
      .catch(console.log)
      .then( () => {
        
        // Determine values to be inserted.
        let values;
        switch (tableName) {
          case 'ability':
            /*
              Need (
                generation_id,
                ability_name,
                ability_formatted_name,
                introduced
              )
            */
            values = require('./processing/processed_data/abilities.json')
              .map(data => [data.gen, data.name, data.formatted_name, data.introduced]);
            break;

          case 'effect':
            /* 
              Need (
                effect_name,
                effect_formatted_name,
                introduced
              )
            */
            values = require('./processing/processed_data/effects.json')
              .map(data => [data.name, data.formatted_name, data.introduced]);
            break;

          case 'item':
            /* 
              Need (
                generation_id,
                item_name,
                item_formatted_name,
                introduced,
                item_class
              ) 
            */
            values = require('./processing/processed_data/items.json')
              .map(data => [data.gen, data.name, data.formatted_name, data.introduced, data.item_type]);
            break;

          case 'pokemon':
            /* 
              Need (
                generation_id,
                pokemon_name,
                pokemon_formatted_name,
                pokemon_species,
                pokemon_dex,
                pokemon_height,
                pokemon_weight,
                introduced,
                pokemon_hp,
                pokemon_attack,
                pokemon_defense,
                pokemon_special_defense,
                pokemon_special_attack,
                pokemon_speed
              )
            */
            values = require('./processing/processed_data/pokemon.json')
              // filter out cosmetic forms and lgpe_only pokemon
              .filter(data => !data.cosmetic && !(data.gen == 'lgpe_only'))
              .map(data => [
                data.gen,
                data.name,
                data.formatted_name,
                data.species,
                data.dex_number,
                data.height,
                data.weight,
                data.introduced,
                data.hp,
                data.attack,
                data.defense,
                data.special_defense,
                data.special_attack,
                data.speed,
              ]);
            break;
          
          case 'pmove':
            /*
              Need (
                generation_id,
                pmove_name,
                pmove_formatted_name,
                introduced,
                pmove_power,
                pmove_pp,
                pmove_accuracy,
                pmove_category,
                pmove_priority,
                pmove_contact,
                pmove_target
              )
            */
            values = require('./processing/processed_data/moves.json')
              .map(data => [
                data.gen,
                data.name,
                data.formatted_name,
                data.introduced,
                data.power,
                data.pp,
                data.accuracy,
                data.category,
                data.priority,
                data.contact,
                data.target
              ]);
            break;

          case 'ptype':
            /*
              Need (
                generation_id,
                ptype_name,
                ptype_formatted_name,
                introduced
              )
            */
            values = require('./processing/processed_data/pTypes.json')
              .map(data => [data.gen, data.name, data.formatted_name, data.introduced]);
            break;

          case 'usage_method':
            /*
              Need (
                usage_method_name
                usage_method_formatted_name
                introduced
              )
            */
            values = require('./processing/processed_data/usageMethods.json')
              .map(data => [data.name, data.formatted_name, data.introduced]);
            break;

          case 'version_group':
            /*
              Need (
                version_group_code,
                version_group_formatted_name
                introduced
              )
            */
            values = require('./processing/processed_data/versionGroups.json').map(data => [data.name, data.formatted_name, data.introduced]);
            break;

          default:
            console.log(`${tableName} unhandled.`);
        }

        db.promise().query(tableStatements.entityTables[tableName].insert, [values])
        .then( ([results, fields]) => {
          console.log(`${tableName} data inserted: ${results.affectedRows} rows.`);
        })
        .catch(console.log);
      });
    });
  }
}

const insertAbilityJunctionData = async () => {
  const relevantEntityTables = ['ability', 'ptype', 'usage_method', 'stat', 'pstatus', 'effect']

  // Get foreign key maps.
  Promise.all(relevantEntityTables.map(async (tableName) => {
    const statement = tableStatements.entityTables[tableName].create;

    console.log(`Getting foreign key map for ${tableName}.`);
    return await getForeignKeyMap(tableName);
  }))
  .then( result => {
    // Assign foreign key maps (FKM). Order is preserved by Promise.all().
    const [ability_FKM, pType_FKM, usageMethod_FKM, stat_FKM, pstatus_FKM, effect_FKM] = result;

    const abilityJunctionTables = [
      'ability_boosts_ptype',
      'ability_resists_ptype',
      'ability_boosts_usage_method',
      'ability_resists_usage_method',
      'ability_modifies_stat',
      'ability_effect',
      'ability_causes_pstatus',
      'ability_resists_pstatus',
    ];
    for (let tableName of abilityJunctionTables) {
      // Delete the tables.
      console.log(tableName);
      db.promise().query(tableStatements.abilityJunctionTables[tableName].delete)
      .then( ([results, fields]) => {
  
        console.log(`${tableName} table deleted.`);
  
      })
      .catch(console.log)
      // Insert data into the tables. No need to reset AUTO_INCREMENT values.
      .then( () => {
        
        // Determine values to be inserted.
        let values, boostOrResist, boostOrResistKey;
        const abilityData = require('./processing/processed_data/abilities.json')
        switch (tableName) {
          case 'ability_boosts_ptype':
          case 'ability_resists_ptype':
            /*
              Need (
                ability_generation_id,
                ability_id,
                ptype_generation_id,
                ptype_id,
                multiplier
              )
            */
           boostOrResist = tableName.split('_')[1];
           boostOrResistKey = boostOrResist + '_type';
            values = abilityData.reduce((acc, curr) => {
              // Get ability data from curr.
              const { gen: gen, name: abilityName, [boostOrResistKey]: typeData } = curr;
              const { ability_id: abilityID } = ability_FKM.get(makeMapKey([abilityName, gen]));
              
              return acc.concat(
                Object.keys(typeData).map(pTypeName => {
                  // We always compare entities of the same generation.
                  const { ptype_id: pTypeID } = pType_FKM.get(makeMapKey([gen, pTypeName]));
                  const multiplier = typeData[pTypeName];

                  return multiplier != 1 
                    ? [gen, abilityID, gen, pTypeID, multiplier]
                    : [];
                })
              )
            }, [])
            // Filter out empty entries
            .filter(data => data.length > 0);
            break;

          case 'ability_boosts_usage_method':
          case 'ability_resists_usage_method':
            /* 
              Need (
                ability_generation_id,
                ability_id,
                usage_method_id,
                multiplier
              ) 
            */
            boostOrResist = tableName.split('_')[1];
            boostOrResistKey = boostOrResist + '_usage_method';

            values = abilityData.reduce((acc, curr) => {
              // Get ability data from curr.
              const { gen: gen, name: abilityName, [boostOrResistKey]: usageMethodData } = curr;
              const { ability_id: abilityID } = ability_FKM.get(makeMapKey([abilityName, gen]));
              
              return acc.concat(
                Object.keys(usageMethodData).map(usageMethodName => {
                  // We always compare entities of the same generation.
                  const { usage_method_id: usageMethodID } = usageMethod_FKM.get(makeMapKey([usageMethodName]));
                  const multiplier = usageMethodData[usageMethodName];

                  return multiplier != 1 
                  ? [gen, abilityID, usageMethodID, multiplier]
                  : [];
                })
              )
            }, [])
            // Filter out empty entries
            .filter(data => data.length > 0);
            break;

          case 'ability_modifies_stat':
            /* 
              Need (
                ability_generation_id,
                ability_id,
                state_id,
                stage,
                multiplier,
                chance,
                recipient
              )
            */
            values = abilityData.reduce((acc, curr) => {
              // Get ability data from curr.
              const { gen: gen, name: abilityName, stat_modifications: statModData } = curr;
              const { ability_id: abilityID } = ability_FKM.get(makeMapKey([abilityName, gen]));

              return acc.concat(
                Object.keys(statModData).map(statName => {
                  // We always compare entities of the same generation.
                  const { stat_id: statID } = stat_FKM.get(makeMapKey([statName]));
                  let [modifier, recipient] = statModData[statName]

                  // True if stage modification, False if multiplier.
                  const stageOrMultiplier = typeof modifier == 'string';

                  // stage
                  if (stageOrMultiplier) {
                    modifier = parseInt(modifier.slice(1), 0);
                    return modifier != 0 
                    ? [gen, abilityID, statID, modifier, 1.0, 100.00, recipient]
                    : [];
                  }
                  // multiplier
                  else {
                    return modifier != 1.0
                    ? [gen, abilityID, statID, 0, modifier, 100.00, recipient]
                    : [];
                  }
                })
              )
            }, [])
            // Filter out empty entries
            .filter(data => data.length > 0);
            break;
          
          case 'ability_effect':
            /*
              Need (
                ability_generation_id,
                ability_id,
                effect_id
              )
            */
            values = abilityData.reduce((acc, curr) => {
              // Get ability data from curr.
              const { gen: gen, name: abilityName, effects: effectData } = curr;
              const { ability_id: abilityID } = ability_FKM.get(makeMapKey([abilityName, gen]));
              return acc.concat(
                Object.keys(effectData).map(effectName => {
                  // We always compare entities of the same generation.
                  const { effect_id: effectID } = effect_FKM.get(makeMapKey([effectName]));

                  // True if effect is present, False otherwise.
                  return effectData[effectName]
                  ? [gen, abilityID, effectID]
                  : [];
                })
              )
            }, [])
            // Filter out empty entries
            .filter(data => data.length > 0);
            break;

          case 'ability_causes_pstatus':
          case 'ability_resists_pstatus':
            /*
              Need (
                ability_generation_id,
                ability_id,
                pstatus_id,
                chance
              ) or (
                ability_generation_id,
                ability_id,
                pstatus_id
              )
            */
            const causeOrResist = tableName.split('_')[1];
            const causeOrResistKey = causeOrResist + '_status';

            values = abilityData.reduce((acc, curr) => {
              // Get ability data from curr.
              const { gen: gen, name: abilityName, [causeOrResistKey]: statusData } = curr;
              const { ability_id: abilityID } = ability_FKM.get(makeMapKey([abilityName, gen]));
              
              return acc.concat(
                Object.keys(statusData).map(statusName => {
                  // We always compare entities of the same generation.
                  const { pstatus_id: statusID } = pstatus_FKM.get(makeMapKey([statusName]));
                  if (causeOrResist === 'causes') {
                    // In case of causes, statusData[statusName] is probability of causing status.
                    const chance = statusData[statusName];
  
                    return chance != 0.0 
                    ? [gen, abilityID, statusID, chance]
                    : [];
                  } else {
                    // In case of resists, statusData[statusName] is either True or False.
                    return statusData[statusName] 
                    ? [gen, abilityID, statusID]
                    : [];
                  }
                })
              )
            }, [])
            // Filter out empty entries
            .filter(data => data.length > 0);
            break;

          default:
            console.log(`${tableName} unhandled.`);
        }

        db.promise().query(tableStatements.abilityJunctionTables[tableName].insert, [values])
        .then( ([results, fields]) => {
          console.log(`${tableName} data inserted: ${results.affectedRows} rows.`);
        })
        .catch(console.log);
      });
    }
  })
  .catch(console.log);
}

const insertItemJunctionData = async () => {
  const relevantEntityTables = ['item', 'ptype', 'usage_method', 'stat', 'pstatus', 'effect']

  // Get foreign key maps.
  Promise.all(relevantEntityTables.map(async (tableName) => {
    const statement = tableStatements.entityTables[tableName].create;

    console.log(`Getting foreign key map for ${tableName}.`);
    return await getForeignKeyMap(tableName);
  }))
  .then( result => {
    // Assign foreign key maps (FKM). Order is preserved by Promise.all().
    const [item_FKM, pType_FKM, usageMethod_FKM, stat_FKM, pstatus_FKM, effect_FKM] = result;

    const itemJunctionTables = [
      'natural_gift',
      'item_boosts_ptype',
      'item_resists_ptype',
      // No items boost usage methods yet, but the code is there. Uncomment if any items are introduced which boost usage methods.
      // 'item_boosts_usage_method',
      'item_resists_usage_method',
      'item_modifies_stat',
      'item_effect',
      'item_causes_pstatus',
      'item_resists_pstatus',
    ];
    for (let tableName of itemJunctionTables) {
      // Delete the tables.
      console.log(tableName);
      db.promise().query(tableStatements.itemJunctionTables[tableName].delete)
      .then( ([results, fields]) => {
  
        console.log(`${tableName} table deleted.`);
  
      })
      .catch(console.log)
      // Insert data into the tables. No need to reset AUTO_INCREMENT values.
      .then( () => {
        
        // Determine values to be inserted.
        let values, boostOrResist, boostOrResistKey;
        const itemData = require('./processing/processed_data/items.json')
        switch (tableName) {
          case 'natural_gift':
            /*
              Need (
                item_generation_id,
                item_id
                ptype_generation_id,
                ptype_id,
                item_power
              )
            */
            
            values = itemData.reduce((acc, curr) => {
              // Get item data from curr.
              const { gen: gen, name: itemName, natural_gift: naturalGiftData } = curr;

              if (!naturalGiftData) return acc;

              const { item_id: itemID } = item_FKM.get(makeMapKey([gen, itemName]));
              
              // Only berries have data for Natural Gift.
              const [pTypeName, power] = naturalGiftData;
              const { ptype_id: pTypeID } = pType_FKM.get(makeMapKey([gen, pTypeName]));

              return acc.concat([
                [gen, itemID, gen, pTypeID, power]
              ]);
            }, [])
            // Filter out empty entries
            .filter(data => data.length > 0);
            break;

          case 'item_boosts_ptype':
          case 'item_resists_ptype':
            /*
              Need (
                item_generation_id,
                item_id,
                ptype_generation_id,
                ptype_id,
                multiplier
              )
            */
            boostOrResist = tableName.split('_')[1];
            boostOrResistKey = boostOrResist + '_type';

            values = itemData.reduce((acc, curr) => {
              // Get item data from curr.
              const { gen: gen, name: itemName, [boostOrResistKey]: typeData } = curr;
              const { item_id: itemID } = item_FKM.get(makeMapKey([gen, itemName]));
              
              return acc.concat(
                Object.keys(typeData).map(pTypeName => {
                  // We always compare entities of the same generation.
                  const { ptype_id: pTypeID } = pType_FKM.get(makeMapKey([gen, pTypeName]));
                  const multiplier = typeData[pTypeName];

                  return multiplier != 1 
                    ? [gen, itemID, gen, pTypeID, multiplier]
                    : [];
                })
              )
            }, [])
            // Filter out empty entries
            .filter(data => data.length > 0);
            break;

          case 'item_boosts_usage_method':
          case 'item_resists_usage_method':
            /* 
              Need (
                item_generation_id,
                item_id,
                usage_method_id,
                multiplier
              ) 
            */
            boostOrResist = tableName.split('_')[1];
            boostOrResistKey = boostOrResist + '_usage_method';

            values = itemData.reduce((acc, curr) => {
              // Get item data from curr.
              const { gen: gen, name: itemName, [boostOrResistKey]: usageMethodData } = curr;
              const { item_id: itemID } = item_FKM.get(makeMapKey([gen, itemName]));
              
              return acc.concat(
                Object.keys(usageMethodData).map(usageMethodName => {
                  // We always compare entities of the same generation.
                  const { usage_method_id: usageMethodID } = usageMethod_FKM.get(makeMapKey([usageMethodName]));
                  const multiplier = usageMethodData[usageMethodName];

                  return multiplier != 1 
                  ? [gen, itemID, usageMethodID, multiplier]
                  : [];
                })
              )
            }, [])
            // Filter out empty entries
            .filter(data => data.length > 0);
            break;

          case 'item_modifies_stat':
            /* 
              Need (
                item_generation_id,
                item_id,
                state_id,
                stage,
                multiplier,
                chance,
                recipient
              )
            */
            values = itemData.reduce((acc, curr) => {
              // Get item data from curr.
              const { gen: gen, name: itemName, stat_modifications: statModData } = curr;
              const { item_id: itemID } = item_FKM.get(makeMapKey([gen, itemName]));

              return acc.concat(
                Object.keys(statModData).map(statName => {
                  // We always compare entities of the same generation.
                  const { stat_id: statID } = stat_FKM.get(makeMapKey([statName]));
                  let [modifier, recipient] = statModData[statName]

                  // True if stage modification, False if multiplier.
                  const stageOrMultiplier = typeof modifier == 'string';

                  // stage
                  if (stageOrMultiplier) {
                    modifier = parseInt(modifier.slice(1), 10);
                    return modifier != 0 
                    ? [gen, itemID, statID, modifier, 1.0, 100.00, recipient]
                    : [];
                  }
                  // multiplier
                  else {
                    return modifier != 1.0
                    ? [gen, itemID, statID, 0, modifier, 100.00, recipient]
                    : [];
                  }
                })
              )
            }, [])
            // Filter out empty entries
            .filter(data => data.length > 0);
            break;
          
          case 'item_effect':
            /*
              Need (
                item_generation_id,
                item_id,
                effect_id
              )
            */
            values = itemData.reduce((acc, curr) => {
              // Get item data from curr.
              const { gen: gen, name: itemName, effects: effectData } = curr;
              const { item_id: itemID } = item_FKM.get(makeMapKey([gen, itemName]));
              return acc.concat(
                Object.keys(effectData).map(effectName => {
                  // We always compare entities of the same generation.
                  const { effect_id: effectID } = effect_FKM.get(makeMapKey([effectName]));

                  // True if effect is present, False otherwise.
                  return effectData[effectName]
                  ? [gen, itemID, effectID]
                  : [];
                })
              )
            }, [])
            // Filter out empty entries
            .filter(data => data.length > 0);
            break;

          case 'item_causes_pstatus':
          case 'item_resists_pstatus':
            /*
              Need (
                item_generation_id,
                item_id,
                pstatus_id
              ) or (
                item_generation_id,
                item_id,
                pstatus_id
              )
            */
            const causeOrResist = tableName.split('_')[1];
            const causeOrResistKey = causeOrResist + '_status';

            values = itemData.reduce((acc, curr) => {
              // Get item data from curr.
              const { gen: gen, name: itemName, [causeOrResistKey]: statusData } = curr;
              const { item_id: itemID } = item_FKM.get(makeMapKey([gen, itemName]));
              
              return acc.concat(
                Object.keys(statusData).map(statusName => {
                  // We always compare entities of the same generation.
                  const { pstatus_id: statusID } = pstatus_FKM.get(makeMapKey([statusName]));

                  return statusData[statusName] 
                  ? [gen, itemID, statusID]
                  : [];
                })
              )
            }, [])
            // Filter out empty entries
            .filter(data => data.length > 0);
            break;

          default:
            console.log(`${tableName} unhandled.`);
        }

        db.promise().query(tableStatements.itemJunctionTables[tableName].insert, [values])
        .then( ([results, fields]) => {
          console.log(`${tableName} data inserted: ${results.affectedRows} rows.`);
        })
        .catch(console.log);
      });
    }
  })
  .catch(console.log);
}

const insertMoveJunctionData = async () => {
  const relevantEntityTables = ['pmove', 'pokemon', 'ptype', 'item', 'usage_method', 'stat', 'pstatus', 'effect']

  // Get foreign key maps.
  Promise.all(relevantEntityTables.map(async (tableName) => {
    const statement = tableStatements.entityTables[tableName].create;

    console.log(`Getting foreign key map for ${tableName}.`);
    return await getForeignKeyMap(tableName);
  }))
  .then( result => {
    // Assign foreign key maps (FKM). Order is preserved by Promise.all().
    const [move_FKM, pokemon_FKM, pType_FKM, item_FKM, usageMethod_FKM, stat_FKM, pstatus_FKM, effect_FKM] = result;

    const moveJunctionTables = [
      'pmove_has_ptype',
      'pmove_requires_ptype',
      'pmove_requires_pmove',
      'pmove_requires_pokemon',
      'pmove_requires_item',
      'pmove_usage_method',
      'pmove_modifies_stat',
      'pmove_effect',
      'pmove_causes_pstatus',
      'pmove_resists_pstatus',
    ];
    for (let tableName of moveJunctionTables) {
      // Delete the tables.
      console.log(tableName);
      db.promise().query(tableStatements.moveJunctionTables[tableName].delete)
      .then( ([results, fields]) => {
  
        console.log(`${tableName} table deleted.`);
  
      })
      .catch(console.log)
      // Insert data into the tables. No need to reset AUTO_INCREMENT values.
      .then( () => {
        
        // Determine values to be inserted.
        let values
        const moveData = require('./processing/processed_data/moves.json')
        switch (tableName) {
          case 'pmove_has_ptype':
            /*
              Need (
                pmove_generation_id,
                pmove_id
                ptype_generation_id,
                ptype_id
              )
            */
            
            values = moveData.reduce((acc, curr) => {
              const { gen: gen, name: moveName, type: pTypeName } = curr;

              const { pmove_id: moveID } = move_FKM.get(makeMapKey([gen, moveName]));
              
              const { ptype_id: pTypeID } = pType_FKM.get(makeMapKey([gen, pTypeName]));

              return acc.concat([
                [gen, moveID, gen, pTypeID]
              ]);
            }, [])
            // Filter out empty entries
            .filter(data => data.length > 0);
            break;

          case 'pmove_requires_ptype':
          case 'pmove_requires_pmove':
          case 'pmove_requires_pokemon':
          case 'pmove_requires_item':
            /*
              Need (
                pmove_generation_id,
                pmove_id,
                <entity>_generation_id,
                <entity>_id,
                multiplier
              ), where <entity> is ptype, pmove, pokemon, or item.
            */

            // Whether the requirement is a type, move, Pokemon, or item. Choose the foreign key map accordingly.
            // dictKey refers to how the data is stored in moves.json; we need the key to extract the requirement data from moveData.
            const entityClass = tableName.split('_')[2];
            const entity_id = entityClass + '_id';
            let entity_FKM, dictKey;
            switch (entityClass) {
              case 'ptype':
                entity_FKM = pType_FKM;
                dictKey = 'type';
                break;
              case 'pmove':
                entity_FKM = move_FKM;
                dictKey = 'move';
                break;
              case 'pokemon':
                entity_FKM = pokemon_FKM;
                dictKey = 'pokemon';
                break;
              case 'item':
                entity_FKM = item_FKM;
                dictKey = 'item'
                break;
              default:
                throw 'Invalid entity class, ' + entityClass;
            }

            values = moveData.reduce((acc, curr) => {
              // Get item data from curr.
              const { gen: gen, name: moveName, requirements: requirementData } = curr;
              const { pmove_id: moveID } = move_FKM.get(makeMapKey([gen, moveName]));

              // Check whether requirementData exists AND has the relevant entity, dictKey. If not, return.
              if (!requirementData || !requirementData[dictKey]) return acc;
              console.log(requirementData);
              
              return acc.concat(
                requirementData[dictKey].map(entityName => {
                  // All the possible entity classes come alphabetically before 'generation_id', so the order [gen, entityName] is correct.
                  const { [entity_id]: entityID } = entity_FKM.get(makeMapKey([gen, entityName]));

                  return multiplier != 1 
                    ? [gen, moveID, gen, entityID]
                    : [];
                })
              )
            }, [])
            // Filter out empty entries
            .filter(data => data.length > 0);
            break;

          case 'pmove_usage_method':
            /* 
              Need (
                pmove_generation_id,
                pmove_id,
                usage_method_id
              ) 
            */
            values = moveData.reduce((acc, curr) => {
              // Get entity data from curr.
              const { gen: gen, name: moveName, usage_method: usageMethodData } = curr;
              const { pmove_id: moveID } = move_FKM.get(makeMapKey([gen, moveName]));

              // Move has no usage method.
              if (!usageMethodData) { return acc; }
              
              return acc.concat(
                Object.keys(usageMethodData).map(usageMethodName => {
                  // We always compare entities of the same generation.
                  const { usage_method_id: usageMethodID } = usageMethod_FKM.get(makeMapKey([usageMethodName]));
                  
                  // A move may lose a usage method. 
                  const present = usageMethodData[usageMethodName];

                  return present
                  ? [gen, moveID, usageMethodID]
                  : [];
                })
              )
            }, [])
            // Filter out empty entries
            .filter(data => data.length > 0);
            break;

          case 'pmove_modifies_stat':
            /* 
              Need (
                pmove_generation_id,
                pmove_id,
                state_id,
                stage,
                multiplier,
                chance,
                recipient
              )
            */
            values = moveData.reduce((acc, curr) => {
              // Get move data from curr.
              const { gen: gen, name: moveName, stat_modifications: statModData } = curr;
              const { pmove_id: moveID } = move_FKM.get(makeMapKey([gen, moveName]));

              return acc.concat(
                Object.keys(statModData).map(statName => {
                  // We always compare entities of the same generation.
                  const { stat_id: statID } = stat_FKM.get(makeMapKey([statName]));
                  let [modifier, recipient, chance] = statModData[statName]

                  // True if stage modification, False if multiplier.
                  const stageOrMultiplier = typeof modifier == 'string';
                  
                  // stage
                  if (stageOrMultiplier) {
                    modifier = parseInt(modifier.slice(1), 10);
                    return modifier != 0 
                    ? [gen, moveID, statID, modifier, 1.0, chance, recipient]
                    : [];
                  }
                  // multiplier
                  else {
                    return modifier != 1.0
                    ? [gen, moveID, statID, 0, modifier, chance, recipient]
                    : [];
                  }
                })
              )
            }, [])
            // Filter out empty entries
            .filter(data => data.length > 0);
            break;
          
          case 'pmove_effect':
            /*
              Need (
                pmove_generation_id,
                pmove_id,
                effect_id
              )
            */
            values = moveData.reduce((acc, curr) => {
              // Get move data from curr.
              const { gen: gen, name: moveName, effects: effectData } = curr;
              const { pmove_id: moveID } = move_FKM.get(makeMapKey([gen, moveName]));
              return acc.concat(
                Object.keys(effectData).map(effectName => {
                  // We always compare entities of the same generation.
                  const { effect_id: effectID } = effect_FKM.get(makeMapKey([effectName]));

                  // True if effect is present, False otherwise.
                  return effectData[effectName]
                  ? [gen, moveID, effectID]
                  : [];
                })
              )
            }, [])
            // Filter out empty entries
            .filter(data => data.length > 0);
            break;

          case 'pmove_causes_pstatus':
          case 'pmove_resists_pstatus':
            /*
              Need (
                pmove_generation_id,
                pmove_id,
                pstatus_id,
                chance
              ) or (
                pmove_generation_id,
                pmove_id,
                pstatus_id
              )
            */
              const causeOrResist = tableName.split('_')[1];
              const causeOrResistKey = causeOrResist + '_status';
  
              values = moveData.reduce((acc, curr) => {
                // Get move data from curr.
                const { gen: gen, name: moveName, [causeOrResistKey]: statusData } = curr;
                const { pmove_id: moveID } = move_FKM.get(makeMapKey([gen, moveName]));
                
                return acc.concat(
                  Object.keys(statusData).map(statusName => {
                    // We always compare entities of the same generation.
                    const { pstatus_id: statusID } = pstatus_FKM.get(makeMapKey([statusName]));
                    if (causeOrResist === 'causes') {
                      // In case of causes, statusData[statusName] is probability of causing status.
                      const chance = statusData[statusName];
    
                      return chance != 0.0 
                      ? [gen, moveID, statusID, chance]
                      : [];
                    } else {
                      // In case of resists, statusData[statusName] is either True or False.
                      return statusData[statusName] 
                      ? [gen, moveID, statusID]
                      : [];
                    }
                  })
                )
              }, [])
              // Filter out empty entries
              .filter(data => data.length > 0);
              break;

          default:
            console.log(`${tableName} unhandled.`);
        }

        db.promise().query(tableStatements.moveJunctionTables[tableName].insert, [values])
        .then( ([results, fields]) => {
          console.log(`${tableName} data inserted: ${results.affectedRows} rows.`);
        })
        .catch(console.log);
      });
    }
  })
  .catch(console.log);
}

/*
  Given a table name, tableName, with an AUTO_INCREMENT column, select identifying columns for the purpose of data insertion. E.g.

    If tableName = 'pokemon', select 'pokemon_id', the AUTO_INCREMENT column, as well as 'generation_id' and 'pokemon_name'. 
*/
const getIdentifyingColumnNames = (tableName) => {
  let identifyingColumns;
  switch(tableName) {
    case 'pdescription':
      identifyingColumns = 'pdescription_index, pdescription_type, entity_name';
      break;
    case 'sprite':
      identifyingColumns = 'sprite_path, entity_name';
      break;
    case 'version_group':
      identifyingColumns = 'version_group_code';
      break;
    case 'ability': 
    case 'effect':
    case 'item':
    case 'pmove':
    case 'pokemon':
    case 'pstatus':
    case 'ptype':
    case 'stat':
    case 'usage_method':
      identifyingColumns = tableName + '_name';
      break;
    default:
      throw `Invalid table name: ${tableName}.`
  } 

  return identifyingColumns;
}

/* 
  Given a table name, tableName, with an AUTO_INCREMENT column, select the AUTO_INCREMENT column, as well as any other identifying columns for the purpose of data insertion. E.g.

    If tableName = 'pokemon', select 'pokemon_id', the AUTO_INCREMENT column, as well as 'generation_id' and 'pokemon_name'. 
    
  We will use this to build Maps for inserting into junction tables. E.g.
  
    To insert rows into 'pokemon_ability', we use getIdentifyingColumns('pokemon') to (in another function) build a map which sends (pokemon_name, generation_id) to (generation_id, pokemon_id), which is one of the foreign keys for 'pokemon_ability'. 
*/
const queryIdentifyingColumns = async (tableName) => {
  // Whether the entity corresponding to tableName is generation-dependent.
  let hasGenID;
  switch (tableName) {
    case 'pdescription':
    case 'sprite':
    case 'version_group':
    case 'stat':
    case 'pstatus':
    case 'usage_method':
    case 'effect':
      hasGenID = false;
      break;
    default:
      hasGenID = true;
  }

  // The column of tableName which AUTO_INCREMENTs.
  const autoIncColumn = `${tableName}_id`;

  // The other columns of tableName which help identify a given row for the purpose of data insertion.
  const identifyingColumns = getIdentifyingColumnNames(tableName);

  return hasGenID 
    ? db.promise().query(tableStatements.entityTables[tableName].select(`generation_id, ${autoIncColumn}, ${identifyingColumns}`))
    : db.promise().query(tableStatements.entityTables[tableName].select(`${autoIncColumn}, ${identifyingColumns}`));
};

/*
  Given a table name, tableName, build a Map, foreignKeyMap, which maps identifying column values to primary key column values. E.g.

    If tableName = 'pokemon', foreignKeyMap maps { generation_id, pokemon_name } to { pokemon_id, generation_id }.

  This will facilitate inserting data into junction tables, indeed into any table with a foreign key.
*/
const getForeignKeyMap = async (tableName) => {
  const foreignKeyMap = new Map();
  const results = await queryIdentifyingColumns(tableName).then( ([results, fields]) => {
    // Maps values in identifying columns of tableName to values in primary key columns of tableName.

    results.map(row => {
      // Check whether tableName depends on 'generation'.
      const hasGenID = row.generation_id != undefined;

      // Name of the AUTO_INCREMENT column.
      const autoIncColumnName = `${tableName}_id`;
      const autoIncColumnValue = row[autoIncColumnName];

      // Compute the primary key column(s).
      const primaryKeyColumns = { [autoIncColumnName]: autoIncColumnValue }
      if (hasGenID) primaryKeyColumns.generation_id = row.generation_id

      // Get the non-AUTO_INCREMENT columns from the given row.
      const identifyingColumns = Object.keys(row).reduce((acc, curr) => {
        // Ignore AUTO_INCREMENT column.
        if (curr === `${tableName}_id`) return acc;

        return {
          ...acc,
          [curr]: row[curr],
        }
      }, {});

      // We can't use objects or arrays as keys for a Map, so we need to use a string (AGHHHHHHHHHHHHHHHHHHHHHHHHHH). Since we aren't guaranteed the order of the object keys, we sort them alphabetically.
      const identifyingColumnsString = Object.keys(identifyingColumns)
        .sort()
        .reduce((acc, curr) => {
          return acc + identifyingColumns[curr] + ' ';
        }, '')
        // Slice to remove space.
        .slice(0, -1);
      foreignKeyMap.set(identifyingColumnsString, primaryKeyColumns);
    });
  });

  return foreignKeyMap;
}

const makeMapKey = arr => arr.join(' ');

// createTables();
// insertBasicEntities();
// insertGenDependentEntities();
// insertAbilityJunctionData();
// insertItemJunctionData();
insertMoveJunctionData();
