#
# communicate with a graphtec printer (Silhouette Cameo or Portrait)
#

import sys
import math

class graphtec:
  def __init__(self):
    self.fd = sys.stdout
    self.scale = 2.54*200
    self.offset = (4.0,0.5)
    self.matrix = (1,0,0,1)
    self.media_size = (12,11)   # default of 12x11 inches

  def emit(self, s):
    self.fd.write(s)

  def start(self):
    papertype = "100"
    trackenhancing = "0"
    orientation = "1"
    page = ["media_size", int(self.scale*self.media_size[0]), int(self.scale*self.media_size[1])]
    margintop = 500                           # margins in device units
    marginright = 320
    self.emit("\x1b\x04")  # initialize plotte
    self.emit("\x1b\x05")  # status request
#receive() "0\x03"
    self.emit("TT\x03")    # home the cutter
    self.emit("FG\x03")    # query version
#receive() "CAMEO V1.10    \x03"
    self.emit("FW" + papertype + "\x03")
    self.emit("FC18\x03")
    self.emit("FY" + trackenhancing + "\x03")
    self.emit("FN" + orientation + "\x03")
    self.emit("FE0\x03")
    self.emit("TB71\x03")
#receive() "    0,    0\x03"
    self.emit("FA\x03")     # begin page definition
    self.emit("FU" + str(page[2] - margintop) + "," + str(page[1] - marginright) + "\x03")
    self.emit("FM1\x03")    # ??
    self.emit("TB50,1\x03") # ??
    self.emit("FO" + str(page[2] - margintop) + "\x03")  # feed command?
    self.emit("&100,100,100,\\0,0,")                     # ??
    self.emit("Z" + str(page[1]) + "," + str(page[2]) + ",L0,")

  def end(self):
    self.emit("&1,1,1,TB50,0\x03")
    self.emit("FO0\x03")    # feed the page out
    self.emit("H,")         # halt?

  def transform(self, x, y):
    tx = self.matrix[0]*x + self.matrix[1]*y + self.offset[0]
    ty = self.matrix[2]*x + self.matrix[3]*y + self.offset[1]
    tx = tx*self.scale
    ty = ty*self.scale
    return tx,ty

  def move(self, x, y):
    x,y = self.transform(x,y)
    self.emit('M%.3f,%.3f\x03' % (x,y))
#    sys.stderr.write('move %f %f\n' % (x/self.scale,y/self.scale))

  def draw(self, x, y):
    x,y = self.transform(x,y)
    self.emit('D%.3f,%.3f\x03' % (x,y))
#    sys.stderr.write('draw %f %f\n' % (x/self.scale,y/self.scale))

  def closed_path(self, s):
    if len(s)<3:
      return
    self.move(*s[0])
    for p in s[1:]:
      self.draw(*p)
    self.draw(*s[0])

  def path(self, s):
    self.move(*s[0])
    for p in s[1:]:
      self.draw(*p)

  def comp(self, x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    theta = math.atan2(dy,dx)
    dist_pre = -0.001
    dist_post = 0.001
    dx1 = dist_pre*math.cos(theta)
    dy1 = dist_pre*math.sin(theta)
    dx2 = dist_post*math.cos(theta)
    dy2 = dist_post*math.sin(theta)
    return (dx1,dy1,dx2,dy2)

  def line(self, x1, y1, x2, y2):
    dx1,dy1,dx2,dy2 = self.comp(x1,y1,x2,y2)
    self.move(x1+dx1,y1+dy1)
    self.draw(x2+dx2,y2+dy2)

  def set(self, **kwargs):
    for k in kwargs:
      if k=='speed':
        self.emit("!" + str(kwargs[k]) + "\x03")
      elif k=='force':
        self.emit("FX" + str(kwargs[k]) + ",0\x03")
      elif k=='offset':
        self.offset = kwargs[k]
      elif k=='matrix':
        self.matrix = kwargs[k]
      elif k=='media_size':
        self.media_size = kwargs[k]
