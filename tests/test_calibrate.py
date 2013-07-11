#!/usr/bin/env python

import graphtec
import math

#
# draw a mark with a given orientation.  The mark consists of 17 segments
# spaced at 1/17 inch, to form a vernier against a 1/16-inch rule.
# An additional segment is included at the beginning, a little offset,
# to make sure the knife angle is correct for each of the main segments.
#

def mark(g,p,theta):
  px,py = p
  theta = theta*(math.pi/180)
  vx,vy = math.cos(theta),math.sin(theta)
  r = theta + math.pi/2
  rx,ry = math.cos(r),math.sin(r)
  for i in range(-2,18):
    if i==-1:
      continue
    cx,cy = px+vx*(i-3*17)/17.0, py+vy*(i-3*17)/17.0
    g.line(cx-0.08*rx,cy-0.08*ry,cx+0.08*rx,cy+0.08*ry)
  for i in range(-2,18):
    if i==-1:
      continue
    cx,cy = px+vx*(i+2*17)/17.0, py+vy*(i+2*17)/17.0
    g.line(cx-0.08*rx,cy-0.08*ry,cx+0.08*rx,cy+0.08*ry)

#
# main program
#

g = graphtec.graphtec()

g.start()

g.set(offset=(4,0.5))
g.set(speed=2)
g.set(force=5)
# this is for my Silhouette Cameo, to rerun this test to
# verify the calibration as measured from a prior run
# with matrix=(1,0,0,1)
g.set(matrix=(1,-0.001,-0.001,0.9952))

mark(g,(3.5,3.5),0)
mark(g,(3.5,3.5),45)
mark(g,(3.5,3.5),90)
mark(g,(3.5,3.5),135)

g.end()
