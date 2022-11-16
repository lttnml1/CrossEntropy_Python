#!/usr/bin/env python

#NATIVE PYTHON IMPORTS
import time

#INSTALLED PACKAGE IMPORTS

#IMPORTS FROM THIS PACKAGE


if __name__ == '__main__':
    """
    from ce_python.testcase_adv5only_accel import TestCase_Adv5Only_accel
    try:
        start_time = time.time()
        TestCase_Adv5Only_accel.test_class()
    except KeyboardInterrupt:
        print("User interrupted by keyboard")
    finally:
        seconds = time.time() - start_time
        print(f"For a data set of size: {TestCase_Adv5Only_accel.DATA_SET_SIZE}, Time Taken To Create: {time.strftime('%H:%M:%S',time.gmtime(seconds))}")
    """
    #****************************
    #Now run the paths in CARLA
    #****************************

    
    import os
    import pathlib
    import CARLA

    data_path = os.path.join(pathlib.Path(__file__).parent.parent.resolve(),"data\\")
    try:
        counter = 0
        start_time = time.time()
        for dirName, subdirList, fileList in os.walk(data_path):
            for file in fileList:
                if("VARIANCES" in file):
                    continue
                s = CARLA.Scenario(os.path.join(data_path,file))
                s.game_loop()
                counter += 1
    finally:
        seconds = time.time() - start_time
        print(f"For a data set of size: {counter}, Time Taken To Replay: {time.strftime('%H:%M:%S',time.gmtime(seconds))}")
    

    #****************************
    #Now we see how many accidents/non-accidents
    #****************************

    import pandas as pd
    import os
    import pathlib
    data_path = os.path.join(pathlib.Path(__file__).parent.parent.resolve(),"features\\")
    num_with_accidents = 0
    num_without_accidents = 0
    for dirName, subdirList, fileList in os.walk(data_path):
        for file in fileList:
            df = pd.read_csv(os.path.join(data_path,file),index_col=0)
            if(True in df['intersect'].unique()):
                num_with_accidents += 1
            else:
                num_without_accidents += 1
    
    print("********************************************************\n")
    print(f"FILES WITH ACCIDENTS: {num_with_accidents}")
    print(f"FILES WITHOUT ACCIDENTS: {num_without_accidents}")
    print("********************************************************\n")



    