#!/usr/bin/env python

from __future__ import annotations
from abc import abstractmethod

from ast import Str
from typing import List

from ce_python.PathPoint import PathPoint
from ce_python.TYPE_OF_RV import TYPE_OF_RV
from ce_python.ChessBoardPositionPair import ChessBoardPositionPair
from ce_python.TestConstants import TestConstants

import re
import math
import sys

class GraphPath:
    #_path: List[PathPoint] = [] #list of pairs <time,index> of graph nodes (0..52 for TSP, 0..20x20-1 for chessboard, 0..numObservableNodes-1 for CrossEntropyBNObservations)
    #_bIsGoodPath: bool #false only for ChessBoard path that doesn't reach destination
    
    #used for debug only
    static_ID: int = 0
    #_sHashID: str #a hash code that is valid only after path is fully set (all "append"'s are done)
    #uniquePathID: int #while sHashID can be shared when a path is regenerated over and over again, unique ID is generated once - better for debug
    #eTYPE_OF_RV: TYPE_OF_RV
    #environment: Environment
    
    #GraphPath(TYPE_OF_RV eTYPE_OF_RV, Environment environment)
    def __init__ (self, eTYPE_OF_RV: TYPE_OF_RV, environment, myRvDistribution = None):
        self.path: List[PathPoint] = []
        self.bIsGoodPath = True #false only for ChessBoard path that doesn't reach destination
        self.sHashID = "" #i.e., unset
        self.eTYPE_OF_RV = eTYPE_OF_RV
        self.environment = environment
        self.myRvDistribution = myRvDistribution
        self.uniquePathID = GraphPath.static_ID
        GraphPath.static_ID+=1

    #for debug, or for setting fixed paths, like Ego and Adversary#1
	#Note: speed setting is for EGO, Adversary#1 will be overwrite this settings
	#GraphPath(String  str, Environment environment, TYPE_OF_RV eTYPE_OF_RV)
    @classmethod
    def from_fixed_path(cls, str: Str, eTYPE_OF_RV: TYPE_OF_RV, environment) -> GraphPath:
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
            #n: int = environment.fromPairToVertex(ChessBoardPositionPair(nPart0,nPart1))
            n = nPart0 * 20 + nPart1
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
    def getBasePath(self) -> GraphPath:
        pass
    
    def printMeAsChessboardPath(self, environment) -> None:
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
            dThisPtTime = prevPoint.time + dOneCellTime; 
        newPointObject: PathPoint = PathPoint(indexInPath, pt, dThisPtTime, speed)
        return newPointObject

    def getPathPointByAccel(self, indexInPath: int, pt: int, accel: float) -> PathPoint:
        dThisPtTime: float = 0
        newSpeed: float = TestConstants.INITIAL_ADVERSARY1_SPEED
        if (indexInPath > 0):
            prevPoint: PathPoint = self.get(indexInPath-1)
            dist: float = self.environment.getCellToCelDist(prevPoint.pt, pt)
            dAvgAccel: float = PathPoint.getAvgSpeedOrAccel(accel, prevPoint.speedOrAccel)
            dOneCellTime: float = 0
            if (dAvgAccel == 0):
                constSpeed: float = prevPoint.speed
                dOneCellTime = dist/constSpeed
                newSpeed = prevPoint.speed
            else:
                dOneCellTime = -prevPoint.speed + math.sqrt(prevPoint.speed * prevPoint.speed + 2 * dAvgAccel * dist) / dAvgAccel
                newSpeed = prevPoint.speed + dAvgAccel * dOneCellTime
                dVsqare: float = prevPoint.speed * prevPoint.speed + 2 * dAvgAccel * dist
                if (dVsqare < 0):
                    dVsqare = prevPoint.speed * prevPoint.speed - 2 * dAvgAccel * dist
                newSpeed = math.sqrt(dVsqare)
                if (newSpeed == 0): dOneCellTime = sys.float_info.max
                else: dOneCellTime = dist/newSpeed
            dThisPtTime = prevPoint.time + dOneCellTime	
        newPointObject: PathPoint = PathPoint(indexInPath, pt, dThisPtTime, accel, newSpeed)
        return newPointObject

