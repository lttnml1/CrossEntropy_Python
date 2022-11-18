#!/usr/bin/env python

#NATIVE PYTHON IMPORTS
import time

#INSTALLED PACKAGE IMPORTS

#IMPORTS FROM THIS PACKAGE


if __name__ == '__main__':

    CE_SEARCH = False
    CARLA_RUN = False
    ANALYZE_FILES = False
    
    if(CE_SEARCH):
        from ce_python.testcase_adv5only_accel import TestCase_Adv5Only_accel
        try:
            start_time = time.time()
            TestCase_Adv5Only_accel.test_class()
        except KeyboardInterrupt:
            print("User interrupted by keyboard")
        finally:
            seconds = time.time() - start_time
            print(f"For a data set of size: {TestCase_Adv5Only_accel.DATA_SET_SIZE}, Time Taken To Create: {time.strftime('%H:%M:%S',time.gmtime(seconds))}")
    

    if(CARLA_RUN):
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
                    print(file)
                    s = CARLA.Scenario(os.path.join(data_path,file))
                    s.game_loop()
                    counter += 1
        finally:
            seconds = time.time() - start_time
            print(f"For a data set of size: {counter}, Time Taken To Replay: {time.strftime('%H:%M:%S',time.gmtime(seconds))}")
    
    if(ANALYZE_FILES):
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
    
    

    
    from ce_python import CARLA
    files = [
        "C:\\Users\\m.litton_local\\CrossEntropy_Python\\data_archive\\left_to_right_lane_change_highway\\data\\0_perturbed.txt",
        "C:\\Users\\m.litton_local\\CrossEntropy_Python\\data_archive\\left_to_right_lane_change_highway\\data\\0_vanilla.txt",
        "C:\\Users\\m.litton_local\\CrossEntropy_Python\\data_archive\\left_to_right_lane_change_highway\\data\\99_perturbed.txt",
        "C:\\Users\\m.litton_local\\CrossEntropy_Python\\data_archive\\left_to_right_lane_change_highway\\data\\99_vanilla.txt",
        

        "C:\\Users\\m.litton_local\\CrossEntropy_Python\\data_archive\\right_to_left_lane_change_highway\\data\\2_perturbed.txt",
        "C:\\Users\\m.litton_local\\CrossEntropy_Python\\data_archive\\right_to_left_lane_change_highway\\data\\2_vanilla.txt",
        "C:\\Users\\m.litton_local\\CrossEntropy_Python\\data_archive\\right_to_left_lane_change_highway\\data\\99_perturbed.txt",
        "C:\\Users\\m.litton_local\\CrossEntropy_Python\\data_archive\\right_to_left_lane_change_highway\\data\\99_vanilla.txt",
        
    ]

    f = ["C:\\Users\\m.litton_local\\CrossEntropy_Python\\data_archive\\left_to_right_lane_change_highway\\data\\99_vanilla.txt"]
    for file in files:
        s = CARLA.Scenario(file)
        s.game_loop()
        time.sleep(2)
    