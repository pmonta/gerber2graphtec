#!/usr/bin/python
import Tkinter
import tkMessageBox
import tkFileDialog
import sys
import os
import string

from Tkinter import *
from os import path, access, R_OK, W_OK

top = Tkinter.Tk()
top.title("Gerber to Graphtec")

Gerber_name = StringVar()
Output_name = StringVar()
gerbv_path = StringVar()
pstoedit_path  = StringVar()
offset_str  = StringVar()
border_str  = StringVar()
matrix_str  = StringVar()
speed_str  = StringVar()
force_str  = StringVar()
cut_mode_str  = StringVar()
cutter_shared_name_str  = StringVar()
CONFPATH='./g2g_gui.cnf'

input_filename = ''
output_filename = ''
gerbv_filename = ''
pstoedit_filename = ''
offset_text = ''
border_text = ''
matrix_text = ''
speed_text = ''
force_text = ''
cut_mode_text = ''
cutter_shared_name_text = ''

offset = (4,0.5)
border = (1,1)
matrix = (1,0,0,1)
speed = [2,2]
force = [8,30]
cut_mode = 0

def floats(s):
  return map(float,string.split(s,','))

def main_program():
  #
  # convert file to pic format
  #

  if not os.path.exists(Gerber_name.get()):
    get_input_filename()
  if not os.path.exists(Gerber_name.get()):
    tkMessageBox.showerror("G2G_GUI ERROR", "The path provided for the input Gerber file is invalid.")
    return

  head, tail = os.path.split(Gerber_name.get())

  if os.name=='nt':
    temp_pdf = os.path.normpath("%s\_tmp_gerber.pdf" % (head))
    temp_pic = os.path.normpath("%s\_tmp_gerber.pic" % (head))
    temp_bat = os.path.normpath("%s\_tmp_gerber.bat" % (head))
  else:
    temp_pdf = "_tmp_gerber.pdf"
    temp_pic = "_tmp_gerber.pic"

  if os.name=='nt':
    if not os.path.exists(gerbv_path.get()):
      tkMessageBox.showerror("G2G_GUI ERROR", "The path provided for gerbv is invalid.")
      return

    if not os.path.exists(pstoedit_path.get()):
      tkMessageBox.showerror("G2G_GUI ERROR", "The path provided for pstoedit is invalid.")
      return
  
  if os.name=='nt':
    os.system("echo \"%s\" --export=pdf --output=%s --border=0 \"%s\" > \"%s\"" % (os.path.normpath(gerbv_path.get()),temp_pdf,os.path.normpath(Gerber_name.get()),temp_bat))
    os.system("echo \"%s\" -q -f pic \"%s\" \"%s\" >> \"%s\"" % (os.path.normpath(pstoedit_path.get()),temp_pdf,temp_pic, temp_bat))
    os.system("\"%s\"" % temp_bat)
  else:
    os.system("%s --export=pdf --output=%s --border=0 \"%s\"" % (os.path.normpath(gerbv_path.get()),temp_pdf,os.path.normpath(Gerber_name.get())))
    os.system("%s -q -f pic \"%s\" \"%s\"" % (os.path.normpath(pstoedit_path.get()),temp_pdf,temp_pic))

  original_stdout = sys.stdout  # keep a reference to STDOUT

  if Output_name.get():
    sys.stdout = open(Output_name.get(), 'w')

  if not offset_str.get():
    default_offset_str()
  if not border_str.get():
    default_border_str()
  if not matrix_str.get():
    default_matrix_str()
  if not speed_str.get():
    default_speed_str()
  if not force_str.get():
    default_force_str()
  if not cut_mode_str.get():
    default_cut_mode_str()
    
  offset = floats(offset_str.get())
  border = floats(border_str.get())
  matrix = floats(matrix_str.get())
  speed = floats(speed_str.get())
  force = floats(force_str.get())
  cut_mode = int(cut_mode_str.get())

  #
  # main program
  #

  import graphtec
  import pic
  import optimize

  g = graphtec.graphtec()

  g.start()

  g.set(offset=(offset[0]+border[0]+0.5,offset[1]+border[1]+0.5), matrix=matrix)
  strokes = pic.read_pic(temp_pic)
  max_x,max_y = optimize.max_extent(strokes)

  tx,ty = 0.5,0.5

  border_path = [
    (-border[0], -border[1]),
    (max_x+border[0], -border[1]),
    (max_x+border[0], max_y+border[1]),
    (-border[0], max_y+border[1])
  ]

  if cut_mode==0:
    lines = optimize.optimize(strokes, border)
    for (s,f) in zip(speed,force):
      g.set(speed=s, force=f)
      for x in lines:
        g.line(*x)
      g.closed_path(border_path)
  else:
    for (s,f) in zip(speed,force):
      g.set(speed=s, force=f)
      for s in strokes:
        g.closed_path(s)
      g.closed_path(border_path)

  g.end()

  if Output_name.get():
    sys.stdout = original_stdout  # restore STDOUT back to its original value
    tkMessageBox.showinfo("G2G_GUI Message", "File '%s' created"  % (Output_name.get()) )

