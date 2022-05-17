#!/usr/bin/env python
from msilib.schema import Environment
from typing import List
from PathPoint import PathPoint
from TYPE_OF_RV import TYPE_OF_RV

class GraphPath:
    _path: List[PathPoint] = [] #list of pairs <time,index> of graph nodes (0..52 for TSP, 0..20x20-1 for chessboard, 0..numObservableNodes-1 for CrossEntropyBNObservations)
    _bIsGoodPath: bool #false only for ChessBoard path that doesn't reach destination
    
    #used for debug only
    _static_ID: int = 0
    _sHashID: str #a hash code that is valid only after path is fully set (all "append"'s are done)
    uniquePathID: int #while sHashID can be shared when a path is regenerated over and over again, unique ID is generated once - better for debug
    eTYPE_OF_RV: TYPE_OF_RV
    environment: Environment
    
    def __init__ (self, *args):
        if isinstance(args[0],TYPE_OF_RV):
            #then first constructor
            #GraphPath(TYPE_OF_RV eTYPE_OF_RV, Environment environment)
        elif isinstance(args[0],int):
            #then second constructor
            #GraphPath(int len, TYPE_OF_RV eTYPE_OF_RV, Environment environment)
        elif isinstance(args[0],str):
            #then third constructor
            #GraphPath(String  str, Environment environment, TYPE_OF_RV eTYPE_OF_RV)
        else:
            print("**No valid constructor for GraphPath object**\n")
