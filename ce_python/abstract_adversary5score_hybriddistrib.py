#!/usr/bin/env python

#NATIVE PYTHON IMPORTS
from enum import Enum, auto
from abc import ABC, abstractmethod
import math

#INSTALLED PACKAGE IMPORTS

#IMPORTS FROM THIS PACKAGE
from ce_python.abstract_score import AbstractScore
from ce_python.bad_score_levels import BadScoreLevels
from ce_python.test_constants import TestConstants
from ce_python.graph_path_adversary5_hybriddistrib import GraphPath_Adversary5_HybridDistrib

"""
//See "DMV-NL Strategy"-NOTE
//Hybrid Adversary  score for DMV  (Hybrid = Adversary3's Categorical and  Adversary3's Normal score combined) w/ DMV-NL strategy listed in "DMV-NL Strategy"-NOTE
// The particular DMV-NL incident dealt with here: "caused by wrong lane change suggestion"
"""

#a return value from getAgentToAdvTimeDiffPack
class TimePtPack:
    def __init__(self, dTime, ptX):
        self.dTime = dTime
        self.ptX = ptX

class NL_DISTANCE_DESCRIPTOR(Enum):
    LANE_CHANGE = auto()
    LANE_CHANGE_WEIGHTED = auto() #// a weighted version - where distance between pert.-path and vanilla-path is weighted based on distance from "accident" -- philosophy: pert.-path=vanilla almost all the time, except for a "slight" perturbation closer to the END

