#!/usr/bin/env python

class Environment():
    def __init__(self, gridContainer: object) -> None:
        self.gridContainer = gridContainer
    def getGrid(self) -> object:
        return self.gridContainer
    def getBoardWidth(self) -> int:
        return self.gridContainer.getGrid().shape[1]
    def getBoardHeight(self) -> int:
        return self.gridContainer.getGrid().shape[0]
    def fromVertexToPair(self, vertex: int):
        return self.gridContainer.fromVertexToPair(vertex)
    def fromPairToVertex(self, pair) -> int:
        return self.gridContainer.fromPairToVertex(pair)
    def isDistanceOneFromLongWall(self, location: int, gridContainer: object) -> bool:
        return self.gridContainer.isDistanceOneFromLongWall(location, gridContainer)
    def isToRightOfRed_L_obstacle(self, pathPoint: int):
        x: int = self.fromVertexToPair(pathPoint).get_j() #X is j!! Y is i!!
        y: int = self.fromVertexToPair(pathPoint).get_i() #X is j!! Y is i!!
        return self.gridContainer.isToRightOfRed_L_obstacle(x,y)
    def getCellToCelDist(self, _pos: int, _next_pos: int) -> float:
        pos = self.fromVertexToPair(_pos)
        next_pos = self.fromVertexToPair(_next_pos)
        len: float = 0
        if(pos.get_i() == next_pos.get_i()):
            len += 1.0
        elif(pos.get_j() == next_pos.get_j()):
            len += 1.0
        else: len += 1.4
        return len
        
        