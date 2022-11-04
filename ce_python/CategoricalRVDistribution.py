#!/usr/bin/env python
from __future__ import annotations

from ce_python.RVDistribution import RVDistribution
from ce_python.TYPE_OF_RV import TYPE_OF_RV
from ce_python.ChessBoardPositionPair import ChessBoardPositionPair

import numpy as np
from abc import abstractmethod

class CategoricalRVDistribution(RVDistribution):
    def __init__(self, nSrc: int, nDest: int, bAllowStutter: bool, scoreObject: object, clazz: str, eTYPE_OF_RV: object, my_CE_Manager: object):
        """
        super().__init__(scoreObject, clazz, my_CE_Manager, eTYPE_OF_RV)
        self.m = my_CE_Manager.m
        self.n = my_CE_Manager.environment.getBoardHeight() * my_CE_Manager.environment.getBoardWidth()
        self.nSrc = nSrc
        self.nDest = nDest
        self.bAllowStutter = bAllowStutter
        """
        #FOR TESTING ONLY *****************
        self.n = 400
        self.m = 8
        #FOR TESTING ONLY *****************
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
        
    
    def avoidOffBoardPositions(self, _trans_mat):
        for i in range(self.n):
            for j in range(self.m):
                if(self.isOffBoard(i,j)):
                    _trans_mat[i,j] = 0 #i.e. don't allow going off board
    
    def isOffBoard(self, vertex: int, neighborCode: int) -> bool:
        pass
        

    

    
    def generateGraphPath(self, nAgent: int):
        return super().generateGraphPath(nAgent)
    def getDest(self) -> int:
        return super().getDest()
    def smoothlyUpdateDistribution(self, alpha: float, scoredSampleParts):
        return super().smoothlyUpdateDistribution(alpha, scoredSampleParts)


    @staticmethod
    def test_class():
        cat = CategoricalRVDistribution(20,80,False,'scoreObject','clazz',TYPE_OF_RV.SPEED_RV,'my_CE_Manager')
        print(cat.trans_mat.shape)
        cat.initDistribution()

CategoricalRVDistribution.test_class()