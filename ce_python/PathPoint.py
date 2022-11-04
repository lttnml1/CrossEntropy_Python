#!/usr/bin/env python

from __future__ import annotations

#** EXAMPLE MULTIPLE CONSTRUCTOR USAGE **
#       pp=PathPoint(1,2,3.0,4.0)
#       print(pp.speed)
#       pp2=PathPoint.from_accel(1,2,3.0,4.0,2,2.0,1.0)
#       print(pp2.speed)

class PathPoint:
    #indexInPath: int #int representing point. Use environment.fromVertexToPair to get i,j of point
    #pt: int #int representing point. Use environment.fromVertexToPair to get i,j of point
    #time: float # time the point is reached
    #speedOrAccel: float #speed or acceleration at the point
    #speed: float #differs from speedOrAccel only when speedOrAccel is accel
    
    #Python cannot overload constructors, so use __init__() to initialize with speed, from_accel initializes with accel
    #used when speedOrAccel RV is speed
    #PathPoint(int indexInPath, int pt, double time, double speed)
    def __init__ (self, indexInPath: int, pt: int, time: float, speed: float, accel: float = None):
        self.indexInPath = indexInPath
        self.pt = pt
        self.time = time
        self.speed = speed
        if accel is not None:
            self.speedOrAccel = accel
        else:
            self.speedOrAccel = speed
    
    @staticmethod
    def getSpeedByAccel(time: float, prevPtTime: float, prevPtSpeed: float, accel: float, prevPtAccel: float) -> float:
        return prevPtSpeed + (time - prevPtTime) * PathPoint.getAvgSpeedOrAccel(accel, prevPtAccel)

    @staticmethod
    def getAvgSpeedOrAccel(accel: float, prevPtAccel: float) -> float:
        return (prevPtAccel + accel)/2