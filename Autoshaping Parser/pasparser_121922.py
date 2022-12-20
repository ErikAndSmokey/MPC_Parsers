#The Art Van DeLay imports/exports... but more imports than exports... and that's the problem
import os
import re
import pandas as pd
import numpy as np
from datetime import date
from shutil import copyfile
import Emailer
import matplotlib.pyplot as plt

#Set your operating directory here
path_to_data = os.getcwd() + '\\PAS Data\\' #create a directory to match this structure if not Erik
path_to_pas_id = os.getcwd() + '\\Identifiers\\PAS Identifier.xlsx'
path_to_figures = os.getcwd() + '\\Figures\\'
path_to_xl = os.getcwd() + '\\XL Files\\'

plt.style.use('fivethirtyeight')


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
        return self.array_to_ap.append(arrayformatcolumn)
    
    def arraycleaner(self):
        for i in self.array_to_ap:
            for x in i:
                x.pop(0)
                
    def arrayvaluesstrip(self):
        for i,x in enumerate(self.array_to_ap):
            for c, b in enumerate(x):
                for d,e in enumerate(b):
                    b[d] = e.strip()
        return self.array_to_ap
    
    def grabtotals(self):
        for i in range(len(self.array_to_ap)):
            for x in range(len(self.array_to_ap[i])):
                for y in range(len(self.array_to_ap[i][x])):
                    if x == 3 and y == 1:
                        total_he.append(float(self.array_to_ap[i][x][y]))
                    elif x == 2 and y == 4:
                        total_csp_presses.append(float(self.array_to_ap[i][x][y]))
                    elif x == 2 and y == 5:
                        total_csm_presses.append(float(self.array_to_ap[i][x][y]))
                    else:
                        pass
                    
    def trial_start_times(self):
        times = []
        for i in self.array_to_ap:
                for x in range(len(i)):
                    for y in range(len(i[x])):
                        if x in range(2,7):
                            times.append((float(i[x][y])/100)) #Convert to seconds while adding to array
        self.array_to_ap.clear()       
        self.array_to_ap.append(times)
        return self.array_to_ap
    
    def he_times_grabber(self):
        delimiter = []
        headentrytimes = []
        for i,x in enumerate(self.array_to_ap):
            for y,z in enumerate(self.array_to_ap[i]):
                if len(self.array_to_ap[i][y]) == 0:
                    delimiter.append(y)
        for i in self.array_to_ap:
            for x in range(len(i)):
                for y in range(len(i[x])):
                    if x in range(0,max(delimiter)):
                        headentrytimes.append((float(i[x][y])/100)) #Convert to seconds while adding to array
                    else:
                        pass
        self.array_to_ap.clear()
        self.array_to_ap.append(headentrytimes)
        return self.array_to_ap
    
class MainInfoParser():
    
    def __init__(self,file,dates_list,subjects_list,msn_list,day_list):
        self.file = file
        self.dates = dates_list
        self.subjects = subjects_list
        self.msns = msn_list
        self.days = day_list
    
    def maininfograbber(self):
        with open(self.file,"r") as f:
            datefinder = re.search(r"Start Date:" + ".+" + "\n",f.read())
            dategrabber = datefinder.group().split(":")
            self.dates.append(dategrabber[1].strip())
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

class PASCalcs():
    
    def __init__(self,press_data_array, he_time_array, trial_start_time,
                 ap_array,total_he_trial_array,he_prob_array,total_lat_he_array,lat_he_prob_array):
        self.press_data_array = press_data_array
        self.he_time_array = he_time_array
        self.trial_start_time = trial_start_time
        self.ap_array = ap_array
        self.total_he_trial_array = total_he_trial_array
        self.he_prob_array = he_prob_array
        self.total_lat_he_array = total_lat_he_array
        self.lat_he_prob_array = lat_he_prob_array
        
    def approachprobability(self):
        for i in self.press_data_array:
            counter = 0
            for x in range(len(i)):
                for y in range(len(i[x])):
                    if i[x][y] == "0.000":
                        counter += 1
                    else:
                        counter += 0
        return self.ap_array.append((25-(counter-1))/25*100)
    
    def headentries(self):
        inter_trial_entries = 0
        inter_trial_id = []
        latent_entries = 0
        latent_trial_id = []
        for x in self.he_time_array[0]:
            for i in self.trial_start_time[0]:
                if i <= x <= i+10:
                    inter_trial_id.append(i)
                    inter_trial_entries += 1
                elif i+10.1 <= x <= i+20.1:
                    latent_trial_id.append(i)
                    latent_entries += 1
                else:
                    pass
        self.total_he_trial_array.append(inter_trial_entries)
        self.total_lat_he_array.append(latent_entries)
        self.he_prob_array.append(((25-(25-len(set(inter_trial_id))))/25)*100)
        self.lat_he_prob_array.append(((25-(25-len(set(latent_trial_id))))/25)*100)
        
