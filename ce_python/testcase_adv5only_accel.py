#!/usr/bin/env python

#NATIVE PYTHON IMPORTS
from typing import List
import math

#INSTALLED PACKAGE IMPORTS
import numpy as np

#IMPORTS FROM THIS PACKAGE
from ce_python.test_constants import TestConstants
from ce_python.grid import Grid
from ce_python.environment import Environment
from ce_python.code_efficiencies import CODE_EFFICIENCIES
from ce_python.fixed_paths import FixedPaths
from ce_python.chess_board_position_pair import ChessBoardPositionPair
from ce_python.ce_manager import CE_Manager
from ce_python.adversary5score_hybriddistrib_vanillapath import Adversary5Score_HybridDistrib_VanillaPath
from ce_python.hybrid_rv_distribution import HybridRVDistribution
from ce_python.type_of_rv import TYPE_OF_RV
from ce_python.adversary5score_hybriddistrib_perturbationpath import Adversary5Score_HybridDistrib_PerturbationPath
from ce_python.gammas import Gammas

class TestCase_Adv5Only_accel:
    #//----- used for experiment that tries to get more interesting perturbation paths (high variance) rather than a second path that is like the first
    dAvgCategorical = 0 #// average of Categorical distrib parameters of best paths chose so far as part of emerging data-set
    dVarCategorical = 0 #// variance of best paths ...
    dAvgCategorical_minus_2Sigma = None #//  dAvgCategorical-2*sigma
    dAvgNormal = 0 #// average of Normal distrib parameters of best paths chose so far as part of emerging data-set
    dVarNormal = 0 #// variance of best paths ...
    dAvgNormal_minus_2Sigma = None #//  dAvgNormal-2*sigma
    nPaths = 0 #// number of paths in emerging data-set
    #//-------

    C = TestConstants.C
    C10 = TestConstants.C10
    C50 = TestConstants.C50

    # *****************************
    # Didn't implement the ML train/test-related values
    # *****************************

    NO_OF_PATHS = 2 #vanilla and perturbation
    DATA_SET_SIZE = 1

    def __init__(self):
        self.grid = Grid(TestConstants.W, TestConstants.H)
        self.environment = Environment(self.grid)

        self.n: int = self.environment.getBoardWidth() * self.environment.getBoardHeight() #//yes..., each one of the board locations is a vertex in this graph, but m is only 8 (8 neighbors)
        self.m: int = TestConstants.NUMBER_OF_POSSIBLE_MOVES

        self.bAllowStutter: bool = False

        self.eNEW_CODE = CODE_EFFICIENCIES.NEW_CODE_FAST

        self.c: int = self.getC()

        self.rho_quantile_idx: int = int(round(TestConstants.RHO * self.c * self.n * self.m))

        self.rand = np.random.default_rng(TestConstants.SEED)

        FixedPaths.genEgoPath(self.environment)

        self.nSrc_Adversary5: int = self.environment.fromPairToVertex(ChessBoardPositionPair(18,2))
        self.nDest_Adversary5: int = self.environment.fromPairToVertex(ChessBoardPositionPair(0,17))
    
    #This test just find a shortest path to see that CE works ok
    def sanityTestCase_forMatt(self):
        print("TestCase Begin")
        N: int = int(TestCase_Adv5Only_accel.C * self.n * self.m)
        

        # INITIALIZE VANILLA CE AND DISTRIBUTIONS**************************
        cE_vanilla = CE_Manager(TestCase_Adv5Only_accel.C, self.rand, self.n, self.m, N, self.environment, self.bAllowStutter, self.eNEW_CODE, self.rho_quantile_idx, True)

        rvDistribution_vanilla = None
        scoreObject5_HybridDistribution_VanillaPath = Adversary5Score_HybridDistrib_VanillaPath(self.environment, self.nDest_Adversary5)

        rvDistribution_vanilla = HybridRVDistribution(self.nSrc_Adversary5, self.nDest_Adversary5, self.bAllowStutter, scoreObject5_HybridDistribution_VanillaPath, "GraphPath_Adversary5_HybridDistrib", TYPE_OF_RV.ACCEL_RV, cE_vanilla)

        cE_vanilla.setMyRVDistribution(rvDistribution_vanilla)
        # --END-- INITIALIZE VANILLA CE AND DISTRIBUTIONS**************************

        # INITIALIZE PERTURBED CE AND DISTRIBUTIONS**************************
        cE_perturbation = CE_Manager(TestCase_Adv5Only_accel.C, self.rand, self.n, self.m, N, self.environment, self.bAllowStutter, self.eNEW_CODE, self.rho_quantile_idx, False)

        rvDistribution_perturbation = None
        scoreObject5_HybridDistribution_PerturbationPath = Adversary5Score_HybridDistrib_PerturbationPath(self.environment, self.nDest_Adversary5)

        rvDistribution_perturbation = HybridRVDistribution(self.nSrc_Adversary5, self.nDest_Adversary5, self.bAllowStutter, scoreObject5_HybridDistribution_PerturbationPath, "GraphPath_Adversary5_HybridDistrib", TYPE_OF_RV.ACCEL_RV, cE_perturbation)

        cE_perturbation.setMyRVDistribution(rvDistribution_perturbation)
        # --END-- INITIALIZE PERTURBED CE AND DISTRIBUTIONS**************************

        #now make sure the distributions know about each other
        scoreObject5_HybridDistribution_PerturbationPath.setVanillaDistribution(rvDistribution_vanilla)
        scoreObject5_HybridDistribution_VanillaPath.setPerturbedDistribution(rvDistribution_perturbation)

        _N: int = N
        bestScoredGraphPaths_vanilla = []
        last_bestScoredGraphPath_vanilla = None
        bestScoredGraphPaths_perturbation = []
        last_bestScoredGraphPath_perturbation = None

        for nDataSetIndex in range(TestCase_Adv5Only_accel.DATA_SET_SIZE):
            t: int = 0
            for nRound in range(1):
                
                while_cond_array: List[bool] = [True] * TestCase_Adv5Only_accel.NO_OF_PATHS
                gammas = self.initGammas(nRound, rvDistribution_vanilla, rvDistribution_perturbation)
                while_cond = True
                while(while_cond):
                    if(t == 0): print("Started shortestPath...")

                    #********************* shortestPath() ***********************
                    _gamma_vanilla = rvDistribution_vanilla.gamma(-1,self.rho_quantile_idx, _N, t)
                    _gamma_vanilla = self.addToGammas(gammas, _gamma_vanilla, 0)
                    _gamma_perturbation = rvDistribution_perturbation.gamma(-1, self.rho_quantile_idx, _N, t)
                    _gamma_perturbation = self.addToGammas(gammas, _gamma_perturbation, 1)
                    rvDistribution_vanilla.smoothlyUpdateDistribution(TestConstants.ALPHA)
                    t+=1
                    while_cond = False
                #*********************END WHILE
            #*********************END FOR(nRound)
        #*********************END FOR(nDataSetIndex)




    def addToGammas(self, gammas, gamma: float, index: int) -> float:
        SCALE = 100000
        _gamma = gamma
        if(_gamma < 0): #truncate to 5 points once it satisfies goal (_gamma < 0)
            _gamma = round(_gamma, 5)
        gammas[index].add(_gamma)
        return _gamma
    
    def initGammas(self, nRound, rvDistribution_vanilla, rvDistribution_perturbation):
        gammas = [None] * TestCase_Adv5Only_accel.NO_OF_PATHS
        for i in range(TestCase_Adv5Only_accel.NO_OF_PATHS):
            if(nRound == 0):
                rvDistribution_vanilla.initDistribution()
                rvDistribution_perturbation.initDistribution()
            gammas[i] = Gammas()
        return gammas
    
    def getC(self) -> int:
        return TestCase_Adv5Only_accel.C
    
    @staticmethod
    def test_class():
        test = TestCase_Adv5Only_accel()
        test.sanityTestCase_forMatt()

TestCase_Adv5Only_accel.test_class()
