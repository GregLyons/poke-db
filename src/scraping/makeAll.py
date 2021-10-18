import abilityList
import abilityEffects
import evolutionChains
import heldItems
import moveDescriptions
import moveList
import movesByContact
import movesByEffect
import movesByPriority
import movesByStatus
import movesByTarget
import movesRemovedFromGen8
import natures
import pokemonByAbilities
import pokemonByBaseStats
import pokemonByType
import statModifyingMoves
import typeMatchups

# This file is for making all the .csv files at once rather than running each individual script
if __name__ == '__main__':
  abilityList.main()
  print('Ability list complete')

  abilityEffects.main()
  print('Ability effects complete')

  evolutionChains.main()
  print('Evolution chains complete')

  heldItems.main()
  print('Held item data complete')

  moveDescriptions.main()
  print('Move description data complete')

  moveList.main()
  print('Moves list complete')

  movesByContact.main()
  print('Contact data complete')

  movesByEffect.main()
  print('Effect data complete')

  movesByPriority.main()
  print('Priority data complete')

  movesByStatus.main()
  print('Move status data complete')

  movesByTarget.main()
  print('Move target data complete')

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

  statModifyingMoves.main()
  print('Stat modificatin data complete')

  typeMatchups.main()
  print('Type matchup data complete')


