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

const timeElapsed = timer => {
  let now = new Date().getTime();
  console.log('Took', Math.floor((now - timer) / 1000), 'seconds.\n');
  timer = now;
  return timer;
}

// CREATING AND DROPPING TABLES
// #region

// Drops foreign keys and indices from pokemon_pmove to facilitate deleting data, as pokemon_pmove has the most rows by far.
const prepareLearnsetTableForDrop = async (db) => {
  console.log('Dropping foreign keys and indices from pokemon_pmove--if they exist--to improve DELETE performance...');

  // Delete foreign keys, if they exist; the index opposite_pokemon_pmove references them, so we must delete them first.
  await db.promise()
    // Selects foreign keys
    .query(`
    SELECT * FROM information_schema.TABLE_CONSTRAINTS 
    WHERE information_schema.TABLE_CONSTRAINTS.CONSTRAINT_TYPE = 'FOREIGN KEY' 
    AND information_schema.TABLE_CONSTRAINTS.TABLE_SCHEMA = '${process.env.DB_NAME}'
    AND information_schema.TABLE_CONSTRAINTS.TABLE_NAME = 'pokemon_pmove'
    `)
    .then( ([results, fields]) => {
      if (results.length == 0) { return; }
      
      // Deletes each returned foreign key.
      return Promise.all(
        results.map(result => {
          return db.promise().query(`ALTER TABLE pokemon_pmove DROP FOREIGN KEY ${result.CONSTRAINT_NAME}`);
        })
      )
    })
    .then( () => console.log('Foreign keys deleted from pokemon_pmove.'))
    .catch(console.log)

  // Deletes the indices.
  await Promise.all([
    db.promise().query(`DROP INDEX opposite_pokemon_pmove ON pokemon_pmove`)
      .then()
      .catch( err => {
        // Index doesn't exist.
        if (err.errno == 1091) console.log('Index doesn\'t exist. Moving on...');
        // Table doesn't exist.
        else if (err.errno == 1146) console.log('Table doesn\'t exist. Moving on...');
        else console.log(err);
      }),
    db.promise().query(`ALTER TABLE pokemon_pmove DROP PRIMARY KEY`)
      .then()
      .catch( err => {
        // Index doesn't exist.
        if (err.errno == 1091) console.log('Primary key index doesn\'t exist. Moving on...');
        // Table doesn't exist.
        else if (err.errno == 1146) console.log('Table doesn\'t exist. Moving on...');
        else console.log(err);
      })
  ])
  .then( () => console.log('Indices deleted from pokemon_pmove.'));

  return;
}

// Drops all tables, if they exist.
const dropTables = async (db, tableStatements) => {
  // Drop junction tables.
  await Promise.all(
    Object.keys(tableStatements)
      .filter(tableGroup => tableGroup != 'entityTables')
      .map(tableGroup => {
        return Promise.all(
          Object.keys(tableStatements[tableGroup]).map(tableName=> {
            const statement = tableStatements[tableGroup][tableName].drop;
            
            return db.promise().query(statement).then( () => console.log(`${tableName} dropped.`));
          })
        );
      })
    )
    .then( () => console.log('\nJunction tables dropped.\n'))
    .catch(console.log);

  // Drop basic entity tables.
  await Promise.all(Object.keys(tableStatements.entityTables)
    .filter(tableName => tableName !== 'generation').map(tableName => {
      const statement = tableStatements.entityTables[tableName].drop;

      return db.promise().query(statement)
        .then( () => console.log(`${tableName} dropped.`));
    }))
    .then( () => console.log(`\nEntity tables dropped.\n`))
    .catch(console.log);

  // Finally, drop generation table.
  return await db.promise().query(tableStatements.entityTables.generation.drop)
    .then( () => console.log('\ngeneration table dropped.\n'))
    .catch(console.log);
}

// Creates all tables, if they don't already exist.
const createTables = async (db, tableStatements) => {
  // Create generation table, which most other tables reference.
  await db.promise().query(tableStatements.entityTables.generation.create)
    .then( () => console.log('\ngeneration table created.\n'))
    .catch(console.log);

  // Create basic entity tables, e.g. stat, pokemon, pmove, which the junction tables reference.
  await Promise.all(Object.keys(tableStatements.entityTables)
    .filter(tableName => tableName !== 'generation').map(tableName => {
      const statement = tableStatements.entityTables[tableName].create;

      return db.promise().query(statement)
        .then( () => console.log(`${tableName} created.`));
    }))
    .then( () => console.log(`\nEntity tables created.\n`))
    .catch(console.log);
  
  // Create junction tables.
  return await Promise.all(
    Object.keys(tableStatements)
      .filter(tableGroup => tableGroup != 'entityTables')
      .map(tableGroup => {
        return Promise.all(
          Object.keys(tableStatements[tableGroup]).map(tableName=> {
            const statement = tableStatements[tableGroup][tableName].create;
            
            return db.promise().query(statement).then( () => console.log(`${tableName} created.`));
          })
        );
      })
  )
  .then( () => console.log('\nJunction tables created.\n'))
  .catch(console.log);
};

