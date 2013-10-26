#!/usr/bin/env python
from __future__ import division
from turtle import Turtle, mainloop, setworldcoordinates
from random import expovariate as randexp, random
import sys

def mean(lst):
    return sum(lst) / len(lst)

def movingaverage(lst):
    """
    Custom built function to obtain moving average
    """
    return [mean(lst[:k]) for k in range(1 , len(lst) + 1)]

class Player(Turtle):
    def __init__(self, lmbda, mu, queue, server, speed):
        Turtle.__init__(self)
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
        self.setx(x)
        self.sety(y)
    def arrive(self, t):
        self.penup()
        self.arrivaldate = t
        self.move(self.queue.position[0] + 5, self.queue.position[1])
        self.color('blue')
        self.queue.join(self)
    def startservice(self, t):
        if not self.served and not self.balked:
            self.move(self.server.position[0], self.server.position[1])
            self.servicedate = t + self.servicetime
            self.server.start(self)
            self.color('green')
            self.endqueuedate = t
    def endservice(self):
        self.color('grey')
        self.move(self.server.position[0] + 50, self.server.position[1] - 50)
        self.server.players = self.server.players[1:]
        self.endservicedate = self.endqueuedate + self.servicetime
        self.waitingtime = self.endqueuedate - self.arrivaldate
        self.served = True

class SelfishPlayer(Player):
    def __init__(self, lmbda, mu, queue, server, speed, costofbalking):
        Player.__init__(self, lmbda, mu, queue, server, speed)
        self.costofbalking = costofbalking
    def arrive(self, t):
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
        self.move(0, self.queue.position[1] - 25)


class Queue():
    def __init__(self, qposition):
        self.players = []
        self.position = qposition
    def __iter__(self):
        return iter(self.players)
    def __len__(self):
        return len(self.players)
    def pop(self, index):
        for p in self.players[:index] + self.players[index + 1:]:  # Shift everyone up one queue spot
            x = p.position()[0]
            y = p.position()[1]
            p.move(x + 10, y)
        self.position[0] += 10  # Reset queue position for next arrivals
        return self.players.pop(index)
    def join(self, player):
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
        setworldcoordinates(-10,-110,275,10)
        qposition = [150, -50]
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
        self.systemstatedict = {}
    def newplayer(self):
        if len(self.players) == 0:
            if not self.costofbalking:
                self.players.append(Player(self.lmbda, self.mu, self.queue, self.server,self.speed))
            elif type(self.costofbalking) is list:
                if random() < self.costofbalking[0]:
                    self.players.append(SelfishPlayer(self.lmbda, self.mu, self.queue, self.server,self.speed, self.costofbalking[1]))
                else:
                    self.players.append(Player(self.lmbda, self.mu, self.queue, self.server,self.speed))
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
    #q = Sim(1000, .5, 1, speed=10)
    q = Sim(200, 3, 1, speed=10, costofbalking = [.5,3])
    #q = Sim(200, 2, 1, speed=10, costofbalking = 1)
    q.run()
    q.plot()
