#!/usr/bin/env python
from __future__ import annotations

class TestConstants:
    C: int = 1 # // 10 was the value that was used in the Python code; all V1...V4 worked fine with C=1; only TSP had better results with C=10, because it is a true hard optiminization problem 
    C10: int = 10
    C50: int = 50  
    C100: int = 100
    C10000: int = 10000
    
    SEED: int = 13
    RHO: float = 0.01
    ALPHA: float = 0.8 # // used when smoothing (see CETutorial.pdf -- eq. (35))
    
    NUM_RV_DISTRIBUTIONS: int = 2
    W: int = 20
    H: int = 20
    NUMBER_OF_POSSIBLE_MOVES: int = 3
    D: int = 5 # // used as number of times (t's) the gamma_t doesn't change (see CETutorial.pdf -- eq. (34))
    
    TIME_EGO_AT_ADV1_POS: float = 8.8
    
    FORCE_INITIAL_ADVERSARY1_SPEED: bool = False # // true means force speed at time 0 to INITIAL_ADVERSARY1_SPEED
    INITIAL_ADVERSARY1_SPEED: float = 0 # // Only applies if FORCE_INITIAL_ADVERSARY1_SPEED==true
    FORCE_INITIAL_ADVERSARY2_SPEED: bool = False # // true means force speed at time 0 to INITIAL_ADVERSARY2_SPEED
    INITIAL_ADVERSARY2_SPEED: float = 0 # // Only applies if FORCE_INITIAL_ADVERSARY2_SPEED==true
    
    ADVERSARY2_FIXED_SPEED: float = 1.75 # // must be fast enough for Adv2 to be able to reach Adv 1 before time ~8.3
    ADVERSARY2_FIXED_SPEED_1a: float = 4 # // ADVERSARY2_FIXED_SPEED is too slow for TestCase_Adv1aAndAdv2: Adv2 reaches Adv1 too late, so Adv1 is too close to the end and cannot decelerate to meet Ego at t=8.x
    ADVERSARY3_FIXED_SPEED: float = 1.5
    
    INITIAL_ADVERSARY3_TEMPORARY_SPEED: float = 1.0 
    ADVERSARY3_TEMPORARY_SPEED: float = INITIAL_ADVERSARY3_TEMPORARY_SPEED # // temporary/placeholder until NormalDistrib CE assigns a speed
    
    #//*** Begin Initial speed/accel mu,sigma values for NormalRVDistribution
    INITIAL_SPEED_MU: float = 1.0 # //mu of speed that the CE starts at, for RV_SPEED case
    INITIAL_SPEED_SIGMA: float = 0.5 # //sigma of speed ...   -"-
    # // initially a car will accelerate, so I chose this as positive
    INITIAL_ACCEL_MU: float = 1.0 # //mu of accel that the CE starts at, for RV_ACCEL case
    INITIAL_ACCEL_SIGMA: float = 0.5 #//sigma of accel ... -"-
    #//*** End
    
    # //*** Begin Initial mu value for EcponentialRVDistribution
    INITIAL_EXP_MU: float = 1.0 # //mu of speed that the CE starts at, for RV_SPEED case
    # //*** End
    
    """
    // When this is true then CE_Manager does 2 rounds, first with small N, second with originally planned N
    // The probability distributions from first round are then used as basis for second round, hoping to converge faster
    // This doesn't work for distributions like exponential which have a hard time converging in first round because they require large sample space
    // NOTE!  results (score of best path) are somewhat better	when SPEEDUP_USING_2_ROUNDS=false
    """
    SPEEDUP_USING_2_ROUNDS: bool = False
    ROUND_0_SPEEDUP_FACTOR: int = 10 # // make N of nRound = 0 1/10'th of originally planned N