#!/usr/bin/env python
import turtle

arrive = [turtle.Turtle() for k in range(50)]

queue = []
service = []
complete = []
qposition = (200, 0)

while arrive:
    queue.append(arrive.pop())
    queue[-1].penup()
    if len(queue) == 1:
        queue[-1].setx(qposition[0])
    else:
        queue[-1].setx(queue[-2].position()[0] -10)
    queue[-1].color('red')

    if len(service) == 0:
        service.append(queue.pop())
        service[-1].setx(qposition[0] + 5)
        service[-1].color('blue')

    if len(service) == 1:
        complete.append(service.pop())
        complete[-1].setx(qposition[0] + 50)
        complete[-1].color('grey')



turtle.mainloop()
