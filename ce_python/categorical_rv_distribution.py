#!/usr/bin/env python

#NATIVE PYTHON IMPORTS
from abc import abstractmethod

#INSTALLED PACKAGE IMPORTS
import numpy as np

#IMPORTS FROM THIS PACKAGE
from ce_python.rv_distribution import RVDistribution
from ce_python.chess_board_position_pair import ChessBoardPositionPair
from ce_python.type_of_rv import TYPE_OF_RV

class CategoricalRVDistribution(RVDistribution):
    def __init__(self, nSrc: int, nDest: int, bAllowStutter: bool, scoreObject: object, clazz: str, eTYPE_OF_RV: object, my_CE_Manager: object):
        super().__init__(scoreObject, clazz, my_CE_Manager, eTYPE_OF_RV)
        self.m = my_CE_Manager.m
        self.n = my_CE_Manager.environment.getBoardHeight() * my_CE_Manager.environment.getBoardWidth()
        self.nSrc = nSrc
        self.nDest = nDest
        self.bAllowStutter = bAllowStutter
        self.trans_mat = np.empty((self.n,self.m),dtype=np.float)
        self.trans_mat_old = np.empty_like(self.trans_mat)
        
    """
    //Initialize the probability transition matrix: Pij is probability of using edge i-->j in a path
	// It should have 0 diag and sum of p's in a row s.b 1
    """
    def initDistribution(self):
        p_ij = 1.0 / float(self.m)
        self.trans_mat[:] = p_ij

        self.avoidOffBoardPositions(self.trans_mat)
        self.avoidObstacles(self.trans_mat, self.my_CE_Manager.environment)
        self.normalizeRowProbabilities(self.trans_mat)

        """
        // Reserves space not only for a new matrix but
        // also for a matrix from the previous iteration:  
        //this.trans_mat = trans_mat
        //this.trans_mat_old = trans_mat
        """
        #make a deep copy of trans_mat and put it into trans_mat_old
        self.trans_mat_old = self.trans_mat.copy()
    
    def avoidObstacles(self, _trans_mat, environment):
        grid = environment.getGrid().getGrid()
        for i in range(self.my_CE_Manager.environment.getBoardHeight()):
            for j in range(self.my_CE_Manager.environment.getBoardWidth()):
                if(grid[i,j] <= 0): #i.e., blocked
                    i_j_vertex = self.my_CE_Manager.environment.fromPairToVertex(ChessBoardPositionPair(i,j))
                    self.markUnvisitableFromNeighbors(i_j_vertex, _trans_mat) #all 0..7 neighbors of i_j_vertex should not be able to visit

    """
    // mark neighbors to not allow them to visit lastVertexInPath
	// Remember second dimension codes (where up is "higher i's"):
	//	|0|1|2|   //NOTE, up means HIGHER i's --> depicts as down in visualize!!!
    //	|4|x|3|
    //	|6|5|7|
	//given @param lastVertexInPath, mark trans_mat so that @param lastVertexInPath cannot be visited from any of its neighbors
    """    
    def markUnvisitableFromNeighbors(self, lastVertexInPath: int, _trans_mat) -> None:
        lastPairInPath = self.my_CE_Manager.environment.fromVertexToPair(lastVertexInPath)
        i = lastPairInPath.get_i()
        j = lastPairInPath.get_j()
        if(i>0): #mark unvisitable from neighbors below i
            unvisitable_from_i = i-1 #row below i
            unvisitable_from_j = j #same column
            neighbor = self.my_CE_Manager.environment.fromPairToVertex(ChessBoardPositionPair(unvisitable_from_i,unvisitable_from_j))
            if(_trans_mat[neighbor].size >= 2): 
                _trans_mat[neighbor][1] = 0 #neighbor's #1 (top) neighbor is lastVertexInPath
            
            if(j>0):
                unvisitable_from_j = j-1 #column to left, i.e. bottom left neighbor
                neighbor = self.my_CE_Manager.environment.fromPairToVertex(ChessBoardPositionPair(unvisitable_from_i,unvisitable_from_j))
                if(_trans_mat[neighbor].size >= 3): 
                    _trans_mat[neighbor][2] = 0 #neighbor's #2 (top-right) neighbor is lastVertexInPath
            if(j<self.my_CE_Manager.environment.getBoardWidth()-1):
                unvisitable_from_j = j+1 #column to right, i.e. bottom right neighbor
                neighbor = self.my_CE_Manager.environment.fromPairToVertex(ChessBoardPositionPair(unvisitable_from_i,unvisitable_from_j))
                _trans_mat[neighbor][0] = 0 #neighbor's #0 (top-left) neighbor is lastVertexInPath
        if(i<self.my_CE_Manager.environment.getBoardHeight()-1): #mark unvisitable from neighbors above i
            unvisitable_from_i = i+1 #row above i
            unvisitable_from_j = j #same column
            neighbor = self.my_CE_Manager.environment.fromPairToVertex(ChessBoardPositionPair(unvisitable_from_i,unvisitable_from_j))
            if(_trans_mat[neighbor].size >= 6): 
                _trans_mat[neighbor][5] = 0 #neighbor's #5 (bottom) neighbor is lastVertexInPath
            
            if(j>0):
                unvisitable_from_j = j-1 #column to left, i.e. top left neighbor
                neighbor = self.my_CE_Manager.environment.fromPairToVertex(ChessBoardPositionPair(unvisitable_from_i,unvisitable_from_j))
                if(_trans_mat[neighbor].size >= 8): _trans_mat[neighbor][7] = 0 #neighbor's #7 (top-right) neighbor is lastVertexInPath
            if(j<self.my_CE_Manager.environment.getBoardWidth()-1):
                unvisitable_from_j = j+1 #column to right, i.e. top right neighbor
                neighbor = self.my_CE_Manager.environment.fromPairToVertex(ChessBoardPositionPair(unvisitable_from_i,unvisitable_from_j))
                if(_trans_mat[neighbor].size >= 7): _trans_mat[neighbor][6] = 0 #neighbor's #6 (bottom-left) neighbor is lastVertexInPath
        if(j>0):
            unvisitable_from_i = i #same row
            unvisitable_from_j = j-1 #column to left, i.e. left neighbor
            neighbor = self.my_CE_Manager.environment.fromPairToVertex(ChessBoardPositionPair(unvisitable_from_i,unvisitable_from_j))
            if(_trans_mat[neighbor].size >= 4): _trans_mat[neighbor][3] = 0 #neighbor's #3 (right) neighbor is lastVertexInPath
        if(j<self.my_CE_Manager.environment.getBoardWidth()-1):
            unvisitable_from_i = i #same row
            unvisitable_from_j = j+1 #column to right, i.e. right neighbor
            neighbor = self.my_CE_Manager.environment.fromPairToVertex(ChessBoardPositionPair(unvisitable_from_i,unvisitable_from_j))
            if(_trans_mat[neighbor].size >= 5): _trans_mat[neighbor][4] = 0 #neighbor's #4 (left) neighbor is lastVertexInPath

    """
    // ex: vertex.j = 0, i.e., left node, then it has no node to its left on the board
	// Remember second dimension (@param neighborCode) codes:
	//	|0|1|2|  //NOTE, up means HIGHER i's --> depicts as down in visualize!!!
    //	|4|x|3|
    //	|6|5|7|
    """
    def isOffBoard(self, vertex: int, neighborCode: int) -> bool:
        chessBoardPositionPair_vertex = self.my_CE_Manager.environment.fromVertexToPair(vertex)
        if(chessBoardPositionPair_vertex.get_i() == 0):
            if(neighborCode == 7 or neighborCode == 5 or neighborCode == 6): return True
        elif(chessBoardPositionPair_vertex.get_i() == self.my_CE_Manager.environment.getBoardHeight() - 1):
            if(neighborCode == 0 or neighborCode == 1 or neighborCode == 2): return True
        
        if(chessBoardPositionPair_vertex.get_j() == 0):
            if(neighborCode == 0 or neighborCode == 4 or neighborCode == 6): return True
        elif(chessBoardPositionPair_vertex.get_j() == self.my_CE_Manager.environment.getBoardWidth() - 1):
            if(neighborCode == 2 or neighborCode == 3 or neighborCode == 7): return True
        
        return False

    def avoidOffBoardPositions(self, _trans_mat):
        for i in range(self.n):
            for j in range(self.m):
                if(self.isOffBoard(i,j)):
                    _trans_mat[i,j] = 0 #i.e. don't allow going off board
    
    """
    //@param j_as_full_index is an index of a neighbor of @param i: @return the 0..7 neighbor-code for i to move to j_as_full_index
	// Remember second dimension (@param neighborCode) codes:
	//	|0|1|2| //NOTE, up means HIGHER i's --> depicts as down in visualize!!!
    //	|4|x|3|
    //	|6|5|7|
    // When getALLOW_STUTTER()==true then neighborRelativePos==5 is NOT node on bottom, but rather is "stutter at same location" 
    """
    def calculateNeighborCode(self, i: int, j_as_full_index: int) -> int:
        chessBoardPositionPair_i = self.my_CE_Manager.environment.fromVertexToPair(i)
        chessBoardPositionPair_j_as_full_index = self.my_CE_Manager.environment.fromVertexToPair(j_as_full_index)
        __i = chessBoardPositionPair_i.get_i()
        __j = chessBoardPositionPair_i.get_j()
        __i_prime = chessBoardPositionPair_j_as_full_index.get_i()
        __j_prime = chessBoardPositionPair_j_as_full_index.get_j()
        if(__i_prime == __i):
            if(__j_prime == __j + 1): return 3
            if(__j_prime == __j - 1): return 4
            if(self.getALLOW_STUTTER()):
                return 5 #when allowing stutter, 5 represents stutter
            else:
                raise Exception(f"j_as_full_index(\"{j_as_full_index}\") is not neighbor of i (\"{i}\")")
        if(__i_prime == __i+1):
            if(__j_prime == __j+1): return 2
            if(__j_prime == __j): return 1
            if(__j_prime == __j-1): return 0
            raise Exception(f"j_as_full_index(\"{j_as_full_index}\") is not neighbor of i (\"{i}\")")
        if(__i_prime == __i-1):
            if(__j_prime == __j + 1): return 7
            if(__j_prime == __j):
                if(not self.getALLOW_STUTTER()): return 5
                else:
                    raise Exception(f"bALLOW_STUTTER==true yet there was a move back, i.e., j=5 but 5 represents stutter")
            if(__j_prime == __j - 1): return 6
            raise Exception(f"j_as_full_index(\"{j_as_full_index}\") is not neighbor of i (\"{i}\")")
        raise Exception("Reached unreachable line in calculateNeighborCode")
    
    """
    //@return position 0..n of neighbor given position (0..399) of @param location and code for relative pos of neighbor (0..7)
    // When getALLOW_STUTTER()==true then neighborRelativePos==5 is NOT node on bottom, but rather is "stutter at same location"
    """
    def getNeighbor(self, location: int, neighborRelativePos: int) -> int:
        neighborLocation = None
        if(neighborRelativePos == 0):
            neighborLocation = location+self.my_CE_Manager.environment.getBoardWidth()-1 #node on top-left
        elif(neighborRelativePos == 1):
            neighborLocation = location+self.my_CE_Manager.environment.getBoardWidth() #node on top
        elif(neighborRelativePos == 2):
            neighborLocation = location+self.my_CE_Manager.environment.getBoardWidth()+1 #node on top-right
        elif(neighborRelativePos == 3):
            neighborLocation = location+1 #node on right
        elif(neighborRelativePos == 4):
            neighborLocation = location-1 #node on left
        elif(neighborRelativePos == 5):
            if(self.getALLOW_STUTTER()):
                neighborLocation = location #stutter
            else:
                neighborLocation = location-self.my_CE_Manager.environment.getBoardWidth() #node on bottom
        elif(neighborRelativePos == 6):
            neighborLocation = location-self.my_CE_Manager.environment.getBoardWidth()-1 #node on bottom-left
        elif(neighborRelativePos == 7):
            neighborLocation = location-self.my_CE_Manager.environment.getBoardWidth()+1 #node on bottom-right
        else:
            raise Exception(f"Unexpected neighborRelativePos = {neighborRelativePos} in getNeighbor()")
        
        if(neighborLocation < 0):
            raise Exception("neighborRelativePos should not be given such that we choode offBoard neighbor (the choice function should have 0 probabilities for off-board neighbors)")
        return neighborLocation

    # //Doron: AVOID future cycles! by putting a 0 probability to go again (in the future) to the last node in the path, no matter from where (the where is i)
    def avoidFutureCycles(self, _trans_mat, path):
        lastVertexInPath = path.getPoint(path.len()-1)
        self.markUnvisitableFromNeighbors(lastVertexInPath, _trans_mat)
    
    def generateGraphPath(self, nAgent: int):
        _trans_mat = self.deepCloneTransMat()
        path = self.generateAdversaryObject()
        speedAt0 = path.getAdversaryCategoricalFixedSpeedAt(0)
        path.putPointAt(0,self.nSrc,speedAt0, TYPE_OF_RV.SPEED_RV)
        for k in range(self.n):
            if(self.m > 3):
                self.avoidFutureCycles(_trans_mat,path)
                self.normalizeRowProbabilities(_trans_mat,path)
            #extend the path
            lastVertexInPath = path.getPoint(path.len()-1)
            choice = self.chooseNextVertex(_trans_mat,path)
            if(choice == -1):
                path.setNotGoodPath()
                break
            if(self.isOffBoard(lastVertexInPath,choice)):
                raise Exception("choice should not point to an offBoard neighbor;  _trans_mat[lastVertexInPath][choice] s.b. 0!")
            next = self.getNeighbor(lastVertexInPath,choice)
            speedAtkp1 = path.getAdversaryCategoricalFixedSpeedAt(k+1)
            path.putPointAt(k+1,next,speedAtkp1,TYPE_OF_RV.SPEED_RV)
            if(self.isPositionTheDestination(next,self.nDest)):
                break #REACHED destination!
        """
        //if path did not reach nDestNode then return null!!
	    // By the problem statement, we need to finish in the same city
	    // where we started:
        """
        lastVertexInPath = path.getPoint(path.len()-1)
        if(lastVertexInPath != self.nDest):
            path.setNotGoodPath()
        
        return path
    
    """
    // get choice made by "choice = chooseNextVertex(_trans_mat, path, rand);",
    // i..e, the m value going  x_ptPair (the 'x') --> nextPtPair 
    // NOTE: The assumption is that the two @param points were generated by chooseNextVertex, i..e, they ARE ADJACENT!
    //Recall:   
    //	|0|1|2|   //NOTE, up means HIGHER i's --> depicts as down in visualize!!!
    //	|4|x|3|
    //	|6|5|7|
    """
    @staticmethod
    def getMvalue(x_ptPair: ChessBoardPositionPair, nextPtPair: ChessBoardPositionPair):
        x_i = x_ptPair.get_i()
        x_j = x_ptPair.get_j()
        next_i = nextPtPair.get_i()
        next_j = nextPtPair.get_j()
        if(x_i == next_i): #same row
            if(x_j == next_j):
                raise Exception("x_i == next_i and x_j == next_j in getChoiceMade()")
            if(x_j+1 == next_j): return 3 #a move from 'x' to right
            elif(x_j-1 == next_j): return 4 #a move from 'x' to left
            else:
                raise Exception("non adjacent @param nodes in getChoiceMade()")
        elif(x_i+1 == next_i): #a move from 'x' row to row above
            if(x_j == next_j): return 1 #same column
            if(x_j+1 == next_j): return 2 #a move from 'x' to right
            elif(x_j-1 == next_j): return 0
            else:
                raise Exception("non adjacent @param nodes in getChoiceMade()")
        elif(x_i-1 == next_i): #a move from 'x' row to row below
            if(x_j == next_j): return 5 #same column
            if(x_j+1 == next_j): return 7
            elif(x_j-1 == next_j): return 6
            else:
                raise Exception("non adjacent @param nodes in getChoiceMade()")
        else:
            raise Exception("non adjacent @param nodes in getChoiceMade()") 

    def normalizeRowProbabilities(self, _trans_mat, path=None) -> None:
        if(path):
            i = path.getPoint(path.len()-1)
            self.norm(_trans_mat, i)
        else:
            for i in range(self.n):
                self.norm(_trans_mat,i)
    
    def norm(self, _trans_mat, i):
        sum = 0
        #sum up all rows
        sum += np.sum(_trans_mat[i])

        if(sum != 0):
            _trans_mat[i] = _trans_mat[i]/sum
            dSum = 0
            dSum += np.sum(_trans_mat[i])
            if(abs(dSum - 1) > 0.0001):
                raise Exception("abs(dSum-1) is too large")

    def chooseNextVertex(self, _trans_mat, path, rand=None):
        lastVertexInPath = path.getPoint(path.len()-1)
        #sanity check
        sum = 0
        sum += np.sum(_trans_mat[lastVertexInPath])
        if(sum > 0 and 1-sum > 0.0001):
            raise Exception("chooseNextVertex sanity test failed")
        
        #here we want to return an integer (i.e., 0 through 7) with the next choice of point to go to next
        probs = _trans_mat[lastVertexInPath]
        sum = np.sum(probs)
        if(sum == 0):
            return -1
        else:
            return self.rand.choice(self.m, p=probs)
        
        
    
    def smoothlyUpdateDistribution(self, alpha: float, scoredGraphPaths):
        self.trans_mat_old = self.deepCloneTransMat()
        _trans_mat = np.zeros_like(self.trans_mat)

        """
        // It is too slow to calculate according to 
        // (Boer et. al, 2004, Equation 49 == CEtutorial.pdf. 
    	// Instead, we will use
        // a trick: increment each time there was a trip from
        // i to j by 1 and add it to a matrix. After that, 
        // we divide each element by a total number of selected paths: 
        """
        nCount = self.countTransMat(_trans_mat,scoredGraphPaths)

        _trans_mat = _trans_mat / nCount

        """
        // Boer et. al (2004), Remark 3.3 (Smoothed Updating).
        //this.trans_mat = alpha*trans_mat + (1-alpha)*this.trans_mat_old
        //Doron: smoothing is critical because newly (counting based) _trans_mat[i][j] is mostly 0's because |_highScoredPaths| is not that large
        """
        self.trans_mat = alpha * _trans_mat + (1-alpha) * self.trans_mat_old

        for i in range(self.n):
            sum = 0
            sum += np.sum(self.trans_mat[i])
            if(sum > 0):
                self.trans_mat[i] = self.trans_mat[i]/sum
    
    def countTransMat(self, _trans_mat, scoredGraphPaths) -> int:
        _highScoredPaths = scoredGraphPaths[:]
        nCount = 0
        for scoredGraphpath in _highScoredPaths:
            nCount += 1
            path = scoredGraphpath.graphPath
            pathLen = path.len()
            for idx in range(pathLen-1):
                i = path.getPoint(idx)
                j_as_full_index = path.getPoint(idx+1)
                j = self.calculateNeighborCode(i,j_as_full_index)
                _trans_mat[i][j] += 1
        return nCount
    
    def isPositionTheDestination(self, pos: int, dest: int) -> bool:
        return pos == dest
    
    def deepCloneTransMat(self) -> np.ndarray:
        return self.trans_mat.copy()

    def getALLOW_STUTTER(self):
        return self.bAllowStutter
    def getDest(self) -> int:
        return self.nDest
