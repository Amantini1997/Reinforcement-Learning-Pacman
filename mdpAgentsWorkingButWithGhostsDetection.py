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

    GHOSTS_MAX_ALLOWED_DISTANCE = 8
    EDIBLE_GHOSTS_MAX_ALLOWED_DISTANCE = 1 # None

    GHOST_REWARD = -7.0
    FOOD_REWARD = 1.0
    MOVE_REWARD = -0.04
    DISCOUNT_FACTOR = 0.9

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
        (0, -1): [(1, 0), (-1, 0)]     # South
    }

    moveToDirection = {
        (1, 0)  : Directions.EAST,
        (-1, 0) : Directions.WEST,
        (0, 1)  : Directions.NORTH,
        (0, -1) : Directions.SOUTH,
        (0, 0)  : Directions.STOP
    }

    def __init__(self):
        self.firstIteration = True
        self.requestedMove_operatedMove_pair = [] # (requested, operated)
        self.previousPosition = None
        
        # STATIC ELEMENTS
        # list of all the locations pacman has access to
        self.accessibleMap = []

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


    def getAction(self, state):

        # One time operations
        if self.firstIteration:
            food = api.food(state)
            capsules = api.capsules(state)
            self.food = food + capsules
            self.firstIteration = False
            self.walls = api.walls(state)
            self.accessibleMap = getNonWallLocations(self.walls, state)
            self.movesMap = getMapMoves(self.accessibleMap)
            self.isSmallGrid = len(capsules) == 0
            self.valueIterationMap = { location : 0 for location in self.accessibleMap }


        # Operations to be performed at every action iteration
        food = api.food(state)
        capsules = api.capsules(state)
        self.food = food + capsules

        # Updates related to pacman
        pacman = api.whereAmI(state)
        self.distancesMap = getLocationsDistanceFromPacman(pacman, self.movesMap)

        # Ghosts related updates
        self.ghostsStates = api.ghostStates(state)


        riskyGhosts = getRiskyGhostsGivenState2(self.ghostsStates, self.distancesMap)

        ghosts = map(lambda ghost: ghost[0], self.ghostsStates)
        
        updateValueIterationMap(self.accessibleMap, 
                                self.movesMap, 
                                self.distancesMap,
                                self.valueIterationMap, 
                                pacman, 
                                ghosts,
                                self.food, 
                                self.isSmallGrid,
                                riskyGhosts=riskyGhosts)

        bestMove = getBestNextMove(self.moves, 
                                    pacman, 
                                    self.valueIterationMap, 
                                    self.movesMap, 
                                    self.distancesMap, 
                                    ghosts, 
                                    self.isSmallGrid,
                                    riskyGhosts,
                                    maxAllowedSteps=MDPAgent.GHOSTS_MAX_ALLOWED_DISTANCE)


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


def getRiskyGhostsGivenState2(ghostsStates, 
                              distancesMap, 
                              allowedDistanceForActiveGhosts=MDPAgent.GHOSTS_MAX_ALLOWED_DISTANCE,
                              allowedDistanceForEdibleGhosts=MDPAgent.EDIBLE_GHOSTS_MAX_ALLOWED_DISTANCE
                            ):
    '''
    Given the ghosts states and a distance map,
    return a dict { ghostLocation: distanceFormPacman } of ghosts
    which distanceFromPacman <= allowedDistance (varying based on the ghost state)
    '''
    riskyGhosts = { }
    IS_EDIBLE = 1
    # 1 -> ghost is edible
    # 0 -> ghost is active

    for ghostState in ghostsStates:
        ghost = ghostState[0]
        if ghostState[1] == IS_EDIBLE:
            # As edible ghosts may have locations (a, b) as (x.5, y) 
            # we consider both locations as x.5 + 0.5 and x.5 - 0.5.
            adjacentGhostsLocations = getAdjacentGhostsLocationsIfLocationNotOnMap(ghost)
            adjacentGhostsLocationsDistances = [distancesMap[ghost] for ghost in adjacentGhostsLocations] 

            # Only the location which is closer to pacman is taken into account.
            ghostDistance = min(adjacentGhostsLocationsDistances)
            if ghostDistance <= allowedDistanceForEdibleGhosts:
                riskyGhosts[ghost] = ghostDistance
        else:
            ghostDistance = distancesMap[ghost]
            if ghostDistance <= allowedDistanceForActiveGhosts:
                riskyGhosts[ghost] = ghostDistance

    return riskyGhosts


def findDistanceToClosestGhostWithinAllowedSteps(startingLocation, movesMap, ghosts, stepsLimit=5):
    ''' 
    Using Breadth First Search, decide if any of the given ghosts is reachable
    within n steps from the starting location where n = stepsLimit.
    The method returns -1 if none of the ghosts is reachable within 
    the steps limit, otherwise it returns the distance to the closest ghost.
    '''

    NO_GHOST_FOUND = -1

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


