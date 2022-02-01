#the Art VanDelay imports/exports... but more imports than exports... and that's the problem
import pandas as pd
import os
import re
from itertools import chain
from datetime import date
import numpy as np
from openpyxl import load_workbook


main_folder = os.getcwd()
data_folder = main_folder +'\\Data\\'
xl_storage = main_folder + '\\XL Files\\'
figure_storage = main_folder + '\\Figures\\'
extract_data_folder = main_folder + '\\Put Your Data Here\\'





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

        
class Analyze():

    def __init__(self, file, dates_list, starttimes_list, subjects_list, msns_list, paradigms_list): 
        self.file = file
        self.dates = dates_list
        self.starttimes = starttimes_list
        self.subjects = subjects_list
        self.msns = msns_list
        self.paradigms = paradigms_list

        
        msn_check = self.msngrabber()
        if 'visual' in msn_check.lower() or 'bias shift' in msn_check.lower():
            self.maininfograbber()
            self.check_next()
        

    #Moved as static methods w/n class for namespace purposes- both are considered main info, but a small subset
    def msngrabber(self):
        with open(self.file,"r") as f:
            msnfinder = re.search(r"MSN:" + ".+" + "\n", f.read())
            msngrabber = msnfinder.group().split(":")
            return msngrabber[1].strip()



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
            self.paradigms.append(paradigmgrabber[1].strip())
        with open(self.file,"r") as f:
            startfinder = re.search(r"Start Time:" + ".+" + "\n",f.read())
            startgrabber = startfinder.group().split(": ")
            self.starttimes.append(pd.to_datetime(startgrabber[1].strip()).time())



#Adding functionality so that appended data files are extracted and moved to the correct folder for parsing
def findawholefile(file):
    starts = []
    ends = []
    with open(file, 'r') as f:
        starts.append(list(re.finditer(r"Start Date:", f.read())))
    for i,x in enumerate(starts[-1]):
        if i != len(starts[-1])-1:
            with open(file, 'r') as f:
                filefinder = (f.read()[starts[-1][i].start():starts[-1][i+1].start()])
                subject = re.search(r"Subject:" + ".+" + "\n", filefinder)
                subject = subject.group().split(":")
                subject = subject[1].strip()
                date = re.search(r"Start Date:" + ".+" + "\n", filefinder)
                date = date.group().split(":")
                date = date[1].replace('/','_').strip()
            with open(data_folder+f'Data from {subject} on {date}.txt', 'w') as writer:
                writer.write(filefinder)
        else:
            with open(file, 'r') as f:
                filefinder = (f.read()[starts[-1][i].start():])
                subject = re.search(r"Subject:" + ".+" + "\n", filefinder)
                subject = subject.group().split(":")
                subject = subject[1].strip()
                date = re.search(r"Start Date:" + ".+" + "\n", filefinder)
                date = date.group().split(":")
                date = date[1].replace('/','_').strip()
            with open(data_folder+f'Data from {subject} on {date}.txt', 'w') as writer:
                writer.write(filefinder)
        



#Main loop, where: extract appended data --> create arrays --> collect data
for i in os.listdir(extract_data_folder):
    file = extract_data_folder+i
    findawholefile(file = file)


dates =[]
starttimes = []
subjects = []
msns = []
paradigms = []
total_time = []
ll_presses = []
rl_presses = []
total_presses = []
ll_ts = []
rl_ts = []
fd_on_ll = []
fd_on_rl = []
fd_off_ll = []
fd_off_rl = []
fd_on_tot = []
fd_off_tot = []
fd_ll_p1 = []
fd_ll_p2 = []
fd_ll_p3 = []
fd_ll_p4 = []
fd_ll_p5 = []
fd_rl_p1 = []
fd_rl_p2 = []
fd_rl_p3 = []
fd_rl_p4 = []
fd_rl_p5 = []
fd_p1_tot = []
fd_p2_tot = []
fd_p3_tot = []
fd_p4_tot = []
fd_p5_tot = []


