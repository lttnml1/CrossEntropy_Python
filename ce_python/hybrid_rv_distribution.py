#!/usr/bin/env python

#NATIVE PYTHON IMPORTS
import math

#INSTALLED PACKAGE IMPORTS

#IMPORTS FROM THIS PACKAGE
from ce_python.categorical_rv_distribution import CategoricalRVDistribution
from ce_python.type_of_rv import TYPE_OF_RV
from ce_python.test_constants import TestConstants
from ce_python.gaussian_parameters import GaussianParameters

class HybridRVDistribution(CategoricalRVDistribution):
    """
    // most of the complex code for hybrid can be inherited from Categorical, including trans_mat
    // matrix size n with speed/accel normal distrib
    """
    def __init__(self, nSrc: int, nDest: int, bAllowStutter: bool, scoreObject: 'AbstractScore', clazz: str, eTYPE_OF_RV: 'TYPE_OF_RV', my_CE_Manager: 'CE_Manager') -> None:
        super().__init__(nSrc, nDest, bAllowStutter, scoreObject, clazz, eTYPE_OF_RV, my_CE_Manager)

        self.gaussianParameters_grid = []

    def initDistribution(self):
        #categorical part of distribution
        super().initDistribution()

        #normal part of hybrid
        if(self.eTYPE_OF_RV == TYPE_OF_RV.SPEED_RV):
            mu = TestConstants.INITIAL_SPEED_MU
            sigma = TestConstants.INITIAL_SPEED_SIGMA
        else:
            mu = TestConstants.INITIAL_ACCEL_MU
            sigma = TestConstants.INITIAL_ACCEL_SIGMA
        
        self.gaussianParameters_grid = [None] * self.n
        for i in range(self.n):
            gaussianParameters = GaussianParameters(mu, sigma)
            self.gaussianParameters_grid[i] = gaussianParameters
    
    #For this Categorical distribution example: a "part" of a sample is a path
    def generateGraphPath(self, nAgent: int) -> 'GraphPath':
        #Categorical Part, taken from CategoricalRVDistribution
        path: 'GraphPath' = super().generateGraphPath(nAgent)
        #---------end Categorical Part

        #Normal distrib Part, taken from NormalRVDistribution
        #Now that Categorical has set the path, we set Normal distrib parameters for it
        for nPt in range(path.len()):
            pt = path.getPoint(nPt)
            gaussianParams = self.gaussianParameters_grid[pt]
            dSpeedOrAccel = HybridRVDistribution.__genRandomSpeedOrAccel(path, nPt, pt, self.eTYPE_OF_RV, gaussianParams, self.rand)
        return path
    
    @staticmethod 
    def __genRandomSpeedOrAccel(path, nPtIndex, pt, eTYPE_OF_RV, gaussianParams, rand):
        #A Path (whether fixed or discovered by categorical) is always forward going, i.e., cell at nPt+1 is forward of cell at nPt --> speed must be positive
        dSpeedOrAccel = 0
        dSpeed = TestConstants.INITIAL_ADVERSARY1_SPEED
        nWatchDog = 1 #100 #The idea with nWatchDog=100 was to eliminate negative speeds, but I did not need to resort to that
        while(nWatchDog >= 0):
            nWatchDog -= 1
            dRand = rand.normal(0,1)
            dSpeedOrAccel = dRand*gaussianParams.sigma + gaussianParams.mu #use gaussianParamsArray[i] to generate a sample
            dSpeed = dSpeedOrAccel #default case: eTYPE_OF_RV == TYPE_OF_RV.SPEED_RV
            if(eTYPE_OF_RV == TYPE_OF_RV.ACCEL_RV):
                pathPoint = path.getPathPointByAccel(nPtIndex, pt, dSpeedOrAccel)
                dSpeed = pathPoint.speed
            if(dSpeed > 0): break
        return dSpeedOrAccel
    
    def smoothlyUpdateDistribution(self, alpha: float, scoredGraphPaths):
        if(alpha <= 0 or alpha >= 1):
            raise Exception("alpha <= 0 or alpha >= 1")
        neighborMuGaussianParameters = []
        #Categorical part
        super().smoothlyUpdateDistribution(alpha, scoredGraphPaths)
        #-------end Categorical part

        #Normal distrib part
        for i in range(self.n):
            dSum = 0
            for j in range(len(scoredGraphPaths)):
                speedSequence = scoredGraphPaths[j].graphPath
                pathPoint = speedSequence.getSpeedPointAtGridPoint(i)
                if(pathPoint is None):
                    dSum += 0
                else:
                    dSum += pathPoint.speedOrAccel
            mu = dSum/len(scoredGraphPaths)
            """
            //if no path affected cell i then retain its distrib -- don't change it from initial random assignment (do not set to 0 because that will lead to paths discovered later using 0 speed instead of the default/initially-set speed
            """
            if(dSum == 0):
                neighborMuGaussianParameters = self.getNeighborGaussianParameters(i) #get all GaussianParameters for neighbors of i
                mu = self.averageFromNeighbors(neighborMuGaussianParameters, True) #average their mus
                continue
            dSum = 0
            for j in range(len(scoredGraphPaths)):
                speedSequence = scoredGraphPaths[j].graphPath
                pathPoint = speedSequence.getSpeedPointAtGridPoint(i)
                if(pathPoint == None):
                    d = 0
                else:
                    d = pathPoint.speedOrAccel - mu
                d = d*d
                dSum += d
            var = dSum/len(scoredGraphPaths)
            sigma = math.sqrt(var)
            if(dSum == 0):
                neighborMuGaussianParameters = self.getNeighborGaussianParameters(i) #added this line, otherwise, get DivByZero Error in averageFromNeighbors b/c len(neighborsGaussianParameters) == 0
                mu = self.averageFromNeighbors(neighborMuGaussianParameters, False)
            #Smoothing
            _newGaussianParameters = self.gaussianParameters_grid[i]
            mu = alpha*mu + (1-alpha)*_newGaussianParameters.mu
            sigma = alpha*sigma + (1-alpha)*_newGaussianParameters.sigma

            self.gaussianParameters_grid[i] = GaussianParameters(mu, sigma)
    
    def getNeighborGaussianParameters(self, pt: int):
        aRet = []
        #get all GaussianParameters for neighbors of i
        for j in range(self.m):
            if(self.isOffBoard(pt,j)): continue
            aRet.append(self.gaussianParameters_grid[pt])
        return aRet

    def averageFromNeighbors(self, neighborsGaussianParameters, calculateMU: bool) -> float:
        dSum = 0
        for gaussianParameters in neighborsGaussianParameters:
            if(calculateMU):
                dSum += gaussianParameters.mu
            else:
                dSum += gaussianParameters.sigma
        return dSum/len(neighborsGaussianParameters)