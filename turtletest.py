#!/usr/bin/env python
from turtle import Turtle, mainloop
from random import expovariate as randexp

class Player(Turtle):
    def __init__(self, lmbda, mu, queue):
        Turtle.__init__(self)
        self.interarrivaltime = randexp(lmbda)
        self.servicetime = randexp(mu)
        self.queue = queue
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

class Queue():
    def __init__(self, qposition):
        self.players = []
        self.position = list(qposition)
    def __iter__(self):
        return iter(self.players)
    def join(self, player):
        self.players.append(player)
        print self.position
        self.position[0] -= 10
    def leave(self, player):
        for p in self:
            x = p.position()[0]
            y = p.position()[1]
            p.move(x + 10, y)

class Sim():
    def __init__(self, N, lmbda, mu, qposition=(200,-200)):
        self.queue = Queue(qposition)
        self.players = [Player(lmbda, mu, self.queue) for k in range(N)]
    def run(self):
        t = 0
        nextplayer = self.players.pop()
        nextplayer.arrive(t)
        nextplayer.joinqueue()
        while self.players:
            t += 1
            if t > self.players[-1].interarrivaltime + nextplayer.arrivaldate:
                nextplayer = self.players.pop()
                nextplayer.arrive(t)
                nextplayer.joinqueue()

if __name__ == '__main__':
    q = Sim(50, .01, 5)
    q.run()