class Abstract_Adversary5Score_HybridDistrib(AbstractScore, ABC): #only extends it so to get access to super.specificScore()

    
    eNL_DISTANCE_DESCRIPTOR = NL_DISTANCE_DESCRIPTOR.LANE_CHANGE_WEIGHTED

    SIGMOID_SATURATION_LEVEL = 5
    
    def __init__(self, environment, nDest):
        #no need to call super().__init__() here - base class has no constructor
        self.environment = environment
        self.nDest = nDest
    """
    //Adversary #5's score for HybridRVDistribution objective where Vanilla path wants to reach target while crossing ego's path within more than 1 sec from Ego
	//while small "lane change" perturbation induces accident with ego
    """
    @abstractmethod
    def specificScore(self, graphPath: object, t: int) -> float:
        pass

    def categoricalDistribScorePart(self, graphPath, dest) -> float:
        dRet = 0
        #//************** Doron artificially imposed agent-specific (intra-agent) constraints: optimize for shortest path and have path prefer points whose sum x+y%3!=0
        dPenalty = -1/float(graphPath.len()) #smaller is better but also negative because this is not a rigid constraint
        dRet += dPenalty
        #//***** End agent-specific (intra-agent) constraints

        #//***** Begin inter-agent constraints
        
        #//***** End Inter-agent constraints
        return dRet
    
    def normalDistribScorePart(self, graphPath, dest) -> float:
        dRet = 0
        #//************** Doron artificially imposed agent-specific (intra-agent) constraints:
        """
        // 1. initial speed must be INITIAL_ADVERSARY_SPEED -- this is implemented in SpeedSequence.putPointAt()?
		// 2. Speed is always positive (otherwise, on one hand some cell has speed 0 or less, on the other hand the path does move on to the next cell, so apparently speed > 0)
		//	  This is implemented in AbstractScore
		// 3. No negative time (this can potentially happen when calculating time from distance and accel)
		//	  This is implemented in AbstractScore
        """
        if(graphPath.get(graphPath.len()-1).pt != dest):
            dRet += BadScoreLevels.SPECIFIC_LEVEL_1
            #same penalty here as for the other adversary
        # #1
        if(TestConstants.FORCE_INITIAL_ADVERSARY1_SPEED):
            initialSpeed = graphPath.getSpeedPointAt(0).speed
            dRet += math.abs(initialSpeed - TestConstants.INITIAL_ADVERSARY1_SPEED) #the more different it is from 0, the worse it is
        
        #//***** End agent-specific (intra-agent) constraints

        #//***** Begin inter-agent constraints
        
        #//***** End Inter-agent constraints
        return dRet
    
    """
    // calculate diff time between the arrival of agent-1 (usually ego) at point ptX and adversary  arrivale at ptX, where ptX is the intersection between the two paths
	// This also implements the rigid constraint that # of intersections with ego is no more than one
    """
    def getAgentToAdvTimeDiffPack(self, agentPath, advGraphPath) -> TimePtPack:
        advPathList = advGraphPath.path
        nPtAdv_intersect = 0
        nPtEgo_intersect = 0
        nNumIntersections = 0
        ptX_ret = -1 #point of intersection
        #find ptX the (first) point of intersection.  If there is no such point, then ptX = -1
        for nPtAdv in range(len(advPathList)):
            ptAdv = advPathList[nPtAdv].pt
            for nPtEgo in range(agentPath.len()):
                ptEgo = agentPath.getPoint(nPtEgo)
                if(ptEgo == ptAdv): #this is ptX
                    ptX_ret = ptAdv
                    nNumIntersections += 1
                    nPtAdv_intersect = nPtAdv
                    nPtEgo_intersect = nPtEgo
                    if(nNumIntersections > 1):
                        return TimePtPack(len(advPathList) * 500, -2)
        if(nNumIntersections == 0):
            return TimePtPack(len(agentPath)*1000,-1)
        
        #time Adversary reached this point
        __adv = advPathList[nPtAdv_intersect]
        agentPoint = agentPath.get(nPtEgo_intersect)

        return TimePtPack(abs(__adv.time - agentPoint.time), ptX_ret)

    def calcpathToPathDistance(self, perturbedPath, vanillaPath, bIsBestPerturbedPath) -> float:
        perturbedPath.__class__ = GraphPath_Adversary5_HybridDistrib
        # ^^^ Python cannot "cast" so change the name of the class explicitly from superclass: GraphPath to sublcass: GraphPath_Adversary5_HybridDistrib
        truncatedPerturbedPath = perturbedPath.getTruncatedPath()
        if(bIsBestPerturbedPath and truncatedPerturbedPath == None):
            raise Exception("No truncatedPerturbedPath (i.e., no accident with Ego) found for best(!) perturbation path")
        if self.eNL_DISTANCE_DESCRIPTOR == NL_DISTANCE_DESCRIPTOR.LANE_CHANGE:
            return self.calcPathToPathLaneDistance(truncatedPerturbedPath, vanillaPath)
        elif self.eNL_DISTANCE_DESCRIPTOR == NL_DISTANCE_DESCRIPTOR.LANE_CHANGE_WEIGHTED:
            return self.calcPathToPathLaneDistance_weighted(truncatedPerturbedPath, vanillaPath)
        else:
            raise Exception(f"Unrecognized eNL_DISTANCE_DESCRIPTOR {self.eNL_DISTANCE_DESCRIPTOR}")
    
    """
    //@return a distance metric, not qualified as in "shorter is better" - just the distance
    // The distance is between truncated prefix of perturbation-path (truncated until point of "accident") and vanilla-path
    """
    def calcPathToPathLaneDistance(self, truncatedPerturbedPath, vanillaPath):
        return self.calcPTPLD(truncatedPerturbedPath, vanillaPath, False)
    
    """
    // version of calcPathToPathLaneDistance() where distance between pert.-path and vanilla-path is weighted based on distance from "accident"
    //***!! philosophy: pert.-path=vanilla almost all the time, except for a "slight" perturbation closer to the END --> 
    //		weights should make deviations (part. vs vanilla) that are father away from "Accident" cost more, and only as pert. approaches
    // 		its end ("accident") weight go down because that is where we want to allow deviation
    """
    def calcpathToPathLaneDistance_weighted(self, truncatedPerturbedPath, vanillaPath):
        return self.calcPTPLD(truncatedPerturbedPath, vanillaPath, True)
    
    def calcPTPLD(self, truncatedPerturbedPath, vanillaPath, bWeighted: bool) -> float:
        if(truncatedPerturbedPath == None): #no "accident" or ego and this pert.-path was found
            return -1
        dDistance = 0
        dSpeedAccelDiff = 0
        _n = len(truncatedPerturbedPath)
        nCnt = 0
        for nPt in range(_n):
            if(nPt >= vanillaPath.len()): break

            #for shorter path, once end is reached, just take last point
            pt = truncatedPerturbedPath[nPt].pt
            pair = self.environment.fromVertexToPair(pt)
            pt_vanilla = vanillaPath.getPoint(nPt)
            pair_vanilla = self.environment.fromVertexToPair(pt_vanilla)

            dDistance_i = pair.get_i() - pair_vanilla.get_i()
            dDistance_i = dDistance_i*dDistance_i
            dDistance_j = pair.get_j() - pair_vanilla.get_j()
            dDistance_j = dDistance_j*dDistance_j
            _d = math.sqrt(dDistance_i + dDistance_j)
            if(bWeighted): _d = _d * (_n-nPt)
            dDistance += _d

            """
            //Initially I thought of using time rather than speedOrAccel for DELTA, but I believe forcing pert. and vanilla to be close in time is an overkill-
            // rather, suppose pert.-path has small overall acceleration DELTA  the time DELTA might be much larger (than when using time DELTA verbatim) yet one can argue that pert. is a slight perturbation (in accel, as well as position) of vanilla
            // be impacted more than if I 
            """
            _d = truncatedPerturbedPath[nPt].speedOrAccel - vanillaPath[nPt].speedOrAccel
            #DELTA (see comment above)
            if(bWeighted): _d = _d * (_n-nPt)
            dSpeedAccelDiff += _d
            nCnt += 1
        nDenom = nCnt
        if(bWeighted):
            nDenom = (nCnt * (_n + _n-nCnt+1)/2) #sum of weights is _n+(_n+1)+...+(_n-(nCnt-1)) = nCnt * (_n+_n-nCnt+1)/2
        dRetCategorical = dDistance/nDenom
        dRetNormal = dSpeedAccelDiff/nDenom
        return dRetCategorical + dRetNormal
    
    #// normalize x (|x|<1) so that all values like 1/len and Normal distrib cost values are all normalized the same way
    @staticmethod
    def normalize_with_sigmoid(x: float, bXisNegativeSmallerIsBetter: bool) -> float:
        if(bXisNegativeSmallerIsBetter and x>0): return x #don't normalize penalties for violating rigid constraints
        _x = x
        if(bXisNegativeSmallerIsBetter):
            _x = 0-x #now _x is positive, larger is better, so sigmoid will be (0.5,1)
        if(not (_x >= 0)):
            raise Exception("!(_x >= 0) in sigmoid")
        sigmoid = 1/(1+math.pow(math.e,(-1*_x)))
        if(not (sigmoid >= 0.5 and (sigmoid <=1))):
            raise Exception("!(sigmoid > 0.5 and (sigmoid < 1)) in sigmoid")
        if(bXisNegativeSmallerIsBetter): return 0.5-sigmoid #negative and smaller is better
        else: return -1 * sigmoid
    
    """
    //DORON-ASSUMPTION-NOTE:
	// Matt, You can experiment with the four weights and observe their impact. This can be useful for you instead of experimenting in CARLA
    """
    def importanceWeigh(self, dRetCategorical, dRetNormal, dRetDistancePerturbedToVanilla, dataSetcost, rigidConstraintCost) -> float:
        #// Normalize so that you can weigh the parts by importance; right now they are equally important
        if(dRetCategorical < -1):
            raise Exception("dRetCategorical < -1") #being -1/path.len it should be a negative fraction
        dRetCategorical = Abstract_Adversary5Score_HybridDistrib.normalize_with_sigmoid(dRetCategorical, True)
        if(dRetNormal < -1):
            raise Exception("dRetNormal < -1") #in this example, dRetNormal is 0, but key it <-1 or worst case -1*SATURATION
        dRetNormal = Abstract_Adversary5Score_HybridDistrib.normalize_with_sigmoid(dRetNormal, True)
        dRetDistancePerturbedToVanilla = Abstract_Adversary5Score_HybridDistrib.normalize_with_sigmoid(dRetDistancePerturbedToVanilla, True)
        if(dataSetcost < -1):
            raise Exception("dataSetcost < -1")
        dataSetcost = Abstract_Adversary5Score_HybridDistrib.normalize_with_sigmoid(dataSetcost, True)
        #no need to normalize: if postive, then it's a penalty -- keep it as is; or else it is 0
        if(rigidConstraintCost < 0):
            raise Exception("rigidConstraintCost < 0")
        dDenom = 1
        
        """
        // Notes:
        // * Let x=rigidConstraintCost + dRetNormal + dRetDistancePerturbedToVanilla + dataSetcost + rigidConstraintCost
        // * when rigidConstraintCost>0 it will be much larger than the negative weight of all other parts of x, resulting in large positive x, which is "smaller is better" - dividing by |x| will make the result "larger is better", i.e, wrong
        // * when rigidConstraintCost=0 x is negative; while being "smaller is better", |x| is "larger is better",  dividing by it will make the outcome "smaller is better" 
        //if (rigidConstraintCost == 0) dDenom = Math.abs(rigidConstraintCost + dRetNormal + dRetDistancePerturbedToVanilla + dataSetcost);
        // NOTE: the use of Sigmoid does not amount to Normalization, but is helps weighing by knowing that all values are [-1,0]
        """
        return (3*dRetCategorical + 3*dRetNormal + 2*dRetDistancePerturbedToVanilla + 1*dataSetcost + rigidConstraintCost)/dDenom #rigidConstraintCost is rigid (i.e., 0 or high, no point in weighting it)
    
