#!/usr/bin/env python
from typing_extensions import Self
import numpy as np

#g=Grid(20,20)
#g.Grid_constructor()

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
        print(self._grid)

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

g=Grid(20,20)
print("NEW\n")
g2 = np.copy(g.getGrid())
rows, columns = g2.shape
print(str(rows) + str(columns))
g2[0,0]=999
print(g._grid[0,0])
print(g2[0,0])
