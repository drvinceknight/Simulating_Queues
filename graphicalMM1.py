#!/usr/bin/env python
"""
Library with some objects that make use of the python Turtle library to show graphics of a discrete event simulation of an MM1 queue (random arrivals and services, a single server).

There are various objects that allow for the simulation and demonstration of emergent behaviour:

- Player (I use the term player instead of customer as I also allow for the selfish and optimal behaviour: graphical representation: blue coloured dot);
- SelfishPlayer (inherited from Player: when passed a value of service, a SelfishPlayer will join the queue if and only if it is in their selfish interest: graphical representation: red coloured dot.);
- OptimalPlayer (uses a result from Naor to ensure that the mean cost is reduced: graphical representation: gold coloured dot.)

- Queue
- Server

- Sim (this is the main object that generates all other objects as required).
"""
from __future__ import division  # Simplify division
from turtle import Turtle, mainloop, setworldcoordinates  # Commands needed from Turtle
from random import expovariate as randexp, random  # Pseudo random number generation
import sys  # Use to write to out

def mean(lst):
    """
    Function to return the mean of a list.

    Argument: lst - a list of numeric variables

    Output: the mean of lst
    """
    return sum(lst) / len(lst)

def movingaverage(lst):
    """
    Custom built function to obtain moving average

    Argument: lst - a list of numeric variables

    Output: a list of moving averages
    """
    return [mean(lst[:k]) for k in range(1 , len(lst) + 1)]

def naorthreshold(lmbda, mu, costofbalking):
    """
    Function to return Naor's threshold for optimal behaviour in an M/M/1 queue. This is taken from Naor's 1969 paper: 'The regulation of queue size by Levying Tolls'

    Arguments:
        lmbda - arrival rate (float)
        mu - service rate (float)
        costofbalking - the value of service, converted to time units. (float)

    Output: A threshold at which optimal customers must no longer join the queue (integer)
    """
    n = 0  # Initialise n
    center = mu * costofbalking  # Center mid point of inequality from Naor's aper
    rho = lmbda / mu
    while True:
        LHS = (n*(1-rho)- rho * (1-rho**n))/((1-rho)**2)
        RHS = ((n+1)*(1- rho)-rho*(1-rho**(n+1)))/((1-rho)**2)
        if LHS <= center and center <RHS:
            return n
        n += 1  # Continually increase n until LHS and RHS are either side of center


class Player(Turtle):
    """
    A generic class for our 'customers'. I refer to them as players as I like to consider queues in a game theoretical framework. This class is inherited from the Turtle class so as to have the graphical interface.

    Attributes:
        lmbda: arrival rate (float)
        mu: service rate (float)
        queue: a queue object
        server: a server object


    Methods:
        move - move player to a given location
        arrive - a method to make our player arrive at the queue
        startservice - a method to move our player from the queue to the server
        endservice - a method to complete service
    """
    def __init__(self, lmbda, mu, queue, server, speed):
        """
        Arguments:
            lmbda: arrival rate (float)
            interarrivaltime: a randomly sampled interarrival time (negative exponential for now)
            mu: service rate (float)
            service: a randomly sampled service time (negative exponential for now)
            queue: a queue object
            shape: the shape of our turtle in the graphics (a circle)
            server: a server object
            served: a boolean that indicates whether or not this player has been served.
            speed: a speed (integer from 0 to 10) to modify the speed of the graphics
            balked: a boolean indicating whether or not this player has balked (not actually needed for the base Player class... maybe remove... but might be nice to keep here...)
        """
        Turtle.__init__(self)  # Initialise all base Turtle attributes
        self.interarrivaltime = randexp(lmbda)
        self.lmbda = lmbda
        self.mu = mu
        self.queue = queue
        self.served = False
        self.server = server
        self.servicetime = randexp(mu)
        self.shape('circle')
        self.speed(speed)
        self.balked = False
    def move(self, x, y):
        """
            A method that moves our player to a given point

            Arguments:
                x: the x position on the canvas to move the player to
                y: the y position on the canvas to move the player to.

            Output: NA
        """
        self.setx(x)
        self.sety(y)
    def arrive(self, t):
        """
        A method that make our player arrive (the player is first created to generate an interarrival time, service time etc...).

        Arguments: t the time of arrival (a float)

        Output: NA
        """
        self.penup()
        self.arrivaldate = t
        self.move(self.queue.position[0] + 5, self.queue.position[1])
        self.color('blue')
        self.queue.join(self)
    def startservice(self, t):
        """
        A method that makes our player start service (This moves the graphical representation of the player and also make the queue update it's graphics).

        Arguments: t the time of service start (a float)

        Output: NA
        """
        if not self.served and not self.balked:
            self.move(self.server.position[0], self.server.position[1])
            self.servicedate = t + self.servicetime
            self.server.start(self)
            self.color('green')
            self.endqueuedate = t
    def endservice(self):
        """
        A method that makes our player end service (This moves the graphical representation of the player and updates the server to be free).

        Arguments: NA

        Output: NA
        """
        self.color('grey')
        self.move(self.server.position[0] + 50 + random(), self.server.position[1] - 50 + random())
        self.server.players = self.server.players[1:]
        self.endservicedate = self.endqueuedate + self.servicetime
        self.waitingtime = self.endqueuedate - self.arrivaldate
        self.served = True

