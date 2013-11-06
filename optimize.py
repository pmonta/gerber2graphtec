# optimize paths for the graphtec cutter by dicing into individual lines, sorting by angle

import math

# rotate all geometry counterclockwise by theta degrees

def rotate(strokes, theta):
  ang = theta*(math.pi/180)
  r = []
  for s in strokes:
    t = []
    for (a,b) in s:
      c = a*math.cos(ang) - b*math.sin(ang)
      d = a*math.sin(ang) + b*math.cos(ang)
      t.append((c,d))
    r.append(t)
  return r

# find bounding box, then offset the geometry to make all coordinates positive

def justify(strokes):
  min_x,min_y = 1e6,1e6
  max_x,max_y = -1e6,-1e6
  for s in strokes:
    for (a,b) in s:
      max_x = max([max_x,a])
      max_y = max([max_y,b])
      min_x = min([min_x,a])
      min_y = min([min_y,b])
  r = []
  for s in strokes:
    t = []
    for (a,b) in s:
      t.append((a-min_x,b-min_y))
    r.append(t)
  return r

def max_extent(strokes):
  max_x,max_y = 0,0
  for s in strokes:
    for (a,b) in s:
      max_x = max([max_x,a])
      max_y = max([max_y,b])
  return max_x,max_y

def emit_line(x1,y1,x2,y2):
  global r
  global loc
  loc = (x2,y2)
  r.append((x1,y1,x2,y2))

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
  cx,cy = 0.25,0.25
  theta = ang*math.pi/8
  x = math.cos(theta)
  y = math.sin(theta)
  x1,y1 = 0.25*x-border[0]-cx, 0.25*y-border[1]-cy
  x2,y2 = 0.05*x-border[0]-cx, 0.05*y-border[1]-cy
  loc = (x2,y2)
  r.append((x1,y1,x2,y2))

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

def optimize(strokes, b):
  global border
  global r

  border = b
  r = []

  lines = dice(strokes)

  for ang in range(0,16):
    a = []
    for x in lines:
      if ang==angle(*x):
        a.append(x)
    if not a:
      continue
    a.sort(key=lambda s:(s[1],s[0]))
    emit_training_line(ang)
#    while a:
#      while True:
#        i = find_next(a)
#        if i==None:
#          break
#        emit_line(*a[i])
#        del a[i]
#      emit_training_line(ang)
    for x in a:
      emit_line(*x)

  return r
