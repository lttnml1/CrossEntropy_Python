#!/usr/bin/env python
from abc import ABC, abstractmethod
from typing import List
from RVDistribution import RVDistribution
from GraphPath import GraphPath
from BadScoreLevels import BadScoreLevels
from PathPoint import PathPoint
import math

class AbstractScore(ABC):

    _allRVDistributions: List[RVDistribution]  = []
        
    @abstractmethod
    def specificScore(self, graphPath: GraphPath) -> float:
        pass

    def setAllRVDistributions(self, allRVDistributions: List[RVDistribution]) -> None:
        self._allRVDistributions = allRVDistributions
    
    def score(self, graphPath: GraphPath) -> float:
        #!isGoodPath is not used for Matt's CE; all egregious paths are scored here anyway 
        if not graphPath.isGoodPath():
            return BadScoreLevels.BAD_PATH #since we're minimizing then indeed this is a bad score
        
        dRet: float = 0
        #No negative speed, no negative time, no time moving backwards, no NaN's
        prev_time: float = 0
        for i in range(0,graphPath.len()):
            pathPoint: PathPoint = graphPath.get(i)
            if (math.isnan(float(pathPoint.speed)) or math.isnan(float(pathPoint.time))):
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
            if (i > 0 and prev_time >= pathPoint.time):
                #return function of speed so CE can strive to improve
                dRet += 100 * abs(prev_time-pathPoint.time) # amplify by 100 because negative speed is much worse than "nNumberOfDecreases>1"
                graphPath.setNotGoodPath()
            prev_time = pathPoint.time
        return dRet + self.specificScore(graphPath)