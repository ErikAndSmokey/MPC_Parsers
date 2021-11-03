#The Art VanDeLay imports/exports... but more imports than exports... and that's his problem
import pandas as pd
import os
import re
from itertools import chain
from datetime import date
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns




#These functions work for all file types... note the "specific" functions below
class MainInfoParser():
    
    def __init__(self,file,dates_list,start_time_list,subjects_list,msn_list,day_list):
        self.file = file
        self.dates = dates_list
        self.start = start_time_list
        self.subjects = subjects_list
        self.msns = msn_list
        self.days = day_list
        
    
    def maininfograbber(self):
        with open(self.file,"r") as f:
            datefinder = re.search(r"Start Date:" + ".+" + "\n",f.read())
            dategrabber = datefinder.group().split(":")
            self.dates.append(pd.to_datetime(dategrabber[1].strip()).date())
        with open(self.file,"r") as f:
            subjectfinder = re.search(r"Subject:" + ".+" + "\n", f.read())
            subjectgrabber = subjectfinder.group().split(":")
            self.subjects.append(subjectgrabber[1].strip())
        with open(self.file,"r") as f:
            msnfinder = re.search(r"MSN:" + ".+" + "\n", f.read())
            msngrabber = msnfinder.group().split(":")
            self.msns.append(msngrabber[1].strip())
        with open(self.file,"r") as f:
            paradigmfinder = re.search(r"Experiment:" + ".+" + "\n",f.read())
            paradigmgrabber = paradigmfinder.group().split(": ")
            self.days.append(paradigmgrabber[1].strip())
        with open(self.file,"r") as f:
            startfinder = re.search(r"Start Time:" + ".+" + "\n",f.read())
            startgrabber = startfinder.group().split(": ")
            self.start.append(pd.to_datetime(startgrabber[1].strip()).time())
            
            
    #Moved as static methods w/n class for namespace purposes- both are considered main info, but a small subset
    @staticmethod
    def msngrabber(file):
        with open(file,"r") as f:
            msnfinder = re.search(r"MSN:" + ".+" + "\n", f.read())
            msngrabber = msnfinder.group().split(":")
            return msngrabber[1].strip()
    @staticmethod
    def dayofparadigm(file):
        with open(file,"r") as f:
            paradigmfinder = re.search(r"Experiment:" + ".+" + "\n",f.read())
            paradigmgrabber = paradigmfinder.group().split(": ")
            return paradigmgrabber[1].strip()

        

class ArrayParser():
    
    def __init__(self,file,array_to_append,upper_delimiter,lower_delimiter):
        self.file = file
        self.array_to_ap = array_to_append
        self.upper = upper_delimiter
        self.lower = lower_delimiter


    def arraygrabber(self):
        with open(self.file,"r") as f:
            arrayfinder = re.search(fr"\n{self.upper}:", f.read())
            arraystart = arrayfinder.start()
        with open(self.file,"r") as f:
            arrayendfinder = re.search(fr"\n{self.lower}:", f.read())
            arrayend = arrayendfinder.start()
        with open(self.file,"r") as f:
            arrayfull = (f.read()[arraystart:arrayend + 1])
            arraystrip = arrayfull.strip(" ")
            arraysplitnewline = arraystrip.split("\n")
            arrayformat1 = (i.strip(" ") for i in arraysplitnewline)
            arrayformatcolumn = [re.split(r"\s{2,8}",i) for i in arrayformat1]
        return self.array_to_ap.append(list(chain.from_iterable(i[1:] for i in arrayformatcolumn)))


    def endarraygrabber(self):
        with open(self.file,'r') as f:
            arrayfinder = re.search(fr'\n{self.upper}:', f.read())
            arraystart = arrayfinder.start()
        with open(self.file,'r') as f:
            arrayfull = (f.read()[arraystart:])
            arraystrip = arrayfull.strip(" ")
            arraysplitnewline = arraystrip.split('\n')
            arrayformat1 = (i.strip(' ') for i in arraysplitnewline)
            arrayformat2 = [re.split(r'\s{2,8}',i) for i in arrayformat1]
            return self.array_to_ap.append(list(chain.from_iterable(i[1:] for i in arrayformat2)))





