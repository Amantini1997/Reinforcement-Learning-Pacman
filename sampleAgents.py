# sampleAgents.py
# parsons/07-oct-2017
#
# Version 1.1
#
# Some simple agents to work with the PacMan AI projects from:
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

# The agents here are extensions written by Simon Parsons, based on the code in
# pacmanAgents.py

from pacman import Directions
from game import Agent
import api
import random
import game
import util

import itertools
from collections import defaultdict
import operator

# RandomAgent
#
# A very simple agent. Just makes a random pick every time that it is
# asked for an action.
class RandomAgent(Agent):

    def getAction(self, state):
        # Get the actions we can try, and remove "STOP" if that is one of them.
        legal = api.legalActions(state)
        if Directions.STOP in legal:
            legal.remove(Directions.STOP)
        # Random choice between the legal options.
        return api.makeMove(random.choice(legal), legal)

# RandomishAgent
#
# A tiny bit more sophisticated. Having picked a direction, keep going
# until that direction is no longer possible. Then make a random
# choice.
class RandomishAgent(Agent):

    # Constructor
    #
    # Create a variable to hold the last action
    def __init__(self):
         self.last = Directions.STOP
    
    def getAction(self, state):
        # Get the actions we can try, and remove "STOP" if that is one of them.
        legal = api.legalActions(state)
        if Directions.STOP in legal:
            legal.remove(Directions.STOP)
        # If we can repeat the last action, do it. Otherwise make a
        # random choice.
        if self.last in legal:
            return api.makeMove(self.last, legal)
        else:
            pick = random.choice(legal)
            # Since we changed action, record what we did
            self.last = pick
            return api.makeMove(pick, legal)

# SensingAgent
#
# Doesn't move, but reports sensory data available to Pacman
class SensingAgent(Agent):

    def getAction(self, state):

        # Demonstrates the information that Pacman can access about the state
        # of the game.

        # What are the current moves available
        legal = api.legalActions(state)
        print "Legal moves: ", legal

        # Where is Pacman?
        pacman = api.whereAmI(state)
        print "Pacman position: ", pacman

        # Where are the ghosts?
        print "Ghost positions:"
        theGhosts = api.ghosts(state)
        for i in range(len(theGhosts)):
            print theGhosts[i]

        # How far away are the ghosts?
        print "Distance to ghosts:"
        for i in range(len(theGhosts)):
            print util.manhattanDistance(pacman,theGhosts[i])

        # Where are the capsules?
        print "Capsule locations:"
        print api.capsules(state)
        
        # Where is the food?
        print "Food locations: "
        print api.food(state)

        # Where are the walls?
        print "Wall locations: "
        print api.walls(state)
        
        # getAction has to return a move. Here we pass "STOP" to the
        # API to ask Pacman to stay where they are.
        return api.makeMove(Directions.STOP, legal)







# ============== My Agents ====================
# GoWestAgent
#
# Tries to go WEST, when this is not possible.
class GoWestAgent(Agent):

    # Constructor
    #
    # Create a variable to hold the last action
    def __init__(self):
         self.last = Directions.STOP
         self.preferred = Directions.WEST
    
    def getAction(self, state):
        # Get the actions we can try, and remove "STOP" if that is one of them.
        legal = api.legalActions(state)
        if Directions.STOP in legal:
            legal.remove(Directions.STOP)
        # If we can repeat the last action, do it. Otherwise make a
        # random choice.
        if self.preferred in legal:
            self.last = self.preferred
            return api.makeMove(self.preferred, legal)
        elif self.last in legal:
            return api.makeMove(self.last, legal)
        elif Directions.NORTH in legal or Directions.SOUTH in legal:
            non_EAST_directions = []
            if Directions.NORTH in legal: 
                non_EAST_directions.append(Directions.NORTH)
            if Directions.SOUTH in legal: 
                non_EAST_directions.append(Directions.SOUTH)
            pick = random.choice(non_EAST_directions)
            # Since we changed action, record what we did
            self.last = pick
            return api.makeMove(pick, legal)
            # return api.makeMove(pick, non_EAST_directions)

        else:
            self.last = Directions.EAST
            return api.makeMove(self.last, legal)


