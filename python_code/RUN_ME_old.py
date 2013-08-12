import sys
import os
import time
import multiprocessing
import subprocess
from multiprocessing import *

from MyDict import *
#import MyCommon 
import setup_directories

import get_bolt 
import get_lucky 
import get_greyhound 
import get_fungwah 
import get_peterpan 
import get_mega 
import get_gobus 
import get_amtrack
import get_eastern 

def run_task_id(id_input):
        
        id_int=id_input[0]
        day_array=id_input[1]
        
        if id_int == 1:
                get_bolt.MyCatcher(day_array).iterate_jobs()
        if id_int == 2:
                get_lucky.MyCatcher(day_array).iterate_jobs()
        if id_int == 3:
                get_greyhound.MyCatcher(day_array).iterate_jobs()
        if id_int == 4:
                get_fungwah.MyCatcher(day_array).iterate_jobs()
        if id_int == 5:
                get_peterpan.MyCatcher(day_array).iterate_jobs()
        if id_int == 6:
                get_mega.MyCatcher(day_array).iterate_jobs()
        if id_int == 7:
                get_gobus.MyCatcher(day_array).iterate_jobs()
        if id_int == 8:
                get_amtrack.MyCatcher(day_array).iterate_jobs()
        if id_int == 9: 
                get_eastern.MyCatcher(day_array).iterate_jobs()
                
def run_makeup_id(id_int):
        
        if id_int == 1:
                get_bolt.MyCatcher(do_makeups=True).iterate_jobs()
        if id_int == 2:
                get_lucky.MyCatcher(do_makeups=True).iterate_jobs()
        if id_int == 3:
                get_greyhound.MyCatcher(do_makeups=True).iterate_jobs()
        if id_int == 4:
                get_fungwah.MyCatcher(do_makeups=True).iterate_jobs()
        if id_int == 5:
                get_peterpan.MyCatcher(do_makeups=True).iterate_jobs()
        if id_int == 6:
                get_mega.MyCatcher(do_makeups=True).iterate_jobs()
        if id_int == 7:
                get_gobus.MyCatcher(do_makeups=True).iterate_jobs()
        if id_int == 8: 
                get_amtrack.MyCatcher(do_makeups=True).iterate_jobs()
        if id_int == 9: 
                get_eastern.MyCatcher(do_makeups=True).iterate_jobs()

def main():
        
        print sys.argv[1]
        
        # assign day_array only if we aren't doing makeups
        if sys.argv[1] == "makeup":
                day_array=None
        
        # if we aren't running makeups
        else:
                if sys.argv[1] == "clean":
                        day_array=range(0,11)
                elif sys.argv[1] == "short":
                        day_array=[0,1,2]
                elif sys.argv[1] == "long": 
                        day_array=[3,4,5,6,7,8,9,10,11]
                elif sys.argv[1] == "medium": 
                        day_array = [0,1,2,3,4,5,6,7,8,9]
                        
        if sys.argv[2] == "1":
                task_id_array = [1,9,7]
        elif sys.argv[2] == "2":
                task_id_array = [3,5,6,8]
	elif sys.argv[2] == "all": 
		task_id_array = [1,9,7,3,5,6,8]
                
        p=[]
        
        if day_array: 
                tasks = [(task_id,day_array) for task_id in task_id_array]
                my_fcn = run_task_id
        else: 
                tasks = task_id_array
                my_fcn = run_makeup_id

        for task in tasks: 
                p.append(Process(target=my_fcn,args=([task])))
                p[-1].start()
                time.sleep(100)
        
        for pp in p:
                pp.join()
        
main()