def Save_Configuration():
    f = open(CONFPATH,'w')
    f.write(Gerber_name.get() + '\n')
    f.write(Output_name.get() + '\n')
    f.write(gerbv_path.get() + '\n')
    f.write(pstoedit_path.get() + '\n')
    f.write(offset_str.get() + '\n')
    f.write(border_str.get() + '\n')
    f.write(matrix_str.get() + '\n')
    f.write(speed_str.get() + '\n')
    f.write(force_str.get() + '\n')
    f.write(cut_mode_str.get() + '\n')
    f.write(cutter_shared_name_str.get() + '\n')
    f.close()

def Just_Exit():
    top.destroy()

def Send_to_Cutter():
    if not Output_name.get():
      get_output_filename()
    if not Output_name.get():
      return
    src=os.path.normpath(Output_name.get())
    
    if not cutter_shared_name_str.get():
      tkMessageBox.showerror("G2G_GUI ERROR", "The name of the cutter (as a shared printer) was not provided.")
      return

    #if not os.path.exists(cutter_shared_name_str.get()):
    #  tkMessageBox.showerror("G2G_GUI ERROR", "The name of the cutter (as a shared printer) does not exist.")
    #  return
    
    dst=os.path.normpath(cutter_shared_name_str.get())
    if os.name=='nt':
      os.system("copy /B \"%s\" \"%s\"" % (src, dst))
    else:
      os.system("cat %s > %s" % (src, dst))

def get_input_filename():
    input_filename=tkFileDialog.askopenfilename(title='Select paste mask Gerber file', filetypes=[('Gerber File', '*.g*'),("All files", "*.*")] )
    if input_filename:
        Gerber_name.set(input_filename)

def get_output_filename():
    output_filename=tkFileDialog.asksaveasfilename(title='Select output filename', filetypes=[('Output files', '*.txt'),("All files", "*.*")] )
    if output_filename:
        Output_name.set(output_filename)

def get_gerbv_path():
    gerbv_filename=tkFileDialog.askopenfilename(title='Select gerbv program', initialfile='gerbv.exe', filetypes=[('Programs', '*.exe')] )
    if gerbv_filename:
        gerbv_path.set(gerbv_filename)

def get_pstoedit_path():
    pstoedit_filename=tkFileDialog.askopenfilename(title='Select gerbv program', initialfile='pstoedit.exe', filetypes=[('Programs', '*.exe')] )
    if pstoedit_filename:
        pstoedit_path.set(pstoedit_filename)

def default_offset_str():
    offset_str.set("4.0,0.5")
    
def default_border_str():
    border_str.set("1,1")
    
def default_matrix_str():
    matrix_str.set("1,0,0,1")

def default_speed_str():
    speed_str.set("2,2")

def default_force_str():
    force_str.set("8,30")
    
def default_cut_mode_str():
    cut_mode_str.set("0")

Label(top, text="Gerber File ").grid(row=1, column=0, sticky=W)
Entry(top, bd =1, width=60, textvariable=Gerber_name).grid(row=1, column=1)
Tkinter.Button(top, width=9, text = "Browse", command = get_input_filename).grid(row=1, column=2)

Label(top, text="Output File ").grid(row=2, column=0, sticky=W)
Entry(top, bd =1, width=60, textvariable=Output_name).grid(row=2, column=1)
Tkinter.Button(top, width=9, text = "Browse", command = get_output_filename).grid(row=2, column=2)

if os.name=='nt':
  Label(top, text="gerbv path ").grid(row=3, column=0, sticky=W)
  Entry(top, bd =1, width=60, textvariable=gerbv_path).grid(row=3, column=1)
  Tkinter.Button(top, width=9, text = "Browse", command = get_gerbv_path).grid(row=3, column=2)

  Label(top, text="pstoedit path ").grid(row=4, column=0, sticky=W)
  Entry(top, bd =1, width=60, textvariable=pstoedit_path).grid(row=4, column=1)
  Tkinter.Button(top, width=9, text = "Browse", command = get_pstoedit_path).grid(row=4, column=2)

Label(top, text="Offset ").grid(row=5, column=0, sticky=W)
Entry(top, bd =1, width=60, textvariable=offset_str).grid(row=5, column=1)
Tkinter.Button(top, width=9, text = "Default", command = default_offset_str).grid(row=5, column=2)

