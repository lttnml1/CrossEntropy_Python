#!/usr/bin/env python
import sys

MAX_VALUE = float(sys.maxsize)

class BadScoreLevels:
	BAD_PATH: float = MAX_VALUE/2 #only used for !graphPath.isGoodPath()
	SPECIFIC_LEVEL_1: float = MAX_VALUE/4
	SPECIFIC_LEVEL_2: float = MAX_VALUE/8