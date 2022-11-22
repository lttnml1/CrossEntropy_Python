#!/usr/bin/env python

#NATIVE PYTHON IMPORTS
from enum import Enum, auto

#INSTALLED PACKAGE IMPORTS

#IMPORTS FROM THIS PACKAGE

class TYPE_OF_RV(Enum):
    SPEED_RV = auto()
    ACCEL_RV = auto()

"""
e = TYPE_OF_RV.SPEED_RV
print(type(e))
print(isinstance(e,TYPE_OF_RV))
"""