#!/usr/bin/env python

class ChessBoardPositionPair:
    def __init__ (self, i_value: int, j_value: int):
        self.i = i_value
        self.j = j_value
    
    def __eq__ (self, other: object):
        if (self.i != other.i): return (self.i - other.i)
        if (self.j != other.j): return (self.j - other.j)
        return 0
    
    def get_i(self) -> int: return self.i
    def get_j(self) -> int: return self.j

    def isDestination(self, destination: object) -> bool:
        return (self.i==destination.get_i() and self.j==destination.get_j())

    def toStr(self) -> str:
        return f"<{self.i},{self.j}>"
    
    def toStr1(self) -> str:
        return f"{self.i}-{self.j}"