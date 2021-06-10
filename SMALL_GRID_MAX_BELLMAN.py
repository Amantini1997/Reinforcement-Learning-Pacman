# mdpAgents.py
# parsons/20-nov-2017
#
# Version 1
#
# The starting point for CW2.
#
# Intended to work with the PacMan AI projects from:
#
# http://ai.berkeley.edu/
#
# These use a simple API that allow us to control Pacman's interaction with
# the environment adding a layer on top of the AI Berkeley code.
#
# As required by the licensing agreement for the PacMan AI we have:
#
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).

# The agent here is was written by Simon Parsons, based on the code in
# pacmanAgents.py

from pacman import Directions
from game import Agent
import api
import random
import game
import math
import itertools
import copy


class MDPAgent(Agent):
    DEBUG = False

    ACTIVE_GHOSTS_MIN_ALLOWED_DISTANCE = 
    EDIBLE_GHOSTS_MIN_ALLOWED_DISTANCE = 3 # None
    DEADEND_MIN_ALLOWED_DISTANCE = 1

    # Rewards
    ACTIVE_GHOST_REWARD = -100.0
    EDIBLE_GHOST_REWARD = -20.0
    FOOD_REWARD = 1.0
    MOVE_REWARD = -0.04
    # prompt him to make move
    PACMAN_REWARD = -5.0
    DEAD_END_REWARD = -15
    DISCOUNT_FACTOR = 0.97
    EPSILON = 0.1

    moves = [
        (1, 0),     # East
        (-1, 0),    # West
        (0, 1),     # North
        (0, -1)     # South
    ]

    traversalMoves = {
        (1, 0):  [(0, 1), (0, -1)],    # East
        (-1, 0): [(0, 1), (0, -1)],    # West
        (0, 1):  [(1, 0), (-1, 0)],    # North
        (0, -1): [(1, 0), (-1, 0)]    # South
    }

    moveToDirection = {
        (1, 0)  : Directions.EAST,
        (-1, 0) : Directions.WEST,
        (0, 1)  : Directions.NORTH,
        (0, -1) : Directions.SOUTH,
        (0, 0)  : Directions.STOP
    }

    def __init__(self):
        self.firstMove = True
        self.requestedMove_operatedMove_pair = [] # (requested, operated)
        self.previousPosition = None
        
        # STATIC ELEMENTS
        # list of all the locations pacman has access to
        self.accessibleMap = []
        # list of all the locations surrounded by 3 walls
        self.deadEnds = []
        self.initialFoodCount = 0

        # the type is { location: moves[] }
        self.movesMap = {}  
        self.walls = []
        
        # DYNAMIC ELEMENTS
        self.ghostsStates = []

        # includes capsules
        self.food = []

        name = "Pacman"

    # Gets run after an MDPAgent object is created and once there is
    # game state to access.
    def registerInitialState(self, state):
        print "Running registerInitialState for MDPAgent!"
        print "I'm at:"
        print api.whereAmI(state)
        
    # This is what gets run in between multiple games
    def final(self, state):
        print "Looks like the game just ended!"

    
    def setUpWorld(self, state):
        '''
        This method sets up the knowledge of the agent about 
        static data of the world. This method deals this data will 
        never change throughout the execution of the game in the same
        world, it is intended to be called only once not to waste 
        resources.
        '''        
        food = api.food(state)
        capsules = api.capsules(state)
        self.food = food + capsules
        self.walls = api.walls(state)
        self.accessibleMap = getNonWallLocations(self.walls, state)
        self.movesMap = getMapMoves(self.accessibleMap)
        self.isSmallGrid = len(capsules) == 0
        self.deadEnds = getDeadEnds(self.accessibleMap, self.movesMap)
        self.initialFoodCount = len(self.food)

        if self.isSmallGrid:
            self.ACTIVE_GHOSTS_MIN_ALLOWED_DISTANCE = 7
            self.ACTIVE_GHOST_REWARD = -2.5 #-.8
            self.FOOD_REWARD = 1.0
            self.PACMAN_REWARD = -10.0
            self.MOVE_REWARD = -0.04
            self.DEAD_END_REWARD = -15.0
            self.LAST_FOOD_REWARD = 1.0
            self.DISCOUNT_FACTOR = 0.95
            self.EPSILON = 0.1


    def getAction(self, state):

        # One time operations
        if self.firstMove:
            self.setUpWorld(state)
            # prevent this method from being called again
            self.firstMove = False

        # Operations to be performed at the beginning of every action
        food = api.food(state)
        capsules = api.capsules(state)
        self.food = food + capsules

        # Updates related to pacman
        pacman = api.whereAmI(state)
        self.distancesMap = getLocationsDistanceFromStartingLocation(pacman, self.movesMap)

        # Ghosts related updates
        self.ghostsStates = api.ghostStates(state)

        activeGhosts, edibleGhosts = getActiveAndEdibleGhostsLocations(self.ghostsStates, self.distancesMap)

        riskyActiveGhosts, riskyEdibleGhosts = getRiskyGhosts(activeGhosts, edibleGhosts, self.distancesMap)
        
        valueIterationMap = getValueIterationMap(self.accessibleMap, 
                                                        self.movesMap, 
                                                        self.distancesMap,
                                                        pacman, 
                                                        activeGhosts, #riskyActiveGhosts,
                                                        edibleGhosts, #riskyEdibleGhosts,
                                                        self.food, 
                                                        self.isSmallGrid,
                                                        self.deadEnds,
                                                        self.initialFoodCount,
                                                        self
                                                    )

        bestMove = getBestNextMove(self.moves, 
                                    pacman, 
                                    valueIterationMap, 
                                    self.movesMap, 
                                    self.distancesMap, 
                                   )


        bestDirection = self.moveToDirection[ bestMove ]

        return api.makeMove(bestDirection, api.legalActions(state))









