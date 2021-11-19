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
  // pmove table needs to be handled after inserting pType.
  const entityTableNames = [
    'ability',
    'effect',
    'item',
    'pokemon',
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

