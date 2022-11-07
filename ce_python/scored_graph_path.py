#!/usr/bin/env python

#NATIVE PYTHON IMPORTS

#INSTALLED PACKAGE IMPORTS

#IMPORTS FROM THIS PACKAGE

class ScoredGraphPath():
    def __init__(self, graphPath, score: float):
        self.graphPath = graphPath
        self.score = score
    def __eq__(self, __o: object) -> bool:
        d: float = self.score - __o.score
        if(d==0): return True
        else: return False
    def __lt__(self, __o: object) -> bool:
        d: float = self.score - __o.score
        if(d<0): return True
        else: return False
    def __gt__(self, __o: object) -> bool:
        d: float = self.score - __o.score
        if(d>0): return True
        else: return False
    def printMe(self, sMsg: str) -> None:
        self.graphPath.printMe(f"{sMsg} score={self.score}:")
    def setScore(self,_score: float) -> None:
        self.score = _score
    def getScore(self) -> float:
        return self.score