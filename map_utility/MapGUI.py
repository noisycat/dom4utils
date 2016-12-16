#!/usr/bin/env python
''' module: MapGUI '''
import Tkinter as tk
from Tkinter import Frame
import subprocess
from PIL import ImageTk

currentMap = None

def App(Frame):
    def __init__(self, master=None):
        Frame.__init__(self,master)
        self.pack()

def display(mapToOpen=currentMap):
    ''' starts the mapEditor GUI'''

    return None

def startASYNC(mapToOpen=currentMap):
    retval = subprocess.Open(display,shell=False)
    return retval

def start(mapToOpen=currentMap):
    return None

def doNothing():
    print("New")
    return None

def FileMenu(): 
    window = tk.Toplevel()
    window.title("File")
    btns = [
    tk.Button(window,  text="New", command=doNothing),
    tk.Button(window,  text="Open", command=doNothing),
    tk.Button(window,  text="Save", command=doNothing),
    tk.Button(window,  text="Save As", command=doNothing),
    tk.Button(window,  text="Update Image", command=doNothing) ]

    for btn in btns:
        btn.pack(side="top", fill="both", expand="yes", padx="10", pady="10")

def MainWindow():
    window = tk.Toplevel()
    window.title("Main")
    window.geometry("900x600")
    return None

def MapOptionsMenu():
    window = tk.Toplevel()
    window.title("Map Options")
    btns=[
            tk.Checkbutton(window, text="Preserve Line Order",command=doNothing),
            tk.Checkbutton(window, text="Scenario", command=doNothing),
            tk.Checkbutton(window, text="Requires Mods", command=doNothing) ]

    for btn in btns:
        btn.pack(side="top", fill="both",expand="yes", padx="10", pady="10")

def OptionsMenu():
    window = tk.Toplevel()
    window.title("Options")
    btns=[
            tk.Checkbutton(window, text="Write-protect original",command=doNothing),
            tk.Checkbutton(window, text="Keep log file", command=doNothing) ]
    for btn in btns:
        btn.pack(side="top", fill="both",expand="yes", padx="10", pady="10")
    return None

root = tk.Tk()
root.title("Update")
FileMenu()
MainWindow()
OptionsMenu()
root.mainloop()
