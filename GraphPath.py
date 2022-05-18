#!/usr/bin/env python
from typing import List
from PathPoint import PathPoint
from TYPE_OF_RV import TYPE_OF_RV

class GraphPath:
    #_path: List[PathPoint] = [] #list of pairs <time,index> of graph nodes (0..52 for TSP, 0..20x20-1 for chessboard, 0..numObservableNodes-1 for CrossEntropyBNObservations)
    #_bIsGoodPath: bool #false only for ChessBoard path that doesn't reach destination
    
    #used for debug only
    _static_ID: int = 0
    #_sHashID: str #a hash code that is valid only after path is fully set (all "append"'s are done)
    #uniquePathID: int #while sHashID can be shared when a path is regenerated over and over again, unique ID is generated once - better for debug
    #eTYPE_OF_RV: TYPE_OF_RV
    #environment: Environment
    
    #GraphPath(TYPE_OF_RV eTYPE_OF_RV, Environment environment)
    def __init__ (self, eTYPE_OF_RV: TYPE_OF_RV, environment):
        self._path: List[PathPoint] = []
        self._bIsGoodPath = True #false only for ChessBoard path that doesn't reach destination
        self._sHashID = "" #i.e., unset
        self.eTYPE_OF_RV = eTYPE_OF_RV
        self.environment = environment
        GraphPath._static_ID+=1
        self.uniquePathID = GraphPath._static_ID
    
    #GraphPath(int len, TYPE_OF_RV eTYPE_OF_RV, Environment environment)
    #**Not implementing at this time, just adds length of path

    #for debug, or for setting fixed paths, like Ego and Adversary#1
	#Note: speed setting is for EGO, Adversary#1 will be overwrite this settings
	#GraphPath(String  str, Environment environment, TYPE_OF_RV eTYPE_OF_RV)
    