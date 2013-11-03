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
    if len(lst) > 0:
        return sum(lst) / len(lst)
    return False

def movingaverage(lst):
    """
    Custom built function to obtain moving average

    Argument: lst - a list of numeric variables

    Output: a list of moving averages
    """
    return [mean(lst[:k]) for k in range(1 , len(lst) + 1)]

def plotwithnobalkers(queuelengths, systemstates, timepoints, savefig, string):
    """
    A function to plot histograms and timeseries.

    Arguments:
        - queuelengths (list of integers)
        - systemstates (list of integers)
        - timtepoints (list of integers)
    """
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
    if savefig:
        plt.savefig(string)
    else:
        plt.show()

def plotwithbalkers(selfishqueuelengths, optimalqueuelengths, selfishsystemstates, optimalsystemstates, timepoints, savefig, string):
    """
    A function to plot histograms and timeseries when you have two types of players

    Arguments:
        - selfishqueuelengths (list of integers)
        - optimalqueuelengths (list of integers)
        - selfishsystemstates (list of integers)
        - optimalsystemstates (list of integers)
        - timtepoints (list of integers)
        - savefig (boolean)
        - string (a string)
    """
    try:
        import matplotlib.pyplot as plt
    except:
        sys.stdout.write("matplotlib does not seem to be installed: no  plots can be produced.")
        return
    queuelengths = [sum(k) for k in zip(selfishqueuelengths, optimalqueuelengths)]
    systemstates = [sum(k) for k in zip(selfishsystemstates, optimalsystemstates)]
    fig = plt.figure(1)
    plt.subplot(221)
    plt.hist([selfishqueuelengths, optimalqueuelengths, queuelengths], normed=True, bins=min(20, max(queuelengths)), label=['Selfish players','Optimal players','Total players'], color=['red', 'green', 'blue'])
    #plt.legend()
    plt.title("Number in queue")
    plt.subplot(222)
    plt.hist([selfishsystemstates, optimalsystemstates, systemstates], normed=True, bins=min(20, max(systemstates)), label=['Selfish players','Optimal players','Total players'], color=['red', 'green', 'blue'])
    #plt.legend()
    plt.title("Number in system")
    plt.subplot(223)
    plt.plot(timepoints, movingaverage(selfishqueuelengths), label='Selfish players', color='red')
    plt.plot(timepoints, movingaverage(optimalqueuelengths), label='Optimal players', color='green')
    plt.plot(timepoints, movingaverage(queuelengths), label='Total', color='blue')
    #plt.legend()
    plt.title("Mean number in queue")
    plt.subplot(224)
    line1, =  plt.plot(timepoints, movingaverage(selfishsystemstates), label='Selfish players', color='red')
    line2, = plt.plot(timepoints, movingaverage(optimalsystemstates), label='Optimal players', color='green')
    line3, = plt.plot(timepoints, movingaverage(systemstates), label='Total', color='blue')
    #plt.legend()
    plt.title("Mean number in system")
    fig.legend([line1,line2,line3],['Selfish players', 'Optimal players', 'Total'],loc='lower center',fancybox=True,ncol=3, bbox_to_anchor=(.5,0))
    plt.subplots_adjust(bottom=.15)
    if savefig:
        plt.savefig(string)
    else:
        plt.show()

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
            self.color('gold')
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
        systemstate = len(self.queue) + len(self.server)
        if (systemstate + 1) / (self.mu) < self.costofbalking:
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
        self.color('green')
        systemstate = len(self.queue) + len(self.server)
        if systemstate < self.naorthreshold:
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
    """
    A class for the server (this could theoretically be modified to allow for more complex queues than M/M/1)

    Attributes:
        - players: list of players in service (at present will be just the one player)
        - position: graphical position of queue

    Methods:
        - start: starts the service of a given player
        - free: a method that returns free if the server is free
    """
    def __init__(self, svrposition):
        self.players = []
        self.position = svrposition
    def __iter__(self):
        return iter(self.players)
    def __len__(self):
        return len(self.players)
    def start(self,player):
        """
        A function that starts the service of a player (there is some functionality already in place in case multi server queue ever gets programmed). Moves all graphical stuff.

        Arguments: A player object

        Outputs: NA
        """
        self.players.append(player)
        self.players = sorted(self.players, key = lambda x : x.servicedate)
        self.nextservicedate =  self.players[0].servicedate
    def free(self):
        """
        Returns True if server is empty.
        """
        return len(self.players) == 0

