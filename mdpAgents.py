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
    ACTIVE_GHOSTS_MIN_ALLOWED_DISTANCE = 7
    EDIBLE_GHOSTS_MIN_ALLOWED_DISTANCE = 3
    DEADEND_MIN_ALLOWED_DISTANCE = 1

    # rewards
    ACTIVE_GHOST_REWARD = -5.0
    EDIBLE_GHOST_REWARD = -2.0
    FOOD_REWARD = 1.0
    MOVE_REWARD = -0.04

    # this is used to prompt him to make move
    PACMAN_REWARD = -10.0
    DEAD_END_REWARD = -15.0
    DISCOUNT_FACTOR = 0.95
    EPSILON = 0.05

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
        static data of the world , i.e. data that will never 
        change throughout the execution of the game in the same
        world, as such, it is intended to be called only once.
        '''        
        self.walls = api.walls(state)
        self.accessibleMap = getNonWallLocations(self.walls, state)
        self.movesMap = getMapMoves(self.accessibleMap)
        self.isSmallGrid = len(self.accessibleMap) < 30
        self.deadEnds = getDeadEnds(self.accessibleMap, self.movesMap)

        if self.isSmallGrid:
            self.ACTIVE_GHOST_REWARD = -2.5 
            self.LAST_FOOD_REWARD = 16.0


    def getAction(self, state):

        # one time operations
        if self.firstMove:
            self.setUpWorld(state)
            # prevent this method from being called again
            self.firstMove = False

        # operations to be performed at the beginning of every action
        food = api.food(state)
        capsules = api.capsules(state)
        self.food = food + capsules

        # updates related to pacman
        pacman = api.whereAmI(state)
        self.distancesMap = getLocationsDistanceFromStartingLocation(pacman, self.movesMap)

        # updates related to ghosts
        self.ghostsStates = api.ghostStates(state)

        activeGhosts, edibleGhosts = getActiveAndEdibleGhostsLocations(self.ghostsStates, self.distancesMap)
        
        valueIterationMap = getValueIterationMap(self.accessibleMap, 
                                                 self.movesMap, 
                                                 self.distancesMap,
                                                 pacman, 
                                                 activeGhosts,
                                                 edibleGhosts,
                                                 self.food, 
                                                 self.isSmallGrid,
                                                 self.deadEnds,
                                                 self)

        bestMove = getBestNextMove(self.moves, 
                                   pacman, 
                                   valueIterationMap, 
                                   self.movesMap, 
                                   self.distancesMap)

        bestDirection = self.moveToDirection[ bestMove ]

        return api.makeMove(bestDirection, api.legalActions(state))









###############
#             #   
#  FUNCTIONS  #
#             #   
###############
def sumTuples(tuple1, tuple2):
    return tuple([(i + j) for i, j in zip(tuple1, tuple2)])


def getDeadEnds(accessibleMap, movesMap):
    '''
    Given the list of the accessible locations on the map,
    return a list of locations surrounded by 3 walls.
    '''
    deadEnds = [location for location in accessibleMap if len(movesMap[location]) == 1]
    return deadEnds


def getActiveAndEdibleGhostsLocations(ghostsStates, distancesMap):
    '''
    Given the ghosts' states, return 2 lists, respectively
    a list containing active ghosts and one containing
    edible ghosts. The location of the ghost is used by default, but if
    a ghost is amid 2 locations (which happens only when it is edible),
    the closest location to Pacman (chosen between the 2 adjacent to the 
    ghost) is used instead.
    '''
    activeGhosts = []
    edibleGhosts = []

    IS_EDIBLE = 1

    for ghostState in ghostsStates:
        ghost = ghostState[0]
        status = ghostState[1]
        if status == IS_EDIBLE:
            # as edible ghosts may have locations (a, b) as (x.5, y) 
            # we consider both locations as x.5 + 0.5 and x.5 - 0.5.
            adjacentGhostLocations = getAdjacentGhostLocationsIfLocationNotOnMap(ghost)
            adjacentGhostLocationsDistances = {distancesMap[ghost]: ghost for ghost in adjacentGhostLocations} 

            # only the location which is closer to pacman is taken into account.
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

    # if the list is empty no ghost is reachable
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

        # transform this list into a set to remove duplicates
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


def getAdjacentGhostLocationsIfLocationNotOnMap(ghost):
    '''
    As edible ghosts may have intermediate locations like (x.5, y),
    this method returns both locations as x.5 + 0.5 and x.5 - 0.5. 
        e.g (2.5, 2) -> [(2, 2), (3, 2)]
    If the ghost is at the centre of a location, that location 
    is returned as an array. ( the same applies to y )
        e.g (3, 3) -> [(3, 3)]
    '''
    x = ghost[0]
    y = ghost[1]
    xs = [x] if x % 1 == 0 else [x + 0.5, x - 0.5]
    ys = [y] if y % 1 == 0 else [y + 0.5, y - 0.5]
    return [location for location in itertools.product(xs, ys)]


def getLocationsDistanceFromStartingLocation(startingLocation, movesMap, limit=float("inf")):
    '''
    Return the distance of each location from a starting location
    as a dict { location: distance_from_starting_location }. 
    The distance can be limited to a max steps limit by passing
    the optional parameter "limit", otherwise the whole map is inspected.
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