###############
#             #   
#  FUNCTIONS  #
#             #   
###############
def sumTuples( tuple1, tuple2 ):
    return tuple([(i + j) for i, j in zip(tuple1, tuple2)])


def manhattanDistance( xy1, xy2 ):
    '''
    Return the manhattan distance between two points
    '''
    return abs( xy1[0] - xy2[0]) + abs(xy1[1] - xy2[1] )


def getDeadEnds(accessibleMap, movesMap):
    '''
    Given the list of the accessible locations on the map,
    return a list of locations surrounded by 3 walls.
    '''
    deadEnds = [location for location in accessibleMap if len(movesMap[location]) == 1]
    return deadEnds


def getRiskyGhosts(activeGhosts,
                   edibleGhosts, 
                   distancesMap, 
                   allowedDistanceForActiveGhosts=MDPAgent.ACTIVE_GHOSTS_MIN_ALLOWED_DISTANCE,
                   allowedDistanceForEdibleGhosts=MDPAgent.EDIBLE_GHOSTS_MIN_ALLOWED_DISTANCE
                ):
    '''
    Given active and edible ghosts, and a distance map,
    return a the ghosts considered risky, that is, too close
    to pacman. The max allowed distance varies based on the ghost
    state {active, edible}.
    '''
    # 1 -> ghost is edible
    # 0 -> ghost is active
    riskyActiveGhosts = filter(lambda ghost: distancesMap[ghost] <= allowedDistanceForActiveGhosts, activeGhosts) 
    riskyEdibleGhosts = filter(lambda ghost: distancesMap[ghost] <= allowedDistanceForEdibleGhosts, edibleGhosts) 

    return riskyActiveGhosts, riskyEdibleGhosts


