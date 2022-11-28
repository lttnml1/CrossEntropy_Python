#!/usr/bin/env python

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
    D: int = 2 # // used as number of times (t's) the gamma_t doesn't change (see CETutorial.pdf -- eq. (34))
    TIME_EGO_AT_ADV1_POS: float = 8.8
    
    FORCE_INITIAL_ADVERSARY1_SPEED: bool = False # // true means force speed at time 0 to INITIAL_ADVERSARY1_SPEED
    INITIAL_ADVERSARY1_SPEED: float = 0.0 # // Only applies if FORCE_INITIAL_ADVERSARY1_SPEED==true
    FORCE_INITIAL_ADVERSARY2_SPEED: bool = False # // true means force speed at time 0 to INITIAL_ADVERSARY2_SPEED
    INITIAL_ADVERSARY2_SPEED: float = 0.0 # // Only applies if FORCE_INITIAL_ADVERSARY2_SPEED==true
    
    ADVERSARY2_FIXED_SPEED: float = 1.75 # // must be fast enough for Adv2 to be able to reach Adv 1 before time ~8.3
    ADVERSARY2_FIXED_SPEED_1a: float = 4.0 # // ADVERSARY2_FIXED_SPEED is too slow for TestCase_Adv1aAndAdv2: Adv2 reaches Adv1 too late, so Adv1 is too close to the end and cannot decelerate to meet Ego at t=8.x
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
    // *11/22/22
	//USE_MULTIPLE_CE_BATCHES NOTE:
	//When three batches
	// #1: small N in Java: get coarse probability distributions  using Java, i.e., no Ego AI
	// #2: large N in Java: get refined probability distributions  using Java, i.e., no Ego AI
	// 		The probability distributions from first round are then used as basis for second round, hoping to converge faster
	// 		This doesn't work for distributions like exponential which have a hard time converging in first round because they require large sample space
	// #3: small N in Carla: update probability distributions  using Python, i.e., Ego AI
	//When two batches
	// #1: large N in Java: get probability distributions  using Java, i.e., no Ego AI
	// #2: small N in Carla: update probability distributions  using Python, i.e., Ego AI
    """
    USE_MULTIPLE_CE_BATCHES: bool = True
    NUM_CE_BATCHES: int = 2
    BATCH_0_SPEEDUP_FACTOR: int = 10 #// Only applies when NUM_CE_BATCHES=3; make N of nBatch = 0 1/10'th of originally planned N (like 20*20*8*C/10)
    NUM_ROUNDS_IN_CARLA_BATCH: int = 3 #// number of CE rounds in CARLA batch
    BATCH_CARLA_SPEEDUP_FACTOR: int = 20 #//make N of CARLA's nBatch (last nBatch) 1/10'th of originally planned N (like 20*20*3*1*NUM_ROUNDS_IN_CARLA_BATCH/20 = 180 which is about ~3min
    CARLA_m: int = 5 #// to speed up CARLA sim, Matt: use m=3? IDK, if the distribution from prior batches was based on m=8...
    EPSILON: float = 0.0000001


