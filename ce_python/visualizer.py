#!/usr/bin/env python

#NATIVE PYTHON IMPORTS
import tkinter

#INSTALLED PACKAGE IMPORTS

#IMPORTS FROM THIS PACKAGE

class Visualizer():
    def __init__(self, vanilla, perturbed, ego):
        self.vanilla = vanilla
        self.perturbed = perturbed
        self.ego = ego
        self.display()
    def display(self):
        root = tkinter.Tk()
        for r in range(20):
            for c in range(20):
                cell_text = f"({r},{c})\n" + self.check_for_more_text(r, c)
                label = tkinter.Label(root, text=cell_text,borderwidth=1)
                label.config(fg="blue")
                label.grid(row=r,column=c)
        root.mainloop()
    
    def check_for_more_text(self, r, c) -> str:
        more_text = ""
        if((r+c)%3 == 0):
            more_text += "E,17,4.5\n"
            more_text += "A,12,331\n"
        return more_text

v = Visualizer(None,None,None)