# HungryAgent
#
# A tiny bit more sophisticated. Having picked a direction, keep going
# until that direction is no longer possible. Then make a random
# choice.
class HungryAgent(Agent):

    def __init__(self):
        self.lastPosition = Directions.NORTH
        self.oppositeDirections = {
            Directions.SOUTH: Directions.NORTH,
            Directions.NORTH: Directions.SOUTH,
            Directions.EAST: Directions.WEST,
            Directions.WEST: Directions.EAST     
        }
        self.lastBestFoodPosition = None
        self.lastMinimumDistance = None

    def getAction(self, state):
        

        # What are the current moves available
        legal = api.legalActions(state)
        if Directions.STOP in legal:
            legal.remove(Directions.STOP)

        # # Where is Pacman?
        pacman = api.whereAmI(state)

        # # Where are the ghosts?
        theGhosts = api.ghosts(state)

        # # How far away are the ghosts?
        # print "Distance to ghosts:"
        # for i in range(len(theGhosts)):
        #     print util.manhattanDistance(pacman,theGhosts[i])

        # # Where are the capsules?
        # print "Capsule locations:"
        # print api.capsules(state)
        
        # # Where is the food?
        food = api.food(state)
        print food
        foodDistances = [(util.manhattanDistance(pacman, point), index) for index, point in enumerate(food)]
        sortedFoodDistances = sorted(foodDistances)
        DISTANCE = 0
        FOOD_INDEX = 1
        firstFood = sortedFoodDistances[0]
        secondFood = sortedFoodDistances[1]
        closestFood = food[firstFood[FOOD_INDEX]]

        # if firstFood[DISTANCE] == secondFood[DISTANCE]:
        #     closestFood = food[firstFood[FOOD_INDEX] if firstFood[FOOD_INDEX] < secondFood[FOOD_INDEX] else secondFood[FOOD_INDEX]]

        xyDistanceToClosestFood = manhattanNotAbsoluteDistance(closestFood, pacman)

        # if new closest food is not closer than the previous one
        # swipe it with the saved closest food
        if (self.lastMinimumDistance and
           sum(xyDistanceToClosestFood) > 1 and
           pacman != self.lastBestFoodPosition):

            if sum(xyDistanceToClosestFood) > sum(self.lastMinimumDistance):
                print "Last Min Distance: ", self.lastMinimumDistance
                print "Last Best Food: ", self.lastBestFoodPosition
                print "ActualDistToClosestFood: ", xyDistanceToClosestFood

                closestFood = self.lastBestFoodPosition
                print "CLOSEST_FOOD: ", closestFood
                xyDistanceToClosestFood = manhattanNotAbsoluteDistance(closestFood, pacman)
            
            elif sum(xyDistanceToClosestFood) == sum(self.lastMinimumDistance):
                pass

        # update pacman knowledge
        self.lastMinimumDistance = xyDistanceToClosestFood
        self.lastBestFoodPosition = closestFood

        print " PAC: ", pacman, "CLOSEST FOOD: ", closestFood, "  DISTANCE FROM IT: ", xyDistanceToClosestFood

        bestMoves = getBestNextMoves(legal, xyDistanceToClosestFood)
        
        # print "Food locations: "
        # print food

        # # Where are the walls?
        # print "Wall locations: "
        # print api.walls(state)

        # AVOID LOOP
        print "BEST MOVES", bestMoves, "  LEGAL: ", legal
        print "LAST POSITION: ", self.lastPosition

        # avoid ghost traplastPosition TODO
        # if self.lastPosition in bestMoves:
        #     return api.makeMove(self.lastPosition, legal)

        # prevent coming back (AVOID LOOP)
        if self.lastPosition in bestMoves and len(bestMoves) > 1:
            bestMoves.remove(self.lastPosition)
            print "REMOVED LAST POSITION: ", self.lastPosition
            print "NEW BEST MOVES: ", bestMoves



        pick = random.choice(bestMoves)
        self.lastPosition = self.oppositeDirections[pick]
        raw_input()
        print "\n====================================\n"
        return api.makeMove(pick, legal)


