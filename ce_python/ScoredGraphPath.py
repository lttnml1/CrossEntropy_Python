#!/usr/bin/env python
from __future__ import annotations

from ce_python.GraphPath import GraphPath

class ScoredGraphPath():
    def __init__(self, graphPath: GraphPath, score: float):
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