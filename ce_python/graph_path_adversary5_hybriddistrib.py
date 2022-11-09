#!/usr/bin/env python

#NATIVE PYTHON IMPORTS

#INSTALLED PACKAGE IMPORTS

#IMPORTS FROM THIS PACKAGE
from ce_python.graph_path import GraphPath
from ce_python.test_constants import TestConstants

class GraphPath_Adversary5_HybridDistrib(GraphPath):
    def __init__(self, eTYPE_OF_RV, environment, myDistribution = None):
        super().__init__(eTYPE_OF_RV, environment, myDistribution)
        self.pertPath_truncatedPath = []
    
    def getAdversaryCategoricalFixedSpeedAt(self, nIndex: int) -> float:
        if(TestConstants.FORCE_INITIAL_ADVERSARY2_SPEED and nIndex == 0):
            return TestConstants.INITIAL_ADVERSARY2_SPEED
        return TestConstants.ADVERSARY2_FIXED_SPEED_1a
    def getBasePath(self) -> object:
        raise Exception("getBasePath() should not be called for GraphPath_Adversary5_HybridDistrib (only called for Normal Distrib GraphPaths that are based on a FixedPath (Adv#1) or previously calculated Categorical (Adv#3)")
    
    def getTruncatedPath(self):
        return self.pertPath_truncatedPath
    def setTruncatedPath(self, truncatedPath):
        self.pertPath_truncatedPath = truncatedPath