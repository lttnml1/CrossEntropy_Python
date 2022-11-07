#!/usr/bin/env python

class Class1():
    def __init__(self, i, j):
        self.i = i
        self.j = j
    
    def __repr__(self) -> str:
        return f"({self.i},{self.j})"
    
    def do_thing(self):
        print("Class1 object doing a thing")