// #endregion

// INSERTING DATA
// #region


/* 
  DELETE FROM tables for generation-independent entities, then INSERT INTO those tables. 
  
  WARNING: Will cause data in most other tables, which depend on generation, to be deleted as well. 
*/
const resetGenDependentEntityTables = async(db, tableStatements) => {
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
  return resetTableGroup(db, tableStatements, entityTableNames)
}

/*
  DELETE FROM tables for generation-dependent entities, then INSERT INTO those tables.

  WARNING: Will cause data in the junction tables to be deleted.
*/
const resetBasicEntityTables = async(db, tableStatements) => {
  // TODO add sprites
  const basicEntityTableNames = [
    'generation',
    'pdescription',
    'pstatus',
    'stat',
  ];
  return await resetTableGroup(db, tableStatements, basicEntityTableNames)
}

/*

*/
const resetAbilityJunctionTables = async(db, tableStatements) => {
  /*
    [
      'ability_boosts_ptype',
      'ability_resists_ptype',
      'ability_boosts_usage_method',
      'ability_resists_usage_method',
      'ability_modifies_stat',
      'ability_effect',
      'ability_causes_pstatus',
      'ability_resists_pstatus',
    ]
  */
  const abilityJunctionTableNames = Object.keys(tableStatements.abilityJunctionTables);

  /* 
    Unpacks as:

      [ability_FKM, pType_FKM, usageMethod_FKM, stat_FKM, pstatus_FKM, effect_FKM]

  */ 
  const foreignKeyMaps = await Promise.all(
    // Array of relevant entity tableNames.
    ['ability', 'ptype', 'usage_method', 'stat', 'pstatus', 'effect']
    .map(async (tableName) => {
        console.log(`Getting foreign key map for ${tableName}...`)
        return await getForeignKeyMap(db, tableStatements, tableName);
      })
  );
  
  const abilityData = require('./processing/processed_data/abilities.json');

  return await resetTableGroup(
    db,
    tableStatements,
    abilityJunctionTableNames,
    'abilityJunctionTables',
    abilityData,
    foreignKeyMaps);
}

const resetItemJunctionTables = async(db, tableStatements) => {
  /*
    [
      'natural_gift',
      'item_boosts_ptype',
      'item_resists_ptype',
      'item_boosts_usage_method',
      'item_resists_usage_method',
      'item_modifies_stat',
      'item_effect',
      'item_causes_pstatus',
      'item_resists_pstatus',
      'item_requires_pokemon',
    ]
  */
  const itemJunctionTableNames = Object.keys(tableStatements.itemJunctionTables)
    // Currently no items boost usage methods; remove if a new game adds it.
    .filter(tableName => tableName != 'item_boosts_usage_method');

  /* 
    Unpacks as:

      [item_FKM, pType_FKM, usageMethod_FKM, stat_FKM, pstatus_FKM, effect_FKM, pokemon_FKM]

  */ 
  const foreignKeyMaps = await Promise.all(
    // Array of relevant entity tableNames.
    ['item', 'ptype', 'usage_method', 'stat', 'pstatus', 'effect', 'pokemon']
    .map(async (tableName) => {
        console.log(`Getting foreign key map for ${tableName}...`)
        return await getForeignKeyMap(db, tableStatements, tableName);
      })
  );
  
  const itemData = require('./processing/processed_data/items.json');

  return await resetTableGroup(
    db,
    tableStatements,
    itemJunctionTableNames,
    'itemJunctionTables',
    itemData,
    foreignKeyMaps);
}