# CornerSeekingAgent
#
# A tiny bit more sophisticated. Having picked a direction, keep going
# until that direction is no longer possible. Then make a random
# choice.
class CornerSeekingAgent(Agent):

    def __init__(self):
        self.lastPosition = Directions.STOP
        self.oppositeDirections = {
            Directions.SOUTH: Directions.NORTH,
            Directions.NORTH: Directions.SOUTH,
            Directions.EAST: Directions.WEST,
            Directions.WEST: Directions.EAST     
        }
        self.lastBestFoodPosition = None
        self.lastMinimumDistance = None
        self.unvisitedCells = None
        self.unvisitedCorners = None
        self.walls = []
        self.firstIteration = True

    def getAction(self, state):
        if self.firstIteration:
            self.firstIteration = False
            self.unvisitedCorners = api.corners(state)
            self.walls = api.walls(state)
            self.unvisitedCells = getNonWallCells(self.walls, state)


        # What are the current moves available
        legal = api.legalActions(state)
        if Directions.STOP in legal:
            legal.remove(Directions.STOP)

        # # Where is Pacman?
        pacman = api.whereAmI(state)

        # Update lists based on pacman new position
        if pacman in self.unvisitedCells: self.unvisitedCells.remove(pacman)
        if pacman == self.lastBestFoodPosition: self.lastBestFoodPosition = None
        for corner in self.unvisitedCorners:
            distanceToCorner = manhattanNotAbsoluteDistance(pacman, corner)
            if (distanceToCorner[0] + distanceToCorner[1]) == 2: 
                self.unvisitedCorners.remove(corner)
            print "distance to corners", manhattanNotAbsoluteDistance(pacman, corner)

        # # Where are the ghosts?
        theGhosts = api.ghosts(state)

        # # How far away are the ghosts?
        # print "Distance to ghosts:"
        # for i in range(len(theGhosts)):
        #     print util.manhattanDistance(pacman,theGhosts[i])

        # # Where are the capsules?
        # print "Capsule locations:"
        # print api.capsules(state)
        
        # # Where is the food?
        food = api.food(state)
        if len(food) == 0:
            food = self.unvisitedCells
        
        ## TODO Remove this
        food = self.unvisitedCorners

        foodDistances = [(util.manhattanDistance(pacman, point), index) for index, point in enumerate(food)]
        sortedFoodDistances = sorted(foodDistances)
        print "SORTED TARGETS: ", sortedFoodDistances
        DISTANCE = 0
        FOOD_INDEX = 1

        firstFood = sortedFoodDistances[0] 
        closestFood = food[firstFood[FOOD_INDEX]]

        # if firstFood[DISTANCE] == secondFood[DISTANCE]:
        #     closestFood = food[firstFood[FOOD_INDEX] if firstFood[FOOD_INDEX] < secondFood[FOOD_INDEX] else secondFood[FOOD_INDEX]]

        xyDistanceToClosestFood = manhattanNotAbsoluteDistance(closestFood, pacman)

        # if new closest food is not closer than the previous one
        # swipe it with the saved closest food
        # TODO UNCOMMENT for newer versions
        # if (self.lastMinimumDistance and
        #    sum(xyDistanceToClosestFood) > 1 and
        #    pacman != self.lastBestFoodPosition):

        #     if sum(xyDistanceToClosestFood) > sum(self.lastMinimumDistance):
        #         print "Last Min Distance: ", self.lastMinimumDistance
        #         print "Last Best Food: ", self.lastBestFoodPosition
        #         print "ActualDistToClosestFood: ", xyDistanceToClosestFood

        #         closestFood = self.lastBestFoodPosition
        #         print "CLOSEST_FOOD: ", closestFood
        #         xyDistanceToClosestFood = manhattanNotAbsoluteDistance(closestFood, pacman)
            
        #     elif sum(xyDistanceToClosestFood) == sum(self.lastMinimumDistance):
        #         pass

        # update pacman knowledge
        self.lastMinimumDistance = xyDistanceToClosestFood
        self.lastBestFoodPosition = closestFood

        print " PAC: ", pacman, "CLOSEST FOOD: ", closestFood, "  DISTANCE FROM IT: ", xyDistanceToClosestFood

        legalCopy = legal
        if self.lastPosition in legalCopy:
            legalCopy.remove(self.lastPosition)
            print "REMOVED LAST POSITION: ", self.lastPosition

        bestMoves = getBestNextMoves(legalCopy, xyDistanceToClosestFood)
        
        # print "Food locations: "
        # print food

        # # Where are the walls?
        # print "Wall locations: "
        # print api.walls(state)

        # AVOID LOOP
        print "BEST MOVES", bestMoves, "  LEGAL: ", legal
        print "LAST POSITION: ", self.lastPosition

        # avoid ghost traplastPosition TODO
        # if self.lastPosition in bestMoves:
        #     return api.makeMove(self.lastPosition, legal)
        if len(bestMoves) == 0:
            bestMoves = legal

        # prevent coming back (AVOID LOOP)
        print self.lastPosition
        if self.lastPosition in bestMoves and len(bestMoves) > 1:
            bestMoves.remove(self.lastPosition)
            print "REMOVED LAST POSITION: ", self.lastPosition
            print "NEW BEST MOVES: ", bestMoves


        pick = random.choice(bestMoves)
        self.lastPosition = self.oppositeDirections[pick]
        print "SELECTED MOVE: ", pick
        raw_input()
        print "\n====================================\n"
        return api.makeMove(pick, legal)

