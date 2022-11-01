#!/usr/bin/env python

from __future__ import annotations

from ast import Str
from typing import List

from ce_python.PathPoint import PathPoint
from ce_python.TYPE_OF_RV import TYPE_OF_RV
from ce_python.ChessBoardPositionPair import ChessBoardPositionPair

import re

class GraphPath:
    #_path: List[PathPoint] = [] #list of pairs <time,index> of graph nodes (0..52 for TSP, 0..20x20-1 for chessboard, 0..numObservableNodes-1 for CrossEntropyBNObservations)
    #_bIsGoodPath: bool #false only for ChessBoard path that doesn't reach destination
    
    #used for debug only
    static_ID: int = 0
    #_sHashID: str #a hash code that is valid only after path is fully set (all "append"'s are done)
    #uniquePathID: int #while sHashID can be shared when a path is regenerated over and over again, unique ID is generated once - better for debug
    #eTYPE_OF_RV: TYPE_OF_RV
    #environment: Environment
    
    #GraphPath(TYPE_OF_RV eTYPE_OF_RV, Environment environment)
    def __init__ (self, eTYPE_OF_RV: TYPE_OF_RV, environment, myRvDistribution = None):
        self.path: List[PathPoint] = []
        self.bIsGoodPath = True #false only for ChessBoard path that doesn't reach destination
        self.sHashID = "" #i.e., unset
        self.eTYPE_OF_RV = eTYPE_OF_RV
        self.environment = environment
        self.myRvDistribution = myRvDistribution
        GraphPath.static_ID+=1
        self.uniquePathID = GraphPath.static_ID

    #for debug, or for setting fixed paths, like Ego and Adversary#1
	#Note: speed setting is for EGO, Adversary#1 will be overwrite this settings
	#GraphPath(String  str, Environment environment, TYPE_OF_RV eTYPE_OF_RV)
    @classmethod
    def from_fixed_path(cls, str: Str, eTYPE_OF_RV: TYPE_OF_RV, environment) -> GraphPath:
        GraphPath = cls(eTYPE_OF_RV,environment)
        dTime: float = 0
        nIndex: int = 0       
        parts = re.split('[\\(||\\)]',str)
        for part in parts:
            sPart = part.strip()
            if(sPart==("")): continue
            subparts = sPart.split(",")
            nPart0: int = int(subparts[0])
            nPart1: int = int(subparts[1])
            n: int = environment.fromPairToVertex(ChessBoardPositionPair(nPart0,nPart1))

            dSpeed: float = float(nIndex)%3 + 1  
            #speed is 1,2,3,1,2,3. NOTE! this speed setting is for EGO, Adversary#1 will be overwrite this settings
            
            dTime += 1/dSpeed


        return GraphPath
    
e = TYPE_OF_RV.ACCEL_RV
env = None
gp = GraphPath.from_fixed_path("(1,2)(3,4)(4,5)(6,7)",e,env)