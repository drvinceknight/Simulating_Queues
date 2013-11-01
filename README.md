# Overview

This repo currently contains two things:

- A basic event driven MM1 queue simulation (that would be nice if someone turned in to an MMC queue). This was used in a screencast (link below).
- A more complicated clock based simulation of an MM1 queue that also allows for the investigation of selfish and social behaviours (currently this is all linked to Naor's 1969 paper). Importantly, this also contains a graphical element: allowing for the visualisation of the queue using the Turtle library.

## Basic event driven MM1 queue

This is some short code that can be used to simulate an *MM1* queue (a queue with Markovian inter-arrival and service rates and 1 server). The code is used in a short video [Simulating a Queue](http://www.youtube.com/watch?v=WEA8m3j-Jqk) describing a basic approach to simulating a queue.

If people would like to mess around with this code please do!

If people are interested in discrete event simulation within python I know that a library called [SimPy](http://simpy.sourceforge.net/) (unfortunate name re SymPy) exists but I've never used it.

## Graphical simulation

### Usage

The file `graphicalMM1.py` is both a library and an executable. It can thus be run directly:

~~~{.bash}
$ python graphicalMM1.py
~~~

This will run the simulation with some default values.

The file can be passed arguments. So help can be obtained by running:

~~~{.bash}
$ python graphicalMM1.py -h
~~~

Finally the file can be passed various arguments at the command line:

~~~{.bash}
$ python graphicalMM1.py -l 5 -m 2 -T 500 -w 200 -s True
~~~

This would run the simulation with an arrival rate of 5, a service rate of 2, for a total runtime of 500 time units, with a warm up period of 200 (for summary statistics) and the option to save summary graphs is set to True (as opposed to them being displayed by the matplotlib viewer).

- Graphical output
- Plots
- Selfish behaviour
- Optimal behaviour
- Mixed behaviour

### Development

Currently on the to do list:

- Include csv write (of results)
- Write command line argparse

# License Information
This work is licensed under a [Creative Commons Attribution-ShareAlike 3.0](http://creativecommons.org/licenses/by-sa/3.0/us/) license.  You are free to:

* Share: copy, distribute, and transmit the work,
* Remix: adapt the work

Under the following conditions:

* Attribution: You must attribute the work in the manner specified by the author or licensor (but not in any way that suggests that they endorse you or your use of the work).
* Share Alike: If you alter, transform, or build upon this work, you may distribute the resulting work only under the same or similar license to this one.

When attributing this work, please include me.