def getVisitableCorners(corners):
    topRightCorner = max(corners)
    visitableCornerns = [(0,0), topRightCorner]









































class BetterHungryAgent(Agent):

    oppositeDirections = {
        Directions.SOUTH: Directions.NORTH,
        Directions.NORTH: Directions.SOUTH,
        Directions.EAST: Directions.WEST,
        Directions.WEST: Directions.EAST     
    }

    moves = [
        (1, 0),     # North
        (0, 1),     # East
        (-1, 0),    # South
        (0, -1)     # West
    ]

    moveToDirection = {
        (0, -1) : Directions.SOUTH,
        (0, 1) : Directions.NORTH,
        (1, 0) : Directions.EAST,
        (-1, 0) : Directions.WEST 
    }

    directionToMove = {
        Directions.SOUTH : (0, -1),
        Directions.NORTH : (0, 1),
        Directions.EAST : (1, 0),
        Directions.WEST : (-1, 0)
    }

    def __init__(self):
        self.lastPosition = Directions.STOP
        self.lastBestFoodPosition = None
        self.lastMinimumDistance = None
        self.unvisitedCells = None
        self.accessibleMap = None
        self.unvisitedCorners = None
        self.walls = []
        self.firstIteration = True

        # ABOUT LOCATIONS
        self.uneatenFood = set()
        self.unvisitedCells = set()
        self.visitedCells = set()
        self.accessibleMap = set()
        self.walls = set()

        # ABOUT GHOSTS
        self.worried = False # TODO: check if can be removed using value iteration

        # ABOUT MOVES
        self.movesMap = {}  # { cell: moves[] }
        self.policyMap = {} # { cell: score }


    def getAccessibleMap(self):
        return self.accessibleMap
    

    def getMovesMap(self):
        return self.movesMap


    def getAction(self, state):
        if self.firstIteration:
            self.firstIteration = False
            self.walls = set(api.walls(state))
            self.accessibleMap.update(getNonWallCells(self.walls, state))
            self.unvisitedCells.update(self.unvisitedCells)
            self.movesMap = map(getMapMoves, self.accessibleMap)
            print "$$$ ", self.accessibleMap
            raw_input()
            self.policyMap = { location : 0 for location in self.unvisitedCells }


        print "PERIMETER", getPerimeterOfUnvisitedAndFoodCells(self.accessibleMap, self.visitedCells, self.movesMap)

        # # Where are the capsules?
        # print "Capsule locations:"
        # print api.capsules(state)

        # AVAILABLE MOVES
        legal = api.legalActions(state)

        # PACMAN Location
        pacman = api.whereAmI(state)
        

        # UPDATE LISTS BASED ON NEW PACMAN POSITION
        if pacman in self.unvisitedCells: 
            self.unvisitedCells.remove(pacman)
            self.visitedCells.add(pacman)

        if pacman in self.uneatenFood: #
            self.uneatenFood.remove(pacman)
            self.visitedCells.add(pacman)

        # if pacman == self.lastBestFoodPosition: self.lastBestFoodPosition = None
        
        # FOOD Location
        food = api.food(state)
        self.uneatenFood.update(food)
        self.accessibleMap.update(food)

        # NO MORE FOOD nearby, looking for 
        #   non eaten registered food first 
        #   and non visited locations second 
        if len(food) == 0:
            message = "NO FOOD FOUND NEARBY, "
            if len(self.uneatenFood) > 0:
                print message, "reaching previously seen food"
                food = [food for food in self.uneatenFood]
            else:
                print message, "reaching unvisited locations"
                food = self.unvisitedCells


        # CLOSEST TARGET
        foodDistances = [(util.manhattanDistance(pacman, point), index) for index, point in enumerate(food)]
        sortedFoodDistances = sorted(foodDistances)
        FOOD_INDEX = 1

        firstFood = sortedFoodDistances[0]
        closestFood = food[firstFood[FOOD_INDEX]]
        xyDistanceToClosestFood = manhattanNotAbsoluteDistance(closestFood, pacman)

        # if new closest food is not closer than the previous one
        # swipe it with the saved closest food
        # TODO UNCOMMENT for newer versions
        # if (self.lastMinimumDistance and
        #    sum(xyDistanceToClosestFood) > 1 and
        #    pacman != self.lastBestFoodPosition):

        #     if sum(xyDistanceToClosestFood) > sum(self.lastMinimumDistance):
        #         print "Last Min Distance: ", self.lastMinimumDistance
        #         print "Last Best Food: ", self.lastBestFoodPosition
        #         print "ActualDistToClosestFood: ", xyDistanceToClosestFood

        #         closestFood = self.lastBestFoodPosition
        #         print "CLOSEST_FOOD: ", closestFood
        #         xyDistanceToClosestFood = manhattanNotAbsoluteDistance(closestFood, pacman)
            
        #     elif sum(xyDistanceToClosestFood) == sum(self.lastMinimumDistance):
        #         pass

        # UPDATE PACMAN TARGET Data
        self.lastMinimumDistance = xyDistanceToClosestFood
        self.lastBestFoodPosition = closestFood

        ## CHECK FOR GHOSTS
        ghosts = api.ghosts(state)
        if ghosts:
            try:
                print " =====> GHOSTS HEARD AT :"
                edibleGhosts = False
                for i in range(len(ghosts)):
                    ghost = ghosts[i]
                    if ghost[0] % 1 == 0.5 or ghost[0] % 1 == 0.5: 
                        print "EDIBLE GHOST: ", ghost
                        edibleGhosts = True
                    else:
                        print "GHOST> ", ghost
                
                if edibleGhosts:
                    raise Exception("Ghosts are edible")

                self.worried = True
                nextMove = getBestNextMoveGivenGhosts(pacman, ghosts, legal)
                print "NEXT MOVE: ", nextMove
                raw_input()
                print "\n====================================\n"
                return api.makeMove(nextMove, legal)
        
            except:
                self.worried = False 

        # CALCULATE BEST MOVES
        bestMoves = getBestNextMoves(legal, xyDistanceToClosestFood, immediateBestMoveFlag=True, maxDistanceForImmediateBestMove=3)

        print "PAC: ", pacman, "CLOSEST TARGET: ", closestFood, "  DISTANCE FROM IT: ", xyDistanceToClosestFood
        print "LAST POSITION: ", self.lastPosition
        print "LEGAL: ", legal
        print "BEST MOVES:", bestMoves

        # AVOID LOOP
        # avoid ghost traplastPosition TODO
        # if self.lastPosition in bestMoves:
        #     return api.makeMove(self.lastPosition, legal)

        # NO BEST MOVE, REVERT TO ALL POSSIBLE
        if len(bestMoves) == 0:
            bestMoves = legal
        else:
            
            # IMMEDIATE BEST MOVE
            if bestMoves[-1] is True:
                bestMoves.pop(-1)
            else:
                # best move takes more than 3 steps, so
                # prevent coming back (AVOID LOOP)
                if self.lastPosition in bestMoves:
                    if len(bestMoves) > 1:
                        print "== OLD BEST MOVES IS ====> ", bestMoves
                        bestMoves.remove(self.lastPosition)
                        print "== REMOVED LAST POSITION: ", self.lastPosition
                        print "== NEW BEST MOVES: ", bestMoves
                    else:
                        if len(legal) > 1:
                            legal.remove(self.lastPosition)
                            bestMoves = legal


        pick = random.choice(bestMoves)
        self.lastPosition = self.oppositeDirections[pick]
        print "SELECTED MOVE: ", pick
        raw_input()
        print "\n====================================\n"
        return api.makeMove(pick, legal)




















 