#Lists for data collection
dates = []
subjects = []
msns = []
day = []
total_he = []
total_csp_presses = []
csp_ap = []
csp_he = []
csp_he_prob = []
csp_lat_he = []
csp_lat_he_prob = []
total_csm_presses = []
csm_ap = []
csm_he = []
csm_he_prob= []
csm_lat_he = []
csm_lat_he_prob = []
pca_score = []
avg_csp_p_latency = []
avg_csp_he_latency = []
all_prob_diff = []
all_latency_scores = []
all_response_bias = []
#Iterate through directory and extract data, place into data collection lists
counter = 0
trial_len = 10
for i in os.listdir(path_to_data):
    file = path_to_data+i
    totals_array = []
    he_time_stamps_array = []
    csm_start_array = []
    csp_presses_array = []
    csp_start_array = []
    csm_presses_array = []
    MainInfoParser(file,dates,subjects,msns,day).maininfograbber()
    totals = ArrayParser(file,totals_array,"C","E")
    totals.arraygrabber()
    totals.arrayvaluesstrip()
    totals.grabtotals()
    he_stamps = ArrayParser(file,he_time_stamps_array,"G","J")
    he_stamps.arraygrabber()
    he_stamps.arraycleaner()
    he_stamps.he_times_grabber()
    csm_start = ArrayParser(file,csm_start_array,"J","K")
    csm_start.arraygrabber()
    csm_start.arraycleaner()
    csm_start.trial_start_times()
    csp_presses = ArrayParser(file,csp_presses_array,"K","L")
    csp_presses.arraygrabber()
    csp_presses.arrayvaluesstrip()
    csp_start = ArrayParser(file,csp_start_array,"L","M")
    csp_start.arraygrabber()
    csp_start.arraycleaner()
    csp_start.trial_start_times()
    csm_presses = ArrayParser(file,csm_presses_array,"M","N")
    csm_presses.arraygrabber()
    csm_presses.arrayvaluesstrip()
    csp_calcs = PASCalcs(csp_presses_array,he_time_stamps_array,
                         csp_start_array,csp_ap,csp_he,csp_he_prob,
                         csp_lat_he,csp_lat_he_prob)
    csp_calcs.approachprobability()
    csp_calcs.headentries()
    csm_calcs = PASCalcs(csm_presses_array,he_time_stamps_array,
                         csm_start_array,csm_ap,csm_he,csm_he_prob,
                         csm_lat_he,csm_lat_he_prob)
    csm_calcs.approachprobability()
    csm_calcs.headentries()

#********************************BEGIN STUFF FOR PCA INDEX!!!!!!!!!!!****************************************************
    temp_csp_timestamps = []
    temp_he_timestamps = []
    csp_ts = []
    csp_start_array_pca = []
    csp_latency = []
    he_ts = []
    csp_he_latency = []


    get_csp_ts = ArrayParser(file, temp_csp_timestamps, 'P', 'T')
    get_csp_ts.arraygrabber()
    get_csp_ts.arraycleaner()

    csp_start_pca = ArrayParser(file,csp_start_array_pca,"L","M")
    csp_start_pca.arraygrabber()
    csp_start_pca.arraycleaner()
    csp_start_pca.trial_start_times()

    he_stamps_pca = ArrayParser(file,temp_he_timestamps,"G","J")
    he_stamps_pca.arraygrabber()
    he_stamps_pca.arraycleaner()
    he_stamps_pca.he_times_grabber()

    #Casually make a list of all the times in a cleaner format...
    for i in temp_csp_timestamps:
        for x in i:
            for z in x:
                csp_ts.append(float(z)/100)

    #Latnecy finder...
    for i in csp_start_array:
        for x in i:
            end = (x + trial_len)
            first_instance = 0
            for z in csp_ts:
                if x <= z <= end and first_instance == 0:
                    csp_latency.append(z-x)
                    first_instance += 1
                elif z == csp_ts[-1] and first_instance == 0:
                    csp_latency.append(trial_len) #basically, max the latency by appending with trial length (0 action at lever)
                    first_instance += 1
                else:
                    pass

    #Clean head entry timestamp list            
    for i in temp_he_timestamps:
        for x in i:
            he_ts.append(x)

    for i in csp_start_array:
        for x in i:
            end = (x + trial_len)
            first_instance = 0
            for z in he_ts:
                if x <= z <= end and first_instance == 0:
                    csp_he_latency.append(z-x)
                    first_instance += 1
                elif z == he_ts[-1] and first_instance == 0:
                    csp_he_latency.append(trial_len)#basically, max the latency by appending with trial length (0 action at lever)
                    first_instance += 1
                else:
                    pass
                
           
    avg_csp_p_latency.append(np.nan_to_num(np.mean(csp_latency)))
    avg_csp_he_latency.append(np.nan_to_num(np.mean(csp_he_latency)))
    latency_score = np.nan_to_num((np.nanmean(csp_latency)-np.nanmean(csp_he_latency))/trial_len)
    

    try:
        prob_diff = (csp_ap[-1]/100)-(csp_he_prob[-1]/100)
    except IndexError:   
        prob_diff = np.nan
    if np.isnan(prob_diff) == True or prob_diff == 0.0:
        pca_score.append(np.nan)
        all_prob_diff.append(np.nan)
        all_response_bias.append(np.nan)
        all_latency_scores.append(np.nan)
        counter += 1
    else:
        response_bias = (total_csp_presses[-1] - csp_he[-1])/(total_csp_presses[-1]+csp_he[-1])
        pca_score.append((latency_score + response_bias + prob_diff)/3)
        all_prob_diff.append(prob_diff)
        all_response_bias.append(response_bias)
        all_latency_scores.append(latency_score)
        counter += 1

