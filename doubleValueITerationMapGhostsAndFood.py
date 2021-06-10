
def getValueIterationMap(accessibleMap,        
                            movesMap,
                            distancesMap,              
                            pacman, 
                            activeGhosts,
                            edibleGhosts,             
                            food,        
                            isSmallGrid,
                            deadEnds,
                            initialFoodCount,
                            allowedDistanceForActiveGhosts=MDPAgent.ACTIVE_GHOSTS_MAX_ALLOWED_DISTANCE,
                            allowedDistanceForEdibleGhosts=MDPAgent.EDIBLE_GHOSTS_MAX_ALLOWED_DISTANCE,
                            foodReward = MDPAgent.FOOD_REWARD,   
                            moveReward = MDPAgent.MOVE_REWARD,  
                            activeGhostReward = MDPAgent.ACTIVE_GHOST_REWARD,
                            edibleGhostReward = MDPAgent.EDIBLE_GHOST_REWARD,
                            pacmanReward = MDPAgent.PACMAN_REWARD,      
                            deadEndReward = MDPAgent.DEAD_END_REWARD,
                            discountFactor = MDPAgent.DISCOUNT_FACTOR,
                            epsilon = 0.05
                        ):
    '''
    Return the value iteration map. Epsilon is the threshold, if the max change in the map 
    is below that number, we stop iterating (to improve performance).
    minAllowedScoreChange prevents location to update their scores by an amount which is 
    too small. 
    '''
    foodValueIterationMap = getFoodValueIterationMap(accessibleMap,
                                                     movesMap,
                                                     distancesMap,
                                                     pacman,
                                                     food,
                                                     initialFoodCount,
                                                     foodReward
                                                    )
                                                    
    ghostsValueIterationMap = getGhostsValueIterationMap(accessibleMap,
                                                     movesMap,
                                                     distancesMap,
                                                     pacman,
                                                     activeGhosts,
                                                     edibleGhosts,
                                                     deadEnds
                                                    )

    valueIterationMap = {location: ghostsValueIterationMap[location] + foodValueIterationMap[location] for location in accessibleMap}
    return valueIterationMap


def getFoodValueIterationMap(accessibleMap,        
                            movesMap,
                            distancesMap,              
                            pacman,             
                            food,       
                            initialFoodCount,
                            foodReward = MDPAgent.FOOD_REWARD,   
                            moveReward = MDPAgent.MOVE_REWARD,  
                            pacmanReward = MDPAgent.PACMAN_REWARD,   
                            discountFactor = MDPAgent.DISCOUNT_FACTOR,
                            epsilon = 0.05
                        ):
    
    # initialise value iteration map
    oldValueIterationMap = { location : 0 for location in accessibleMap }

    scoreableMap = [ location for location in accessibleMap ]

    # The value of food increase as less food remains
    ## MEDIUM GRID SETTINGS
    foodReward *= initialFoodCount / (len(food) + 0.0)

    # Create the next value iteration map
    newValueIterationMap = {}
    
    # Update the old map in food and ghosts locations
    for foodLocation in food: oldValueIterationMap[foodLocation] += foodReward

    ## MEDIUM CLASSIC SETTINGS
    # pacman should try to always change location
    # oldValueIterationMap[pacman] = pacmanReward 

    # This is used to determine the end of the 
    # value iteration loop
    maxUpdate = epsilon + 1

    while maxUpdate > epsilon:
        maxUpdate = 0
        
        for scoreableLocation in scoreableMap:

            locationValue = bellmanEquation(moveReward, 
                                            scoreableLocation, 
                                            oldValueIterationMap, 
                                            movesMap, 
                                            distancesMap,
                                            utilitiesDealerFunction=max, 
                                            includeNoMove=True)    

            locationValueUpdate = abs(locationValue - oldValueIterationMap[scoreableLocation])

            maxUpdate = max(maxUpdate, locationValueUpdate)
            
            newValueIterationMap[scoreableLocation] = locationValue

        # update old value iteration map
        for key, newValue in newValueIterationMap.items():
            oldValueIterationMap[key] = newValue

        newValueIterationMap = {}

    return oldValueIterationMap


def getGhostsValueIterationMap(accessibleMap,        
                            movesMap,
                            distancesMap,              
                            pacman, 
                            activeGhosts,
                            edibleGhosts, 
                            deadEnds,
                            allowedDistanceForActiveGhosts=MDPAgent.ACTIVE_GHOSTS_MAX_ALLOWED_DISTANCE,
                            allowedDistanceForEdibleGhosts=MDPAgent.EDIBLE_GHOSTS_MAX_ALLOWED_DISTANCE,
                            moveReward = MDPAgent.MOVE_REWARD,  
                            activeGhostReward = MDPAgent.ACTIVE_GHOST_REWARD,
                            edibleGhostReward = MDPAgent.EDIBLE_GHOST_REWARD,
                            pacmanReward = MDPAgent.PACMAN_REWARD,      
                            deadEndReward = MDPAgent.DEAD_END_REWARD,
                            discountFactor = MDPAgent.DISCOUNT_FACTOR,
                            epsilon = 0.05
                        ):
    
    # initialise value iteration map
    oldValueIterationMap = { location : 0 for location in accessibleMap }
    scoreableMap = [ location for location in accessibleMap ]

    # Create the next value iteration map
    newValueIterationMap = {}
    
    # Update the old map in food and ghosts locations
    for ghostLocation in activeGhosts: oldValueIterationMap[ghostLocation] += activeGhostReward
    for ghostLocation in edibleGhosts: oldValueIterationMap[ghostLocation] += edibleGhostReward
    for deadEnd in deadEnds: oldValueIterationMap[deadEnd] += deadEndReward

    ## MEDIUM CLASSIC SETTINGS
    # pacman should try to always change location
    oldValueIterationMap[pacman] = pacmanReward 

    # This is used to determine the end of the 
    # value iteration loop
    maxUpdate = epsilon + 1

    while maxUpdate > epsilon:
        maxUpdate = 0
        
        for scoreableLocation in scoreableMap:

            locationValue = bellmanEquation(moveReward, 
                                            scoreableLocation, 
                                            oldValueIterationMap, 
                                            movesMap, 
                                            distancesMap,
                                            utilitiesDealerFunction=min,
                                            includeNoMove=True)    

            locationValueUpdate = abs(locationValue - oldValueIterationMap[scoreableLocation])

            maxUpdate = max(maxUpdate, locationValueUpdate)

            newValueIterationMap[scoreableLocation] = locationValue

        # update old value iteration map
        for key, newValue in newValueIterationMap.items():
            oldValueIterationMap[key] = newValue

        newValueIterationMap = {}

    return oldValueIterationMap
