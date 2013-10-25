#!/usr/bin/env python
from turtle import Turtle, mainloop
from random import expovariate as randexp

class Player(Turtle):
    def __init__(self, lmbda, mu, queue, server):
        Turtle.__init__(self)
        self.interarrivaltime = randexp(lmbda)
        self.servicetime = randexp(mu)
        self.queue = queue
        self.server = server
        self.shape('circle')
    def move(self, x, y):
        self.setx(x)
        self.sety(y)
    def arrive(self, t):
        self.penup()
        self.arrivaldate = t
        self.move(self.queue.position[0], self.queue.position[1])
        self.color('red')
    def joinqueue(self):
        self.move(self.queue.position[0] + 5, self.queue.position[1])
        self.color('blue')
        self.queue.join(self)
    def startservice(self, t):
        self.move(self.server.position[0], self.server.position[1])
        self.servicedate = t + self.servicetime
        self.server.start(self)
        self.color('green')
    def endservice(self):
        self.move(self.server.position[0] + 50, self.server.position[1] - 50)
        self.color('black')
        self.server.players = self.server.players[1:]

class Queue():
    def __init__(self, qposition):
        self.players = []
        self.position = qposition
    def __iter__(self):
        return iter(self.players)
    def __len__(self):
        return len(self.players)
    def pop(self, index):
        return self.players.pop(index)
    def join(self, player):
        self.players.append(player)
        print self.position
        self.position[0] -= 10
    def leave(self, player):
        for p in self:
            x = p.position()[0]
            y = p.position()[1]
            p.move(x + 10, y)

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
    def __init__(self, N, lmbda, mu, qposition=[200,-200]):
        self.queue = Queue(qposition)
        self.server = Server([qposition[0] + 20, qposition[1]])
        self.players = [Player(lmbda, mu, self.queue, self.server) for k in range(N)]
    def run(self):
        t = 0
        nextplayer = self.players.pop()
        nextplayer.arrive(t)
        nextplayer.joinqueue()
        while self.players:
            t += 1
            if self.server.free():
                if len(self.queue) == 0:
                    nextplayer.startservice(t)
                else:
                    nextservice = self.queue.pop(0)
                    nextservice.startservice(t)
            elif t > self.server.nextservicedate:
                self.server.players[0].endservice()
            if t > self.players[-1].interarrivaltime + nextplayer.arrivaldate:
                nextplayer = self.players.pop()
                nextplayer.arrive(t)
                nextplayer.joinqueue()

if __name__ == '__main__':
    q = Sim(50, .01, .02)
    q.run()
