# General structure

Most of the `.py` files here create Python `dict`s storing data for a given entity class. We also have:

- `makeAll.py` 
  - Runs all the `main()` methods for the entity files to get the corresponding `dict`s. 
  - Tests for consistency between entity `dict`s, e.g. do the names of the Abilities in `pokemonDict` match up with the names of the Abilities in `abilityDict`?
  - Writes each `dict` to a `.json` file in `../../data/raw_data/json`.
- `utils.py`
  - Contains various helper functions for making the entity `dict`s.
  - Contains lists of the names of entities which are easy to list out, e.g. Statuses, Stats, Usage Methods, etc. These are used for checking consistency between the entity `dict`s.
- `tests.py`
  - Contains various tests for many of the entity `dict`s.
  - Checks that the names of the Stats referenced in `abilityDict`, `itemDict`, etc. match the names of the Stats in `statDict`. 
  - Checks for generational consistency in the data, i.e. that no patch o an entity is applied *before* when the entity was actually released.
  - For entities whose corresponding scripts are complicated due to needing to combine many different `.csv`s (e.g. `pokemon.py`), several unit tests are included.

# Conventions for entity `dict`s

A given `dict` satisfies the following conventions:

1. The key names are the `snake_case` names of a given entity, e.g. the keys of `pokemonDict` are the names of Pokemon, e.g. `meowth_alola`, `charizard_gmax`, etc. 
2. The values of a given `dict` are themselves `dict`s, storing data for the given entity, e.g. `pokemonDict["pikachu"]` is a `dict` containing data on Pikachu.
3. Most of these inner `dict`s have a `gen` key for the generation in which the entity was introduced, e.g. `pokemonDict["pikachu"]["gen"] = 1`, `abilityDict["adaptability"]["gen"] = 4`. 
4. For inner keys whose values can change across generations, e.g. `moveDict["karate_chop"]["type"]`, we use a 'patch list', which is a `list` of patches. Each 'patch' is itself ` list`, whose last entry is the generation in which the patch is applied, and whose other entries are values. For example, the value of `moveDict["karate_chop"]["type"]` is `[["normal", 1], ["fighting", 2]]`, since the Move Karate Chop was Normal Type in Gen 1, then it changed to Fighting Type in Gen 2.
5. For relationships between entities, we use nested `dict`s. For example, the Move Karate Chop has the Effect `high_crit_chance` from Gen 1 onwards. This relationship is stored in `moveDict["karate_chop"]["effects"]`, which is a `dict` whose keys are the names of Effects. In this case, it is a `dict` with a single key, `high_crit_chance`, and value `[[true, 1]]`.
6. To determine which entity `dict` a relationship should go on (should the above relationship be in `moveDict` or `effectDict`?), identify the subject and the object (or owner/owned, respectively) in the relationship, e.g. 'Move has Effect', 'Item modifies Stat', 'Type ignores Field State' ('subject verb object'). The data for the relationship should go in the `dict` corresponding to the subject entity.

The extended example below shows a complete entry in `natureDict`, illustrating each of these Conventions.


# Extended example: Adding Natures

## Adding Nature entities in `natures.py` 

Now that we have the Nature data in `../../data/raw_data/csv/natures/natureList.csv`, we're ready to process it. Our `dict` has the following structure (the keys are the `snake_case` names of the Natures, Convention 1):

    {
      natureName {
        gen: <the Generation in which the Nature was introcuded>
        formatted_name: <the name of the Nature in Title Case>
        favorite_flavors: <e.g. [['spicy', 3]]>
        disliked_flavors: <e.g. [['bitter', 3]]>
        stat_modifications: {
          <name of a stat>: <patch for stat modification>
        }
      }
    }

For example, `natureDict["lonely"]` would be (Conventions 2 and 3):

    {
      ...
      lonely {
        gen: 3,
        formatted_name: 'Lonely',
        favorite_flavors: [['spicy', 3]],
        disliked_flavors: [['sour', 3]],
        stat_modifications: {
          attack: [[1.1, 3]],
          defense: [[0.9, 3]]
        }
      }
      ...
    }

First, note that we use a patch structure for the flavors (Convention 4 ). Its conceivable that a new Pokemon game could change which flavors a Nature is associated with, in which case the patch list could be, for example, `favorite_flavors: [['spicy', 3], ['bitter', 9]]`. 

Second, observe that the `stat_modifications` field is another `dict`, whose keys are the names of stats (Convention 5). The value for each key is a patch representing the corresponding stat modification. Again, it's conceivable that this value could change across generations. Perhaps a new generation would make Natures only influence Stats by a factor of 5% (e.g. `[[1.1, 3], [1.05, 9]]`).

The `main()` function for `natures.py` returns `natureDict` to be used by `makeAll.py`. Before exiting, however, we run `checkGenConsistency(natureDict)` and `natureTests(natureDict)`, which we wrote in `tests.py`.

## Adding new entity relationship data to `items.py`

At this point, we have not only added new entities (Natures). We have also added a new relationship between entities (Nature and Stat), represented in the `stat_modifications` key of `natureDict`. The other relationship we need to add is between Items and Natures (recall our checklist for the data to be added in `../../README.md`).

Do we add this relationship in `natures.py` or `items.py`? We can call our relationship "Item confuses Nature". In this relationship, Item is the owner/subject, and Nature is the owned/object (Convention 6), so we add this relationship data to `itemDict` in `items.py`. To this end, we simply write a new function `addNatureData(itemDict)`, which takes in `itemDict` and adds the `confuses_nature` key. The keys of this `dict` are, by convention, the names of Natures, and the values are simple patches, e.g. `[[True, 3]]`. 

## Adding to `makeAll.py`

Finally, in the `main()` function of `makeAll.py`, we call `natures.main()` to access `natureDict`. Then, at the end, we add `[natureDict, 'natures.json']` to `dicts_fnames`, so that running `makeAll.py` will create `natures.json` in `../../data/raw_data/json`. `makeAll.py` will also add in the `confuses_nature` data we added in `items.py` to `../../data/raw_json/json/items.json`. 

Now that we've done our first processing step for the Nature data, we move on to `../../processing` to process the data further.