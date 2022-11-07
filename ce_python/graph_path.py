#!/usr/bin/env python

#NATIVE PYTHON IMPORTS
from abc import abstractmethod
from typing import List
import re
import math
import sys

#INSTALLED PACKAGE IMPORTS

#IMPORTS FROM THIS PACKAGE
from ce_python.path_point import PathPoint
from ce_python.chess_board_position_pair import ChessBoardPositionPair
from ce_python.test_constants import TestConstants
from ce_python.type_of_rv import TYPE_OF_RV

class GraphPath:
	static_ID: int = 0
	def __init__ (self, eTYPE_OF_RV, environment: object, myRvDistribution = None):
		self.path: List[object] = []
		self.bIsGoodPath = True #false only for ChessBoard path that doesn't reach destination
		self.sHashID = "" #i.e., unset
		self.eTYPE_OF_RV = eTYPE_OF_RV
		self.environment = environment
		self.myRvDistribution = myRvDistribution
		self.uniquePathID = GraphPath.static_ID
		GraphPath.static_ID+=1

	# for debug, or for setting fixed paths, like Ego and Adversary#1
	# Note: speed setting is for EGO, Adversary#1 will be overwrite this settings
	# GraphPath(String  str, Environment environment, TYPE_OF_RV eTYPE_OF_RV)
	@classmethod
	def from_fixed_path(cls, str, eTYPE_OF_RV, environment) -> object:
		graphPath = cls(eTYPE_OF_RV,environment)
		dTime: float = 0
		nIndex: int = 0
        # []: split on pattern that contains these characters
        # \(: literal '('
		# \(: literal ')'
		# | : logical 'or' (compare to '||' in Java)
		parts = re.split('[\(|\)]',str)
		for part in parts:
			sPart = part.strip()
			if(sPart==("")): continue
			subparts = sPart.split(",")
			nPart0: int = int(subparts[0])
			nPart1: int = int(subparts[1])
			n: int = environment.fromPairToVertex(ChessBoardPositionPair(nPart0,nPart1))
			#n = nPart0 * 20 + nPart1
			dSpeed: float = float(nIndex)%3 + 1  
			#speed is 1,2,3,1,2,3. NOTE! this speed setting is for EGO, Adversary#1 will be overwrite this settings
			dTime += 1/dSpeed
			graphPath.append(nIndex, n, dTime, dSpeed)
			nIndex += 1
		return graphPath
	
	def append(self, indexInPath: int, pt: int, time: float, speed: float):
		pathPt = PathPoint(indexInPath, pt, time, speed)
		self.path.append(pathPt)
		self.sHashID += str(pathPt.pt)+","

	@abstractmethod
	def getBasePath(self) -> object:
		pass
	
	def printMeAsChessboardPath(self, environment, Msg: str = None) -> None:
		if(str): print(str)
		print(f"2D (ChessBoard) path(uniquePathID=\"{self.getUniquePathID()}\")")
		for pairPt in self.path:
			pair: ChessBoardPositionPair = environment.fromVertexToPair(pairPt.pt)
			print(f"n={pairPt.pt}<{pair.get_i()},{pair.get_j()}>@t={pairPt.time}-->")
	
	#get speed for Adversaries that DON'T use CE to compute speed, but rather have pre-determined fixed speed
	def getAdversaryCategoricalFixedSpeedAt(self, nIndex: int) -> float:
		raise Exception("GraphPath.getAdversaryCategoricalFixedSpeedAt should not be reached! Only an inherited method such as GraphPath_Adversary2.getAdversaryCategoricalFixedSpeedAt() should be reached")
	def getHashID(self) -> str: return self.sHashID
	def getUniquePathID(self) -> int: return self.uniquePathID
	
	def getPathPointBySpeed(self, indexInPath: int, pt: int,speed: float) -> PathPoint:
		dThisPtTime: float = 0
		if (indexInPath > 0):
			prevPoint: PathPoint = self.get(indexInPath-1)
			dist: float = self.environment.getCellToCelDist(prevPoint.pt, pt)
			dAvgSpeed: float = PathPoint.getAvgSpeedOrAccel(speed, prevPoint.speedOrAccel) # speed to get from pt i to i+1 is the avg of speeds at points i,i+1
			if (dAvgSpeed == 0): dOneCellTime: float = 0
			else: dOneCellTime: float = dist/dAvgSpeed;# meter/(meter/sec) == sec
			dThisPtTime = prevPoint.time + dOneCellTime
		newPointObject: PathPoint = PathPoint(indexInPath, pt, dThisPtTime, speed)
		return newPointObject
		
	def getPathPointByAccel(self, indexInPath: int, pt: int, accel: float) -> PathPoint:
		dThisPtTime: float = 0
		newSpeed: float = TestConstants.INITIAL_ADVERSARY1_SPEED
		if (indexInPath > 0):
			prevPoint: PathPoint = self.get(indexInPath-1)
			dist: float = self.environment.getCellToCelDist(prevPoint.pt, pt)
			#dist = 3
			dAvgAccel: float = PathPoint.getAvgSpeedOrAccel(accel, prevPoint.speedOrAccel)
			dOneCellTime: float = 0
			if (dAvgAccel == 0):
				constSpeed: float = prevPoint.speed
				dOneCellTime = dist/constSpeed
				newSpeed = prevPoint.speed
			else:
				dVsqare: float = prevPoint.speed * prevPoint.speed + 2 * dAvgAccel * dist
				if (dVsqare < 0):
					dVsqare = prevPoint.speed * prevPoint.speed - 2 * dAvgAccel * dist
				newSpeed = math.sqrt(dVsqare)
				if (newSpeed == 0): dOneCellTime = sys.float_info.max
				else: dOneCellTime = dist/newSpeed
			dThisPtTime = prevPoint.time + dOneCellTime	
		newPointObject: PathPoint = PathPoint(indexInPath, pt, dThisPtTime, newSpeed, accel)
		return newPointObject
	
	def putPointAt(self, indexInPath: int, pt: int, speedOrAccel: float):
		eTYPE_OF_RV: TYPE_OF_RV = self.eTYPE_OF_RV # // is speedOrAccel speed or acceleration?
		if(eTYPE_OF_RV == TYPE_OF_RV.SPEED_RV):
			newPointObject = self.getPathPointBySpeed(indexInPath, pt, speedOrAccel)
		elif(eTYPE_OF_RV == TYPE_OF_RV.ACCEL_RV):
			newPointObject = self.getPathPointByAccel(indexInPath, pt, speedOrAccel)
		else:
			raise Exception("Unrecognized eTYPE_OF_RV in putPointAt()")
		self.append(newPointObject)
	
	def updatePointAt(self, indexInPath: int, pt: int, speedOrAccel: float):
		eTYPE_OF_RV: TYPE_OF_RV = self.eTYPE_OF_RV
		if(eTYPE_OF_RV == TYPE_OF_RV.SPEED_RV):
			newPointObject = self.getPathPointBySpeed(indexInPath, pt, speedOrAccel)
		elif(eTYPE_OF_RV == TYPE_OF_RV.ACCEL_RV):
			newPointObject = self.getPathPointByAccel(indexInPath, pt, speedOrAccel)
		else:
			raise Exception("Unrecognized eTYPE_OF_RV in updatePointAt()")
		self.path[indexInPath] = newPointObject
	
	def getPathPoints(self) -> List[PathPoint]:
		return self.path
	
	def get(self, k: int) -> PathPoint:
		return self.path[k]
	
	def getPoint(self, k: int) -> int:
		return self.path[k].pt
	
	def len(self) -> int:
		return len(self.path)

	def isGoodPath(self) -> bool:
		return self.isGoodPath
	
	def setNotGoodPath(self) -> None:
		self.bIsGoodPath = False
	
	def printMe(self, sMsg: str) -> None:
		print(sMsg)
		for pathPt in self.path:
			print(f"{pathPt.pt}@t={pathPt.time}/{pathPt.speedOrAccel},\n")
	
	"""
	def visualize(environment, src: ChessBoardPositionPair, dest: ChessBoardPositionPair, egoPath: GraphPath, paths: List[GraphPath]):
		v = Visualizer()
		v._main([], environment, src, dest, paths, egoPath)
	"""

	def putSpeedPointAt(self, index: int, speedPoint: PathPoint) -> None:
		if (index >= self.len()):
			raise Exception("index >= len in putSpeedPointAt()")
		self.path.insert(index, speedPoint)

	# only used by adversaries that calculate their own speed (NormalDistrib and ExponentialDistrib)
	def getSpeedPointAt(self, index: int) -> PathPoint:
		if (index >= self.len()):
			raise Exception("index >= len() in getSpeedPointAt()")
		return self.get(index)
	
	# only used by Hybrid-distribution RV's, i.e., Adversary4 type
	def getSpeedPointAtGridPoint(self, pt: int) -> PathPoint:
		for nPt in range(self.len()):
			pathPoint: PathPoint = self.getSpeedPointAt(nPt)
			if (pathPoint.pt != pt): continue
			return pathPoint
		return None #i.e., point i,j is not on path
	
	def getPointAt(self, index: int) -> int:
		return self.getSpeedPointAt(index).pt
	"""
	// get some measure of the path -- used for experimental data-set creation (hopefully data-set with high variance)
	   	// Use truncated Perturbation path that ends in "accident" point.
	   	// This facilitated the generation a high-variance data-set that is based only on the part of the perturbation path UNTIL the "accident"
	"""
	def getCategoricalPathMeasure(self, truncatedPath: List[PathPoint]) -> float:
		dMeasure: float = 0
		for pathPt in truncatedPath:
			pair: ChessBoardPositionPair = self.environment.fromVertexToPair(pathPt.pt)
			d_i: float = pair.get_i()**2
			d_j: float = pair.get_j()**2
			dMeasure += math.sqrt(d_i + d_j)
		return dMeasure/len(truncatedPath) #otherwise longer paths will be rewarded more

	"""
	// Use truncated Perturbation path that ends in "accident" point.
   	// This facilitated the generation a high-variance data-set that is based only on the part of the perturbation path UNTIL the "accident"
	"""
	def getNormalPathMeasure(self, truncatedPath: List[PathPoint]) -> float:
		dMeasure: float = 0
		for pathPt in truncatedPath:
			dMeasure += pathPt.speedOrAccel
		return dMeasure/len(truncatedPath) #otherwise longer paths will be rewarded more
	
	"""
	// Truncate Perturbation path! (now ends in "accident" point)
	// This allows getNormalPathMeasure() and getCategoricalPathMeasure() [both here and in TestCase_Adv5Only_accel] to come up with 
	//  a high-variance data-set that is beased only on the part of the perturbation path UNTIL the "accident"
	"""
	def truncatePathAfterPoint(self, endPoint: int) -> List[PathPoint]:
		bEndPointFound: bool = False
		nPt: int = 0
		for i in range(self.len()):
			pt: int = self.getPoint(nPt)
			if(pt == endPoint):
				bEndPointFound = True
				break
			nPt += 1
		if (not bEndPointFound):
			raise Exception("truncateAfterPoint error: endPoint not found, but should exist for perturbation path")
			# for pert. path end point is point of "accident", which should exist by definition of being a pert. path
		if (nPt < self.len()-1):
			return self.path[0:nPt+1]
		return self.path
	
