import mongoose from 'mongoose';

const pokemonSchema = new mongoose.Schema({
  name: String,
  species: String,
  introduced: Number,
  dexNumber: Number,

  abilities: [String],
  typing: [String],
  pastTyping: mongoose.Schema.Types.Mixed,
  baseStats: mongoose.Schema.Types.Mixed,
  weight: Number,
});



export {pokemonSchema};