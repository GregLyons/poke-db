import mongoose from 'mongoose';
import {fetchPokemonData} from './data/fetchData.js';
import {pokemonSchema} from './schema/mongoSchema.js';

mongoose.connect(process.env.DB_CONNECTION_STRING);

const Pokemon = mongoose.model('Pokemon', pokemonSchema);

async function start() {
  console.log('deleting old pokemon...');
  await Pokemon.deleteMany({});

  const data = await fetchPokemonData(5, 80);

  for (const obj of data) {
    console.log(obj);
    const pokemon = new Pokemon(obj);
    await pokemon.save();
    console.log(obj.name, 'uploaded to database.');
  }
}

start();

// await bulbasaur.save();
// const finder = await Pokemon.find({name: 'bulbasaur'});
// console.log(finder);


