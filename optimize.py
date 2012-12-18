# optimize paths for the graphtec cutter by dicing into individual segments

def eq(a,b):
  return abs(a-b)<0.000001

def seg(x1,y1,x2,y2,d):
  global hsegs
  global vsegs
  if eq(y1,y2):
    x1 = x1 - 0.001
    x2 = x2 + 0.001
    if d=='forward':
      hsegs.append((x1,y1,x2,y1))
    else:
      hsegs.append((x2,y1,x1,y1))
  elif eq(x1,x2):
    y1 = y1 - 0.001
    y2 = y2 + 0.001
    if d=='forward':
      vsegs.append((x1,y1,x1,y2))
    else:
      vsegs.append((x1,y2,x1,y1))
  else:
    pass
#    print 'non-aligned rectangle',x1,y1,x2,y2

def quad(x):
  p1,p2,p3,p4 = x[0],x[1],x[2],x[3]
  lx = [p1[0],p2[0],p3[0],p4[0]]
  ly = [p1[1],p2[1],p3[1],p4[1]]
  x1,x2 = min(lx),max(lx)
  y1,y2 = min(ly),max(ly)
  return (x1,y1,x2,y2)

def emit_segment(x1,y1,x2,y2):
  global r
  r.append([(x1,y1),(x2,y2)])

def emit_training_segment(x1,y1,x2,y2):
  global r
  r.append([(x1-0.5,y1-0.5),(x2-0.5,y2-0.5)])

def optimize(strokes):
  global hsegs
  global vsegs
  global r

  zs = 0.1      # offset from origin
  zd = 0.3      # length of "training line"
  zeps = 0.02   # distance between forward and reverse strokes
  r = []        # new list of strokes

  hsegs = []
  vsegs = []
  d = 'forward'
  for x in strokes:
    x1,y1,x2,y2 = quad(x)
    seg(x1,y1,x2,y1,d)
    seg(x2,y1,x2,y2,d)
    seg(x1,y2,x2,y2,d)
    seg(x1,y1,x1,y2,d)
  hsegs.sort(key=lambda p:[p[1],p[0]])
  vsegs.sort(key=lambda p:[p[1],p[0]])

  for (a,b,c,d) in hsegs:
    emit_training_segment(zs, 0, zs+zd, 0) # set up knife for horizontal cuts (also antibacklash)
    emit_segment(a,b,c,d)
  for (a,b,c,d) in vsegs:
    emit_training_segment(0, zs, 0, zs+zd) # set up knife for vertical cuts (also antibacklash)
    emit_segment(a,b,c,d)

  hsegs = []
  vsegs = []
  dir = 'reverse'
  for x in strokes:
    x1,y1,x2,y2 = quad(x)
    seg(x1,y1,x2,y1,d)
    seg(x2,y1,x2,y2,d)
    seg(x1,y2,x2,y2,d)
    seg(x1,y1,x1,y2,d)
  hsegs.sort(key=lambda p:[p[1],p[0]])
  vsegs.sort(key=lambda p:[p[1],p[0]])

  for (a,b,c,d) in hsegs:
    emit_training_segment(zs+zd, zeps, zs, zeps) # set up knife for reverse horizontal cuts (also antibacklash)
    emit_segment(a,b,c,d)
  for (a,b,c,d) in vsegs:
    emit_training_segment(zeps, zs+zd, zeps, zs) # set up knife for reverse vertical cuts (also antibacklash)
    emit_segment(a,b,c,d)

  return r