def getActiveAndEdibleGhostsLocations(ghostsStates, distancesMap):
    '''
    Given the ghost states return 2 lists, respectively
    the list containing active ghosts and the one containing
    edible ghosts. The distances map is used in the case 
    a ghost is not amid 2 locations, the closest one to pacman is
    considered as its position.
    '''
    activeGhosts = []
    edibleGhosts = []

    IS_EDIBLE = 1
    # 1 -> ghost is edible
    # 0 -> ghost is active

    for ghostState in ghostsStates:
        ghost = ghostState[0]
        status = ghostState[1]
        if status == IS_EDIBLE:
            # As edible ghosts may have locations (a, b) as (x.5, y) 
            # we consider both locations as x.5 + 0.5 and x.5 - 0.5.
            adjacentGhostLocations = getAdjacentGhostLocationsIfLocationNotOnMap(ghost)
            adjacentGhostLocationsDistances = {distancesMap[ghost]: ghost for ghost in adjacentGhostLocations} 

            # Only the location which is closer to pacman is taken into account.
            closestGhostDistance = min(adjacentGhostLocationsDistances.keys())
            edibleGhostLocation = adjacentGhostLocationsDistances[closestGhostDistance]
            edibleGhosts.append(edibleGhostLocation)
        
        else:
            activeGhosts.append(ghost)

    return activeGhosts, edibleGhosts


def findDistanceToClosestGhostWithinAllowedSteps(startingLocation, movesMap, ghosts, stepsLimit=5):
    ''' 
    Using Breadth First Search, decide if any of the given ghosts is reachable
    within n steps from the starting location where n = stepsLimit.
    The method returns -1 if none of the ghosts is reachable within 
    the steps limit, otherwise it returns the distance to the closest ghost.
    '''

    NO_GHOST_FOUND = -1

    # if the list is empty the ghost cannot be found
    if ghosts == []:
        return NO_GHOST_FOUND

    # if a ghost is in the starting location its distance is 0
    if startingLocation in ghosts: 
        return 0 

    visitedLocations = {startingLocation}    
    unvisitedLocations = {startingLocation}

    # iterate once for each step within the admissible distance
    for step in range(1, stepsLimit + 1):
        # find the locations reachable from the current unvisited locations
        reachableLocations = map(lambda location: 
                                map(lambda move: sumTuples(location, move), movesMap[location]),
                             unvisitedLocations)

        # transform into a set to remove duplicates
        reachableLocations = { location for locations in reachableLocations for location in locations }

        # remove locations already visited
        newUnvisitedLocations = filter(lambda location: not location in visitedLocations, reachableLocations)

        # check if a ghost is in any of the new unvisited locations
        for ghost in ghosts:
            if ghost in newUnvisitedLocations:
                return step

        visitedLocations.update(unvisitedLocations)
        unvisitedLocations = newUnvisitedLocations
    
    # no ghost has been found within the steps limit
    return NO_GHOST_FOUND
        

def getLocationsDistanceFromStartingLocation(startingLocation, movesMap, limit=float("inf")):
    '''
    Return the distance of each location from a starting location
    as a dict { location: distance }. 
    The distance can be limited if a number is passed
    as a parameter a steps limit
    '''

    currentDistance = 0

    visitedLocations = { startingLocation: currentDistance }

    unvisitedLocations = { startingLocation }

    while len(unvisitedLocations) > 0 and currentDistance < limit:
        
        currentDistance += 1

        # find the locations reachable from the current unvisited locations
        reachableLocations = map(lambda location: 
                                map(lambda move: sumTuples(location, move), movesMap[location]),
                             unvisitedLocations)

        # transform into a set to remove duplicates
        reachableLocations = { location for locations in reachableLocations for location in locations }

        newUnvisitedLocations = filter(lambda location: not location in visitedLocations, reachableLocations)

        # each new unvisited location must be 1 step away from the previous locations
        for newLocation in newUnvisitedLocations:
            visitedLocations[newLocation] = currentDistance

        unvisitedLocations = newUnvisitedLocations
    
    return visitedLocations