"""
public void putPointAt(int indexInPath, int pt, double speedOrAccel) throws Exception {
		TYPE_OF_RV eTYPE_OF_RV = this.eTYPE_OF_RV; // is speedOrAccel speed or acceleration?
		putPointAt( indexInPath,  pt, speedOrAccel, eTYPE_OF_RV);
	}
	public void putPointAt(int indexInPath, int pt, double speedOrAccel, TYPE_OF_RV __eTYPE_OF_RV) throws Exception {
		
		PathPoint newPointObject = null;
		if (__eTYPE_OF_RV == TYPE_OF_RV.SPEED_RV) newPointObject = getPathPointBySpeed(indexInPath, pt, speedOrAccel);
		else if (__eTYPE_OF_RV == TYPE_OF_RV.ACCEL_RV) newPointObject = getPathPointByAccel(indexInPath, pt, speedOrAccel);
		else throw new Exception("Unrecognized __eTYPE_OF_RV in putPointAt()");
		
		this.append(newPointObject);

	}
	
	public void updatePointAt(int indexInPath, int pt, double speedOrAccel) throws Exception {
		TYPE_OF_RV eTYPE_OF_RV = this.eTYPE_OF_RV; // is speedOrAccel speed or acceleration?
		updatePointAt(indexInPath, pt, speedOrAccel, eTYPE_OF_RV);
	}
	public void updatePointAt(int indexInPath, int pt, double speedOrAccel, TYPE_OF_RV __eTYPE_OF_RV) throws Exception {
		
		PathPoint newPointObject = null;
		if (__eTYPE_OF_RV == TYPE_OF_RV.SPEED_RV) newPointObject = getPathPointBySpeed(indexInPath, pt, speedOrAccel);
		else if (__eTYPE_OF_RV == TYPE_OF_RV.ACCEL_RV) newPointObject = getPathPointByAccel(indexInPath, pt, speedOrAccel);
		else throw new Exception("Unrecognized __eTYPE_OF_RV in putPointAt()");
		
		this.path.set(indexInPath,newPointObject);

	}
	
	public ArrayList<PathPoint> getPathPoints() {
		return this.path;
	}
	
	public PathPoint get(int k) {
		return this.path.get(k);
	}


	public int getPoint(int k) {
		return this.path.get(k).pt;
	}
	
	public int len() {
		return this.path.size();
	}
	
	public boolean isGoodPath() {
		return this.bIsGoodPath;
	}
	public void setNotGoodPath() {
		this.bIsGoodPath = false;
	}

	
	
	public void printMe(String sMsg) {
		System.out.print(sMsg);
		for (PathPoint pathPt: path) System.out.print(pathPt.pt+"@t=" + pathPt.time + "/" + pathPt.speedOrAccel + ",");
		System.out.println();
	}



	public void printMeAsChessboardPath(String Msg, Environment environment) {
		System.out.println(Msg);
		for (PathPoint pathPt: path) {
			ChessBoardPositionPair pair = environment.fromVertexToPair(pathPt.pt);
			System.out.println("n="+pathPt.pt+"<" + pair.get_i() + "," + pair.get_j()+"> -->");
		}
		System.out.println();
	}

	


	public static void visualize(Environment environment,  ChessBoardPositionPair src, ChessBoardPositionPair dest, GraphPath egoPath, GraphPath[] paths) {
				Visualizer v = new Visualizer();
				v._main(new String[0], environment, src, dest, paths, egoPath);
	}

	/*
	boolean isPathForDebug() {
		String s = this.toStr();;
		//if ( s.contains("209,188,168,149,130,111,90,89,68,47,26,7,8,29,10,31")) {
		if ( s.contains("209,188,168,149,130,")) {
			return true;
		};
		return false;
	}

	*/


	

	
	public void putSpeedPointAt(int index, PathPoint speedPoint) throws Exception{
		if (index >= this.len()) throw new Exception("index >= len in putSpeedPointAt()");
		this.path.add(index, speedPoint);
	}
	// only used by adversaries that calculate their own speed (NormalDistrib and ExponentialDistrib)
	public PathPoint getSpeedPointAt(int index) throws Exception {
		if (index >= len()) 
			throw new Exception("index >= len() in getSpeedPointAt()");
		return this.get(index);
	}
	// only used by Hybrid-distribution RV's, i.e., Adversary4 type
	public PathPoint getSpeedPointAtGridPoint(int pt) throws Exception {
		for (int nPt = 0; nPt < this.len(); nPt++) {	
			PathPoint pathPoint = getSpeedPointAt(nPt);
			if (pathPoint.pt != pt) continue;
			return pathPoint;
		}
		return null; //i.e., point i,j is not on path
	}

	public int getPointAt(int index) throws Exception{
		return getSpeedPointAt(index).pt;
	}

	// get some measure of the path -- used for experimental data-set creation (hopefully data-set with high variance)
	   	// Use truncated Perturbation path that ends in "accident" point.
	   	// This facilitated the generation a high-variance data-set that is based only on the part of the perturbation path UNTIL the "accident"
	double getCategoricalPathMeasure(ArrayList<PathPoint> truncatedPath) throws Exception {
		double dMeasure = 0;
		for (PathPoint pathPt: truncatedPath) {
			ChessBoardPositionPair pair = environment.fromVertexToPair(pathPt.pt);
			double d_i = pair.get_i()*pair.get_i();
			double d_j = pair.get_j()*pair.get_j();
			dMeasure += Math.sqrt(d_i + d_j);
		}
		return dMeasure/truncatedPath.size(); // otherwise longer paths will be rewarded more
	}
	
   	// Use truncated Perturbation path that ends in "accident" point.
   	// This facilitated the generation a high-variance data-set that is based only on the part of the perturbation path UNTIL the "accident"
	double getNormalPathMeasure(ArrayList<PathPoint> truncatedPath) throws Exception {
		double dMeasure = 0;
		for (PathPoint pathPt: truncatedPath) {
			dMeasure += pathPt.speedOrAccel;
		}
		return dMeasure/truncatedPath.size();// otherwise longer paths will be rewarded more
	}
	
	   	// Truncate Perturbation path! (now ends in "accident" point)
	   	// This allows getNormalPathMeasure() and getCategoricalPathMeasure() [both here and in TestCase_Adv5Only_accel] to come up with 
	   	//  a high-variance data-set that is beased only on the part of the perturbation path UNTIL the "accident"
	public ArrayList<PathPoint>  truncatePathAfterPoint(int endPoint) throws Exception {
		boolean bEndPointFound = false;
		int nPt = 0;
		for (; nPt < this.len(); nPt++) {
			int pt = this.getPoint(nPt);
			if (pt == endPoint) {
				bEndPointFound = true;
				break;
			}
		}
		if (!bEndPointFound) 
			throw new Exception("truncateAfterPoint error: endPoint not found, but should exists for perturbation path "); // for pert. path end point is point of "accident", which should exist by definition of being a pert. path
		
		if (nPt<this.len()-1) {
			return new ArrayList<PathPoint>(this.path.subList(0, nPt+1)); // truncate but leave last point ("accident" point
		}
		return this.path;
	}
"""

e = TYPE_OF_RV.ACCEL_RV
env = None
gp = GraphPath.from_fixed_path("(1,2)(3,4)(4,5)(6,7)",e,env)
assert gp.getHashID() == "22,64,85,127,", f"Expected \"22,64,85,127\", got {gp.getHashID()}"
assert gp.getUniquePathID() == 0, f"Expected 0, got {gp.getUniquePathID()}"
gp.getPathPointByAccel(3,3,3.0)