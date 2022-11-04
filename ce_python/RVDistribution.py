#!/usr/bin/env python


from ce_python.GraphPath import GraphPath
from ce_python.TYPE_OF_RV import TYPE_OF_RV
from abc import abstractmethod


class RVDistribution:

    def __init__(self, scoreObject, clazz: str, my_CE_Manager, eTYPE_OF_RV: TYPE_OF_RV):
        self.scoreObject = scoreObject
        self.clazz = clazz
        self.my_CE_Manager = my_CE_Manager
        self.rho_quantile_idx = my_CE_Manager.rho_quantile_idx
        self.rand = my_CE_Manager.rand
        self.eTYPE_OF_RV = eTYPE_OF_RV
        self.eNEW_CODE = my_CE_Manager.eNEW_CODE
        self.scored_graphpath_samples = []
        self.rand = None
    @abstractmethod
    def initDistribution(self):
        pass
    @abstractmethod
    def smoothlyUpdateDistribution(self, alpha: float, scoredSampleParts):
        pass
    @abstractmethod
    def generateGraphPath(self, nAgent: int) -> GraphPath:
        pass
    @abstractmethod
    def getDest(self) -> int:
        pass

    def score(self, graphPath: GraphPath, t: int):
        return self.scoreObject.score(graphPath, t)
    def getScoredGraphPath(self, index: int):
        return self.scored_graphpath_samples[index]
    """
    def generateAdversaryObject(self, args = None) -> GraphPath:
        if(args):
            raise NotImplementedError("generateAdversaryObject with arguments not implemented")
        return GraphPath_Adversary5_HybridDistrib(self.eTYPE_OF_RV,self.my_CE_Manager.environment, self.my_CE_Manager.myRVDistribution)
    """
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
        bestPath: GraphPath = self.getScoredGraphPath(0).graphPath
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


    



