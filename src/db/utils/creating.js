/*
  Throughout, db refers to the MySQL database, and tableStatements refers to the object of MySQL statements created in the ./sql folder. 
  
  tableGroup will refer to keys of this object, and tableName will refer to keys of nested object tableStatements[tableGroup].

  If a given table already exists, then this code will do nothing to that table, since the MySQL statements are of the form 'CREATE TABLE IF NOT EXISTS...'
*/

// Creates all tables.
const createAllTables = async (db, tableStatements) => {
  // Create generation table, which most other tables reference.
  await createSingleTableInGroup(db, tableStatements, 'entityTables', 'generation');

  // Create basic entity tables, e.g. stat, pokemon, pmove, which the junction tables reference.
  await createTablesInGroup(db, tableStatements, 'entityTables');
  
  // Create junction tables.
  return createAllJunctionTables(db, tableStatements);
};

// Creates all junction tables.
const createAllJunctionTables = async (
  db,
  tableStatements
) => {
  console.log(`\nCreating all junction tables...\n`)

  return Promise.all(
    Object.keys(tableStatements)
      .filter(tableGroup => tableGroup != 'entityTables')
      .map(tableGroup => {
        return createTablesInGroup(db, tableStatements, tableGroup);
      })
  )
  .then( () => console.log(`\nCreated all junction tables.\n`))
  .catch(console.log);
}

// Creates all tables in tableGroup.
const createTablesInGroup = async (
  db,
  tableStatements,
  tableGroup
) => {
  console.log(`\nCreating tables in '${tableGroup}'...\n`);
  return Promise.all(
    Object.keys(tableStatements[tableGroup])
      .map(tableName => {
        return createSingleTableInGroup(db, tableStatements, tableGroup, tableName);
      })
  )
  .then( () => console.log(`\nCreated all tables in '${tableGroup}'.\n`))
  .catch(console.log);
}

// Creates tableName in tableGroup.
const createSingleTableInGroup = async (
  db,
  tableStatements,
  tableGroup,
  tableName
) => {
  return db.promise().query(tableStatements[tableGroup][tableName].create)
    .then( () => console.log(`'${tableName}' table created if it didn't already exist.`))
    .catch(console.log);
}

module.exports = {
  createSingleTableInGroup,
  createTablesInGroup,
  createAllJunctionTables,
  createAllTables,
}