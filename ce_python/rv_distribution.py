#!/usr/bin/env python
#NATIVE PYTHON IMPORTS
from abc import ABC, abstractmethod
import math

#INSTALLED PACKAGE IMPORTS
import numpy as np

#IMPORTS FROM THIS PACKAGE
from ce_python.code_efficiencies import CODE_EFFICIENCIES
from ce_python.scored_graph_path import ScoredGraphPath
from ce_python.test_constants import TestConstants
from ce_python.graph_path_adversary5_hybriddistrib import GraphPath_Adversary5_HybridDistrib

class RVDistribution(ABC):

    def __init__(self, scoreObject, clazz: str, my_CE_Manager, eTYPE_OF_RV):
        self.scoreObject = scoreObject
        self.clazz = clazz
        self.my_CE_Manager = my_CE_Manager
        self.rho_quantile_idx = my_CE_Manager.rho_quantile_idx
        self.rand = my_CE_Manager.rand
        self.eTYPE_OF_RV = eTYPE_OF_RV
        self.eNEW_CODE = my_CE_Manager.eNEW_CODE
        self.scored_graphpath_samples = []
        self.rand = my_CE_Manager.rand
    @abstractmethod
    def initDistribution(self):
        pass
    @abstractmethod
    def smoothlyUpdateDistribution(self, alpha: float, scoredSampleParts):
        pass
    @abstractmethod
    def generateGraphPath(self, nAgent: int):
        pass
    @abstractmethod
    def getDest(self) -> int:
        pass

    def score(self, graphPath, t: int):
        return self.scoreObject.score(graphPath, t)
    def getScoredGraphPath(self, index: int):
        return self.scored_graphpath_samples[index]
    
    def generateAdversaryObject(self, args = None):
        if(args):
            raise NotImplementedError("generateAdversaryObject with arguments not implemented")
        return GraphPath_Adversary5_HybridDistrib(self.eTYPE_OF_RV,self.my_CE_Manager.environment, self.my_CE_Manager.myRVDistribution)
    
    """
    //Overriden by Ecponentia;RVDistribution
    //Gamma is the  S(a path) = score of a path = cost of path at quantile rho 
    // Same code exists in highScoredPaths()... 
    // the code here is used for: (1) calling calculateScoredConfigurationSamples() (2) termination condition
    """
    def gamma(self, nAgent: int, gammaIndex: int, _N:int, t: int):
        # Returns gamma (rho-quantile score)
        self.generateScoredGraphPathSamples(nAgent, gammaIndex, _N, t)
        return self.scored_graphpath_samples[gammaIndex].getScore()
    
    def doesBestPathEndAtDestination(self) -> bool:
        b: bool = True
        nDest: int = self.getDest()
        bestPath = self.getScoredGraphPath(0).graphPath
        b = b and (bestPath.get(bestPath.len()-1).pt==nDest)
        return b
    
    def isBestPathScoreNegative(self) -> bool:
        b: bool = True
        b = b and self.getScoredGraphPath(0).getScore() < 0
        return b
    
    def areConstraintsSatisfied(self) -> bool:
        b: bool = self.doesBestPathEndAtDestination()
        return b and self.isBestPathScoreNegative()
    
    # return the score at position rho_quantile_idx of sorted scored_graphpath_samples
    def generateScoredGraphPathSamples(self, nAgent: int, gammaIndex: int, _N: int, t: int) -> None:
        self.scored_graphpath_samples = self.generateScoredGraphPathSamplesArray(nAgent, _N, t)
        # sanity test: verify sort order ([lowest, --, highest])
        for i in range(1,len(self.scored_graphpath_samples)):
            scoredPath_im1 = self.scored_graphpath_samples[i-1]
            scoredPath_i = self.scored_graphpath_samples[i]
            if(scoredPath_im1.getScore() > scoredPath_i.getScore()):
                raise Exception('self.scored_graphpath_samples should be sorted in ascending order')

    def generateScoredGraphPathSamplesArray (self, nAgent: int, _N: int, t: int):
        retArray = None
        if(self.eNEW_CODE == CODE_EFFICIENCIES.OLD_CODE):
            retArray = self.generateScoredGraphPathSamples_OLD_CODE(nAgent, _N, t)
        elif(self.eNEW_CODE == CODE_EFFICIENCIES.NEW_CODE_SLOW):
            retArray = self.generateScoredGraphPathSamples_NEW_CODE_SLOW(nAgent, _N, t)
        elif(self.eNEW_CODE == CODE_EFFICIENCIES.NEW_CODE_FAST):
            retArray = self.generateScoredGraphPathSamples_NEW_CODE_FAST(nAgent, _N, t)
        elif(self.eNEW_CODE == CODE_EFFICIENCIES.CARLA_CODE):
            retArray = self.generateScoredGraphPathSamples_CARLA(nAgent, _N, t)
        else:
            raise Exception("Unexpected case in generateScoredGraphPathSamples()")
        return retArray
    
    def generateScoredGraphPathSamples_CARLA(self, nAgent: int, _N: int, t: int):
        raise NotImplementedError("generateScoredGraphPathSamples_CARLA not implemented")
    def generateScoredGraphPathSamples_NEW_CODE_SLOW(self, nAgent: int, _N: int, t: int):
        raise NotImplementedError("generateScoredGraphPathSamples_NEW_CODE_SLOW not implemented")
    def generateScoredGraphPathSamples_OLD_CODE(self, nAgent: int, _N: int, t: int):
        raise NotImplementedError("generateScoredGraphPathSamples_OLD_CODE not implemented")
    def generateScoredGraphPathSamples_NEW_CODE_FAST(self, nAgent: int, _N: int, t: int):
        _retArray = [None] * _N #creates an empty list of size _N, all of ScoredGraphPath types
        nSizeofArray: int = self.rho_quantile_idx+1
        worst = None
        nextIndex: int = 0
        for i in range(_N):
            new_scoredGraphPath = self.generateONEScoredGraphPathSample(nAgent, t)
            if(math.isnan(new_scoredGraphPath.getScore())):
                raise Exception(f"NaN discovered in generateScoredGraphPathSamples_NEW_CODE_FAST for i={i}")
            if(i >= nSizeofArray):
                if(self.newScoreIsBetter(new_scoredGraphPath.getScore(), worst.getScore())):
                    _retArray[nextIndex] = new_scoredGraphPath
                    nextIndex += 1
                    #NOTE! last Arrays.sort(retPaths) will be done in calculateScoredPaths()
            else:
                _retArray[nextIndex] = new_scoredGraphPath
                nextIndex += 1
                if(worst == None or not self.newScoreIsBetter(new_scoredGraphPath.getScore(),worst.getScore())):
                    worst = new_scoredGraphPath #keep worst path so far
        # new truncate and sort _retPaths to its effetive size and sort
        truncated_ret_state_config_samples = [None] * nextIndex
        for i in range(nextIndex):
            truncated_ret_state_config_samples[i] = _retArray[i]
        try:
            truncated_ret_state_config_samples.sort()
        except:
            print("You probably have a NaN!")
            for i in range(len(truncated_ret_state_config_samples)):
                if(math.isnan(truncated_ret_state_config_samples[i].getScore())):
                    print(f" --> truncated_ret_state_config_samples[{i}] is NaN!")
        #take elite set
        ret_state_config_samples = [None] * nSizeofArray
        for i in range(nSizeofArray):
            ret_state_config_samples[i] = truncated_ret_state_config_samples[i]
    
    def getGammaIndex(self):
        return self.rho_quantile_idx
    
    def newScoreIsBetter(self, newScore: float, oldScore: float) -> bool:
        return newScore < oldScore
    
    def generateONEScoredGraphPathSample(self, nAgent: int, t: int):
        # //CARLA-interface-point-1: instruct(!) Carla the new graphPart (seq of position/speed or position/accel)
        graphPath = self.generateGraphPath(nAgent)
        """
        // Carla - system call python client or wrapper + put path as commandline args
        //String sAdversaryClassNameforMatt = graphPart.getClass().getName(); // Matt: use this string to annotate which adversary's graph path it is
        //CARLA-interface-point-2: read(!) from Carla
        //	(i) information about Ego every time step (this is where the demo differs; demo has a primitive/fixed Ego)
        //  (ii) possibly (unlikely?) adjusting adversary path (seq of pos/speed/accel) because 
        //								 Carla "could not conform" to the demands of CARLA-interface-point-1, or
        //								 My calculation of time to cover distance as func of avg accelaration (getPathPointByAccel()) is not accurate
        // (iii) system calls/wait synchronize with Python: wait for return results (score)
        """
        _score = self.score(graphPath, t) #get info from carla (e.g., Ego location and timing)
        scoredGraphPath = ScoredGraphPath(graphPath, _score)
        if (math.isnan(_score)):
            _score1 = self.score(graphPath,t) #for debug
            scoredGraphPath = scoredGraphPath(graphPath,_score1)
        return scoredGraphPath
    
    # //all samples (paths) with score > gamma (see that code here and code in gamma() are the same, but we really don't use gamma()...)
    def highScoredPaths(self):
        scoredSample_parts = self.scored_graphpath_samples
        if(self.eNEW_CODE != CODE_EFFICIENCIES.OLD_CODE):
            return scoredSample_parts
        else:
            # /*Returns a list with only high scored paths -- the ones that are scored lower than the rho-quantile path (gamma).
            aRet = [None] * self.rho_quantile_idx+1
            for i in range(self.rho_quantile_idx+1):
                aRet[i] = scoredSample_parts[i]
            return aRet
    
    # specific tests can override this
    def getD(self) -> int:
        return TestConstants.D
    
    def smoothlyUpdateDistributions(self, alpha: float) -> None:
        _highScoredPaths = self.highScoredPaths()
        self.smoothlyUpdateDistribution(alpha, _highScoredPaths)