#!/usr/bin/env python

#NATIVE PYTHON IMPORTS
import math

#INSTALLED PACKAGE IMPORTS

#IMPORTS FROM THIS PACKAGE
from ce_python.abstract_adversary5score_hybriddistrib import Abstract_Adversary5Score_HybridDistrib
from ce_python.fixed_paths import FixedPaths
from ce_python.graph_path_adversary5_hybriddistrib import GraphPath_Adversary5_HybridDistrib
from ce_python.bad_score_levels import BadScoreLevels
#from ce_python.testcase_adv5only_accel import TestCase_Adv5Only_accel
#^^^^^moved this import down to specificScore because it was causing circular dependency with TestCase_Adv5Only_accel

from ce_python.gaussian_parameters import GaussianParameters

"""
//See "DMV-NL Strategy"-NOTE
//Hybrid Adversary  score for DMV  (Hybrid = Adversary3's Categorical and  Adversary3's Normal score combined) w/ DMV-NL strategy listed in "DMV-NL Strategy"-NOTE
// The particular DMV-NL incident dealt with here: "caused by wrong lane change suggestion"
"""
class Adversary5Score_HybridDistrib_PerturbationPath(Abstract_Adversary5Score_HybridDistrib): #only extends it to get access to super().specificScore()
    def __init__(self, environment, nDest):
        super().__init__(environment,nDest)
        self.rvDistributions_vanilla = None

    def setVanillaDistribution(self, rvDistributions_vanilla):
        self.rvDistributions_vanilla = rvDistributions_vanilla
    
    """
    //Adversary #5's score for HybridRVDistribution objective where Vanilla path wants to reach target while crossing ego's path within more than 1 sec from Ego
	//	while small "lane change" perturbation induces accident with ego
    """
    def specificScore(self, graphPath: object, t: int) -> float:
        from ce_python.testcase_adv5only_accel import TestCase_Adv5Only_accel
        egoToAdv5TimeDiffPack = self.getAgentToAdvTimeDiffPack(FixedPaths.egoPath, graphPath) #time diff of point it intersects ego's path w.r.t. when ego gets there
        egoToAdv5TimeDiff = egoToAdv5TimeDiffPack.dTime
        ptX = egoToAdv5TimeDiffPack.ptX
        truncatedPath = None
        #calc truncated Perturbation path that ends in "accident" point
        #this facilitated the generation of a high-varince data-set that is based only on the part of the perturbation path UNITL the "accident"
        if(ptX >= 0):
            truncatedPath = graphPath.truncatePathAfterPoint(ptX)
            graphPath.__class__ = GraphPath_Adversary5_HybridDistrib
            graphPath.setTruncatedPath(truncatedPath) #remember the truncated path prefix
        bestVanillaScoredGraphPath = None
        dRetDistanceFromVanilla = 1000 #just penalty for being round 0 and not having this.rvDistributions_vanilla yet
        if(t>0):
            bestVanillaScoredGraphPath = self.rvDistributions_vanilla.getScoredGraphPath(0).graphPath
            dDistance = self.calcPathToPathDistance(graphPath, bestVanillaScoredGraphPath, False) #distance between this and vanilla -- smaller is better, and the intersection point
            if(dDistance <= 0):
                dRetDistanceFromVanilla = BadScoreLevels.BAD_PATH #dDistance=0  happens when bestVanillaScoredGraphPath and graphPath are same path - that is a violation of a rigid constraint for the paired <vanilla/perturbation> approach (the two HAVE to be different, otherwise how would one be good while the other is bad?)
            else:
                dRetDistanceFromVanilla = -1/dDistance #// smaller is better; have it negative too. 
    			#//dRetDistanceFromVanilla = dRetDistanceFromVanilla/SHORTEST_DIST_PREFERENCE_WEIGHT; // make much smaller so that shortest path is more important than dist from vanilla
        dRetCategorical = 0
        dRetNormal = 0

        #Categorical Part************
        dRetCategorical += self.categoricalDistribScorePart(graphPath, self.nDest)
        #END Categorical Part********
        #****************************
        #Normal Part*****************
        dRetNormal += self.normalDistribScorePart(graphPath, self.nDest)
        #END Normal Part*************

        #*** Experimenting with code for finding path that maximized distance from previously chosen paths
        delta = 0
        if(ptX >= 0): #if perturbation path does not have an "accident" then it should not be used here (it violates rigid constraint anyway)
            #//DORON-ASSUMPTION-NOTE: I added this CE objective to the perturbation only, perhaps I should have added it to the Vanilla cost function too.
            nComponents = 0
            if(TestCase_Adv5Only_accel.dVarNormal != 0):
                dNormalPathMeasure = graphPath.getNormalPathMeasure(truncatedPath)
                cdf_in_range = 0
                lower_bound = TestCase_Adv5Only_accel.dAvgNormal - TestCase_Adv5Only_accel.dAvgNormal_minus_2Sigma #mu-2*sigma
                if(dNormalPathMeasure > lower_bound and dNormalPathMeasure < TestCase_Adv5Only_accel.dAvgNormal):
                    cdf_in_range = GaussianParameters.cdf_in_range(lower_bound, dNormalPathMeasure,TestCase_Adv5Only_accel.dAvgNormal, math.sqrt(TestCase_Adv5Only_accel.dVarNormal))
                    #reward closeness to lower_bound, smaller is better
                    if(cdf_in_range <= 0):#smaller-is-better and negative
                        delta += 0
                    else:
                        delta += cdf_in_range-1
                    nComponents += 1
            if(TestCase_Adv5Only_accel.dVarCategorical != 0):
                dCategoricalPathMeasure = graphPath.getCategoricalPathMeasure(truncatedPath)
                cdf_in_range = 0
                lower_bound = TestCase_Adv5Only_accel.dAvgCategorical - TestCase_Adv5Only_accel.dAvgCategorical_minus_2Sigma #mu-2*sigma
                if(dCategoricalPathMeasure > lower_bound and dCategoricalPathMeasure < TestCase_Adv5Only_accel.dAvgCategorical):
                    cdf_in_range = GaussianParameters.cdf_in_range(lower_bound, dCategoricalPathMeasure, TestCase_Adv5Only_accel.dAvgCategorical, math.sqrt(TestCase_Adv5Only_accel.dVarCategorical))
                    #reward cloness to lower_bound, smaller is better
                    if(cdf_in_range <= 0):#smaller-is-better and negative
                        delta += 0
                    else:
                        delta += cdf_in_range-1
                    nComponents += 1
            if(nComponents>0): delta = delta/nComponents #normalize the sume of the two components so it is still in [-1,0]
            delta = GaussianParameters.round(delta,3)
            """
            //DORON-ASSUMPTION-NOTE: delta can be overwhelming or underwhelming w.r.t dRetCategorical and/or dRetNormal - its an art to get the right balance. Example of overwhelming delta - it will make CE find a path that is clearly not even close to being  shortest path
            """
        #Perturbed path --> accident
        if(egoToAdv5TimeDiff >= 1): #accident! --> if there's no accident, then its a rigid constraint failure
            egoToAdv5TimeDiff = 1000*egoToAdv5TimeDiff #make it very high positive so it becomes rigid constraint
        else:
            egoToAdv5TimeDiff = 0 #***IMPORTANT!!*** don't punish (constraint satisfied) --> let optimization constraints kick in as usual

        return self.importanceWeigh(dRetCategorical, dRetNormal, dRetDistanceFromVanilla, delta, egoToAdv5TimeDiff)
