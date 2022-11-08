#!/usr/bin/env python
#NATIVE PYTHON IMPORTS

#INSTALLED PACKAGE IMPORTS

#IMPORTS FROM THIS PACKAGE

class Gammas:
    def __init__(self):
        self.gammas = []
    def add(self, _d: float):
        self.gammas.append(_d)
    def size(self):
        return len(self.gammas)
    def get(self, k: int) -> float:
        return self.gammas[k]