# optimize paths for the graphtec cutter by dicing into individual lines, sorting by angle

import math

def emit_line(x1,y1,x2,y2):
  global r
  global loc
  loc = (x2,y2)
  r.append((x1+1.5,y1+1.5,x2+1.5,y2+1.5))

def angle(x1,y1,x2,y2):
  dx = x2 - x1
  dy = y2 - y1
  theta = math.atan2(dy,dx)
  theta = theta + math.pi
  ang = round(theta/(math.pi/8))
  if ang==16:
    ang = 0
  return ang

def emit_training_line(ang):
  global r
  global loc
  cx,cy = 0.5,0.5
  theta = ang*math.pi/8
  x = math.cos(theta)
  y = math.sin(theta)
  x1,y1 = 0.5*x, 0.5*y
  x2,y2 = 0.2*x, 0.2*y
  loc = (x2-1,y2-1)
  r.append((cx+x1,cy+y1,cx+x2,cy+y2))

def dice(strokes):
  lines = []
  for s in strokes:
    p = s[0]
    for q in s[1:]:
      lines.append((p[0],p[1],q[0],q[1]))
      lines.append((q[0],q[1],p[0],p[1]))
      p = q
    lines.append((p[0],p[1],s[0][0],s[0][1]))
    lines.append((s[0][0],s[0][1],p[0],p[1]))
  return lines

def find_next(a):
  global loc
  lx,ly = loc
  n = len(a)
  i = 0
  while i<n:
    x1,y1,x2,y2 = a[i]
    if x1>(lx+0.1) and y1>(ly+0.1):
      return i
    i = i + 1
  return None

def optimize(strokes):
  global r
  r = []

  lines = dice(strokes)

  for ang in xrange(0,16):
    a = []
    for x in lines:
      if ang==angle(*x):
        a.append(x)
    if not a:
      continue
    a.sort(key=lambda s:(s[1],s[0]))
    emit_training_line(ang)
    while a:
      while True:
        i = find_next(a)
        if i==None:
          break
        emit_line(*a[i])
        del a[i]
      emit_training_line(ang)

  return r
