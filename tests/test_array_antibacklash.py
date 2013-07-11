#!/usr/bin/env python

import random
import graphtec

def pads1(g):
  for i in range(0,20):
    for j in range(0,20):
      g.path([(0,0),(0.05,0)])
      x = 0.05+0.016*i
      y = 0.05+0.016*j
      g.path([(x,y),(x+0.008,y)])

g = graphtec.graphtec()

g.start()

g.set(offset=(1.75,1.75))
g.set(speed=1)
g.set(force=1)

pads1(g)

g.end()