for i in os.listdir(data_folder):
    file = data_folder+ f'{i}'
    test = Analyze(file, dates, starttimes, subjects, msns, paradigms)
    test.maininfograbber()
    if 'food' in msns[-1].lower() or 'drug' in msns[-1].lower():
        
        #Get all of the general shit out of the way
        temper = []
        grab_a = ArrayParser(file, temper, 'A','B')
        grab_a.arraygrabber()
        ll_ts.append([float(i) for i in temper[-1]])
        temper = []
        grab_b = ArrayParser(file, temper, 'B', 'C')
        grab_b.arraygrabber()
        rl_ts.append([float(i) for i in temper[-1]])
        ll_presses.append(len(ll_ts[-1]))
        rl_presses.append(len(rl_ts[-1]))
        total_presses.append(ll_presses[-1]+rl_presses[-1])
        temper = []
        grab_d = ArrayParser(file, temper, 'D', 'E')
        grab_d.arraygrabber()
        total_time.append(float(temper[0][0])/60)
        
        max_time = float(temper[0][0])
        
        #Grab the start times for each of the phases
        phases_temp = []
        grab_c = ArrayParser(file, phases_temp, 'C','D')
        grab_c.arraygrabber()
        phase_starts = []
        for i in phases_temp[0]:
            phase_starts.append(float(i))
        phase_starts.append(max_time)
        
        
        #Track the on/off phases
        on_presses = 0
        off_presses = 0
        ll_p1 = 0
        ll_p2 = 0
        ll_p3 = 0
        ll_p4 = 0
        ll_p5 = 0
        for i in ll_ts[-1]:
            if phase_starts[0] <= i <= phase_starts[1] or phase_starts[2] <= i <= phase_starts[3] or phase_starts[4] <= i <= phase_starts[5]:
                on_presses +=1
                if phase_starts[0] <= i <= phase_starts[1]:
                    ll_p1 += 1
                elif phase_starts[2] <= i <= phase_starts[3]:
                    ll_p3 += 1
                elif phase_starts[4] <= i <= phase_starts[5]:
                    ll_p5 += 1
            else:
                off_presses +=1
                if phase_starts[1] <= i <= phase_starts[2]:
                    ll_p2 += 1
                elif phase_starts[3] <= i <= phase_starts[4]:
                    ll_p4 += 1
        fd_on_ll.append(on_presses)
        fd_off_ll.append(off_presses)
        fd_ll_p1.append(ll_p1)
        fd_ll_p2.append(ll_p2)
        fd_ll_p3.append(ll_p3)
        fd_ll_p4.append(ll_p4)
        fd_ll_p5.append(ll_p5)
        
        
        
        on_presses = 0
        off_presses = 0
        rl_p1 = 0
        rl_p2 = 0
        rl_p3 = 0
        rl_p4 = 0
        rl_p5 = 0
        
        
        for i in rl_ts[-1]:
            if phase_starts[0] <= i <= phase_starts[1] or phase_starts[2] <= i <= phase_starts[3] or phase_starts[4] <= i <= phase_starts[5]:
                on_presses +=1
                if phase_starts[0] <= i <= phase_starts[1]:
                    rl_p1 += 1
                elif phase_starts[2] <= i <= phase_starts[3]:
                    rl_p3 += 1
                elif phase_starts[4] <= i <= phase_starts[5]:
                    rl_p5 += 1
            else:
                off_presses += 1
                if phase_starts[1] <= i <= phase_starts[2]:
                    rl_p2 += 1
                elif phase_starts[3] <= i <= phase_starts[4]:
                    rl_p4 += 1
        fd_on_rl.append(on_presses)
        fd_off_rl.append(off_presses)
        
        fd_rl_p1.append(rl_p1)
        fd_rl_p2.append(rl_p2)
        fd_rl_p3.append(rl_p3)
        fd_rl_p4.append(rl_p4)
        fd_rl_p5.append(rl_p5)
        
        fd_on_tot.append(fd_on_ll[-1] + fd_on_rl[-1])
        fd_off_tot.append(fd_off_ll[-1] + fd_off_rl[-1])
        fd_p1_tot.append(rl_p1 + ll_p1)
        fd_p2_tot.append(rl_p2 + ll_p2)
        fd_p3_tot.append(rl_p3 + ll_p3)
        fd_p4_tot.append(rl_p4 + ll_p4)
        fd_p5_tot.append(rl_p5 + ll_p5)
        
        
        
persev_df_maker= {'Subject':subjects,
                 'Date' : dates,
                 'MSN': msns,
                 'Start Time': starttimes,
                 'Total Time (Minutes)' :total_time,
                 'Total Presses': total_presses,
                 'Left Lever Presses': ll_presses,
                 'Right Lever Presses': rl_presses,
                 'Food ON Total Presses': fd_on_tot,
                 'Food ON LL Presses' : fd_on_ll,
                 'Food ON RL Presses': fd_on_rl,
                 'Food OFF Total Presses': fd_off_tot,
                 'Food OFF LL Presses': fd_off_ll,
                 'Food OFF RL Presses': fd_off_rl,
                 'TOTAL Phase 1 Presses': fd_p1_tot,
                 'P1 LL Presses': fd_ll_p1,
                 'P1 RL Presses': fd_rl_p1,
                 'TOTAL Phase 2 Presses': fd_p2_tot,
                 'P2 LL Presses': fd_ll_p2,
                 'P2 RL Presses': fd_rl_p2,
                 'TOTAL Phase 3 Presses': fd_p3_tot,
                 'P3 LL Presses': fd_ll_p3,
                 'P3 RL Presses': fd_rl_p3,
                 'TOTAL Phase 4 Presses': fd_p4_tot,
                 'P4 LL Presses': fd_ll_p4,
                 'P4 RL Presses': fd_rl_p4,
                 'TOTAL P5 Presses': fd_p5_tot,
                 'P5 LL Presses': fd_ll_p5,
                 'P5 RL Presses': fd_rl_p5}

persev_df = pd.DataFrame(persev_df_maker)


today = date.today()
with pd.ExcelWriter(xl_storage+ f'Perseverance Data from {today}.xlsx') as writer:
    for i,x in persev_df.groupby('Subject'):
        x.to_excel(writer, sheet_name = i)


print('Data parsed and analyzed!')