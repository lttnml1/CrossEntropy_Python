#!/usr/bin/env python
from __future__ import annotations

from enum import Enum, auto

class TYPE_OF_RV(Enum):
    SPEED_RV = auto()
    ACCEL_RV = auto()

#e = TYPE_OF_RV.SPEED_RV
#print(type(e))
#print(isinstance(e,TYPE_OF_RV))