def getAdjacentGhostLocationsIfLocationNotOnMap(ghost):
    '''
    As edible ghosts may have locations (a, b) as (x.5, y) 
    this method returns both locations as x.5 + 0.5 and x.5 - 0.5
    when the ghost is an mid state. If the ghost is at the centre
    of a location, that location is returned as an array.
    ( the same applies to y )
    '''
    x = ghost[0]
    y = ghost[1]
    xs = [x] if x % 1 == 0 else [x + 0.5, x - 0.5]
    ys = [y] if y % 1 == 0 else [y + 0.5, y - 0.5]
    return [location for location in itertools.product(xs, ys)]


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
                            agent
                        ):
    '''
    Return the value iteration map. Epsilon is the threshold, if the max change in the map 
    is below that number, we stop iterating (to improve performance).
    minAllowedScoreChange prevents location to update their scores by an amount which is 
    too small. 
    '''
    allowedDistanceForActiveGhosts=agent.ACTIVE_GHOSTS_MIN_ALLOWED_DISTANCE
    allowedDistanceForEdibleGhosts=agent.EDIBLE_GHOSTS_MIN_ALLOWED_DISTANCE
    allowedDistanceForDeadends=agent.DEADEND_MIN_ALLOWED_DISTANCE
    foodReward=agent.FOOD_REWARD   
    moveReward=agent.MOVE_REWARD  
    activeGhostReward=agent.ACTIVE_GHOST_REWARD
    edibleGhostReward=agent.EDIBLE_GHOST_REWARD
    pacmanReward=agent.PACMAN_REWARD      
    deadEndReward=agent.DEAD_END_REWARD
    discountFactor=agent.DISCOUNT_FACTOR
    epsilon=agent.EPSILON

    # initialise value iteration map
    oldValueIterationMap = { location : 0 for location in accessibleMap }

    # The value of food increase as less food remains
    ## MEDIUM GRID SETTINGS
    # foodReward *= initialFoodCount / (len(food) - 0.0)
    
    # A list of locations with variable score is created 
    # removing the food and ghosts from the map.
    nonScoreableLocations = edibleGhosts + activeGhosts
    if isSmallGrid:
        nonScoreableLocations += food

    if isSmallGrid and len(food) == 1:
        foodReward = agent.LAST_FOOD_REWARD
        nonScoreableLocations.append(food[0])
        pacmanReward = 0
        deadEndReward = 0
     
    # deadEnds are risky, but if Pacman is too close it could be wrong
    # to tell him to leave
    deadEndIsAdjacent = lambda deadEnd: distancesMap[deadEnd] == 1 
    adjacentDeadEnds = filter(deadEndIsAdjacent, deadEnds)
    if len(adjacentDeadEnds) > 0:
        deadEndReward = 0

    scoreableLocations = [ location for location in accessibleMap if location not in nonScoreableLocations ]

    temporaryValueIterationMap = { location : 0 for location in accessibleMap }

    # if isSmallGrid or True:
    for ghost in activeGhosts:
        ghostIterationMap = getGradientMap(ghost, activeGhostReward, movesMap, allowedDistanceForActiveGhosts) 
        for location in ghostIterationMap:
            temporaryValueIterationMap[location] += ghostIterationMap[location]
                    
    for ghost in edibleGhosts:
        ghostIterationMap = getGradientMap(ghost, edibleGhostReward, movesMap, allowedDistanceForEdibleGhosts) 
        for location in ghostIterationMap:
            temporaryValueIterationMap[location] += ghostIterationMap[location]

    for deadEnd in deadEnds:
        deadendIterationMap = getGradientMap(deadEnd, deadEndReward, movesMap, allowedDistanceForDeadends) 
        for location in deadendIterationMap:
            temporaryValueIterationMap[location] += deadendIterationMap[location]

    for location in temporaryValueIterationMap:
        oldValueIterationMap[location] += temporaryValueIterationMap[location]

    # MEDIUM CLASSIC SETTINGS
    # reduce the initial score of pacman's adjacent location (and 
    # pacman's location itself) based on how closer they are to ghosts
    # NO_MOVE = (0, 0)
    # for move in movesMap[pacman] + [NO_MOVE]:
    #     newLocation = sumTuples(pacman, move)
    #     closestActiveGhostDistance = findDistanceToClosestGhostWithinAllowedSteps(newLocation, movesMap, activeGhosts, allowedDistanceForActiveGhosts)
    #     closestEdibleGhostDistance = findDistanceToClosestGhostWithinAllowedSteps(newLocation, movesMap, edibleGhosts, allowedDistanceForEdibleGhosts)
        
    #     closestActiveGhostReward = getGhostRewardBasedOnDistance(closestActiveGhostDistance, activeGhostReward)
    #     closestEdibleGhostReward = getGhostRewardBasedOnDistance(closestEdibleGhostDistance, edibleGhostReward)

    #     lowestGhostReward = min(closestActiveGhostReward, closestEdibleGhostReward)
    #     oldValueIterationMap[newLocation] += lowestGhostReward**9


    # Update the old map in food and ghosts locations
    for foodLocation in food: oldValueIterationMap[foodLocation] += foodReward
    # for ghostLocation in activeGhosts: oldValueIterationMap[ghostLocation] += activeGhostReward
    # for ghostLocation in edibleGhosts: oldValueIterationMap[ghostLocation] += edibleGhostReward
    # for deadEnd in deadEnds: oldValueIterationMap[deadEnd] += deadEndReward
    oldValueIterationMap[pacman] += pacmanReward 

    return valueIterationFunction(oldValueIterationMap, 
                                    movesMap, 
                                    distancesMap, 
                                    scoreableLocations, 
                                    moveReward, 
                                    epsilon, 
                                    discountFactor
                                    ) 


