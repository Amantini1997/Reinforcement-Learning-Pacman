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

    MOVE_DEBUG = False

    ## MEDIUM CLASSIC SETTINGS
    ACTIVE_GHOSTS_MAX_ALLOWED_DISTANCE = 6
    EDIBLE_GHOSTS_MAX_ALLOWED_DISTANCE = 3 # None

    ## MEDIUM CLASSIC SETTINGS (all +18.0)
    ACTIVE_GHOST_REWARD = -18.0
    EDIBLE_GHOST_REWARD = -4.0
    FOOD_REWARD = 2.0
    NO_FOOD_REWARD = -0.5
    # Pacman will not be penalised
    # for operating more moves
    MOVE_REWARD = -0.04
    # but its location will be to prompt him
    # to make move
    PACMAN_REWARD = -2.0
    DEAD_END_REWARD = -1.5
    DISCOUNT_FACTOR = 0.97

    oppositeDirections = {
        Directions.SOUTH: Directions.NORTH,
        Directions.NORTH: Directions.SOUTH,
        Directions.EAST: Directions.WEST,
        Directions.WEST: Directions.EAST     
    }

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

        # the type is { location: score }
        self.valueIterationMap = {} 

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
        self.walls = api.walls(state)
        self.accessibleMap = getNonWallLocations(self.walls, state)
        self.movesMap = getMapMoves(self.accessibleMap)
        self.deadEnds = getDeadEnds(self.accessibleMap, self.movesMap)

        food = api.food(state)
        capsules = api.capsules(state)
        self.food = food + capsules
        self.isSmallGrid = len(capsules) == 0
        self.initialFoodCount = len(self.food)


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
        self.distancesMap = getLocationsDistanceFromPacman(pacman, self.movesMap)

        # Ghosts related updates
        self.ghostsStates = api.ghostStates(state)

        activeGhosts, edibleGhosts = getActiveAndEdibleGhostsLocations(self.ghostsStates, self.distancesMap)

        # riskyActiveGhosts, riskyEdibleGhosts = getRiskyGhosts(activeGhosts, edibleGhosts, self.distancesMap)
        
        self.valueIterationMap = getValueIterationMap(self.accessibleMap, 
                                                        self.movesMap, 
                                                        self.distancesMap,
                                                        pacman, 
                                                        activeGhosts, #riskyActiveGhosts,
                                                        edibleGhosts, #riskyEdibleGhosts,
                                                        self.food, 
                                                        self.isSmallGrid,
                                                        self.deadEnds,
                                                        self.initialFoodCount)

        bestMove = getBestNextMove(self.moves, 
                                    pacman, 
                                    self.valueIterationMap, 
                                    self.movesMap, 
                                    self.distancesMap, 
                                    self.isSmallGrid)


        bestDirection = self.moveToDirection[ bestMove ]

        return api.makeMove(bestDirection, api.legalActions(state))






 








###############
#             #   
#  FUNCTIONS  #
#             #   
###############
def avg( list ):
    '''
    Return the average value of a list
    '''
    return sum(list) / (0.0 + len(list))


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


# def getRiskyGhosts(activeGhosts,
#                    edibleGhosts, 
#                    distancesMap, 
#                    allowedDistanceForActiveGhosts=MDPAgent.ACTIVE_GHOSTS_MAX_ALLOWED_DISTANCE,
#                    allowedDistanceForEdibleGhosts=MDPAgent.EDIBLE_GHOSTS_MAX_ALLOWED_DISTANCE
#                 ):
#     '''
#     Given active and edible ghosts, and a distance map,
#     return a the ghosts considered risky, that is, too close
#     to pacman. The max allowed distance varies based on the ghost
#     state {active, edible}.
#     '''
#     # 1 -> ghost is edible
#     # 0 -> ghost is active
#     riskyActiveGhosts = filter(lambda ghost: distancesMap[ghost] <= allowedDistanceForActiveGhosts, activeGhosts) 
#     riskyEdibleGhosts = filter(lambda ghost: distancesMap[ghost] <= allowedDistanceForEdibleGhosts, edibleGhosts) 

#     return riskyActiveGhosts, riskyEdibleGhosts


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
        

