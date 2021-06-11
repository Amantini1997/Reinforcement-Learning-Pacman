# Reinforcement Learning Pacman

## Description
This project is about a Pacman agent using a combination of Bellman's equation and value iteration to operate in a stochastic world.

The Pacman code used was developed at *UC Berkeley* for their AI course and made available to everyone. The homepage for the Berkeley AI Pacman projects is [here](http://ai.berkeley.edu/).

<br>
<br>

## Starting the Agent

#### Basic command
To run the program, navigate to the directory containing the project and run

    python pacman.py -p <agent> -l <world> [-q]

The existing worlds are specified in the folder called `layouts`. 

The flag `-q` is optional. If present, the GUI will not be rendered and the results will be printed in the terminal executing the program. 
As a result the program will run faster.

Different agents exist, but only two were implemented by myself, namely the Q-Learning Agent and the agent applying the value iteration.

The command will automatically open a GUI to see Pacman operating in the world. 

<br>



#### Running the Q-Learning Agent
To run the Q-Learning Agent execute

    python pacman.py -p QLearnAgent -x <training-episodes> -n<training-episodes + non-training-episodes> -l <world>

Notice that the agent will require a fair amount of time to train. As such, it is recommended to run it into small worlds such as *smallGrid*.

> E.g. 
> - training episodes: **500**,
> - non-training episodes: **10** (this will become 510 = 500 + 10),
> - world: **smallGrid**
>
>       python pacman.py -p QLearnAgent -x 500 -n 510 -l smallGrid -q


<br>

#### Bellman & Value Iteration Agent
To run the Value Iteration Agent run

    python pacman.py -n <number-games> -p MDPAgent -l <world> [-q]


<br>

## Limitations
The program uses **Python 2.7**, running this program using **Python 3.x** will result in an error.