def elementValueIterationMap(element, elementReward, movesMap, stepsLimit, moveReward, epsilon, discountFactor, utilitiesSelectorFunction=min):
    # computing the distance of cells from the element
    elementDistancesMap = getLocationsDistanceFromStartingLocation(element, movesMap, limit=stepsLimit)
    elementValueMapPreIteration = { location: 0 for location in elementDistancesMap.keys() }
    elementValueMapPreIteration[element] = elementReward
    # else:
    #     elementValueMapPreIteration = { location: valueIterationMap[location] for location in valueIterationMap if location in elementDistancesMap.keys()}
    elementMovesMap = { location: [] for location in elementDistancesMap}
    for location in elementMovesMap:
        for move in movesMap[location]:
            if sumTuples(location, move) in elementMovesMap:
                elementMovesMap[location].append(move)
    return valueIterationFunction(elementValueMapPreIteration, 
                                                elementMovesMap, 
                                                elementDistancesMap, 
                                                elementDistancesMap.keys(), 
                                                moveReward, 
                                                epsilon,
                                                discountFactor,
                                                utilitiesSelectorFunction=utilitiesSelectorFunction
                                            ) 


def getGradientMap(element, elementReward, movesMap, stepsLimit, discountFactor=0.7):
    # computing the distance of cells from the element
    elementDistancesMap = getLocationsDistanceFromStartingLocation(element, movesMap, limit=stepsLimit)
    elementGradientValueMap = { location: (discountFactor**elementDistancesMap[location])*elementReward for location in elementDistancesMap.keys() }
    
        
    if MDPAgent.DEBUG:
        l = ""
        for i in range(9, 0, -1):
            for j in range(1, 19):
                l+= str(elementGradientValueMap[(j, i)]) if (j,i) in elementGradientValueMap else '-'*5
                if len(l) < 5:
                    l = (l + "0000")[:5]
                l+= " | "
            l+="\n"
        print l
    return elementGradientValueMap


