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
  // pmove table needs to be handled after inserting pType.
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
    // Delete the tables to overcome foreign key constraints.
    console.log(tableName);
    db.promise().query(tableStatements.abilityJunctionTables[tableName].delete)
    .then( ([results, fields]) => {

      console.log(`${tableName} table deleted.`);

    })
    .catch(console.log)
    .then( () => {
      db.promise().query(tableStatements.abilityJunctionTables[tableName].reset_auto_inc)
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

        db.promise().query(tableStatements.abilityJunctionTables[tableName].insert, [values])
        .then( ([results, fields]) => {
          console.log(`${tableName} data inserted: ${results.affectedRows} rows.`);
        })
        .catch(console.log);
      });
    });
  }
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
const buildForeignKeyMaps = async (tableName) => {
  const results = await queryIdentifyingColumns(tableName).then( ([results, fields]) => {
    // Maps values in identifying columns of tableName to values in primary key columns of tableName.
    const foreignKeyMap = new Map();

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

      //
      foreignKeyMap.set(identifyingColumns, primaryKeyColumns);
    });

    console.log(foreignKeyMap);
  });
}


// insertGenDependentEntities();


// const targetNames = ['adjacent_ally', 'adjacent_foe', 'all_adjacent','all_adjacent_foes', 'all', 'all_allies', 'all_foes', 'any', 'any_adjacent', 'user', 'user_and_all_allies', 'user_or_adjacent_ally']
const categoryNames = ['physical', 'special', 'status', 'varies']

const values = require('./processing/processed_data/moves.json');
values.map(data => {
  if (categoryNames.indexOf(data.category) < 0) console.log(data.name, data.category);
})

// queryIdentifyingColumns('pokemon')
//   .then( ([results, fields]) => {
//     console.log(results);
//   })
//   .catch(console.log);

// db.promise().query(tableStatements.entityTables.generation.select('*'))
// .then( ([results, fields]) => {
//   console.log(results);
// }).catch(console.log);