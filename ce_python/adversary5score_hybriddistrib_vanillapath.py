#!/usr/bin/env python

#NATIVE PYTHON IMPORTS

#INSTALLED PACKAGE IMPORTS

#IMPORTS FROM THIS PACKAGE
from ce_python.abstract_adversary5score_hybriddistrib import Abstract_Adversary5Score_HybridDistrib
from ce_python.fixed_paths import FixedPaths
from ce_python.bad_score_levels import BadScoreLevels

"""
//See "DMV-NL Strategy"-NOTE
//Hybrid Adversary  score for DMV  (Hybrid = Adversary3's Categorical and  Adversary3's Normal score combined) w/ DMV-NL strategy listed in "DMV-NL Strategy"-NOTE
// The particular DMV-NL incident dealt with here: "caused by wrong lane change suggestion"
"""
class Adversary5Score_HybridDistrib_VanillaPath(Abstract_Adversary5Score_HybridDistrib): #only extends it to get access to super().specificScore()
    def __init__(self, environment, nDest):
        super().__init__(environment, nDest)
        self.rvDistributions_perturbed = None
    
    def setPerturbedDistribution(self, rvDistributions_perturbed):
        self.rvDistributions_perturbed = rvDistributions_perturbed
    
    def specificScore(self, graphPath: object, t: int) -> float:
        dRetDistanceFromPerturbed = 0
        egoToAdv5TimeDiffPack = self.getAgentToAdvTimeDiffPack(FixedPaths.egoPath, graphPath)
        egoToAdv5TimeDiff = egoToAdv5TimeDiffPack.dTime
        ptX = egoToAdv5TimeDiffPack.ptX
        
        dRetDistanceFromPerturbed = 1000 #just penalty for being round 0 and not having this.rvDistributions_vanilla yet
        if(t>0):
            bestPerturbedScoredGraphPath = self.rvDistributions_perturbed.getScoredGraphPath(0).graphPath
            dDistance = self.calcPathToPathDistance(bestPerturbedScoredGraphPath, graphPath, True) #distance between this and vanilla -- smaller is better, and the intersection point
            if(dDistance == 0):
                dRetDistanceFromPerturbed = BadScoreLevels.BAD_PATH #dDistance=0  happens when bestVanillaScoredGraphPath and graphPath are same path - that is a violation of a rigid constraint for the paired <vanilla/perturbation> approach (the two HAVE to be different, otherwise how would one be good while the other is bad?)
            else:
                dRetDistanceFromPerturbed = -1/dDistance #// smaller is better; have it negative too. 
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

        #Vanilla path --> no accident
        egoToAdv5TimeDiff = self.getAgentToAdvTimeDiffPack(FixedPaths.egoPath,graphPath).dTime
        if(egoToAdv5TimeDiff < 1): #NO accident! --> if there is, then its a rigid constraint failure
            egoToAdv5TimeDiff = 1000*egoToAdv5TimeDiff #make it very high positive so it becomes rigid constraint
        else:
            egoToAdv5TimeDiff = 0 #***IMPORTANT!!*** don't punish (constraint satisfied) --> let optimization constraints kick in as usual
        delta = 0
        """
        //DORON-ASSUMPTION-NOTE: I added this CE objective to the permutation only,
        // Q. perhaps I should have added it to the Vanilla cost function too? 
        //But remember that path metrics used for learning a data-set with high variance are based on truncated path (see truncatePathAfterPoint() calls in getCategoricalPathMeasure() and getNormalPathMeasure())
        //			where truncation is from point of "accident", which only perturbation path knows
        """
        return self.importanceWeigh(dRetCategorical, dRetNormal, dRetDistanceFromPerturbed, delta, egoToAdv5TimeDiff)

        