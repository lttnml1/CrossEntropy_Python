#!/usr/bin/env python
from abc import ABC, abstractmethod
from ce_python.RVDistribution import RVDistribution
from ce_python.GraphPath import GraphPath
from ce_python.BadScoreLevels import BadScoreLevels
from ce_python.PathPoint import PathPoint
from typing import List
import math

class AbstractScore(ABC):
        
    @abstractmethod
    def specificScore(self, graphPath: GraphPath, t: int) -> float:
        pass

    def setAllRVDistributions(self, allRVDistributions: List[RVDistribution]) -> None:
        self.allRVDistributions = allRVDistributions
    
    def score(self, graphPath: GraphPath, t: int) -> float:
        #!isGoodPath is not used for Matt's CE; all egregious paths are scored here anyway 
        if not graphPath.isGoodPath():
            return BadScoreLevels.BAD_PATH #since we're minimizing then indeed this is a bad score
        
        dRet: float = AbstractScore.s_AbstractScoreDueDiligence(graphPath)

        d: float = dRet + self.specificScore(graphPath, t)

        return d
    
    @staticmethod
    def s_AbstractScoreDueDiligence(graphPath: GraphPath) -> float:
        dRet: float = 0
        #No negative speed, no negative time, no time moving backwards, no NaN's
        prev_time: float = 0
        for i in range(0,graphPath.len()):
            pathPoint: PathPoint = graphPath.get(i)
            if (math.isnan(pathPoint.speed) or math.isnan(pathPoint.time)):
                #NaN can happen in getPathPointByAccel() when sqrt is performed on a negative
                #**What happens in python with the square root of a negative number? Throws ValueError - do exception handling like:
                #def sqRoot(x: float) -> float:
                #   try:
                #       result = math.sqrt(x)
                #   except ValueError:
                #       result = float('nan')
                #   return result
                graphPath.setNotGoodPath()
                return BadScoreLevels.BAD_PATH
            if pathPoint.speed < 0:
                #return function of speed so CE can strive to improve
                dRet += 100 * abs(pathPoint.speed); #amplify by 100 because negative speed is much worse than "nNumberOfDecreases>1"
                graphPath.setNotGoodPath()
            if pathPoint.time < 0:
                #return function of speed so CE can strive to improve
                dRet += 100 * abs(pathPoint.time) #amplify by 100 because negative speed is much worse than "nNumberOfDecreases>1"
                graphPath.setNotGoodPath()
            if (i > 0 and prev_time > 0 and prev_time >= pathPoint.time):
                #return function of speed so CE can strive to improve
                dRet += 100 * abs(prev_time-pathPoint.time) # amplify by 100 because negative speed is much worse than "nNumberOfDecreases>1"
                graphPath.setNotGoodPath()
            prev_time = pathPoint.time
        return dRet