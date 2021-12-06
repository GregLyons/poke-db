/*
  COMPUTING VALUES TO BE INSERTED INTO A GIVEN TABLE
*/ 

const { makeMapKey } = require('./foreignKeyMaps.js');
const { GEN_ARRAY, NUMBER_OF_GENS, PROCESSED_DATA_PATH, getGenOfVersionGroup } = require('./helpers.js');

// Use entityData and foreignKeyMaps to determine the array, values, which will be inserted into tableName.
const getValuesForTable = (
  tableName, 
  tableGroup, 
  entityData, 
  foreignKeyMaps
) => {

  // UNPACK foreignKeyMaps AND ASSIGN entityData BASED ON tableGroup
  // #region

  // Declarations for foreign key maps.
  let ability_FKM, item_FKM, move_FKM, pokemon_FKM, pType_FKM, usageMethod_FKM, stat_FKM, pstatus_FKM, effect_FKM, description_FKM, sprite_FKM, versionGroup_FKM;
  // Declarations for entity data.
  let abilityData, metaEntityData, itemData, moveData, pokemonData, pTypeData;
  switch(tableGroup) {
    case 'abilityJunctionTables':
      [ability_FKM, pType_FKM, usageMethod_FKM, stat_FKM, pstatus_FKM, effect_FKM] = foreignKeyMaps;
      abilityData = entityData;
      break;

    case 'itemJunctionTables':
      [item_FKM, pType_FKM, usageMethod_FKM, stat_FKM, pstatus_FKM, effect_FKM, pokemon_FKM] = foreignKeyMaps;
      itemData = entityData;
      break;

    case 'moveJunctionTables':
      [move_FKM, pokemon_FKM, pType_FKM, item_FKM, usageMethod_FKM, stat_FKM, pstatus_FKM, effect_FKM] = foreignKeyMaps;
      moveData = entityData;
      break;
    
    case 'typeJunctionTables':
      [pType_FKM] = foreignKeyMaps;
      pTypeData = entityData;
      break;

    case 'pokemonJunctionTables':
      // We handle pokemon_pmove separately since it is so large.
      if (tableName == 'pokemon_pmove') {
        [pokemon_FKM, move_FKM] = foreignKeyMaps;
      } else {
        [pokemon_FKM, pType_FKM, ability_FKM] = foreignKeyMaps;
      }
      pokemonData = entityData;
      break;
    case 'versionGroupJunctionTables':
      if (tableName.split('_')[0] == 'pdescription') {
        [description_FKM, ability_FKM, move_FKM, item_FKM, versionGroup_FKM] = foreignKeyMaps;
        metaEntityData = entityData;
      } else {
        throw `Sprites not handled yet! ${tableName}`;
      }
      break;
    default: 
      // console.log('No foreign key maps necessary for this table group.')
  }

  // #endregion

  // This is where we will store the array representing the data to be inserted.
  let values;

  // COMPUTE values BASED ON tableName
  // #region

  // Calculating values is very similar for, e.g. '<entity class>_boosts_ptype' and '<entity_class>_resists_ptype'. We declare these variables for use in multiple places in the following switch-statement.
  let boostOrResist, boostOrResistKey, causeOrResist, causeOrResistKey;

  // Assign values based on tableName
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
          pdescription_class,
          entity_name
        )
      */
     require('./../')
      const descriptions = require(PROCESSED_DATA_PATH + 'descriptions.json');
      values = descriptions.reduce((acc, descriptionObj) => {
        // extract entityName and description type
        const { entity_name: entityName, description_class: descriptionClass } = descriptionObj;
        
        // descriptionObj contains all the descriptions for entity name, so we need to split them up. The unique descriptions are indexed by numeric keys.
        return acc.concat(Object.keys(descriptionObj)
          // numeric keys contain description info
          .filter(key => !isNaN(key))
          .map(descriptionIndex => {
            // descriptionObj[descriptionIndex] is a two-element array, whose first element is the description itself, and whose second element is another array containing version group codes; we don't need the latter at this moment
            const description = descriptionObj[descriptionIndex][0];
            
            return [description, descriptionIndex, descriptionClass, entityName];
          }));
      }, []);
      break;
    
    case 'pstatus':
      /*
        Need (
          generation_id,
          pstatus_name,
          pstatus_formatted_name
        )
      */
      values = require(PROCESSED_DATA_PATH + 'statuses.json').map(data => [data.gen, data.name, data.formatted_name]);
      break;
    
    case 'stat':
      /*
        Need (
          generation_id
          stat_name,
          stat_formatted_name
        )
      */
      values = require(PROCESSED_DATA_PATH + 'stats.json').map(data => [data.gen, data.name, data.formatted_name]);
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
      values = require(PROCESSED_DATA_PATH + 'abilities.json')
        .map(data => [data.gen, data.name, data.formatted_name, data.introduced]);
      break;

    case 'effect':
      /* 
        Need (
          generation_id
          effect_name,
          effect_formatted_name,
          introduced
        )
      */
      values = require(PROCESSED_DATA_PATH + 'effects.json')
        .map(data => [data.gen, data.name, data.formatted_name, data.introduced]);
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
      values = require(PROCESSED_DATA_PATH + 'items.json')
        .map(data => [data.gen, data.name, data.formatted_name, data.introduced, data.item_class]);
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
      values = require(PROCESSED_DATA_PATH + 'pokemon.json')
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
          pmove_target,
          pmove_removed_from_swsh
          pmove_removed_from_bdsp
        )
      */
      values = require(PROCESSED_DATA_PATH + 'moves.json')
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
          data.target,
          data.removed_from_swsh,
          data.removed_from_bdsp
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
      values = require(PROCESSED_DATA_PATH + 'pTypes.json')
        .map(data => [data.gen, data.name, data.formatted_name, data.introduced]);
      break;

    case 'usage_method':
      /*
        Need (
          generation_id,
          usage_method_name
          usage_method_formatted_name
          introduced
        )
      */
      values = require(PROCESSED_DATA_PATH + 'usageMethods.json')
        .map(data => [data.gen, data.name, data.formatted_name, data.introduced]);
      break;

    case 'version_group':
      /*
        Need (
          version_group_code,
          version_group_formatted_name
          introduced
        )
      */
      values = require(PROCESSED_DATA_PATH + 'versionGroups.json').map(data => [data.name, data.formatted_name, data.introduced]);
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
            const { usage_method_id: usageMethodID } = usageMethod_FKM.get(makeMapKey([gen, usageMethodName]));
            const multiplier = usageMethodData[usageMethodName];

            return multiplier != 1 
            ? [gen, abilityID, gen, usageMethodID, multiplier]
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
            const { stat_id: statID } = stat_FKM.get(makeMapKey([gen, statName]));
            let [modifier, recipient] = statModData[statName]

            // True if stage modification, False if multiplier.
            const stageOrMultiplier = typeof modifier == 'string';

            // stage
            if (stageOrMultiplier) {
              modifier = parseInt(modifier.slice(1), 0);
              return modifier != 0 
              ? [gen, abilityID, gen, statID, modifier, 1.0, 100.00, recipient]
              : [];
            }
            // multiplier
            else {
              return modifier != 1.0
              ? [gen, abilityID, gen, statID, 0, modifier, 100.00, recipient]
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
          effect_generation_id
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
            const { effect_id: effectID } = effect_FKM.get(makeMapKey([effectName, gen]));

            // True if effect is present, False otherwise.
            return effectData[effectName]
            ? [gen, abilityID, gen, effectID]
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
            const { pstatus_id: statusID } = pstatus_FKM.get(makeMapKey([gen, statusName]));
            if (causeOrResist === 'causes') {
              // In case of causes, statusData[statusName] is probability of causing status.
              const chance = statusData[statusName];

              return chance != 0.0 
              ? [gen, abilityID, gen, statusID, chance]
              : [];
            } else {
              // In case of resists, statusData[statusName] is either True or False.
              return statusData[statusName] 
              ? [gen, abilityID, gen, statusID]
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
            const { usage_method_id: usageMethodID } = usageMethod_FKM.get(makeMapKey([gen, usageMethodName]));
            const multiplier = usageMethodData[usageMethodName];

            return multiplier != 1 
            ? [gen, itemID, gen, usageMethodID, multiplier]
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
            const { stat_id: statID } = stat_FKM.get(makeMapKey([gen, statName]));
            let [modifier, recipient] = statModData[statName]

            // True if stage modification, False if multiplier.
            const stageOrMultiplier = typeof modifier == 'string';

            // stage
            if (stageOrMultiplier) {
              modifier = parseInt(modifier.slice(1), 10);
              return modifier != 0 
              ? [gen, itemID, gen, statID, modifier, 1.0, 100.00, recipient]
              : [];
            }
            // multiplier
            else {
              return modifier != 1.0
              ? [gen, itemID, gen, statID, 0, modifier, 100.00, recipient]
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
          effect_generation_id,
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
            const { effect_id: effectID } = effect_FKM.get(makeMapKey([effectName, gen]));

            // True if effect is present, False otherwise.
            return effectData[effectName]
            ? [gen, itemID, gen, effectID]
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
            const { pstatus_id: statusID } = pstatus_FKM.get(makeMapKey([gen, statusName]));

            return statusData[statusName] 
            ? [gen, itemID, gen, statusID]
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
    
    /*
      MOVE JUNCTION TABLES
    */
    case 'pmove_ptype':
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

            // if (entity_FKM.get(makeMapKey([gen, entityName])) == undefined) {
            //   console.log(requirementData, entityName);
            // }

            // All the possible entity classes come alphabetically before 'generation_id', so the order [gen, entityName] is correct.
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
            const { usage_method_id: usageMethodID } = usageMethod_FKM.get(makeMapKey([gen, usageMethodName]));
            
            // A move may lose a usage method. 
            const present = usageMethodData[usageMethodName];

            return present
            ? [gen, moveID, gen, usageMethodID]
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
            const { stat_id: statID } = stat_FKM.get(makeMapKey([gen, statName]));
            let [modifier, recipient, chance] = statModData[statName]

            // True if stage modification, False if multiplier.
            const stageOrMultiplier = typeof modifier == 'string';
            
            // stage
            if (stageOrMultiplier) {
              modifier = parseInt(modifier.slice(1), 10);
              return modifier != 0 
              ? [gen, moveID, gen, statID, modifier, 1.0, chance, recipient]
              : [];
            }
            // multiplier
            else {
              return modifier != 1.0
              ? [gen, moveID, gen, statID, 0, modifier, chance, recipient]
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
          effect_generation_id,
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
            const { effect_id: effectID } = effect_FKM.get(makeMapKey([effectName, gen]));

            // True if effect is present, False otherwise.
            return effectData[effectName]
            ? [gen, moveID, gen, effectID]
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
      causeOrResist = tableName.split('_')[1];
      causeOrResistKey = causeOrResist + '_status';

      values = moveData.reduce((acc, curr) => {
        // Get move data from curr.
        const { gen: gen, name: moveName, [causeOrResistKey]: statusData } = curr;
        const { pmove_id: moveID } = move_FKM.get(makeMapKey([gen, moveName]));
        
        return acc.concat(
          Object.keys(statusData).map(statusName => {
            // We always compare entities of the same generation.
            const { pstatus_id: statusID } = pstatus_FKM.get(makeMapKey([gen, statusName]));
            if (causeOrResist === 'causes') {
              // In case of causes, statusData[statusName] is probability of causing status.
              const chance = statusData[statusName];

              return chance != 0.0 
              ? [gen, moveID, gen, statusID, chance]
              : [];
            } else {
              // In case of resists, statusData[statusName] is either True or False.
              return statusData[statusName] 
              ? [gen, moveID, gen, statusID]
              : [];
            }
          })
        )
      }, [])
      // Filter out empty entries
      .filter(data => data.length > 0);
      break;
    
    /*
      TYPE JUNCTION TABLES
    */
    case 'ptype_matchup':
      /*
        Need (
          attacking_ptype_generation_id,
          attacking_ptype_id,
          defending_ptype_generation_id,
          defending_ptype_id,
          multiplier          
        )
      */ 
      values = pTypeData.reduce((acc, curr) => {
        // Get offensive type data from curr.
        const { gen: gen, name: pTypeName_att, damage_to: matchupData } = curr;
        const { ptype_id: pTypeID_att } = pType_FKM.get(makeMapKey([gen, pTypeName_att]));
        
        return acc.concat(
          Object.keys(matchupData).map(pTypeName_def => {
            // if (pType_FKM.get(makeMapKey([gen, pTypeName_def])) == undefined) {
            //   console.log(requirementData, pTypeName_def);
            // }
            const { ptype_id: pTypeID_def } = pType_FKM.get(makeMapKey([gen, pTypeName_def]));

            const multiplier = curr.damage_to[pTypeName_def];

            return multiplier != 1
              ? [gen, pTypeID_att, gen, pTypeID_def, multiplier]
              : [];
          })
        )
      }, [])
      // Filter out empty entries
      .filter(data => data.length > 0);
      break;

    /*
      POKEMON JUNCTION TABLES
    */
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
    
    case 'pokemon_requires_item':
      /*
        Need (
          pokemon_generation_id,
          pokemon_id,
          item_generation_id,
          item_id
        )
      */
      
      values = pokemonData.reduce((acc, curr) => {
        // Get item data from curr.
        const { gen: gen, name: pokemonName, requirements: requirementData } = curr;
        const { pokemon_id: pokemonID } = pokemon_FKM.get(makeMapKey([gen, pokemonName]));
        
        // If item is not Pokemon-specific
        if (!requirementData || !requirementData["item"]) return acc;
        
        return acc.concat(
          Object.keys(requirementData["item"]).map(itemName => {

            // We always compare entities of the same generation.
            const { item_id: itemID } = item_FKM.get(makeMapKey([gen, itemName]));

            return pokemonData[pokemonName] 
            ? [gen, pokemonID, gen, itemID]
            : [];
          })
        )
      }, [])
      // Filter out empty entries
      .filter(data => data.length > 0);
      break;

    /*
      VERSION GROUP JUNCTION TABLES
    */ 
    case 'pdescription_ability':
    case 'pdescription_item':
    case 'pdescription_pmove':
    // case 'sprite_item':
    // case 'sprite_pokemon':
      /*
        Need (
          <base entity>_generation_id
          <base entity>_id
          version_group_id
          <meta entity>_id
        ), where <entity> is an ability, item, pmove, or pokemon, and <meta entity> is a pdescription or sprite.
      */
      
      // 
      // #region

      const metaEntityClass = tableName.split('_')[0];
      const metaEntity_id = metaEntityClass + '_id';
      
      // Whether the pdescription/sprite is of an ability, item, pokemon, or pmove. Choose the foreign key map accordingly.
      // baseEntityDataClass refers to how the data is stored in descriptions.json or sprites.json.
      const baseEntityClass = tableName.split('_')[1];
      const baseEntity_id = baseEntityClass + '_id';

      let baseEntity_FKM, baseEntityDataClass;
      switch (baseEntityClass) {
        case 'ability':
          baseEntity_FKM = ability_FKM;
          baseEntityDataClass = 'ability';
          break;
        case 'item':
          baseEntity_FKM = item_FKM;
          baseEntityDataClass = 'item'
          break;
        case 'pmove':
          baseEntity_FKM = move_FKM;
          baseEntityDataClass = 'move';
          break;
        case 'pokemon':
          baseEntity_FKM = pokemon_FKM;
          baseEntityDataClass = 'pokemon';
          break;
        default:
          throw 'Invalid base entity class, ' + baseEntityClass;
      }

      let metaEntity_FKM, metaEntityKey;
      switch (metaEntityClass) {
        case 'pdescription':
          metaEntity_FKM = description_FKM;
          metaEntityKey = 'description_class'
          break;
        case 'sprite':
          metaEntity_FKM = sprite_FKM;
          metaEntityKey = 'sprite_class';
          break;
        default:
          throw 'Invalid meta entity class, ' + metaEntityClass;
      }

      // #endregion

      values = metaEntityData.filter(data => data[metaEntityKey] == baseEntityDataClass).reduce((acc, curr) => {
        // Get item data from curr.
        const { entity_name: baseEntityName } = curr;
        
        return acc.concat(
          Object.keys(curr)
            .filter(key => !isNaN(key))
            .reduce((innerAcc, metaEntityIndex) => {
              const [metaEntityContent, versionGroups] = curr[metaEntityIndex];

              // 'pdescription_index, pdescription_class, entity_name' sorted alphabetically is 'entity_name, pdescription_index, pdescription_class'
              const { [metaEntity_id]: metaEntityID } = metaEntity_FKM.get(makeMapKey([baseEntityName, baseEntityDataClass, metaEntityIndex]));

              return innerAcc.concat(
                versionGroups.map(versionGroupCode => {

                  const { version_group_id: versionGroupID } = versionGroup_FKM.get(versionGroupCode);

                  const versionGroupGen = getGenOfVersionGroup(versionGroupCode);

                  const { [baseEntity_id]: baseEntityID } = 
                  baseEntityClass == 'ability' 
                    // 'ability_id' comes before 'generation_id' alphabetically.
                    ? baseEntity_FKM.get(makeMapKey([baseEntityName, versionGroupGen]))
                    // Otherwise, 'generation_id' comes first alphabetically.
                    : baseEntity_FKM.get(makeMapKey([versionGroupGen, baseEntityName]));
      
                  // <base entity>_generation_id
                  // <base entity>_id
                  // version_group_id
                  // <meta entity>_id
                  return [versionGroupGen, baseEntityID, versionGroupID, metaEntityID];
                })
              );
            }, [])
        );
      }, [])
      // Filter out empty entries
      .filter(data => data.length > 0);
      break;

    default:
      console.log(`${tableName} unhandled.`);
  }

  // #endregion

  return values;
}

module.exports = {
  getValuesForTable,
}