#!/usr/bin/env python

class PathPoint:
    indexInPath: int #int representing point. Use environment.fromVertexToPair to get i,j of point
    pt: int #int representing point. Use environment.fromVertexToPair to get i,j of point
    time: float # time the point is reached
    speedOrAccel: float #speed or acceleration at the point
    speed: float #differs from speedOrAccel only when speedOrAccel is accel
    
    #Python cannot overload constructors, so use number of arguments to construct PathPoint object
    def __init__(self, *args):
        if len(args) == 4:
            self.speed_init(args[0],args[1],args[2],args[3])
        elif len(args) == 7:
            self.accel_init(args[0],args[1],args[2],args[3],args[4],args[5],args[6])
        else:
            print("**No valid constructor for PathPoint object**\n")

    #used when speedOrAccel RV is speed
    def speed_init (self, indexInPath: int, pt: int, time: float, speed: float):
        self.indexInPath = indexInPath
        self.pt = pt
        self.speedOrAccel = speed
        self.speed = speed
        self.time = time

	#used when speedOrAccel RV is accl
    def accel_init (self, indexInPath: int, pt: int, time: float, accel: float, prevPtTime: float, prevPtSpeed: float, prevPtAccel: float):
        self.indexInPath = indexInPath
        self.pt = pt
        self.speedOrAccel = accel
        self.time = time

        self.speed = self.getSpeedByAccel(time, prevPtTime, prevPtSpeed, accel, prevPtAccel)
    
    @staticmethod
    def getSpeedByAccel(time: float, prevPtTime: float, prevPtSpeed: float, accel: float, prevPtAccel: float) -> float:
        if accel < 0.4:
            zzz: int = 1
        return prevPtSpeed + (time - prevPtTime) * (prevPtAccel + (accel - prevPtAccel)/2)