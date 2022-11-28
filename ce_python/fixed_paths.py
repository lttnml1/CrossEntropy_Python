#!/usr/bin/env python
#NATIVE PYTHON IMPORTS

#INSTALLED PACKAGE IMPORTS

#IMPORTS FROM THIS PACKAGE
from ce_python.graph_path_ego import GraphPath_Ego
from ce_python.type_of_rv import TYPE_OF_RV
from ce_python.point_pair import PointPair

class FixedPaths:
    egoPath: GraphPath_Ego = None

    

    @staticmethod
    def genEgoPath(environment) -> None:
        path_str = "(6,17)" + \
            "(7,17)" + \
			"(7,16)" + \
			"(7,15)" + \
			"(7,14)" + \
			"(7,13)" + \
			"(7,12)" + \
			"(6,11)" + \
			"(5,10)" + \
			"(4,9)" + \
			"(3,8)" + \
			"(3,7)" + \
			"(2,6)" + \
			"(2,5)" + \
			"(1,4)" + \
			"(0,3)" + \
			"(0,2)" + \
			"(0,1)" 
        path_str2 = \
            "(0,12)" + \
            "(1,12)" + \
			"(2,12)" + \
			"(3,12)" + \
			"(4,12)" + \
			"(5,12)" + \
			"(6,12)" + \
			"(7,12)" + \
			"(8,12)" + \
			"(9,12)" + \
			"(10,12)" + \
			"(11,12)" + \
			"(12,12)" + \
			"(13,12)" + \
			"(14,12)" + \
			"(15,12)" + \
			"(16,12)" + \
			"(17,12)" + \
			"(18,12)"
        FixedPaths.egoPath = GraphPath_Ego.from_fixed_path(path_str, TYPE_OF_RV.SPEED_RV, environment)
    
    @staticmethod
    def findMeetPoints(adversary1_seq, adversary2_seq):
        if(adversary1_seq is None): return None
        if(adversary2_seq is None): return None
        ht = {}
        for pathPoint in adversary1_seq.getPathPoints():
            pt = pathPoint.pt
            ht[pt] = pathPoint

        for adv2PathPoint in adversary1_seq.getPathPoints():
            pt = adv2PathPoint.pt
            #check and see if pt exists in ht
            if pt in ht: #if the key exists in the dictionary
                return PointPair(ht.get(pt), adv2PathPoint)
        return None

    