#!/usr/bin/env python

#NATIVE PYTHON IMPORTS
import time

#INSTALLED PACKAGE IMPORTS

#IMPORTS FROM THIS PACKAGE


if __name__ == '__main__':
    from ce_python.testcase_adv5only_accel import TestCase_Adv5Only_accel
    try:
        start_time = time.time()
        TestCase_Adv5Only_accel.test_class()
    except KeyboardInterrupt:
        print("User interrupted by keyboard")
    finally:
        seconds = time.time() - start_time
        print(f"For a data set of size: {TestCase_Adv5Only_accel.DATA_SET_SIZE}, Time Taken: {time.strftime('%H:%M:%S',time.gmtime(seconds))}")