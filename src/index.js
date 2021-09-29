import mongoose from 'mongoose';
import {pokemonSchema, pokemonSchema} from './mongoSchema';

mongoose.connect(process.env.DB_CONNECTION_STRING);

const pokemonSchema = new mongoose.Schema(pokemonSchema);

// const Pokemon = mongoose.model('Pokemon', pokemonSchema);

// const bulbasaur = new Pokemon({name: 'bulbasaur', id: 1, typing: ['grass', 'poison']});

// await bulbasaur.save();
// const finder = await Pokemon.find({name: 'bulbasaur'});
// console.log(finder);