# WORKING
def manhattanNotAbsoluteDistance( xy1, xy2 ):
    "Returns the Manhattan distance between points xy1 and xy2"
    return ( xy1[0] - xy2[0], xy1[1] - xy2[1] )


def sumTuples(tuple1, tuple2):
    return tuple([(i + j) for i, j in zip(tuple1, tuple2)])


def getBestNextMoves(legal, closestPointDistancesXY, immediateBestMoveFlag = False, maxDistanceForImmediateBestMove = 1):
    '''
    Given the legal moves and the closes point to pacman,
    Calculates and return the best moves Direction wise
    as an array. If best move is best move, return True
    at the end of the array
    '''
    EAST_DISTANCE = closestPointDistancesXY[0]
    NORTH_DISTANCE = closestPointDistancesXY[1]

    bestMoves = []
    # immediate move NORTH SOUTH
    if EAST_DISTANCE == 0 and abs(NORTH_DISTANCE) <= maxDistanceForImmediateBestMove: 
        if Directions.NORTH in legal and NORTH_DISTANCE > 0:
            bestMoves.append(Directions.NORTH)
        elif Directions.SOUTH in legal and NORTH_DISTANCE < 0:
            bestMoves.append(Directions.SOUTH)

    # immediate move WEST EAST
    if NORTH_DISTANCE == 0 and abs(EAST_DISTANCE) <= maxDistanceForImmediateBestMove: 
        if Directions.EAST in legal and EAST_DISTANCE > 0:
            bestMoves.append(Directions.EAST)
        elif Directions.WEST in legal and EAST_DISTANCE < 0:
            bestMoves.append(Directions.WEST)
    
    # immediate move exists
    if len(bestMoves) > 0:
        if immediateBestMoveFlag: bestMoves.append(True)
        return bestMoves


    bestMoves = []
    # x-axis move
    if EAST_DISTANCE >= 0 and Directions.EAST in legal:
        bestMoves.append(Directions.EAST)

    elif EAST_DISTANCE <= 0 and Directions.WEST in legal:
        bestMoves.append(Directions.WEST)

    # y-axis move
    if NORTH_DISTANCE >= 0 and Directions.NORTH in legal:
        bestMoves.append(Directions.NORTH)

    elif NORTH_DISTANCE <= 0 and Directions.SOUTH in legal:
        bestMoves.append(Directions.SOUTH)


    # print "EAST_D: ", EAST_DISTANCE, "  NORTH_D: ", NORTH_DISTANCE

    return bestMoves