def getValueIterationMap(accessibleMap,        
                         movesMap,
                         distancesMap,              
                         pacman, 
                         activeGhosts,
                         edibleGhosts,             
                         food,        
                         isSmallGrid,
                         deadEnds,
                         agent):
    '''
    Return the value iteration map. Epsilon is a threshold and, if the max change in the map 
    is below that number, we stop iterating (to improve performance).
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

    if isSmallGrid and len(food) == 1:
        foodReward = agent.LAST_FOOD_REWARD
     
    # deadEnds are risky, but if Pacman is too close it could be wrong
    # to tell him to leave
    deadEndIsAdjacent = lambda deadEnd: distancesMap[deadEnd] == 1 
    adjacentDeadEnds = filter(deadEndIsAdjacent, deadEnds)
    if len(adjacentDeadEnds) > 0:
        deadEndReward = 0

    preValueIterationMap = { location : 0 for location in accessibleMap }

    # active ghosts, edible ghosts and deadEnds are
    # dangerous for Pacman, so, for each of these elements, create a
    # halo of negative rewards which is weaker the further
    # the location is from the dangerous element
    for ghost in activeGhosts:
        ghostIterationMap = getGradientMap(ghost, activeGhostReward, movesMap, allowedDistanceForActiveGhosts) 
        for location in ghostIterationMap:
            preValueIterationMap[location] += ghostIterationMap[location]
                    
    for ghost in edibleGhosts:
        ghostIterationMap = getGradientMap(ghost, edibleGhostReward, movesMap, allowedDistanceForEdibleGhosts) 
        for location in ghostIterationMap:
            preValueIterationMap[location] += ghostIterationMap[location]

    for deadEnd in deadEnds:
        deadendIterationMap = getGradientMap(deadEnd, deadEndReward, movesMap, allowedDistanceForDeadends) 
        for location in deadendIterationMap:
            preValueIterationMap[location] += deadendIterationMap[location]


    # Update the value map in food locations
    for foodLocation in food: preValueIterationMap[foodLocation] += foodReward
    # Update the map in Pacman's location
    preValueIterationMap[pacman] += pacmanReward 
    
    
    # a list of locations with non updatable score is created 
    nonUpdatableLocations = edibleGhosts + activeGhosts + food

    # define the locations with updatable score considering all the locations
    # in the map that are not included in the nonUpdatableLocations list
    updatableLocations = [ location for location in accessibleMap if location not in nonUpdatableLocations ]

    return valueIterationFunction(preValueIterationMap, 
                                  movesMap,
                                  updatableLocations, 
                                  moveReward, 
                                  epsilon, 
                                  discountFactor) 


def getGradientMap(element, elementReward, movesMap, stepsLimit, discountFactor=0.7):
    '''
    Given a an element on the map and its reward, consider a
    halo of locations reachable within a steps limit and assign them a value.
    The value assigned is proportional to their distance from the element,
    meaning that a location adjacent to the element will have a value closer to 
    the original element reward, whereas a location far away will be closer to 0.
    The formula used is (value = discountFactor ^ distance * score).
    The element location is included in this dict, and the value 
    will be equal to the reward of the element itself.
    The function returns a dict { location: value }.

    '''
    # computing the distance of cells from the element
    elementDistancesMap = getLocationsDistanceFromStartingLocation(element, movesMap, limit=stepsLimit)
    elementGradientValueMap = { location: (discountFactor**elementDistancesMap[location])*elementReward for location in elementDistancesMap.keys() }
    return elementGradientValueMap


def valueIterationFunction(oldValueIterationMap, 
                           movesMap, 
                           updatableLocations, 
                           moveReward, 
                           epsilon, 
                           discountFactor):
    '''
    Update the value of each updatable location in the map
    using an iterative process which stops when the max update
    is less than a given threshold (epsilon).
    '''
    maxUpdate = epsilon + 1

    while maxUpdate > epsilon:

        # initialise the next value iteration map
        newValueIterationMap = {}
        maxUpdate = 0
        
        # update the value of each updatable location
        for updatableLocation in updatableLocations:
            locationValue = bellmanEquation(moveReward, 
                                            updatableLocation, 
                                            oldValueIterationMap, 
                                            movesMap,  
                                            discountFactor)    
            locationValueUpdate = abs(locationValue - oldValueIterationMap[updatableLocation])
            newValueIterationMap[updatableLocation] = locationValue

            maxUpdate = max(maxUpdate, locationValueUpdate)

        # update old value iteration map
        for key, newValue in newValueIterationMap.items():
            oldValueIterationMap[key] = newValue

    return oldValueIterationMap 


def getBestNextMove(moves, 
                    pacman, 
                    valueIterationMap, 
                    movesMap,
                    distancesMap):
    '''
    Given Pacman's location and the valueIterationMap,
    Calculate and return the best move for Pacman.
        e.g. If the best move is NORTH the function returns (0, 1)
    '''

    # this is a list containing all the policies in the 
    # form (score, (x, y))
    policies = []

    # this loop aims to populate the policies list, as such, we consider all the moves
    # here, even if they would result in Pacman hitting the wall.
    for move in moves:
        expectedUtility = getMoveUtility(pacman, move, valueIterationMap, movesMap)

        policies.append((expectedUtility, move))

    # sort the policies by their value and get the first 
    # policy [0th], which is a 
    # tuple (score, move), and from it get the second element [1], 
    # which is the best move
    bestMove = sorted(policies, reverse=True)[0][1]

    return bestMove


def bellmanEquation(reward, 
                    location, 
                    valueIterationMap, 
                    movesMap, 
                    discountFactor,
                    moves=MDPAgent.moves):
    '''
    Return the result of Bellman's equation.
    '''
    utilities = []
    
    # calculate the utility for each move
    for move in moves:
        moveUtility = getMoveUtility(location, move, valueIterationMap, movesMap)
        utilities.append(moveUtility)
    
    expectedUtility = max(utilities)
    
    return reward + discountFactor * expectedUtility


def getMoveUtility(location, move, valueIterationMap, movesMap):
    '''
    Given a location and a move, calculate the values you would obtain
    trying to perform that move (keeping into account that you only have 80%
    chance to actually perform it) and return their sum.
    '''
    values = []

    # main move value
    values.append(getLocationUtility(location, move, valueIterationMap, movesMap) * .8)

    # traversal moves values
    for traversalMove in MDPAgent.traversalMoves[move]:
        values.append(getLocationUtility(location, traversalMove, valueIterationMap, movesMap) * .1)

    return sum(values)


def getLocationUtility(startingLocation, 
                       move,    
                       valueIterationMap, 
                       movesMap):
    '''
    Given a location and a move, calculate the value you
    would obtain performing that move from that location (which could result
    in hitting the wall).
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
    accessible location in the map.
    '''
    topRightCorner = max(api.walls(state))

    # the corners belong to the walls, so in a map 4 x 4
    # the top right corner is (3, 3), but it's a wall, so the map is
    # 2 x 2 from the agent perspective, so the width is 3 - 1
    return (topRightCorner[0] - 1, topRightCorner[1] - 1)


def getMapLocations(mapWidth, mapHeight):
    '''
    Return a list of all the locations in the map.
    '''
    widthArray = range(1, mapWidth + 1)
    heightArray = range(1, mapHeight + 1)
    return [element for element in itertools.product(heightArray, widthArray)]


def getNonWallLocations(walls, state):
    '''
    Return a list of non-wall locations.
    '''
    width, height = getVisitbaleWidthAndHeight(state)
    mapLocationsMatrix = getMapLocations(height, width)
    return [x for x in mapLocationsMatrix if x not in walls]


def getLegalMoves(accessibleMap, location):
    '''
    Given a location and the accessibleMap, 
    Return the moves that can be made from there.
        e.g. [(1, 0), (-1, 0)]
        Pacman can only move EAST or WEST
    '''
    return [move for move in MDPAgent.moves if sumTuples(location, move) in accessibleMap]


def getMapMoves(accessibleMap):
    '''
    Return a dictionary of the possible moves (i.e. that moves)
    that lead to a a different location) for each location
    in the form {location: moves[]}
        e.g. { (6, 5): [(1, 0), (-1, 0)]} 
        the only moves are EAST and WEST
    '''
    return {location: getLegalMoves(accessibleMap, location) for location in accessibleMap}