class SelfishPlayer(Player):
    """
    A class for a player who acts selfishly (estimating the amount of time that they will wait and comparing to a value of service). The only modification is the arrive method that now allows players to balk.
    """
    def __init__(self, lmbda, mu, queue, server, speed, costofbalking):
        Player.__init__(self, lmbda, mu, queue, server, speed)
        self.costofbalking = costofbalking
    def arrive(self, t):
        """
        As described above, this method allows players to balk if the expected time through service is larger than some alternative.

        Arguments: t - time of arrival (a float)

        Output: NA
        """
        self.penup()
        self.arrivaldate = t
        self.color('red')
        queuelength = len(self.queue)
        if (queuelength + 1) / (self.mu) < self.costofbalking:
            self.queue.join(self)
            self.move(self.queue.position[0] + 5, self.queue.position[1])
        else:
            self.balk()
            self.balked = True
    def balk(self):
        """
        Method to make player balk.

        Arguments: NA

        Outputs: NA
        """
        self.move(random(), self.queue.position[1] - 25 + random())

class OptimalPlayer(Player):
    """
    A class for a player who acts within a socially optimal framework (using the threshold from Naor's paper). The only modification is the arrive method that now allows players to balk and a new attribute for the Naor threshold.
    """
    def __init__(self, lmbda, mu, queue, server, speed, naorthreshold):
        Player.__init__(self, lmbda, mu, queue, server, speed)
        self.naorthreshold = naorthreshold
    def arrive(self, t):
        """
        A method to make player arrive. If more than Naor threshold are present in queue then the player will balk.

        Arguments: t - time of arrival (float)

        Outputs: NA
        """
        self.penup()
        self.arrivaldate = t
        self.color('gold')
        queuelength = len(self.queue)
        if (queuelength) < self.naorthreshold:
            self.queue.join(self)
            self.move(self.queue.position[0] + 5, self.queue.position[1])
        else:
            self.balk()
            self.balked = True
    def balk(self):
        """
        A method to make player balk.
        """
        self.move(10 + random(), self.queue.position[1] - 25 + random())

class Queue():
    """
    A class for a queue.

    Attributes:
        players - a list of players in the queue
        position - graphical position of queue

    Methods:
        pop - returns first in player from queue and updates queue graphics
        join - makes a player join the queue

    """
    def __init__(self, qposition):
        self.players = []
        self.position = qposition
    def __iter__(self):
        return iter(self.players)
    def __len__(self):
        return len(self.players)
    def pop(self, index):
        """
        A function to return a player from the queue and update graphics.

        Arguments: index - the location of the player in the queue

        Outputs: returns the relevant player
        """
        for p in self.players[:index] + self.players[index + 1:]:  # Shift everyone up one queue spot
            x = p.position()[0]
            y = p.position()[1]
            p.move(x + 10, y)
        self.position[0] += 10  # Reset queue position for next arrivals
        return self.players.pop(index)
    def join(self, player):
        """
        A method to make a player join the queue.

        Arguments: player object

        Outputs: NA
        """
        self.players.append(player)
        self.position[0] -= 10

class Server():
    def __init__(self, svrposition):
        self.players = []
        self.position = svrposition
    def __iter__(self):
        return iter(self.players)
    def __len__(self):
        return len(self.players)
    def start(self,player):
        self.players.append(player)
        self.players = sorted(self.players, key = lambda x : x.servicedate)
        self.nextservicedate =  self.players[0].servicedate
    def free(self):
        return len(self.players) == 0