def getBestNextMoveGivenGhosts(pacman, ghosts, legal):
    distances = [manhattanNotAbsoluteDistance(pacman, ghost) for ghost in ghosts]
    print "distances ", distances
    print "legal ", legal


    # ghosts can only be 2 steps away at most so...
    oneStepDistance = [distance for distance in distances if (abs(distance[0]) == 1 or abs(distance[1]) == 1)]
    twoOrMoreStepsDistance = [distance for distance in distances if (abs(distance[0]) >= 2 or abs(distance[1]) >= 2)]

    print "oneStepDistance ", oneStepDistance
    print "twoOrMoreStepsDistance ", twoOrMoreStepsDistance

    priorityGhost = (oneStepDistance if oneStepDistance else twoOrMoreStepsDistance)[0]

    EAST_DISTANCE = priorityGhost[0]
    NORTH_DISTANCE = priorityGhost[1]

    bestMoves = []

    if EAST_DISTANCE > 0 and Directions.EAST in legal:
        bestMoves.append(Directions.EAST)

    elif EAST_DISTANCE < 0 and Directions.WEST in legal:
        bestMoves.append(Directions.WEST)

    # y-axis move
    if NORTH_DISTANCE > 0 and Directions.NORTH in legal:
        bestMoves.append(Directions.NORTH)

    elif NORTH_DISTANCE < 0 and Directions.SOUTH in legal:
        bestMoves.append(Directions.SOUTH)

    # ghost on the same line and cannot go to oppsite direction
    if not bestMoves:
        print("___unsatisfied__")
        if abs(EAST_DISTANCE) > 0:
            if Directions.NORTH in legal:
                bestMoves.append(Directions.NORTH)
            elif Directions.SOUTH in legal:
                bestMoves.append(Directions.SOUTH)
        else:
            if Directions.EAST in legal:
                bestMoves.append(Directions.EAST)
            elif Directions.WEST in legal:
                bestMoves.append(Directions.WEST)

    # pacman is trapped
    print "BEST MOVES ", bestMoves
    return Directions.STOP if not bestMoves else random.choice(bestMoves)

