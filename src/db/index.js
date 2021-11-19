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
const createTables = () => {
  // Create entity tables first for foreign keys in junction tables.
  console.log('Creating entity tables if they don\'t already exist.')
  Promise.all(Object.keys(tableStatements.entityTables).map(tableName => {
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
  
  return;
};

// Inserts generation, version group, description, and sprite data; these are entities which don't depend on generation.
// WARNING: most of the data depends on generation, so performing this will cause most of the other data to be deleted.


const insertBasicEntities = async () => {
  const basicEntityTableNames = ['generation', 'pdescription'];
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

// 
const abilities = require('./processing/processed_data/abilities.json');
const effects = require('./processing/processed_data/effects.json');
const items = require('./processing/processed_data/items.json');
const moves = require('./processing/processed_data/moves.json');
const pokemon = require('./processing/processed_data/pokemon.json');
const pTypes = require('./processing/processed_data/pTypes.json');
const statuses = require('./processing/processed_data/statuses.json');
const usageMethods = require('./processing/processed_data/usageMethods.json');
const versionGroups = require('./processing/processed_data/versionGroups.json');

// // need (generation_id, version_group_code, formatted_name)
// values = versionGroups.map(data => [data.gen, data.name, data.formatted_name]);

const insertGenDependentEntities = (
  abilities,
  effects,
  items,
  moves,
  pokemon,
  pTypes,
  statuses,
  usageMethods,
  versionGroups,
) => {
  // pmove table needs to be handled after inserting pType.
  const entityTableNames = [
    'ability',
    'effect',
    'item',
    'pokemon',
    'pstatus',
    'ptype',
    'stat',
    'usageMethod',
    'versionGroup'
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


// createTables();
// insertBasicEntities();