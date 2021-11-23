require('dotenv').config();
const mysql = require('mysql2');
const tableStatements = require('./sql/index.js');
const { timeElapsed } = require('./utils.js');


const db = mysql.createPool({
  host: process.env.DB_HOST,
  user: process.env.DB_USERNAME,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME,
  connectionLimit: 30,
  connectTimeout: 20000,
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

/* 1. Reset tables. */
// #region
const { prepareLearnsetTableForDrop, dropTables, createTables } = require('./utils.js');

// Drop tables if they exist, then recreate them.
const resetTables = async () => {
  console.log('Resetting tables...\n');
  let timer = new Date().getTime();
  let now;

  return prepareForDrop(db)
    .then( () => {

      now = new Date().getTime();
      console.log('Took', Math.floor((now - timer) / 1000), 'seconds.\n');
      timer = now;

      console.log('\nDropping tables...\n')
      return dropTables(db, tableStatements);
    })
    .then( () => {

      now = new Date().getTime();
      console.log('Took', Math.floor((now - timer) / 1000), 'seconds.\n');
      timer = now;

      console.log('\nCreating tables...\n')
      return createTables(db, tableStatements);
    })
    .then( () => {

      now = new Date().getTime();
      console.log('Took', Math.floor((now - timer) / 1000), 'seconds.\n');
      timer = now;

      console.log('\nFinished resetting tables!\n');
    })
    .catch(console.log);
}

// resetTables();

// #endregion

/* 2. Insert data for basic entities. */ 
// #region
const { resetBasicEntityTables } = require('./utils.js');

const reinsertBasicEntityTables = async () => {
  console.log('Re-inserting data for basic entities...\n');
  let timer = new Date().getTime();

  return resetBasicEntityTables(db, tableStatements)
    .then( () => {
      timer = timeElapsed(timer);
    })
    .then ( () => {
      console.log('\nFinished inserting data for basic entities!\n');
    })
    .catch(console.log);
}

// reinsertBasicEntityTables();

// #endregion

/* 3. Insert data for gen-dependent entities. */
// #region
const { resetGenDependentEntityTables } = require('./utils.js');

const reinsertGenDependentEntityTables = async () => {
  console.log('Re-inserting data for gen-dependent entities...\n');
  let timer = new Date().getTime();

  return resetGenDependentEntityTables(db, tableStatements)
    .then( () => {
      timer = timeElapsed(timer);
    })
    .then ( () => {
      console.log('\nFinished inserting data for gen-dependent entities!\n');
    })
    .catch(console.log);
}

// reinsertGenDependentEntityTables();

// #endregion

/* 4. Insert data for ability junction tables. */
// #region
const { resetAbilityJunctionTables } = require('./utils.js');

const reinsertAbilityJunctionTables = async () => {
  console.log('Re-inserting data for ability junction tables...\n');
  let timer = new Date().getTime();

  return resetAbilityJunctionTables(db, tableStatements)
    .then( () => {
      timer = timeElapsed(timer);
    })
    .then ( () => {
      console.log('\nFinished inserting data for ability junction tables!\n');
    })
    .catch(console.log);
}

// reinsertAbilityJunctionTables();

// #endregion

/* 5. Insert data for item junction tables. */
// #region
const { resetItemJunctionTables } = require('./utils.js');

const reinsertItemJunctionTables = async () => {
  console.log('Re-inserting data for item junction tables...\n');
  let timer = new Date().getTime();

  return resetItemJunctionTables(db, tableStatements)
    .then( () => {
      timer = timeElapsed(timer);
    })
    .then ( () => {
      console.log('\nFinished inserting data for item junction tables!\n');
    })
    .catch(console.log);
}

reinsertItemJunctionTables();

// Inserts data for item junction tables.
const insertItemJunctionData = async () => {
  const relevantEntityTables = ['item', 'ptype', 'usage_method', 'stat', 'pstatus', 'effect', 'pokemon']

  // Get foreign key maps.
  Promise.all(relevantEntityTables.map(async (tableName) => {
    const statement = tableStatements.entityTables[tableName].create;

    console.log(`Getting foreign key map for ${tableName}.`);
    return await getForeignKeyMap(tableName);
  }))
  .then( result => {
    // Assign foreign key maps (FKM). Order is preserved by Promise.all().
    const [item_FKM, pType_FKM, usageMethod_FKM, stat_FKM, pstatus_FKM, effect_FKM, pokemon_FKM] = result;

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
      'item_requires_pokemon',
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
          
          case 'item_requires_pokemon':
            /*
              Need (
                item_generation_id,
                item_id,
                pokemon_generation_id,
                pokemon_id
              )
            */
            
              values = itemData.reduce((acc, curr) => {
                // Get item data from curr.
                const { gen: gen, name: itemName, pokemon_specific: pokemonData } = curr;
                const { item_id: itemID } = item_FKM.get(makeMapKey([gen, itemName]));

                
                // If item is not Pokemon-specific
                if (!pokemonData) { return acc; }
                
                return acc.concat(
                  Object.keys(pokemonData).map(pokemonName => {
                    // We always compare entities of the same generation.
                    const { pokemon_id: pokemonID } = pokemon_FKM.get(makeMapKey([gen, pokemonName]));
  
                    return pokemonData[pokemonName] 
                    ? [gen, itemID, gen, pokemonID]
                    : [];
                  })
                )
              }, [])
              // Filter out empty entries
              .filter(data => data.length > 0);
              break;
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

  return;
}

// Inserts data for move junction tables.
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
              
              return acc.concat(
                requirementData[dictKey].map(entityName => {
                  // All the possible entity classes come alphabetically before 'generation_id', so the order [gen, entityName] is correct.
                  if (entity_FKM.get(makeMapKey([gen, entityName])) == undefined) {
                    console.log(requirementData, entityName);
                  }
                  const { [entity_id]: entityID } = entity_FKM.get(makeMapKey([gen, entityName]));

                  return [gen, moveID, gen, entityID]
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
      })
      .catch(console.log);;
    }
  })
  .catch(console.log);

  return;
}

// Inserts data for move junction tables.
const insertPokemonJunctionData = async () => {
  const relevantEntityTables = ['pokemon', 'ptype', 'ability']

  // Get foreign key maps.
  Promise.all(relevantEntityTables.map(async (tableName) => {
    const statement = tableStatements.entityTables[tableName].create;

    console.log(`Getting foreign key map for ${tableName}.`);
    return await getForeignKeyMap(tableName);
  }))
  .then( result => {
    // Assign foreign key maps (FKM). Order is preserved by Promise.all().
    const [pokemon_FKM, pType_FKM, ability_FKM] = result;

    const pokemonJunctionTables = [
      'pokemon_evolution',
      'pokemon_form',
      'pokemon_ptype',
      'pokemon_ability',
    ];
    for (let tableName of pokemonJunctionTables) {
      // Delete the tables.
      db.promise().query(tableStatements.pokemonJunctionTables[tableName].delete)
      .then( ([results, fields]) => {
  
        console.log(`${tableName} table deleted.`);
  
      })
      .catch(console.log)
      // Insert data into the tables. No need to reset AUTO_INCREMENT values.
      .then( () => {
        
        // Determine values to be inserted.
        let values
        const pokemonData = require('./processing/processed_data/pokemon.json')
        switch (tableName) {
          case 'pokemon_evolution':
            /*
              Need (
                prevolution_generation_id,
                prevolution_id,
                evolution_generation_id,
                evolution_id,
                evolution_method
              )
            */

            values = pokemonData.reduce((acc, curr) => {
              const { gen: gen, name: pokemonName, evolves_to: evolvesToData } = curr;

              const { pokemon_id: pokemonID } = pokemon_FKM.get(makeMapKey([gen, pokemonName]));
              
              return acc.concat(
                Object.keys(evolvesToData).map(evolutionName => {
                  const { pokemon_id: evolutionID } = pokemon_FKM.get(makeMapKey([gen, evolutionName]));
                  
                  const evolutionMethod = evolvesToData[evolutionName];

                  return [gen, pokemonID, gen, evolutionID, evolutionMethod];
                })
              );
            }, [])
            // Filter out empty entries
            .filter(data => data.length > 0);
            break;
          
          case 'pokemon_form':
            /*
              Need (
                base_form_generation_id,
                base_form_id,
                form_generation_id,
                form_id,
                form_class
              )
            */

              values = pokemonData.reduce((acc, curr) => {
                const { gen: gen, name: pokemonName, form_data: formData } = curr;
  
                const { pokemon_id: pokemonID } = pokemon_FKM.get(makeMapKey([gen, pokemonName]));
                
                return acc.concat(
                  Object.keys(formData).map(formName => {
                    const { pokemon_id: formID } = pokemon_FKM.get(makeMapKey([gen, formName]));
                    
                    const formClass = formData[formName];
  
                    return [gen, pokemonID, gen, formID, formClass];
                  })
                );
              }, [])
              // Filter out empty entries
              .filter(data => data.length > 0);
              break;

          case 'pokemon_ptype':
            /*
              Need (
                pokemon_generation_id,
                pokemon_id,
                ptype_generation_id,
                ptype_id
              )
            */
            
            values = pokemonData.reduce((acc, curr) => {
              const { gen: gen, name: pokemonName, type_1: pType1Name, type_2: pType2Name } = curr;

              const { pokemon_id: pokemonID } = pokemon_FKM.get(makeMapKey([gen, pokemonName]));
              
              // Filter out empty type name, e.g. for monotype Pokemon.
              return acc.concat(
                [pType1Name, pType2Name]
                .filter(pTypeName => pTypeName.length > 0)
                .map(pTypeName => {
                  const { ptype_id: pTypeID } = pType_FKM.get(makeMapKey([gen, pTypeName]));
                  
                  return [gen, pokemonID, gen, pTypeID];
                })
              );
            }, [])
            // Filter out empty entries
            .filter(data => data.length > 0);
            break;

          case 'pokemon_pmove': 
            /*
              Need (
                pokemon_generation_id,
                pokemon_id,
                pmove_generation_id,
                pmove_id,
                learn_method
              )
            */
            
            values = pokemonData.reduce((acc, curr) => {
              const { gen: gen, name: pokemonName, learnset: learnsetData } = curr;

              const { pokemon_id: pokemonID } = pokemon_FKM.get(makeMapKey([gen, pokemonName]));
              
              return acc.concat(
                Object.keys(learnsetData).reduce((innerAcc, moveName)=> {
                  const { pmove_id: moveID } = move_FKM.get(makeMapKey([gen, moveName]));
                  
                  return innerAcc.concat([
                    // We can have multiple different learn methods within the same generation.
                    learnsetData[moveName].map(learnMethod => {
                      return [gen, pokemonID, gen, moveID, learnMethod];
                    })
                  ]);
                }, [])
              );
            }, [])
            // Filter out empty entries
            .filter(data => data.length > 0);
            break;

          case 'pokemon_ability':
            /*
              Need (
                pokemon_generation_id,
                pokemon_id,
                ability_generation_id,
                ability_id,
                ability_slot
              )
            */
            
            values = pokemonData.reduce((acc, curr) => {
              const { gen: gen, name: pokemonName, ability_1: ability1Name, ability_2: ability2Name, ability_hidden: abilityHiddenName } = curr;

              // No abilities in Gen 3
              if (gen < 3) { return acc; }

              const { pokemon_id: pokemonID } = pokemon_FKM.get(makeMapKey([gen, pokemonName]));
              
              // Filter out empty ability slots, e.g. for Mimikyu, who only has one ability.
              return acc.concat(
                [ability1Name, ability2Name, abilityHiddenName]
                .filter(abilityName => abilityName && abilityName.length > 0)
                .map(abilityName => {
                  const { ability_id: abilityID } = ability_FKM.get(makeMapKey([abilityName, gen]));

                  let abilitySlot;
                  switch (abilityName) {
                    case ability1Name:
                      abilitySlot = '1';
                      break;
                    case ability2Name:
                      abilitySlot = '2';
                      break;
                    case abilityHiddenName:
                      abilitySlot = 'hidden';
                      break;
                  }
                  
                  return [gen, pokemonID, gen, abilityID, abilitySlot];
                })
              );
            }, [])
            // Filter out empty entries
            .filter(data => data.length > 0);
            break;

          default:
            console.log(`${tableName} unhandled.`);
        }

        db.promise().query(tableStatements.pokemonJunctionTables[tableName].insert, [values])
        .then( ([results, fields]) => {
          console.log(`${tableName} data inserted: ${results.affectedRows} rows.`);
        })
        .catch(console.log);
      })
      .catch(console.log);;
    }
  })
  .catch(console.log);

  return;
}

// Inserts data for Pokemon learnsets.
const insertPokemonLearnsetData = async () => {
  const relevantEntityTables = ['pokemon', 'pmove']

  // Get foreign key maps.
  Promise.all(relevantEntityTables.map(async (tableName) => {
    const statement = tableStatements.entityTables[tableName].create;

    console.log(`Getting foreign key map for ${tableName}.`);
    return await getForeignKeyMap(tableName);
  }))
  .then( result => {
    // Assign foreign key maps (FKM). Order is preserved by Promise.all().
    const [pokemon_FKM, move_FKM] = result;

    console.log('Deleting pokemon_pmove table...');

    // Truncate the table rather than delete, since there are so many rows.
    db.promise().query(tableStatements.pokemonJunctionTables['pokemon_pmove'].delete)
    .then( ([results, fields]) => {

      console.log(`pokemon_pmove table deleted.`);

    })
    .catch(console.log)
    // Insert data into the tables. No need to reset AUTO_INCREMENT values.
    .then( () => {

      // Determine values to be inserted.
      let values
      const pokemonData = require('./processing/processed_data/pokemon.json')

      // Number of Pokemon to process at each step.
      const chunk = 250;

      for (let i = 0; i < pokemonData.length; i += chunk) {
        /*
          Need (
            pokemon_generation_id,
            pokemon_id,
            pmove_generation_id,
            pmove_id,
            learn_method
          )
        */
        values = pokemonData.slice(i, Math.min(i + chunk, pokemonData.length)).reduce((acc, curr) => {
          const { gen: gen, name: pokemonName, learnset: learnsetData } = curr;

          const { pokemon_id: pokemonID } = pokemon_FKM.get(makeMapKey([gen, pokemonName]));
          
          return acc.concat(
            Object.keys(learnsetData).reduce((innerAcc, moveName)=> {
              const { pmove_id: moveID } = move_FKM.get(makeMapKey([gen, moveName]));
              
              return innerAcc.concat(
                // We can have multiple different learn methods within the same generation.
                learnsetData[moveName].map(learnMethod => {
                  return [gen, pokemonID, gen, moveID, learnMethod];
                })
              );
            }, [])
          );
        }, [])
        // Filter out empty entries
        .filter(data => data.length > 0);

        console.log('Inserting rows', i, 'to', Math.min(i + chunk, pokemonData.length));

        db.promise().query(tableStatements.pokemonJunctionTables['pokemon_pmove'].insert, [values])
        .then( ([results, fields]) => {
          console.log(`pokemon_pmove data inserted: ${results.affectedRows} rows.`);
      })
      .catch(console.log);
      
      }
    })
    .catch(console.log);
    
  })
  .catch(console.log);

  return;
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

// dropTables();
// createTables();
// insertBasicEntities();
// insertGenDependentEntities();
// insertAbilityJunctionData();
// insertItemJunctionData();
// insertMoveJunctionData();
// insertPokemonJunctionData();
// insertPokemonLearnsetData();
