import abilityList
import abilityEffects
import descriptions
import evolutionChains
import heldItems
import moveList
import movesByContact
import movesByEffect
import movesByMaxPower
import movesByPriority
import movesByRequirement
import movesByStatus
import movesByTarget
import movesByZPower
import movesRemovedFromGen8
import natures
import pokemonByAbilities
import pokemonByBaseStats
import pokemonByType
import pokemonRemovedFromGen8
import movesModifyStat
import typeMatchups

# This file is for making all the .csv files at once rather than running each individual script
if __name__ == '__main__':
  abilityList.main()
  print('Ability list complete')

  abilityEffects.main()
  print('Ability effects complete')

  descriptions.main()
  print('Description data complete')

  evolutionChains.main()
  print('Evolution chains complete')

  heldItems.main()
  print('Held item data complete')

  moveList.main()
  print('Moves list complete')

  movesByContact.main()
  print('Contact data complete')

  movesByEffect.main()
  print('Effect data complete')

  movesByMaxPower.main()
  print('Max power data complete')

  movesByPriority.main()
  print('Priority data complete')

  movesByRequirement.main()
  print('Move requirement data complete')

  movesByStatus.main()
  print('Move status data complete')

  movesByTarget.main()
  print('Move target data complete')

  movesByZPower.main()
  print('Z-Power data complete')

  movesRemovedFromGen8.main()
  print('Removed moves data complete')

  natures.main()
  print('Nature data complete')

  pokemonByAbilities.main()
  print('Pokemon ability data complete')

  pokemonByBaseStats.main()
  print('Base stat data complete')

  pokemonByType.main()
  print('Pokemon type data complete')

  pokemonRemovedFromGen8.main()
  print('Removed Pokemon data complete')

  movesModifyStat.main()
  print('Stat modification data complete')

  typeMatchups.main()
  print('Type matchup data complete')


