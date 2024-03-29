#!/usr/bin/env python
#NATIVE PYTHON IMPORTS

#INSTALLED PACKAGE IMPORTS

#IMPORTS FROM THIS PACKAGE
from ce_python.chess_board_position_pair import ChessBoardPositionPair

class CE_Manager:
    def __init__(self, c: int, rand, n: int, m: int, N: int, environment, bAllowStutter: bool, eNEW_CODE, rho_quantile_idx: int, isForVanillaPath: bool):
        self.m = m
        self.environment = environment
        self.n = self.environment.getBoardHeight() * self.environment.getBoardWidth()
        self.N = N
        self.rand = rand
        self.eNEW_CODE = eNEW_CODE
        self.rho_quantile_idx = rho_quantile_idx
        self.isForVanillaPath = isForVanillaPath
        self.t = None
        self.myRVDistribution = None
    
    def setMyRVDistribution(self, rvDistribution):
        self.myRVDistribution = rvDistribution
    
    #=================
    # * 11/22/22
    def get_m(self):
        return self.m
    def set_m(self, _m):
        self.m = _m
    def get_eNEW_CODE(self):
        return self.eNEW_CODE
    def set_eNEW_CODE(self, _eNEW_CODE):
        self.eNEW_CODE = _eNEW_CODE
    def get_rho_quantile_idx(self):
        return self.rho_quantile_idx
    def set_rho_quantile_idx(self, n):
        self.rho_quantile_idx = n

    """
    // mark neighbors to not allow them to visit lastVertexInPath
	// Remember second dimension codes (where up is "higher i's"):
	//	|0|1|2|   //NOTE, up means HIGHER i's --> depicts as down in visualize!!!
    //	|4|x|3|
    //	|6|5|7|
	//given @param lastVertexInPath, mark trans_mat so that @param lastVertexInPath cannot be visited from any of its neighbord
    """  
    def markUnvisitableFromNeighbors(self, lastVertexInPath: int, _trans_mat) -> None:
        lastPairInPath = self.environment.fromVertexToPair(lastVertexInPath)
        i = lastPairInPath.get_i()
        j = lastPairInPath.get_j()
        if(i>0): #mark unvisitable from neighbors below i
            unvisitable_from_i = i-1 #row below i
            unvisitable_from_j = j #same column
            neighbor = self.environment.fromPairToVertex(ChessBoardPositionPair(unvisitable_from_i,unvisitable_from_j))
            if(_trans_mat[neighbor].size >= 2): _trans_mat[neighbor][1] = 0 #neighbor's #1 (top) neighbor is lastVertexInPath
            
            if(j>0):
                unvisitable_from_j = j-1 #column to left, i.e. bottom left neighbor
                neighbor = self.environment.fromPairToVertex(ChessBoardPositionPair(unvisitable_from_i,unvisitable_from_j))
                if(_trans_mat[neighbor].size >= 3): _trans_mat[neighbor][2] = 0 #neighbor's #2 (top-right) neighbor is lastVertexInPath
            if(j<self.environment.getBoardWidth()-1):
                unvisitable_from_j = j+1 #column to right, i.e. bottom right neighbor
                neighbor = self.environment.fromPairToVertex(ChessBoardPositionPair(unvisitable_from_i,unvisitable_from_j))
                _trans_mat[neighbor][0] = 0 #neighbor's #0 (top-left) neighbor is lastVertexInPath
        if(i<self.environment.getBoardHeight()-1): #mark unvisitable from neighbors above i
            unvisitable_from_i = i+1 #row above i
            unvisitable_from_j = j #same column
            neighbor = self.environment.fromPairToVertex(ChessBoardPositionPair(unvisitable_from_i,unvisitable_from_j))
            if(_trans_mat[neighbor].size >= 6): _trans_mat[neighbor][5] = 0 #neighbor's #5 (bottom) neighbor is lastVertexInPath
            
            if(j>0):
                unvisitable_from_j = j-1 #column to left, i.e. top left neighbor
                neighbor = self.environment.fromPairToVertex(ChessBoardPositionPair(unvisitable_from_i,unvisitable_from_j))
                if(_trans_mat[neighbor].size >= 8): _trans_mat[neighbor][7] = 0 #neighbor's #7 (top-right) neighbor is lastVertexInPath
            if(j<self.environment.getBoardWidth()-1):
                unvisitable_from_j = j+1 #column to right, i.e. top right neighbor
                neighbor = self.environment.fromPairToVertex(ChessBoardPositionPair(unvisitable_from_i,unvisitable_from_j))
                if(_trans_mat[neighbor].size >= 7): _trans_mat[neighbor][6] = 0 #neighbor's #6 (bottom-left) neighbor is lastVertexInPath
        if(j>0):
            unvisitable_from_i = i #same row
            unvisitable_from_j = j-1 #column to left, i.e. left neighbor
            neighbor = self.environment.fromPairToVertex(ChessBoardPositionPair(unvisitable_from_i,unvisitable_from_j))
            if(_trans_mat[neighbor].size >= 4): _trans_mat[neighbor][3] = 0 #neighbor's #3 (right) neighbor is lastVertexInPath
        if(j<self.environment.getBoardWidth()-1):
            unvisitable_from_i = i #same row
            unvisitable_from_j = j+1 #column to right, i.e. right neighbor
            neighbor = self.environment.fromPairToVertex(ChessBoardPositionPair(unvisitable_from_i,unvisitable_from_j))
            if(_trans_mat[neighbor].size >= 5): _trans_mat[neighbor][4] = 0 #neighbor's #4 (left) neighbor is lastVertexInPath
    
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

    @staticmethod
    def getClassName(__rvDistribution): 
        raise NotImplementedError("ce_manager getClassName not implemented")
        #__rvDistribution.__class__.__name__

    @staticmethod
    def isRigidConstraintsSatisfied(rvDistribution) -> bool:
        score = rvDistribution.getScoredGraphPath(0).getScore()
        if(score >= 0): return False
        else: return True
    
    @staticmethod 
    def updateWhileCond(t: int, nRound: int, gammas, _d: int) -> bool:
        while_cond_retval: bool = True
        if(_d < 2):
            raise Exception("_d cannot be less than 2 otherwise \"for(j=2; j< _d; j++\" below will be an infinite loop")
        # We need to have lists longer than d (stopping criterion)
        # to check the elif condition
        if(t < _d):
            while_cond_retval =  True
        # if the previous d gamm are the same, exit the while-loop:
        else: #if (gammas[-this.d] == ([gammas[-1]] * this.d))
            #print(f"t:{t} >= d:{_d}")
            aGammas = gammas.gammas
            bAllAreEqual = (aGammas[-_d:] == ([aGammas[-1]] * _d))
            #print(f"{aGammas[-_d:]} == {([aGammas[-1]] * _d)}: {bAllAreEqual}")
            if(bAllAreEqual):
                while_cond_retval = False
        return while_cond_retval
    