def valueIterationFunction(oldValueIterationMap, 
                            movesMap, 
                            distancesMap, 
                            scoreableLocations, 
                            moveReward, 
                            epsilon, 
                            discountFactor):
    # This is used to determine the end of the 
    # value iteration loop
    maxUpdate = epsilon + 1
    cycles = 0
    while maxUpdate > epsilon:

        # initialise the next value iteration map
        newValueIterationMap = {}
        maxUpdate = 0
        
        for scoreableLocation in scoreableLocations:
            locationValue = bellmanEquation(moveReward, 
                                            scoreableLocation, 
                                            oldValueIterationMap, 
                                            movesMap, 
                                            distancesMap, 
                                            discountFactor)    
            locationValueUpdate = abs(locationValue - oldValueIterationMap[scoreableLocation])
            maxUpdate = max(maxUpdate, locationValueUpdate)

            # if locationValueUpdate < epsilon:
            #     locationValue = oldValueIterationMap[scoreableLocation]
            newValueIterationMap[scoreableLocation] = locationValue

        # update old value iteration map
        for key, newValue in newValueIterationMap.items():
            oldValueIterationMap[key] = newValue
        cycles+=1
    if MDPAgent.DEBUG:
        l = ""
        for i in range(9, 0, -1):
            for j in range(1, 19):
                l+= str(oldValueIterationMap[(j, i)])[:5] if (j,i) in oldValueIterationMap else '-'*5
                if len(l) < 5:
                    l = (l + "0000")[0:4]
                l+= " | "
            l+="\n"
        print l
        print "---------------" + str(cycles) + "--------------"

    return oldValueIterationMap 


def getGhostRewardBasedOnDistance(distance, reward):
    '''
    Return the reward associated to a ghost adjusted according
    to its distance. If the distance is -1 (that is, the ghost is not 
    located or too distant) the reward is 0.
    '''
    # ghost is not close enough
    if distance == -1:
        return 0
    elif distance == 0:
        # ghost is on the location; to avoid division by 0
        # we set it 0 + epsilon (an arbitrarily small number)
        distance = 0.01
    
    return reward / distance


def getBestNextMove(moves, 
                    pacman, 
                    valueIterationMap, 
                    movesMap,
                    distancesMap
                  ):
    '''
    Given pacman's location and the valueIterationMap,
    Calculates and return the best move for pacman.
    If a given move gets pacman closer to a ghost, such a move is penalised
    based on how close the ghost would be given that move.
        e.g. If the best move is NORTH the function returns (0, 1)
    '''

    ## CHANGE
    if False:
        # This is a dict of the form 
        # { pacmanAdjacentLocation: distanceToClosestGhost }.
        # Pacman location itself can be included here if any risky ghosts
        # can be reached from such a location.
        # only risky ghosts appear here.
        locationToGhostsDistances = {}

        # If pacman is close enough to a ghost, add pacman's location 
        # and that distance to the locationToGhostsDistances.
        # If there are not risky ghosts, set the value to -1.
        locationToGhostsDistances[pacman] = min(riskyGhosts.values()) if len(riskyGhosts) > 0 else -1

        # This loop aim is to populate locationToGhostsDistances, hence, we only
        # consider the moves that will get pacman to a different location
        for move in movesMap[pacman]:
            newLocation = sumTuples(pacman, move)
            closestGhostDistance = findDistanceToClosestGhostWithinAllowedSteps(newLocation, movesMap, ghosts, maxAllowedSteps)
            locationToGhostsDistances[newLocation] = closestGhostDistance
    

    # This is a list containing all the policies in the 
    # form (score, (x, y))
    policies = []

    # This loop aim is to populate the policies list, as such, we consider all the moves
    # here, even if they would result in pacman hitting the wall.
    for move in moves:
        expectedUtility = getMoveUtility(pacman, move, valueIterationMap, movesMap)
        # newMoveLocation = sumTuples(pacman, move) if move in movesMap[pacman] else pacman
        
        ## CHANGE
        if False:
            closestGhostDistance = locationToGhostsDistances[newMoveLocation]

            # a move ending up in a ghost location is terrible
            if closestGhostDistance == 0:
                expectedUtility += ghostReward * 2
            # if the closest ghost is risky
            elif closestGhostDistance != -1:
                # the factor "2" is used to obtain 
                # better results
                delta = ghostReward * 2 / closestGhostDistance
                expectedUtility += delta

        policies.append((expectedUtility, move))

    # get the first policy (the one with the highest score), which is a 
    # tuple (score, move), and from it get the second element, which 
    # is the best move
    bestMove = sorted(policies, reverse=True)[0][1]

    if MDPAgent.DEBUG:
        print MDPAgent.moveToDirection[bestMove]
    return bestMove