main_folder = os.getcwd()
path_to_data = main_folder + '\\Data\\'




subjects = []
dates = []
msn = []
experiment = []
correct_presses = []
total_time = []
starttimes = []
max_allowed = []
first_press_latency = []
pass_check = []



incorrect_presses = []
last_completed = []
remainder = []

for i in os.listdir(path_to_data):
    print(i)
    file = path_to_data + i
    msn_check = MainInfoParser.msngrabber(file)
    main_info = MainInfoParser(file,dates,starttimes,subjects,msn,experiment)
    main_info.maininfograbber()
    if 'food' in msn_check.lower():
        total_presses_temp = []
        get_presses = ArrayParser(file, total_presses_temp, 'A','B')
        get_presses.arraygrabber()
        correct_presses.append(int(float(total_presses_temp[-1][0])))

        if total_presses[-1] >= 50:
            pass_check.append('Run test')
        else:
            pass_check.append('Run food')


        total_time_temp = []
        get_total_time = ArrayParser(file, total_time_temp, 'T', 'U')
        get_total_time.arraygrabber()
        total_time.append(int(float(total_time_temp[-1][0]))/60)
        temp_max_allowed = []
        get_max_allowed = ArrayParser(file, temp_max_allowed, 'B','D')
        get_max_allowed.arraygrabber()
        max_allowed.append(int(float(temp_max_allowed[-1][0])))
        temp_latency = []
        get_first_press_latency = ArrayParser(file, temp_latency, 'C','NONE')
        get_first_press_latency.endarraygrabber()
        first_press_latency.append(float(temp_latency[-1][0]))



    elif 'test' in msn_check.lower():
        #Grab the total correct lever presses
        total_presses_temp = []
        get_presses = ArrayParser(file, total_presses_temp, 'A','B')
        get_presses.arraygrabber()
        correct_presses.append(int(float(total_presses_temp[-1][0])))

        #Grab the total incorrect lever presses
        temp_incorrect = []
        get_incorrect = ArrayParser(file, temp_incorrect, 'B','D')
        get_incorrect.arraygrabber()
        incorrect_presses.append(int(float(temp_incorrect[-1][0])))

        #Grab the total time
        total_time_temp = []
        get_total_time = ArrayParser(file, total_time_temp, 'T', 'U')
        get_total_time.arraygrabber()
        total_time.append(int(float(total_time_temp[-1][0]))/60)


        #Create the increment slider (array F... the thing that allows you to move across the E array)
        temp_increment = []
        get_increment_mover = ArrayParser(file, temp_increment, 'F','G')
        get_increment_mover.arraygrabber()
        increment_slider = int(float(temp_increment[-1][0]))

        #Figure out what the last completed increment was
        temp_available_increments = []
        get_available_increments = ArrayParser(file, temp_available_increments, 'E','J')
        get_available_increments.arraygrabber()
        available_increments = [float(int(i)) for i in temp_available_increments[-1][0]]
        last_completed.append(available_increments[increment_slider-1])

        #Remainder since last increment
        remainder.append(correct_presses - sum(available_increments[0:increment_slider+1]))






    else:
        pass




df_maker = {'Subject': subjects,
            'Date': dates,
            'MSN': msn,
            'Day of paradigm': experiment,
            'Session Total Time (min)': total_time,
            'Max Allowed Presses': max_allowed,
            'Correct Presses': correct_presses,
            'First Press Latency': first_press_latency,
            'Move to test?': pass_check}


df = pd.DataFrame(df_maker)


with pd.ExcelWriter(main_folder + f'\\XL Files\\PR Data from {date.today()}.xlsx') as writer:
    for i,x in df.groupby('Subject'):
        x.to_excel(writer, sheet_name = i)