def getAdjacentGhostsLocationsIfLocationNotOnMap(ghost):
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


def getBestNextMove(moves, 
                    pacman, 
                    valueIterationMap, 
                    movesMap,
                    distancesMap, 
                    ghosts, 
                    isSmallGrid,
                    riskyGhosts,
                    maxAllowedSteps=MDPAgent.GHOSTS_MAX_ALLOWED_DISTANCE,
                    ghostReward=MDPAgent.GHOST_REWARD,
                    discountFactor=MDPAgent.DISCOUNT_FACTOR
                  ):
    '''
    Given pacman's location and the valueIterationMap,
    Calculates and return the best move for pacman.
    If a given move gets pacman closer to a ghost, such a move is penalised
    based on how close the ghost would be given that move.
        e.g. If the best move is NORTH the function returns (0, 1)
    '''

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

    return bestMove


def updateValueIterationMap(accessibleMap,        
                            movesMap,
                            distancesMap,              
                            oldValueIterationMap, 
                            pacman, 
                            ghosts,             
                            food,        
                            isSmallGrid,        
                            riskyGhosts = [], 
                            foodReward = MDPAgent.FOOD_REWARD,   
                            moveReward = MDPAgent.MOVE_REWARD,  
                            ghostReward = MDPAgent.GHOST_REWARD,      
                            discountFactor = MDPAgent.DISCOUNT_FACTOR,
                            epsilon = 0.01       
                        ):
    '''
    Update the value iteration map. Epsilon is the threshold, if the max change in the map 
    is below that number, we stop iterating (to improve performance).
    '''

    # A list of locations with no initial score is created 
    # removing the food and ghosts from the map.
    scoreableMap = [location for location in accessibleMap if not(location in food or location in ghosts)]

    # Create the next value iteration map
    newValueIterationMap = {}
    
    # Update the old map in food and ghosts locations
    for foodLocation in food: oldValueIterationMap[foodLocation] = foodReward
    for ghostLocation in ghosts: oldValueIterationMap[ghostLocation] = ghostReward

    if isSmallGrid:
        onePieceOfFoodLeft = not len(food) > 1
        ghost = ghosts[0]
        ghostIsTooCloseToPacman = len(riskyGhosts) > 0 and riskyGhosts[ghost] < 4
        
        # locations with no escapes are considered risky
        noEscapeLocations = filter(lambda location: len(movesMap[location]) == 1, movesMap.keys())
        
        pacmanIsNextToANoEscapeLocation = any(map(lambda location: distancesMap[location] < 2, noEscapeLocations))

        # In the small grid, due to the stochasticism, dead end locations are
        # very dangerous and pacman should avoid them if 
        # these dead ends do not contain the last piece of food or 
        if not (onePieceOfFoodLeft or 
                # the ghost is far enough from pacman or 
                ghostIsTooCloseToPacman or 
                # the dead end is far enough from pacman
                pacmanIsNextToANoEscapeLocation
            ):
            for noEscapeLocation in noEscapeLocations:
                oldValueIterationMap[noEscapeLocation] = ghostReward

        # If pacman gets into a dead end location, not to have him stuck 
        # there, we reduce the max allowed ghost distance so the ghosts
        # do not affect the policies when they are far enough
        if pacman in noEscapeLocations:
            MDPAgent.GHOSTS_MAX_ALLOWED_DISTANCE = 4


    # This is used to determine the end of the 
    # value iteration loop
    maxUpdate = epsilon + 1

    while maxUpdate > epsilon:
        maxUpdate = 0
        
        for scoreableLocation in scoreableMap:
            locationValue = bellmanEquation(moveReward, scoreableLocation, oldValueIterationMap, movesMap, distancesMap)    

            locationValueUpdate = abs(locationValue - oldValueIterationMap[scoreableLocation])

            maxUpdate = max(maxUpdate, locationValueUpdate)

            # update the respective value in the new map
            newValueIterationMap[scoreableLocation] = locationValue

        # update old value iteration map
        for key, newValue in newValueIterationMap.items():
            oldValueIterationMap[key] = newValue

        newValueIterationMap = {}


def bellmanEquation(reward, location, valueIterationMap, movesMap, distancesMap, moves=MDPAgent.moves, discountFactor=MDPAgent.DISCOUNT_FACTOR):
    '''
    Return the result of Bellman's equation.
    '''
    utilities = []
    for move in moves:
        moveUtility = getMoveUtility(location, move, valueIterationMap, movesMap)
        utilities.append(moveUtility)
        
    expectedUtility = max(utilities)
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