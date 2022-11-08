#!/usr/bin/env python
#NATIVE PYTHON IMPORTS

#INSTALLED PACKAGE IMPORTS

#IMPORTS FROM THIS PACKAGE
from ce_python.graph_path import GraphPath

class GraphPath_Ego(GraphPath):
    def __init__(self, eTYPE_OF_RV, environment):
        super().__init__(eTYPE_OF_RV, environment)
    
    @classmethod
    def from_fixed_path(cls, str, eTYPE_OF_RV, environment):
        return super().from_fixed_path(str, eTYPE_OF_RV,environment)
    
    def getBasePath(self):
        raise Exception("getBasePath() should not be called for GraphPath_Ego (only called for NormalDistrib GraphPaths that are based on a FixedPath (Adv#1) or previously calculated Categorical (Adv#3)")