class Sim():
    def __init__(self, T, lmbda, mu, speed=6, costofbalking=False):
        """
        costofbalking: an integer or a list. If it is a list, the first element is the probability of having a selfish player
        """
        bLx = -10
        bLy = -110
        tRx = 230
        tRy = 5
        setworldcoordinates(bLx,bLy,tRx,tRy)
        qposition = [(tRx+bLx)/2, (tRy+bLy)/2]
        self.costofbalking = costofbalking
        self.T = T
        self.completed = []
        self.lmbda = lmbda
        self.mu = mu
        self.players = []
        self.queue = Queue(qposition)
        self.queuelengthdict = {}
        self.server = Server([qposition[0] + 50, qposition[1]])
        self.speed = max(0,min(10,speed))
        if type(costofbalking) is list:
            self.naorthreshold = naorthreshold(lmbda, mu, costofbalking[1])
        else:
            self.naorthreshold = naorthreshold(lmbda, mu, costofbalking)
        self.systemstatedict = {}
    def newplayer(self):
        if len(self.players) == 0:
            if not self.costofbalking:
                self.players.append(Player(self.lmbda, self.mu, self.queue, self.server,self.speed))
            elif type(self.costofbalking) is list:
                if random() < self.costofbalking[0]:
                    self.players.append(SelfishPlayer(self.lmbda, self.mu, self.queue, self.server,self.speed, self.costofbalking[1]))
                else:
                    self.players.append(OptimalPlayer(self.lmbda, self.mu, self.queue, self.server,self.speed, self.naorthreshold))
            else:
                self.players.append(SelfishPlayer(self.lmbda, self.mu, self.queue, self.server,self.speed, self.costofbalking))
    def printprogress(self, t):
        sys.stdout.write('\r%.2f%% of simulation completed (t=%s of %s)' % (100 * t/self.T, t, self.T))
        sys.stdout.flush()
    def run(self):
        t = 0
        self.newplayer()  # Create a new player
        nextplayer = self.players.pop()  # Set this player to be the next player
        nextplayer.arrive(t)  # Make the next player arrive for service (potentially at the queue)
        nextplayer.startservice(t)  # This player starts service immediately
        self.newplayer()  # Create a new player that is now waiting to arrive
        while t < self.T:
            t += 1
            self.printprogress(t)  # Output progress to screen
            # Check if service finishes
            if not self.server.free() and t > self.server.nextservicedate:
                self.completed.append(self.server.players[0]) # Add completed player to completed list
                self.server.players[0].endservice()  # End service of a player in service
                if len(self.queue)>0:  # Check if there is a queue
                    nextservice = self.queue.pop(0)  # This returns player to go to service and updates queue.
                    nextservice.startservice(t)
                    self.newplayer()
            # Check if player that is waiting arrives
            if t > self.players[-1].interarrivaltime + nextplayer.arrivaldate:
                nextplayer = self.players.pop()
                nextplayer.arrive(t)
                if self.server.free():
                    if len(self.queue) == 0:
                        nextplayer.startservice(t)
                    else:  # Check if there is a queue
                        nextservice = self.queue.pop(0)  # This returns player to go to service and updates queue.
                        nextservice.startservice(t)
            self.newplayer()
            self.collectdata(t)
    def collectdata(self,t):
        self.queuelengthdict[t] = len(self.queue)
        if self.server.free():
            self.systemstatedict[t] = 0
        else:
            self.systemstatedict[t] = self.queuelengthdict[t] + 1
    def plot(self, warmup=0):
        queuelengths = []
        systemstates = []
        timepoints = []
        for t in self.queuelengthdict:
            if t >= warmup:
                queuelengths.append(self.queuelengthdict[t])
                systemstates.append(self.systemstatedict[t])
                timepoints.append(t)
        try:
            import matplotlib.pyplot as plt
        except:
            sys.stdout.write("matplotlib does not seem to be installed: no  plots can be produced.")
            return
        plt.figure(1)
        plt.subplot(221)
        plt.hist(queuelengths, normed=True, bins=min(20, max(queuelengths)))
        plt.title("Queue length")
        plt.subplot(222)
        plt.hist(systemstates, normed=True, bins=min(20, max(systemstates)))
        plt.title("System state")
        plt.subplot(223)
        plt.plot(timepoints, movingaverage(queuelengths))
        plt.title("Mean queue length")
        plt.subplot(224)
        plt.plot(timepoints, movingaverage(systemstates))
        plt.title("Mean system state")
        plt.show()

if __name__ == '__main__':
    #q = Sim(200, 2, 1, speed=10, costofbalking = [0,7])
    #q = Sim(200, 2, 1, speed=10, costofbalking = [1,7])
    #q = Sim(200, 2, 1, speed=10, costofbalking = [.8,7])
    #q = Sim(200, 2, 1, speed=10, costofbalking = [.2,7])
    q = Sim(200, 2, 1, speed=0, costofbalking = [.5,7])
    q.run()
    q.plot()