def bellmanEquation(reward, 
                    location, 
                    valueIterationMap, 
                    movesMap, 
                    distancesMap, 
                    discountFactor,
                    moves=MDPAgent.moves
                ):
    '''
    Return the result of Bellman's equation.
    '''
    utilities = []
    for move in moves:
        moveUtility = getMoveUtility(location, move, valueIterationMap, movesMap)
        utilities.append(moveUtility)
    
    expectedUtility = max(utilities)
    ################# CHANGEEEEEEEEEEEEEEEEEe
    return reward + discountFactor * expectedUtility


def getMoveUtility(location, move, valueIterationMap, movesMap):
    '''
    Given a location and a move, calculate the values you would obtain
    trying to perform that move keeping into account that you only have 80%
    chance to actually perform that move, and return their sum. 
    The list returned is a 3-value vectors wherein the elements in order are:
        1) expected value from making the decided move;
        2 & 3) expected values from making a traversal move.
    '''
    values = []

    # main move value
    values.append(getLocationUtility(location, move, valueIterationMap, movesMap) * .8)

    for traversalMove in MDPAgent.traversalMoves[move]:
        values.append(getLocationUtility(location, traversalMove, valueIterationMap, movesMap) * .1)

    return sum(values)


def getLocationUtility(startingLocation, 
                       move,    
                       valueIterationMap, 
                       movesMap
                    ):
    '''
    Given a location and a move, calculate the value you
    would obtain performing that move from that location (which could result
    in hitting the wall).
    This value takes into account ghosts, which influence the score 
    based on their distance from the landing location.
    '''

    NO_MOVE = (0, 0)

    # find out the landinding location given the starting location and the move
    operatedMove = move if move in movesMap[startingLocation] else NO_MOVE

    landingLocation = sumTuples(startingLocation, operatedMove)

    # sum the value of the location with the totalGhostsRewards and then
    # multiply by the probability of landing on that location
    return valueIterationMap[landingLocation]


def getVisitbaleWidthAndHeight(state):
    '''
    Return a tuple (x, y) of the top-most right-most
    location in the map
    '''
    topRightCorner = max(api.walls(state))

    # the corners belong to the walls, so in a map 4 x 4
    # the top right corner is (3, 3), but it's a wall, so the map is
    # 2 x 2 from the agent perspective, so the width is 3 - 1
    return (topRightCorner[0] - 1, topRightCorner[1] - 1)


def getMapLocations(mapWidth, mapHeight):
    '''
    Return a list of all the locations in the map
    '''
    widthArray = range(1, mapWidth + 1)
    heightArray = range(1, mapHeight + 1)
    return [element for element in itertools.product(heightArray, widthArray)]


def getNonWallLocations(walls, state):
    '''
    Return a list of non-wall locations
    '''
    width, height = getVisitbaleWidthAndHeight(state)
    mapLocationsMatrix = getMapLocations(height, width)
    return [x for x in mapLocationsMatrix if x not in walls]


def getLegalMoves(accessibleMap, location):
    '''
    Given a location and the accessibleMap, 
    Return the moves that can be made from there
        e.g. [(1, 0), (-1, 0)]
        Pacman can only move EAST or WEST
    '''
    return [move for move in MDPAgent.moves if sumTuples(location, move) in accessibleMap]


def getMapMoves(accessibleMap):
    '''
    Return a dictionary of the possible moves for each location
    in the form {location: moves[]}
        e.g. { (6, 5): [(1, 0), (-1, 0)]} 
        the only moves are going either EAST or WEST
    '''
    return {location: getLegalMoves(accessibleMap, location) for location in accessibleMap}









        if MDPAgent.DEBUG:
        l = ""
        for i in range(9, 0, -1):
            for j in range(1, 19):
                l+= str(elementGradientValueMap[(j, i)]) if (j,i) in elementGradientValueMap else '-'*5
                if len(l) < 5:
                    l = (l + "0000")[:5]
                l+= " | "
            l+="\n"
        print l