#********************************END STUFF FOR PCA INDEX!!!!!!!!!!!****************************************************    
    
    
#DataFrame builder (create main df, then add additional columns for analysis and perform analysis)
importantinfo = {"Date": dates,
                "Subject":subjects,
                "Program":msns,
                "Day": day,
                'PCA Score': pca_score,
                "CS+ AP (%)": csp_ap,
                "CS- AP (%)": csm_ap,
                "CS+ HE Probability (%)": csp_he_prob,
                "CS- HE Probability (%)": csm_he_prob,
                "CS+ Latent HE Prob (%)":csp_lat_he_prob,
                "CS- Latent HE Prob (%)":csm_lat_he_prob,
                "Head Entries": total_he,
                "CS+ Total Presses": total_csp_presses,
                "CS- Total Presses": total_csm_presses,
                "Total CS+ Head Entries":csp_he,
                "Total Latent CS+ HEs":csp_lat_he,
                "Total CS- Head Entries": csm_he,
                "Total Latent CS- HEs":csm_lat_he,
                'CS+ Deflection Latency': avg_csp_p_latency,
                'CS+ HE Latency': avg_csp_he_latency,
                'Goal Approach Diff': all_prob_diff,
                'Response Bias': all_response_bias,
                'Latency Score': all_latency_scores}

df = pd.DataFrame(importantinfo)
df['Date'] = pd.to_datetime(df.Date) #Uniformly format the date for sorting purposes
df['Subject']= [i.upper().replace(' ','') for i in df['Subject']] #Uniformly format the subject names
df.sort_values(['Subject','Date'],inplace=True)

range_by_animal = [] #This is a list for collecting all the day numbers- needs to be after the sort
for i in df.groupby('Subject'):
    x = range(1,len(i[1])+1)
    for num in x:
        range_by_animal.append(num)
df['Day Number'] = range_by_animal #in essence, sort by date and then use the sorting to create a list of day nums based on date


#################################################TESTSETSETSETSTSETSETSET##############################################
#Create a dictionary to define controls vs. experimentals
dfgroups = pd.ExcelFile(path_to_pas_id).parse()

sexes = []
groups = []
for i in df['Subject']:
    sexes.append(dfgroups['Sex'][dfgroups['ID'] == i].values[-1])
    groups.append(dfgroups['Group'][dfgroups['ID'] == i].values[-1])


df['Subject Sex'] = sexes
df['Subject Group'] = groups
        
        
        
        
        
        
        
dfmean = df.groupby(['Subject Group', 'Subject Sex', 'Day Number']).mean()
dfsem = df.groupby(['Subject Group','Subject Sex', 'Day Number']).sem()


#Build excel file info
file = "PAS Data From " + str(date.today()) + ".xlsx"
save_xl_path = path_to_xl + file
with pd.ExcelWriter(save_xl_path) as writer:
        #First, collect all the data, by day, for individual analysis
        for i,x in df.groupby("Day Number"):
            x.to_excel(writer,sheet_name = "Day " + str(i).split('.')[0])
        #Next, add in all your analysis to the workbook as separate sheets
        dfmean.to_excel(writer,sheet_name = "AVERAGES")
        dfsem.to_excel(writer,sheet_name = "SEM")