Label(top, text="Border ").grid(row=6, column=0, sticky=W)
Entry(top, bd =1, width=60, textvariable=border_str).grid(row=6, column=1)
Tkinter.Button(top, width=9, text = "Default", command = default_border_str).grid(row=6, column=2)

Label(top, text="Matrix ").grid(row=7, column=0, sticky=W)
Entry(top, bd =1, width=60, textvariable=matrix_str).grid(row=7, column=1)
Tkinter.Button(top, width=9, text = "Default", command = default_matrix_str).grid(row=7, column=2)

Label(top, text="Speed ").grid(row=8, column=0, sticky=W)
Entry(top, bd =1, width=60, textvariable=speed_str).grid(row=8, column=1)
Tkinter.Button(top, width=9, text = "Default", command = default_speed_str).grid(row=8, column=2)

Label(top, text="Force ").grid(row=9, column=0, sticky=W)
Entry(top, bd =1, width=60, textvariable=force_str).grid(row=9, column=1)
Tkinter.Button(top, width=9, text = "Default", command = default_force_str).grid(row=9, column=2)

Label(top, text="Cut Mode ").grid(row=10, column=0, sticky=W)
Entry(top, bd =1, width=60, textvariable=cut_mode_str).grid(row=10, column=1)
Tkinter.Button(top, width=9, text = "Default", command = default_cut_mode_str).grid(row=10, column=2)

if os.name=='nt':
  Label(top, text="Cutter Shared Name").grid(row=11, column=0, sticky=W)
else:
  Label(top, text="Cutter Device Name").grid(row=11, column=0, sticky=W)
Entry(top, bd =1, width=60, textvariable=cutter_shared_name_str).grid(row=11, column=1, sticky=E)

Tkinter.Button(top, width=40, text = "Create Graphtec File", command = main_program).grid(row=12, column=1)
Tkinter.Button(top, width=40, text = "Send Graphtec File to Silhouette Cutter", command = Send_to_Cutter).grid(row=13, column=1)
Tkinter.Button(top, width=40, text = "Save Configuration", command = Save_Configuration).grid(row=14, column=1)
Tkinter.Button(top, width=40, text = "Exit", command = Just_Exit).grid(row=15, column=1)

if path.isfile(CONFPATH) and access(CONFPATH, R_OK):
    f = open(CONFPATH,'r')
    input_filename = f.readline()
    input_filename = input_filename.strip()
    output_filename = f.readline()
    output_filename = output_filename.strip()
    gerbv_filename = f.readline()
    gerbv_filename = gerbv_filename.strip()
    pstoedit_filename = f.readline()
    pstoedit_filename = pstoedit_filename.strip()
    offset_text =  f.readline()
    offset_text = offset_text.strip()
    border_text =  f.readline()
    border_text = border_text.strip()
    matrix_text =  f.readline()
    matrix_text = matrix_text.strip()
    speed_text =  f.readline()
    speed_text = speed_text.strip()
    force_text =  f.readline()
    force_text = force_text.strip()
    cut_mode_text =  f.readline()
    cut_mode_text = cut_mode_text.strip()
    cutter_shared_name_text =  f.readline()
    cutter_shared_name_text = cutter_shared_name_text.strip()
    f.close()

if not input_filename:
    input_filename=""
if not output_filename:
    output_filename="result.txt"
if not gerbv_filename:
    if os.name=='nt':
        gerbv_filename="C:/Program Files (x86)/gerbv-2.6.0/bin/gerbv.exe"
    else:
        gerbv_filename="gerbv"
if not pstoedit_filename:
    if os.name=='nt':
        pstoedit_filename="C:/Program Files/pstoedit/pstoedit.exe"
    else:
        pstoedit_filename="pstoedit"
if not offset_text:
    offset_text="4.0,0.5"
if not border_text:
    border_text="1,1"
if not matrix_text:
    matrix_text="1,0,0,1"
if not speed_text:
    speed_text="2,2"
if not force_text:
    force_text="8,30"
if not cut_mode_text:
    cut_mode_text="0"
if not cutter_shared_name_text:
    if os.name=='nt':
        cutter_shared_name_text="\\\\[Computer Name]\\[Shared Name]"
    else:
        cutter_shared_name_text="/dev/usb/lp0"

Gerber_name.set(input_filename)
Output_name.set(output_filename)
gerbv_path.set(gerbv_filename)
pstoedit_path.set(pstoedit_filename)
offset_str.set(offset_text)
border_str.set(border_text)
matrix_str.set(matrix_text)
speed_str.set(speed_text)
force_str.set(force_text)
cut_mode_str.set(cut_mode_text)
cutter_shared_name_str.set(cutter_shared_name_text)

top.mainloop()