const resetTableGroup = async(
  db,
  tableStatements,
  tableNameArr,
  tableGroup,
  entityData,
  foreignKeyMaps,
) => {
  /*
    1. DELETE FROM tableName.
    2. Reset AUTO_INCREMENT counter for tableName.
    3. INSERT INTO tableName.
  */
  return await Promise.all(
    tableNameArr.map(async (tableName) => {
      // DELETE FROM tableName.
      await deleteTableRows(db, tableStatements, tableGroup, tableName);

      // Reset AUTO_INCREMENT counter for tableName.
      await resetAutoIncrement(db, tableStatements, tableGroup, tableName);

      // INSERT INTO tableName.
      const values = getValuesForTable(
        tableName,
        tableGroup,
        entityData,
        foreignKeyMaps
      );

      return await db.promise()
        .query(tableStatements[tableGroup][tableName].insert, [values])
        .then( ([results, fields]) => {
          console.log(`${tableName} data inserted: ${results.affectedRows} rows.\n`);
        })
        .catch(console.log);
    })
  )
  .catch(console.log);
}

// #endregion


// DASDSADSADSA
// #region
const deleteTableRows = async(db, tableStatements, tableGroup, tableName) => {
  return db.promise().query(tableStatements[tableGroup][tableName].delete)
    .then( () => console.log(`${tableName} table deleted.`))
    .catch(console.log);
}

const resetAutoIncrement = async(db, tableStatements, tableGroup, tableName) => {
  return db.promise().query(tableStatements[tableGroup][tableName].reset_auto_inc)
    .then( () => console.log(`Reset AUTO_INCREMENT counter for ${tableName} table.`))
    .catch(console.log)
}

const getValuesForTable = (
  tableName, 
  tableGroup, 
  entityData, 
  foreignKeyMaps
) => {
  // 
  // Declarations for foreign key maps.
  let ability_FKM, item_FKM, pokemon_FKM, pType_FKM, usageMethod_FKM, stat_FKM, pstatus_FKM, effect_FKM;
  // Declarations for entity data.
  let abilityData, itemData;
  switch(tableGroup) {
    case 'abilityJunctionTables':
      [ability_FKM, pType_FKM, usageMethod_FKM, stat_FKM, pstatus_FKM, effect_FKM] = foreignKeyMaps;
      abilityData = entityData;
      break;

    case 'itemJunctionTables':
      [item_FKM, pType_FKM, usageMethod_FKM, stat_FKM, pstatus_FKM, effect_FKM, pokemon_FKM] = foreignKeyMaps;
      itemData = entityData;
      break;

    default: 
      console.log('No foreign key maps necessary for this table group.')
  }

  let values, boostOrResist, boostOrResistKey, causeOrResist, causeOrResistKey;
  switch(tableName) {
    /*
      BASIC ENTITIES
    */
    case 'generation':
      /*
        Need (
          generation_id,
          generation_code
        )
      */
      values = GEN_ARRAY;
      break;
    
    case 'pdescription':
      /*
        Need (
          pdescription_text,
          pdescription_index,
          pdescription_type,
          entity_name
        )
      */
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
    
    case 'pstatus':
      /*
        Need (
          pstatus_name,
          pstatus_formatted_name
        )
      */
      values = require('./processing/processed_data/statuses.json').map(data => [data.name, data.formatted_name]);
      break;
    
    case 'stat':
      /*
        Need (
          stat_name,
          stat_formatted_name
        )
      */
      values = require('./processing/processed_data/stats.json').map(data => [data.name, data.formatted_name]);
      break;

    /*
      GENERATION-DEPENDENT ENTITIES
    */
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

    /*
      ABILITY JUNCTION TABLES
    */
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
      causeOrResist = tableName.split('_')[1];
      causeOrResistKey = causeOrResist + '_status';

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

    /*
      ITEM JUNCTION TABLES
    */
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

      
    // No items boost usage methods yet, but the code is there. Uncomment if any items are introduced which boost usage methods.
    // case 'item_boosts_usage_method':
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
      causeOrResist = tableName.split('_')[1];
      causeOrResistKey = causeOrResist + '_status';

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
    default:
        console.log(`${tableName} unhandled.`);
  }
  return values;
}



// #endregion

// FOREIGN KEY MAPS AND KEYS
// #region

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
const queryIdentifyingColumns = async (db, tableStatements, tableName) => {
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
const getForeignKeyMap = async (db, tableStatements, tableName) => {
  const foreignKeyMap = new Map();
  const results = await queryIdentifyingColumns(db, tableStatements,tableName).then( ([results, fields]) => {
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

// #endregion


module.exports = {
  // Miscellaneous utilities
  NUMBER_OF_GENS,
  GEN_ARRAY,
  timeElapsed,
  // Create and drop statements
  prepareLearnsetTableForDrop,
  dropTables,
  createTables,
  // Entity tables
  resetBasicEntityTables,
  resetGenDependentEntityTables,
  // Junction tables
  resetAbilityJunctionTables,
  resetItemJunctionTables,
}