class Sim():
    """
    The main class for a simulation.

    Attributes:
        - costofbalking (by default set to False for a basic simulation). Can be a float (indicating the cost of balking) in which case all players act selfishly. Can also be a list: l. In which case l[0] represents proportion of selfish players (other players being social players). l[1] then indicates cost of balking.
        - naorthresholed (by default set to False for a basic simulation). Can be an integer (not to be input but calculated using costofbalking).
        - T total run time (float)
        - lmbda: arrival rate (float)
        - mu: service rate (float)
        - players: list of players (list)
        - queue: a queue object
        - queuelengthdict: a dictionary that keeps track of queue length at given times (for data handling)
        - systemstatedict: a dictionary that keeps track of system state at given times (for data handling)
        - server: a server object
        - speed: the speed of the graphical animation

    Methods:
        - run: runs the simulation model
        - newplayer: generates a new player (that does not arrive until the clock advances past their arrivaldate)
        - printprogress: print the progress of the simulation to stdout
        - collectdata: collects data at time t
        - plot: plots summary graphs
    """

    def __init__(self, T, lmbda, mu, speed=6, costofbalking=False):
        ##################
        bLx = -10 # This sets the size of the canvas (I think that messing with this could increase speed of turtles)
        bLy = -110
        tRx = 230
        tRy = 5
        setworldcoordinates(bLx,bLy,tRx,tRy)
        qposition = [(tRx+bLx)/2, (tRy+bLy)/2]  # The position of the queue
        ##################
        self.costofbalking = costofbalking
        self.T = T
        self.completed = []
        self.balked = []
        self.lmbda = lmbda
        self.mu = mu
        self.players = []
        self.queue = Queue(qposition)
        self.queuelengthdict = {}
        self.server = Server([qposition[0] + 50, qposition[1]])
        self.speed = max(0,min(10,speed))
        self.naorthreshold = False
        if type(costofbalking) is list:
            self.naorthreshold = naorthreshold(lmbda, mu, costofbalking[1])
        else:
            self.naorthreshold = naorthreshold(lmbda, mu, costofbalking)
        self.systemstatedict = {}

    def newplayer(self):
        """
        A method to generate a new player (takes in to account cost of balking). So if no cost of balking is passed: only generates a basic player. If a float is passed as cost of balking: generates selfish players with that float as worth of service. If a list is passed then it creates a player (either selfish or optimal) according to a random selection.

        Arguments: NA

        Outputs: NA
        """
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
        """
        A method to print to screen the progress of the simulation.

        Arguments: t (float)

        Outputs: NA
        """
        sys.stdout.write('\r%.2f%% of simulation completed (t=%s of %s)' % (100 * t/self.T, t, self.T))
        sys.stdout.flush()

    def run(self):
        """
        The main method which runs the simulation. This will collect relevant data throughout the simulation so that if matplotlib is installed plots of results can be accessed. Furthermore all completed players can be accessed in self.completed.

        Arguments: NA

        Outputs: NA
        """
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
                if nextplayer.balked:
                    self.balked.append(nextplayer)
                if self.server.free():
                    if len(self.queue) == 0:
                        nextplayer.startservice(t)
                    else:  # Check if there is a queue
                        nextservice = self.queue.pop(0)  # This returns player to go to service and updates queue.
                        nextservice.startservice(t)
            self.newplayer()
            self.collectdata(t)

    def collectdata(self,t):
        """
        Collect data at each time step: updates data dictionaries.

        Arguments: t (float)

        Outputs: NA
        """
        if self.costofbalking:
            selfishqueuelength = len([k for k in self.queue if type(k) is SelfishPlayer])
            self.queuelengthdict[t] = [selfishqueuelength,len(self.queue) - selfishqueuelength]
            if self.server.free():
                self.systemstatedict[t] = [0,0]
            else:
                self.systemstatedict[t] = [self.queuelengthdict[t][0] + len([p for p in self.server.players if type(p) is SelfishPlayer]),self.queuelengthdict[t][1] + len([p for p in self.server.players if type(p) is OptimalPlayer])]
        else:
            self.queuelengthdict[t] = len(self.queue)
            if self.server.free():
                self.systemstatedict[t] = 0
            else:
                self.systemstatedict[t] = self.queuelengthdict[t] + 1

    def plot(self, savefig, warmup=0):
        """
        Plot the data
        """
        string = "lmbda=%s-mu=%s-T=%s-cost=%s.pdf" % (self.lmbda, self.mu, self.T, self.costofbalking) # An identifier
        if self.costofbalking:
            selfishqueuelengths = []
            optimalqueuelengths = []
            selfishsystemstates = []
            optimalsystemstates = []
            timepoints = []
            for t in self.queuelengthdict:
                if t >= warmup:
                    selfishqueuelengths.append(self.queuelengthdict[t][0])
                    optimalqueuelengths.append(self.queuelengthdict[t][1])
                    selfishsystemstates.append(self.systemstatedict[t][0])
                    optimalsystemstates.append(self.systemstatedict[t][1])
                    timepoints.append(t)
            plotwithbalkers(selfishqueuelengths, optimalqueuelengths, selfishsystemstates, optimalsystemstates, timepoints, savefig, string)
        else:
            queuelengths = []
            systemstates = []
            timepoints = []
            for t in self.queuelengthdict:
                if t >= warmup:
                    queuelengths.append(self.queuelengthdict[t])
                    systemstates.append(self.systemstatedict[t])
                    timepoints.append(t)
            plotwithnobalkers(queuelengths, systemstates, timepoints, savefig, string)

    def printsummary(self, warmup=0):
        """
        A method to print summary statistics.
        """
        if not self.costofbalking:
            self.queuelengths = []
            self.systemstates = []
            for t in self.queuelengthdict:
                if t >= warmup:
                    self.queuelengths.append(self.queuelengthdict[t])
                    self.systemstates.append(self.systemstatedict[t])
            self.meanqueuelength = mean(self.queuelengths)
            self.meansystemstate = mean(self.systemstates)
            self.waitingtimes = []
            self.servicetimes = []
            for p in self.completed:
                if p.arrivaldate >= warmup:
                    self.waitingtimes.append(p.waitingtime)
                    self.servicetimes.append(p.servicetime)
            self.meanwaitingtime = mean(self.waitingtimes)
            self.meansystemtime = mean(self.servicetimes) + self.meanwaitingtime
            sys.stdout.write("\n%sSummary statistics%s\n" % (10*"-",10*"-"))
            sys.stdout.write("Mean queue length: %.02f\n" % self.meanqueuelength)
            sys.stdout.write("Mean system state: %.02f\n" % self.meansystemstate)
            sys.stdout.write("Mean waiting time: %.02f\n" % self.meanwaitingtime)
            sys.stdout.write("Mean system time: %.02f\n" % self.meansystemtime)
            sys.stdout.write(39 * "-" + "\n")
        else:

            self.selfishqueuelengths = []
            self.optimalqueuelengths = []
            self.selfishsystemstates = []
            self.optimalsystemstates = []
            for t in self.queuelengthdict:
                if t >= warmup:
                    self.selfishqueuelengths.append(self.queuelengthdict[t][0])
                    self.optimalqueuelengths.append(self.queuelengthdict[t][1])
                    self.selfishsystemstates.append(self.systemstatedict[t][0])
                    self.optimalsystemstates.append(self.systemstatedict[t][1])
            self.meanselfishqueuelength = mean(self.selfishqueuelengths)
            self.meanoptimalqueuelength = mean(self.optimalqueuelengths)
            self.meanqueuelength = mean([sum(k) for k in zip(self.selfishqueuelengths, self.optimalqueuelengths)])
            self.meanselfishsystemstate = mean(self.selfishsystemstates)
            self.meanoptimalsystemstate = mean(self.optimalsystemstates)
            self.meansystemstate = mean([sum(k) for k in zip(self.selfishsystemstates, self.optimalsystemstates)])

            self.selfishwaitingtimes = []
            self.optimalwaitingtimes = []
            self.selfishservicetimes = []
            self.optimalservicetimes = []
            for p in self.completed:
                if p.arrivaldate >= warmup:
                    if type(p) is SelfishPlayer:
                        self.selfishwaitingtimes.append(p.waitingtime)
                        self.selfishservicetimes.append(p.servicetime)
                    else:
                        self.optimalwaitingtimes.append(p.waitingtime)
                        self.optimalservicetimes.append(p.servicetime)
            self.meanselfishwaitingtime = mean(self.selfishwaitingtimes)
            self.meanselfishsystemtime = mean(self.selfishservicetimes) + self.meanselfishwaitingtime
            self.meanoptimalwaitingtime = mean(self.optimalwaitingtimes)
            self.meanoptimalsystemtime = mean(self.optimalservicetimes) + self.meanoptimalwaitingtime

            self.selfishprobbalk = 0
            self.optimalprobbalk = 0
            for p in self.balked:
                if p.arrivaldate >= warmup:
                    if type(p) is SelfishPlayer:
                        self.selfishprobbalk += 1
                    else:
                        self.optimalprobbalk += 1

            self.meanselfishcost = self.selfishprobbalk * self.costofbalking[1] + sum(self.selfishservicetimes) + sum(self.selfishwaitingtimes)
            self.meanoptimalcost = self.optimalprobbalk * self.costofbalking[1] + sum(self.optimalservicetimes) + sum(self.optimalwaitingtimes)
            self.meancost = self.meanselfishcost + self.meanoptimalcost
            if len(self.selfishwaitingtimes) + self.selfishprobbalk != 0:
                self.meanselfishcost /= self.selfishprobbalk + len(self.selfishwaitingtimes)
            else:
                self.meanselfishcost = False
            if len(self.optimalwaitingtimes) + self.optimalprobbalk != 0:
                self.meanoptimalcost /= self.optimalprobbalk + len(self.optimalwaitingtimes)
            else:
                self.meanselfishcost = False

            if self.selfishprobbalk + self.optimalprobbalk + len(self.selfishwaitingtimes) + len(self.optimalwaitingtimes) != 0:
                self.meancost /= self.selfishprobbalk + self.optimalprobbalk + len(self.selfishwaitingtimes) + len(self.optimalwaitingtimes)
            else:
                self.meancost = False

            if self.selfishprobbalk + len(self.selfishwaitingtimes) != 0:
                self.selfishprobbalk /= self.selfishprobbalk + len(self.selfishwaitingtimes)
            else:
                self.selfishprobbalk = False
            if self.optimalprobbalk + len(self.optimalwaitingtimes) != 0:
                self.optimalprobbalk /= self.optimalprobbalk + len(self.optimalwaitingtimes)
            else:
                self.optimalprobbalk = False

            sys.stdout.write("\n%sSummary statistics%s\n" % (10*"=",10*"="))

            sys.stdout.write("\n%sSelfish players%s\n" % (13*"-",10*"-"))
            sys.stdout.write("Mean number in queue: %.02f\n" % self.meanselfishqueuelength)
            sys.stdout.write("Mean number in system: %.02f\n" % self.meanselfishsystemstate)
            sys.stdout.write("Mean waiting time: %.02f\n" % self.meanselfishwaitingtime)
            sys.stdout.write("Mean system time: %.02f\n" % self.meanselfishsystemtime)
            sys.stdout.write("Probability of balking: %.02f\n" % self.selfishprobbalk)

            sys.stdout.write("\n%sOptimal players%s\n" % (13*"-",10*"-"))
            sys.stdout.write("Mean number in queue: %.02f\n" % self.meanoptimalqueuelength)
            sys.stdout.write("Mean number in system: %.02f\n" % self.meanoptimalsystemstate)
            sys.stdout.write("Mean waiting time: %.02f\n" % self.meanoptimalwaitingtime)
            sys.stdout.write("Mean system time: %.02f\n" % self.meanoptimalsystemtime)
            sys.stdout.write("Probability of balking: %.02f\n" % self.optimalprobbalk)

            sys.stdout.write("\n%sOverall mean cost (in time)%s\n" % (9*"-","-"))
            sys.stdout.write("All players: %.02f\n" % self.meancost)
            sys.stdout.write("Selfish players: %.02f\n" % self.meanselfishcost)
            sys.stdout.write("Optimal players: %.02f\n" % self.meanoptimalcost)
            sys.stdout.write(39 * "=" + "\n")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="A simulation of an MM1 queue with a graphical representation made using the python Turtle module. Also, allows for some agent based aspects which at present illustrate results from Naor's paper: 'The Regulation of Queue Size by Levying Tolls'")
    parser.add_argument('-l', action="store", dest="lmbda", type=float, help='The arrival rate', default=2)
    parser.add_argument('-m', action="store", dest="mu", type=float, help='The service rate', default = 1)
    parser.add_argument('-T', action="store", dest="T", type=float, help='The overall simulation time', default=500)
    parser.add_argument('-p', action="store", dest="probofselfish", help='Proportion of selfish players (default: 0)', default=0, type=float)
    parser.add_argument('-c', action="store", dest="costofbalking", help='Cost of balking (default: False)', default=False, type=float)
    parser.add_argument('-w', action="store", dest="warmuptime", help='Warm up time', default=0, type=float)
    parser.add_argument('-s', action="store", dest="savefig", help='Boolean to save the figure or not', default=False, type=bool)
    inputs = parser.parse_args()
    lmbda = inputs.lmbda
    mu = inputs.mu
    T = inputs.T
    warmup = inputs.warmuptime
    savefig = inputs.savefig
    costofbalking = inputs.costofbalking
    if costofbalking:
        costofbalking = [inputs.probofselfish, inputs.costofbalking]
    q = Sim(T, lmbda, mu, speed=10, costofbalking=costofbalking)
    q.run()
    q.printsummary(warmup=warmup)
    q.plot(savefig)
