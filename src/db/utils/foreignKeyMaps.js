// Helper function for taking an array of strings and making a key for a foreign key map. We need this since the keys of a Map cannot be an array or an object.

const makeMapKey = arr => arr.join(' ');

/*
  Given a table name, tableName, build a Map, foreignKeyMap, which maps identifying column values to primary key column values. E.g.

    If tableName = 'pokemon', foreignKeyMap maps { generation_id, pokemon_name } to { pokemon_id, generation_id }.

  This will facilitate inserting data into junction tables, indeed into any table with a foreign key.
*/
const getForeignKeyMap = async (db, tableStatements, tableName) => {
  const foreignKeyMap = new Map();
  
  await queryIdentifyingColumns(db, tableStatements,tableName).then( ([results, fields]) => {
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

/*
  Given an array of table names, tableNameArr, get the foreign key match for each table.

  Since Promise.all() preserves order, the foreign key maps will be returned in the same order as that of the table names in tableNameArr.
*/ 
const getForeignKeyMaps = async(db, tableStatements, tableNameArr) => {
  return Promise.all(
    tableNameArr.map(tableName => getForeignKeyMap(db, tableStatements, tableName))
  )
  .catch(console.log);
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
  Given a table name, tableName, with an AUTO_INCREMENT column, select identifying columns for the purpose of data insertion. E.g.

    If tableName = 'pokemon', select 'pokemon_id', the AUTO_INCREMENT column, as well as 'generation_id' and 'pokemon_name'. 
*/
const getIdentifyingColumnNames = (tableName) => {
  let identifyingColumns;
  switch(tableName) {
    case 'pdescription':
      identifyingColumns = 'pdescription_index, pdescription_entity_class, pdescription_entity_name';
      break;
    case 'sprite':
      identifyingColumns = 'sprite_path, entity_name';
      break;
    case 'version_group':
      identifyingColumns = 'version_group_code';
      break;
    case 'ability': 
    case 'effect':
    case 'field_state':
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

module.exports = {
  makeMapKey,
  getForeignKeyMaps
}