# WORKING
def getFullWallAndPerimeterFromWallBlock(block, walls):
    ''' 
    Given a block and the walls map,
    return perimeter and full wall of the block
    '''
    # print block
    surroundings = []
    for i in [-1, 0, 1]:
        for j in [-1, 0, 1]:
            surroundings.append((i, j))
    surroundings.remove((0, 0))
    
    perimeter = set()
    knownWall = set()
    newWall = set([block])

    while len(newWall) > 0:
        print newWall
        currentBlock = newWall.pop()
        if currentBlock in knownWall:
            continue
        else:
            knownWall.add(currentBlock)

        currentSurroundings = surroundings + currentBlock
        for currentSurrounding in currentSurroundings:
            if (currentSurrounding[0], currentSurrounding[1]) in walls:
                newWall.add((currentSurrounding[0], currentSurrounding[1]))
            else:
                perimeter.add((currentSurrounding[0], currentSurrounding[1]))
    return knownWall, perimeter
                

def getPerimeterAroundWall(pacmanPosition, foodPosition, wall):
    perimeter = getWallPerimeter(wall)
    path1, path2 = getPathsAroundTheWall(pacmanPosition, foodPosition, perimeter)


def getWallPerimeter(wall):
    surroundings = []
    for i in [-1, 0, 1]:
        for j in [-1, 0, 1]:
            surroundings.append((i, j))
    surroundings.remove((0, 0))

    perimeter = []
    for block in wall:
        for surrounding in surroundings:
            position = sumTuples(surrounding, block)
            if position not in wall and position not in perimeter:
                perimeter.append(position)
    return perimeter
    

