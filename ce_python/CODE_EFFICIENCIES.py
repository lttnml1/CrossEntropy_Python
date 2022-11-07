#!/usr/bin/env python

#NATIVE PYTHON IMPORTS
from enum import Enum, auto

class CODE_EFFICIENCIES(Enum):
    OLD_CODE = auto()
    NEW_CODE_SLOW = auto()
    NEW_CODE_FAST = auto()
    CARLA_CODE = auto()