def getLocationsDistanceFromPacman(pacman, movesMap):
    '''
    Return the distance of each location from pacman
    as a dict { location: distance }
    '''

    currentDistance = 0

    visitedLocations = { pacman: currentDistance }

    unvisitedLocations = { pacman }

    while len(unvisitedLocations) > 0:
        
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
                            allowedDistanceForActiveGhosts=MDPAgent.ACTIVE_GHOSTS_MAX_ALLOWED_DISTANCE,
                            allowedDistanceForEdibleGhosts=MDPAgent.EDIBLE_GHOSTS_MAX_ALLOWED_DISTANCE,
                            foodReward=MDPAgent.FOOD_REWARD,   
                            moveReward=MDPAgent.MOVE_REWARD,  
                            activeGhostReward=MDPAgent.ACTIVE_GHOST_REWARD,
                            edibleGhostReward=MDPAgent.EDIBLE_GHOST_REWARD,
                            pacmanReward=MDPAgent.PACMAN_REWARD,      
                            deadEndReward=MDPAgent.DEAD_END_REWARD,
                            noFoodReward=MDPAgent.NO_FOOD_REWARD,
                            discountFactor=MDPAgent.DISCOUNT_FACTOR,
                            epsilon=0.1
                        ):
    '''
    Return the value iteration map. Epsilon is the threshold, if the max change in the map 
    is below that number, we stop iterating (to improve performance).
    minAllowedScoreChange prevents location to update their scores by an amount which is 
    too small. 
    '''
    # initialise value iteration map
    oldValueIterationMap = { location : noFoodReward for location in accessibleMap }

    # a list of locations with variable score is created 
    # removing the food and ghosts from the map.
    ## MEDIUM CLASSIC SETTINGS
    nonScoreableLocations = edibleGhosts + activeGhosts
    scoreableLocations = [ location for location in accessibleMap if location not in nonScoreableLocations ]
    # nonScoreableObjects = edibleGhosts + activeGhosts if isSmallGrid else []

    # the value of food increase as less food remains
    ## MEDIUM GRID SETTINGS
    foodReward *= initialFoodCount / (len(food) + 0.0)

    
    # update the old map in food and ghosts locations
    for foodLocation in food: oldValueIterationMap[foodLocation] += foodReward
    for ghostLocation in activeGhosts: oldValueIterationMap[ghostLocation] += activeGhostReward
    for ghostLocation in edibleGhosts: oldValueIterationMap[ghostLocation] += edibleGhostReward
    for deadEnd in deadEnds: oldValueIterationMap[deadEnd] += deadEndReward
    
    NO_MOVE = (0, 0)
    ## MEDIUM CLASSIC SETTINGS
    # reduce the initial score of pacman's adjacent location (and 
    # pacman's location itself) based on how closer they are to ghosts
    for move in movesMap[pacman] + [NO_MOVE]:
        newLocation = sumTuples(pacman, move)
        closestActiveGhostDistance = findDistanceToClosestGhostWithinAllowedSteps(newLocation, movesMap, activeGhosts, allowedDistanceForActiveGhosts)
        closestEdibleGhostDistance = findDistanceToClosestGhostWithinAllowedSteps(newLocation, movesMap, edibleGhosts, allowedDistanceForEdibleGhosts)
        
        closestActiveGhostReward = getGhostRewardBasedOnDistance(closestActiveGhostDistance, activeGhostReward)
        closestEdibleGhostReward = getGhostRewardBasedOnDistance(closestEdibleGhostDistance, edibleGhostReward)

        lowestGhostReward = min(closestActiveGhostReward, closestEdibleGhostReward)
        oldValueIterationMap[newLocation] += lowestGhostReward

    ## MEDIUM CLASSIC SETTINGS
    # Pacman should try to always change location
    oldValueIterationMap[pacman] = pacmanReward 

    # this is used to determine the end of the 
    # value iteration loop
    maxUpdate = epsilon + 1

    while maxUpdate > epsilon:
        # initialise the next value iteration map
        newValueIterationMap = {}

        maxUpdate = 0
        
        for scoreableLocation in scoreableLocations:

            locationValue = bellmanEquation(moveReward, scoreableLocation, oldValueIterationMap, movesMap, distancesMap)    

            locationValueUpdate = abs(locationValue - oldValueIterationMap[scoreableLocation])

            maxUpdate = max(maxUpdate, locationValueUpdate)

            ## MEDIUM CLASSIC SETTINGS
            # update the respective value in the new map if the change
            # is sufficiently big
            # if locationValueUpdate > minAllowedScoreChange:
            #     newValueIterationMap[scoreableLocation] = locationValue
            # allow 
            # if locationValueUpdate > oldValueIterationMap[scoreableLocation] * .2:
            #     maxAllowedUpdate = oldValueIterationMap[scoreableLocation] * .2
            #     # adjust the update sign
            #     maxAllowedUpdate *= 1 if locationValueUpdate > 0 else -1  
            #     newValueIterationMap[scoreableLocation] = locationValue
            newValueIterationMap[scoreableLocation] = locationValue

        # update old value iteration map
        for key, newValue in newValueIterationMap.items():
            oldValueIterationMap[key] = newValue

    ## MEDIUM GRID SETTINGS
    # pacman should try to always chenage location
    # oldValueIterationMap[pacman] -= 0.5
    for location in distancesMap:
        oldValueIterationMap[location] -= distancesMap[location] * moveReward

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
                    distancesMap, 
                    isSmallGrid
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
        expectedValue = getMoveUtility(pacman, move, valueIterationMap, movesMap)
        newMoveLocation = sumTuples(pacman, move) if move in movesMap[pacman] else pacman
        
        ## CHANGE
        if False:
            closestGhostDistance = locationToGhostsDistances[newMoveLocation]

            # a move ending up in a ghost location is terrible
            if closestGhostDistance == 0:
                expectedValue += ghostReward * 2
            # if the closest ghost is risky
            elif closestGhostDistance != -1:
                # the factor "2" is used to obtain 
                # better results
                delta = ghostReward * 2 / closestGhostDistance
                expectedValue += delta

        policies.append((expectedValue, move))

    # get the first policy (the one with the best score), which is a 
    # tuple (score, move), and from it get the second element, which 
    # is the best move
    bestMove = sorted(policies, reverse = True)[0][1]

    # l = ""
    # for i in range(9, 0, -1):
    #     for j in range(1, 19):
    #         l+= str(valueIterationMap[(j, i)])[:5] if (j,i) in valueIterationMap else "     "
    #         l+= " | "
    #     l+="\n"
    # print l
    return bestMove


