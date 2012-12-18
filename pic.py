# read paths from a pic file produced by "pstoedit -f pic"

def read_pic(filename):
  strokes = []
  f = open(filename,"r")

  for line in f.readlines():
    if line[:10] != "line from ":
      continue
    line = line[10:]
    x = line.find(" ")
    if x < 0:
      continue
    p = line[:x].split(",")
    p[0] = float(p[0])
    p[1] = float(p[1])
    stroke = [p]
    line = line[x:] + " "
    while line[:4] == " to ":
      line = line[4:]
      x = line.find(" ")
      if x < 0:
        break
      p = line[:x].split(",")
      p[0] = float(p[0])
      p[1] = float(p[1])
      stroke.append(p)
      line = line[x:]
    strokes.append(stroke)

  return strokes
