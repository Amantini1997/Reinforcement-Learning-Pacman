# mlLearningAgents.py
# parsons/27-mar-2017
#
# A stub for a reinforcement learning agent to work with the Pacman
# piece of the Berkeley AI project:
#
# http://ai.berkeley.edu/reinforcement.html
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

# The agent here was written by Simon Parsons, based on the code in
# pacmanAgents.py
# learningAgents.py

from pacman import Directions
from game import Agent
import random
from collections import defaultdict

# QLearnAgent
#
class QLearnAgent(Agent):

    # Constructor, called when we start running the game
    def __init__(self, alpha=0.2, epsilon=0.1, gamma=0.8, numTraining=10):
        # alpha       - learning rate
        # epsilon     - exploration rate
        # gamma       - discount factor
        # numTraining - number of training episodes
        #
        # These values are either passed from the command line or are
        # set to the default values above. We need to create and set
        # variables for them
        self.alpha = float(alpha)
        self.epsilon = float(epsilon)
        self.gamma = float(gamma)
        self.numTraining = int(numTraining)
        # Count the number of games we have played
        self.episodesSoFar = 0

        # These variables are used for the Q Learning of the agent
        # 
        # The values of state-action pairs stored as a dict.
        # If an action has never been performed from a given state,
        # then its value is 0
        self.QTable = defaultdict(int)

        # Keep track of the score of Pacman from the previous state
        # as well as the last state-action pair, i.e. the previous state 
        # and the action that was performed from such a state.
        # These values are both None upon the beginning of a game.
        self.previousScore = None
        self.previousStateActionPair = None
    

    ########################
    #                      #
    #  Accessor functions  #
    #                      #
    ########################
    
    def incrementEpisodesSoFar(self):
        self.episodesSoFar +=1

    def getEpisodesSoFar(self):
        return self.episodesSoFar

    def getNumTraining(self):
        return self.numTraining

    def setEpsilon(self, value):
        self.epsilon = value

    def getAlpha(self):
        return self.alpha

    def setAlpha(self, value):
        self.alpha = value
        
    def getGamma(self):
        return self.gamma

    def getMaxAttempts(self):
        return self.maxAttempts        
    

    ########################
    #                      #
    #  Default functions   #
    #                      #
    ########################

    # This is called by the game after a win or a loss.
    def final(self, state):     
        
        self.updateQTable(state, gameIsOver=True)

        # Game is over and Q-table was updated already,
        # so reset the values about to the previous state
        # as the next move will be the first one of a new game.
        self.previousStateActionPair = None
        self.previousScore = None
        
        # Game (episode) is over, so increase the count
        # episodes performed so far 
        self.incrementEpisodesSoFar()
        if self.getEpisodesSoFar() == self.getNumTraining():
            # The agent has finished its training. From now on
            # it should always pick the best action
            self.stopExploration()
    
    
    # The main method required by the game. Called every time that
    # Pacman is expected to move
    def getAction(self, state):
        
        # If this is not the agent's first move
        # then update the Q-table
        if self.previousStateActionPair != None:
            self.updateQTable(state)


        action = self.nextAction(state)

        self.previousStateActionPair = (state, action)
        self.previousScore = state.getScore()
        # We have to return an action
        return action


    ####################################
    #                                  #
    #      Agent-related functions     #
    #                                  #
    ####################################

    # Select and return a random action from the ones the agent 
    # can legally perform 
    # 
    # Parameters
    # ----------
    # state: 
    #   the current state of the game
    # 
    # Return
    # ------
    # A randomly selected function
    def randomAction(self, state):
        return random.choice(self.getLegalActions(state))


    # Given the current state of the game, consult the 
    # Q-table to decide what action would produce the 
    # highest reward. Return that action.
    # 
    # Parameters
    # ----------
    # state: game.GameStateData
    #   the current state of the game
    # 
    # Return
    # ------
    # The best action that the agent can perform
    # in the current state
    def bestAction(self, state):
        bestReward = None
        bestAction = None

        for action in self.getLegalActions(state):
            actionReward = self.QTable[(state, action)]
            if bestReward == None or bestReward < actionReward:
                bestAction = action  
                bestReward = actionReward          
        return bestAction
            

    
    # Using the epsilon-greedy approach, decide
    # whether the agent's next action should aim 
    # at exploring or exploiting. Then, return
    # such an action
    #
    # Parameters
    # ----------
    # state: game.GameStateData 
    #   the current state of the game
    # 
    # Return
    # ------
    # the next action the agent should perform
    def nextAction(self, state):
        agentShouldExplore = random.random() < self.epsilon

        if agentShouldExplore:
            return self.randomAction(state)
        else:
            return self.bestAction(state) 

    
    # Given the current state, update the value in the Q-table 
    # according to formula:
    #  
    # Q[s,a] <- Q[s,a] + alpha * (reward + gamma * argmax_over_a'( Q[s',a'] ) - Q[s,a])
    # 
    # What this formula means is that the Q-value for the 
    # previous state-action pair should update based on the 
    # best action that the agent can take from the current 
    # state. In this formula, alpha is the (fixed) learning 
    # rate and gamma is the (fixed) discount factor as set 
    # in the constructor. 
    #
    # If the game is over, as Pacman cannot perform any more 
    # actions, set the max Q-value to 0 when updating the Q-value.
    #
    # Parameters
    # ----------
    #   state: game.GameStateData
    #       the current state of the game
    #
    #   gameIsOver: Boolean
    #       flag that indicates whether the game is over. 
    #       If True, agent is in a terminal state and will 
    #       not be able to perform any further moves from this 
    #       state.
    # 
    # Reference
    # ---------
    #  
    # The update formula is taken from slide 46 from week 9 - "Reinforcement Learning 2".
    # [https://keats.kcl.ac.uk/pluginfile.php/6784507/mod_resource/content/11/rl2.pdf]
    def updateQTable(self, state, gameIsOver=False):

        currentQValue = self.QTable[self.previousStateActionPair]
        reward = state.getScore() - self.previousScore

        # if the game is over the agent cannot select any actions
        # from here, so the bestAction is just set to be None
        bestAction = None if gameIsOver else self.bestAction(state)

        maxQValue = self.QTable[(state, bestAction)]
        
        self.QTable[self.previousStateActionPair] = currentQValue + (self.alpha * (reward + self.gamma * maxQValue - currentQValue))


    
    # Return all the action that the agent can
    # perform from the current state excluding 
    # the non-move action (i.e. the agent does
    # not move)
    #
    # Parameters
    # ----------
    # state: game.GameStateData 
    #   the current state of the game
    # 
    # Return
    # ------
    # A list of all the legal actions for the agent
    def getLegalActions(self, state):
        legal = state.getLegalPacmanActions()
        if Directions.STOP in legal:
            legal.remove(Directions.STOP)
        return legal


    # Set to 0 both the values of alpha and 
    # epsilon so that the agent stops training 
    # and only picks the best actions
    def stopExploration(self):
        self.setAlpha(0)
        self.setEpsilon(0)