def bellmanEquation(reward, 
                    location, 
                    valueIterationMap, 
                    movesMap, 
                    distancesMap, 
                    moves=MDPAgent.moves, 
                    discountFactor=MDPAgent.DISCOUNT_FACTOR,
                    utilitiesDealerFunction=avg,
                ):
    '''
    Return the result of Bellman's equation.
    '''
    utilities = []
    for move in moves:
        moveUtility = getMoveUtility(location, move, valueIterationMap, movesMap)
        utilities.append(moveUtility)
    
    ## CHANGE
    # expectedUtility = max(utilities)
    expectedUtility = utilitiesDealerFunction(utilities)
    return reward + pow(discountFactor, distancesMap[location]) * expectedUtility


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


def getVisitableWidthAndHeight(state):
    '''
    Return a tuple (x, y) where x and y are, respectively,
    the width and the height of the map.
    '''
    topRightCorner = max(api.walls(state))
    # Corners belong to the perimeter wall. As the program uses
    # an array index notation to indicate the position of cells,
    # in a 4 x 8 map the top-right corner is (3, 7).
    # If (3, 7) is the top-right corner, the most right accessible
    # cell is 3 - 1, and the top most accessible cell is 7 - 1 
    return (topRightCorner[0] - 1, topRightCorner[1] - 1)


def getNonPerimeterLocations(mapWidth, mapHeight):
    '''
    Return a list of all the locations in the map
    which do not belong to the perimeter wall
    '''
    # using the array notation, a cell (x, y) with x = 0
    # or y = 0 belongs to the perimeter wall, so we start 
    # from 1. 
    widthArray = range(1, mapWidth + 1)
    heightArray = range(1, mapHeight + 1)
    return [element for element in itertools.product(heightArray, widthArray)]


def getNonWallLocations(walls, state):
    '''
    Return a list of non-wall locations
    '''
    width, height = getVisitableWidthAndHeight(state)
    nonPerimeterLocations = getNonPerimeterLocations(height, width)
    return [x for x in nonPerimeterLocations if x not in walls]


def getLegalMoves(accessibleMap, location):
    '''
    Given a location and the accessibleMap, 
    Return the moves that can be performed from 
    that location
        e.g. [(1, 0), (-1, 0)]
        Pacman can only move EAST or WEST
    '''
    return [move for move in MDPAgent.moves if sumTuples(location, move) in accessibleMap]


def getMapMoves(accessibleMap):
    '''
    Return a dict of the possible moves for each location
    in the form { location: moves[] }
        e.g. { (6, 5): [(1, 0), (-1, 0)]} 
        the only moves are going either EAST or WEST
    '''
    return {location: getLegalMoves(accessibleMap, location) for location in accessibleMap}