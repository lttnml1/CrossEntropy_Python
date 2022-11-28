#!/usr/bin/env python
#NATIVE PYTHON IMPORTS
from typing_extensions import Self
from abc import abstractmethod
import math

#INSTALLED PACKAGE IMPORTS
import numpy as np

#IMPORTS FROM THIS PACKAGE
from ce_python.chess_board_position_pair import ChessBoardPositionPair

class Grid:
    #_WIDTH: int
    #_HEIGHT: int 
    #_grid: np.ndarray

    #Grid with custom dimensions, used by Environment - not by subclasses of Environment
    def __init__ (self, nWIDTH: int, nHEIGHT: int):
        self._WIDTH =  nWIDTH
        self._HEIGHT = nHEIGHT
        self._grid = np.ones((nHEIGHT,nWIDTH))
        Grid.Grid_constructor(self)

    def Grid_constructor(self) -> None:
        #all values already initialized to ones in constructor: "np.ones..."
        
        """
        #highway: block out all lanes for which j < 9 or j > 15
        self._grid[:,:9] = -1
        self._grid[:,16:] = -1
        """
        
        #cone
        self._grid[3:7,13:17] = 0
        
        #cabinet
        self._grid[11:16,14:17] = -1 
        
        self._grid[16:19,4] = -2
        self._grid[18,3] = -2

        #small diagonal near barrel
        self._grid[11:14,2] = -3
        self._grid[12:14,1] = -3

        #long diagonal near barrel -- WALL (BURLYWOOD). Recall: //i is Y in visualizer!!
        self._grid[7:9,1] = -4
        self._grid[8:11,2] = -4
        self._grid[9:12,3] = -4
        self._grid[11:13,4] = -4
        self._grid[12:14,5] = -4
        self._grid[13:15,6] = -4

        #small "coffin" on bottom left
        self._grid[1:3,1:4] = -5

        #small box on bottom left
        self._grid[3,3:5] = -6
        self._grid[4,3] = -6

        self._grid[11,8] = -7 #small box in middle

        #//--- 4 boxes in middle Y rows
        self._grid[4,11] = -8 #left most one:
        self._grid[7,11] = -8 #second left most one

        #third from left
        self._grid[9:11,9] = -8
        self._grid[10,10] = -8

        #right most one
        self._grid[12:14,10] = -8
        self._grid[13:15,11] = -8

        np.set_printoptions(linewidth=np.inf)
        #print(self._grid)
        
        #**DID NOT IMPLEMENT the section for: //***When height > 20 then add more obstacles
    
    def getGrid(self) -> np.ndarray:
        return self._grid
    
    @staticmethod
    def isOnLongWall(i: int, j: int, gridContainer: Self) -> bool:
        grid = np.copy(gridContainer.getGrid())
        num_rows, num_columns = grid.shape
        if (i < 0 or j < 0): return False
        if (i >= num_rows or j >= num_columns): return False
        return grid[i,j]==-4
    
    def isDistanceOneFromLongWall(self, location: int, gridContainer: Self) -> bool:
        chessBoardPositionPair_location = self.fromVertexToPair(location)
        i: int = chessBoardPositionPair_location.get_i()
        j: int = chessBoardPositionPair_location.get_j()
        #Remember, the grid is transposed (see constructor above)
        b: bool = Grid.isOnLongWall(i,j,gridContainer) or \
                Grid.isOnLongWall(i+1,j, gridContainer) or \
                Grid.isOnLongWall(i,j+1,gridContainer) or \
                Grid.isOnLongWall(i-1,j,gridContainer) or \
                Grid.isOnLongWall(i,j-1,gridContainer) or \
                Grid.isOnLongWall(i+1,j+1,gridContainer) or \
                Grid.isOnLongWall(i-1,j-1,gridContainer) or \
                Grid.isOnLongWall(i+1,j-1,gridContainer) or \
                Grid.isOnLongWall(i-1,j+1,gridContainer)
        return b

    def isToRightOfRed_L_obstacle(self, x: int, y: int) -> bool:
        b: bool = (y >= 16 and y <= 18 and x >4)
        # X is j, Y is i in visualizer!!
        return b
    
    def fromVertexToPair(self, vertex: int) -> ChessBoardPositionPair:
        j: int = vertex % self.getBoardWidth()
        i: int = math.floor(vertex / self.getBoardWidth())
        return ChessBoardPositionPair(i,j)
    
    def fromPairToVertex(self, pair: ChessBoardPositionPair) -> int:
        return pair.get_i() * self.getBoardWidth() + pair.get_j()
    
    def setGrid(self, newGrid: np.ndarray) -> None:
        self._grid = newGrid
    
    def getBoardHeight(self) -> int: 
        return self._grid.shape[0]
    
    def getBoardWidth(self) -> int: 
        return self._grid.shape[1]
    
    def loadASWgridFromFile(self):
        raise NotImplementedError("loadASWgridFromFile not implemented")
    
    @staticmethod
    def test_class():
        g=Grid(20,20)
        print("NEW\n")
        g2 = np.copy(g.getGrid())
        rows, columns = g2.shape
        print(str(rows) + str(columns))
        g2[0,0]=999
        print(g._grid[0,0])
        print(g2[0,0])
        print(g.getBoardHeight())

