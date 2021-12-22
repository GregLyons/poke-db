# General structure

Several different files define various functions necessary for processing the data. These files are gathered in `index.js` then exported, so that these functions can be accessed from a single file, `index.js`.

- `helpers.js`
  - Miscellaneous helper functions.
- `learnsetProcessing.js`
  - Merges Gen 2 learnsets and current learnsets into a single learnset object.
  - Adds Z-Moves, Max-Moves, etc. to the learnset data. 
  - Adds learnset data to PokemonArr. 
  - Functions like `computePokemonLearnsetName` and `getPokemonLearnsetMaps` are used to (1) match our Pokemon names with the Pokemon names used by the Pokemon Showdown team in the learnset files, and (2) apply the appropriate learnsets to Pokemon forms which don't have learnset data in the Pokemon Showdown data.
- `serializing.js`
  - Extends each patch list by filling in missing generations, even if no changes were applied in those generations.
  - Serializes each of the big entity objects by converting them to arrays whose entries correspond to individual entity objects (before, each entity class was represented by a single object).
- `splitting.js`
  - Splits each entry in the entity array (created using code from `serializing.js`) into multiple entries, one for each generation.