def getPathsAroundTheWall(startPosition, goalPosition, perimeter):
    path1 = [startPosition, goalPosition]
    path2 = [startPosition, goalPosition]
    perimeter.remove(startPosition)
    perimeter.remove(goalPosition)
    directionPointer = 0
    while True:
        newPosition = sumTuples(startPosition, BetterHungryAgent.moves[directionPointer])
        if newPosition in perimeter:
            path1.append(newPosition)
            perimeter.remove(newPosition)
        else:
            directionPointer %= directionPointer + 1

        if newPosition == goalPosition:
            return path1, path2 + perimeter


def getVisitbaleWidthAndHeight(state):
    topRightCorner = max(api.walls(state))

    # the corners belong to the walls, so in a map 4 x 4
    # the top right corner is (3, 3), but it's a wall, so the map is
    # 2 x 2 from the agent perspective, so the width is 3 - 1
    return (topRightCorner[0] - 1, topRightCorner[1] - 1)


def getMapCellsMatrix(mapWidth, mapHeight):
    widthArray = range(1, mapWidth+1)
    heightArray = range(1, mapHeight+1)
    return [element for element in itertools.product(heightArray, widthArray)]


def getNonWallCells(walls, state):
    width, height = getVisitbaleWidthAndHeight(state)
    mapCellsMatrix = getMapCellsMatrix(height, width)
    return [x for x in mapCellsMatrix if x not in walls]

## TODO MAKE THIS WORKING
def policyMetric(accessibleMap, unvisitedMap = [], foodMap = [], ghosts = [], policyMap = [], epsilon = 0.1):
    policyMap = policyMap or 0


def getLegalMoves(accessibleMap, location):
    '''
    Given a cell and the accessibleMap, 
    Return the moves that can be made from there
    e.g. [(0,1), (0, -1)]
    Pacman can only move EAST or WEST
    '''
    print "++++++++++", accessibleMap,"\n", location,"\n" , BetterHungryAgent.moves
    raw_input()
    return [move for move in BetterHungryAgent.moves if sumTuples(location, move) in accessibleMap]


def getMapMoves(accessibleMap):
    '''
    Return a dictionary in the form {cell: moves[]}
    e.g. { (6, 5): [(0, 1), (0, -1)]} 
    the only moves are going either EAST or WEST
    '''
    return {location: getLegalMoves(accessibleMap, location) for location in accessibleMap}



def getValueIterationMap(accessibleMap,      visitedLocations,      mapMoves,      pacman, 
                            knownFood,       unvisitedLocations,    ghosts = [], 
                            foodReward = 2,  unvisitedReward = .3,  ghostPenalty= -10, 
                            epsilon = 0.01,  penalty = 0.04,        discountFactor = 0.9
                        ):
    '''
        The input parameters are, (beside the obvious ones)
        epsilon -> this is the value below which we stop iterating (to improve performance)
        penalty -> the cost to make a move
        discountFactor -> the lambda factor that reduces the value of further away elements
        foodReward -> the reward for getting food
        unvisitedReward -> the reward for getting on unvisited locations
        ghostPenalty -> the reward (negative) for bumping into a ghost
    '''
    pass

def getPerimeterOfUnvisitedAndFoodCells(accessibleMap, visitedCells, movesMap):
    perimeter = set()
    notVisitedCells = accessibleMap.difference(visitedCells)
    notVisitedCellsSurroundingCells = map(lambda cell: {cell: getSurroundingCells(cell, movesMap[cell], accessibleMap)}, notVisitedCells)

    reachablePerimeter = filter(lambda cellEntry: isFirstReachable(notVisitedCells[cellEntry], notVisitedCells))
    return set(reachablePerimeter.keys())


def isFirstReachable(surroundingCells, notVisitedCells):
    '''
    Return True if any of the surrounding cells has been visited.
    In other words, return True if the cell can be visited without passing
    on unvisited cells.
    '''
    return any(cell not in notVisitedCells for cell in surroundingCells) 


def getSurroundingCells(cell, cellMoves, accessibleMap):
    '''
    Given the accessible map, a cell position and the moves that can be taken
    from that cell, return the position of the surrounding cells
    '''
    newCells = [sumTuples(move, cell) for move in cellMoves]
    return filter(lambda c: c in accessibleMap, newCells)
