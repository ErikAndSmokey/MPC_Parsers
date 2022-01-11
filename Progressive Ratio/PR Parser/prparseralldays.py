#The Art VanDeLay imports/exports... but more imports than exports... and that's his problem
import pandas as pd
import os
import re
from itertools import chain
from datetime import date
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from shutil import copyfile



#Grab the directory that the script is located in.. create any other file paths here
main_folder = os.getcwd()
path_to_data = main_folder + '\\Data\\'
path_to_save = main_folder + '\\XL FILES\\'
path_to_figures = main_folder + '\\Figures\\'

plt.style.use('fivethirtyeight')

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
        
    @staticmethod 
    def subject_grabber(file):
        with open(file,"r") as f:
            subjectfinder = re.search(r"Subject:" + ".+" + "\n", f.read())
            subjectgrabber = subjectfinder.group().split(":")
            #self.subjects.append(subjectgrabber[1].strip())
            return subjectgrabber[1].strip()
        
    @staticmethod
    def date_grabber(file):
        with open(file,"r") as f:
            datefinder = re.search(r"Start Date:" + ".+" + "\n",f.read())
            dategrabber = datefinder.group().split(":")
            #self.dates.append(pd.to_datetime(dategrabber[1].strip()).date())
            #return pd.to_datetime(dategrabber[1].strip().date())
            return dategrabber[1].strip()


        

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

        
        
def create_groups(df): 
    dfgroups = pd.ExcelFile(main_folder +'\\Group Identifier.xlsx').parse() #FILE PATH!
    control_name = dfgroups.keys()[0] #Handles group ID name changes
    experimental_name = dfgroups.keys()[1] #Handles group ID name changes
    listofcontrols = [str(i).upper() for i in dfgroups[control_name]] #Because df to df comparisons weren't working...
    listofexps = [str(i).upper() for i in dfgroups[experimental_name]] #Because df to df comparisons weren't working...
    group_column = []
    for i in df['Subject']:
        if i.upper() in listofcontrols:
            group_column.append(dfgroups.columns[0]) #You can change the names of the columns to match the study!
        elif i.upper() in listofexps:
            group_column.append(dfgroups.columns[1]) #You can change the names of the columns to match the study!
        else:
            group_column.append('NaN') #Because we need to match the df lengths
            print(f'{i} is not in your Group Identifier spreadsheet!!!! Please Check!!!')
    return df.insert(0,'Group', group_column)


    
def day_numberer(df):
    #Create a 'day number' column by animal (i.e., see what day of the paradigm each individual animal is on)
    range_by_animal = [] #This is a list for collecting all the day numbers- needs to be after the sort
    for i in df.groupby('Subject'):
        x = range(1,len(i[1])+1)
        for num in x:
            range_by_animal.append(num)
    return df.insert(1,'Day Number', range_by_animal)      


def the_dots_graph(test_subjects, test_max_time, test_cts,test_its,test_trial_finishes):
    cts_fg = list(zip(test_subjects, test_max_time, test_cts))
    cts_fg.sort()
    its_fg = list(zip(test_subjects, test_max_time, test_its))
    its_fg.sort()
    trialcomps_fg = list(zip(test_subjects, test_max_time, test_trial_finishes))
    trialcomps_fg.sort()

    plt.figure(figsize = (24,24))


    a = 1
    for i in trialcomps_fg:
        why = [i[0] for x in range(1,len(i[2])+1)]
        plt.scatter(y = i[2], x = why, alpha=0.5, s = 1500)

    a = 1
    for i in its_fg:
        why = [i[0] for x in range(1,len(i[2])+1)]
        plt.scatter (y = i[2], x = why, alpha = 0.3, s=500,marker = 'X', c= 'r')
        a +=1

    a=1
    for i in cts_fg:
        why = [i[0] for x in range(1,len(i[2])+1)]
        plt.scatter (y = i[2], x = why, alpha = 0.4, s=200)
        a +=1

    plt.ylabel('Correct Timestamp (seconds)', fontsize = 22)
    plt.xticks(fontsize = 18)
    plt.yticks(fontsize = 18)

    plt.savefig(path_to_figures+ f'Incorrect + Correct Timestamps vs. Session Time from {date.today()}.png', dpi= 300)

    
    
    
def individ_rr_graphs(df):
    df_indiv = df.explode('All ITRR')
    df_indiv['ITRR (resp/min)'] = df_indiv['All ITRR'].astype('float')
    set_o_subs = list(set(df_indiv.index))
    day_nums = list(set(df_indiv['Day Number']))
    x = round(np.sqrt(len(set_o_subs)))
    y = round(np.sqrt(len(set_o_subs)))


    fig,axes = plt.subplots(x,y, figsize = (24,36))


    a= 0
    b= 0
    for i in set_o_subs:
        for day in day_nums:
            sns.lineplot(x = list(range(1,len(df_indiv[(df_indiv.index == i) & (df_indiv['Day Number'] == day)])+1,1)), 
                        y = 'ITRR (resp/min)', data = df_indiv[(df_indiv.index == i) & (df_indiv['Day Number'] == day)], ax = axes[a,b], hue= 'Day Number')
        axes[a,b].set_title(i)
        if b >= y-1:
            a += 1
            b = 0
        else:
            b += 1
    plt.savefig(path_to_figures + f'Individual inter-trial response rates from {date.today()}.png', dpi = 300)

def summary_by_day_graphs(df):
    fig2,axes2 = plt.subplots(2,2, figsize = (36,24) )


    sns.barplot(x = 'Group', y = 'Correct Presses', data= df, ci = 68, hue= 'Day Number', ax= axes2[0,0])
    sns.barplot(x = 'Group', y = 'Response Rate (resp/min)', data = df, ci = 68, hue='Day Number', ax = axes2[0,1])
    sns.barplot(x = 'Group', y = 'Incorrect Presses', data = df, ci=68, hue ='Day Number', ax = axes2[1,0])
    sns.barplot(x = 'Group', y = 'Correct Presses', data= df, ci = 68, hue= 'Day Number', ax = axes2[1,1])

    plt.savefig(path_to_figures + f'PR Graphs BY DAY from {date.today()}.png', dpi = 300)


def summary_graphs(df):
    fig3,axes3 = plt.subplots(2,2, figsize = (36,24) )


    sns.barplot(x = 'Group', y = 'Correct Presses', data= df, ci = 68,ax= axes3[0,0])
    sns.barplot(x = 'Group', y = 'Response Rate (resp/min)', data = df, ci = 68,  ax = axes3[0,1])
    sns.barplot(x = 'Group', y = 'Incorrect Presses', data = df, ci=68, ax = axes3[1,0])
    sns.barplot(x = 'Group', y = 'Correct Presses', data= df, ci = 68,  ax = axes3[1,1])

    plt.savefig(path_to_figures + f'PR Graphs from {date.today()}.png', dpi = 300)







def parse():
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


    test_subjects = []
    test_dates = []
    test_starttimes = []
    test_msns = []
    test_experiments = []
    test_total_time=  []
    test_correct_presses = []
    test_incorrect_presses = []
    test_breakpoint = []
    test_last_completed_increment = []
    test_remainder = []
    test_response_rate = []
    test_itt_mean = []
    test_itt_q1 = []
    test_itt_q2 = []
    test_itt_q3 = []
    test_cts = []
    test_max_time = []
    test_its = []
    test_trial_finishes = []

    all_itrr = []




    for i in os.listdir(path_to_data):
        print(i)
        file = path_to_data + i
        msn_check = MainInfoParser.msngrabber(file)
        if 'food' in msn_check.lower():
            main_info = MainInfoParser(file,dates,starttimes,subjects,msn,experiment)
            main_info.maininfograbber()
            total_presses_temp = []
            get_presses = ArrayParser(file, total_presses_temp, 'A','B')
            get_presses.arraygrabber()
            correct_presses.append(int(float(total_presses_temp[-1][0])))

            if correct_presses[-1] >= 50:
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



        else:
            test_main_info = MainInfoParser(file,test_dates,test_starttimes,test_subjects,test_msns,test_experiments)
            test_main_info.maininfograbber()


            #Grab the total correct lever presses
            total_presses_temp = []
            get_presses = ArrayParser(file, total_presses_temp, 'A','B')
            get_presses.arraygrabber()
            test_correct_presses.append(int(float(total_presses_temp[-1][0])))

            #Grab the total incorrect lever presses
            temp_incorrect = []
            get_incorrect = ArrayParser(file, temp_incorrect, 'B','D')
            get_incorrect.arraygrabber()
            test_incorrect_presses.append(int(float(temp_incorrect[-1][0])))

            #Grab the total time
            total_time_temp = []
            get_total_time = ArrayParser(file, total_time_temp, 'T', 'U')
            get_total_time.arraygrabber()
            test_total_time.append(int(float(total_time_temp[-1][0]))/60)

            #Grab the response rate per min
            test_response_rate.append(test_correct_presses[-1]/test_total_time[-1])


            #Create the increment slider (array F... the thing that allows you to move across the E array)
            temp_increment = []
            get_increment_mover = ArrayParser(file, temp_increment, 'F','G')
            get_increment_mover.arraygrabber()
            increment_slider = int(float(temp_increment[-1][0]))
            test_breakpoint.append(increment_slider) #this is the animal's progressive ratio breakpoint

            #Figure out what the last completed increment was
            temp_available_increments = []
            get_available_increments = ArrayParser(file, temp_available_increments, 'E','J')
            get_available_increments.arraygrabber()
            available_increments = [int(float(i)) for i in temp_available_increments[-1]]
            test_last_completed_increment.append(available_increments[increment_slider-1])

            #Remainder since last increment
            test_remainder.append(sum(available_increments[0:increment_slider+1]) - test_correct_presses[-1])

            #Avg. time spent per trial
            temp_trial_timestamps = []
            get_trial_timestamps = ArrayParser(file, temp_trial_timestamps, 'C', 'E')
            get_trial_timestamps.arraygrabber()
            trial_timestamps = [float(i) for i in temp_trial_timestamps[-1]]
            test_trial_finishes.append(trial_timestamps)
            inter_trial_time = []
            for i,x in enumerate(trial_timestamps):
                if i == 0:
                    inter_trial_time.append(x)
                elif i != 0:
                    inter_trial_time.append((x - trial_timestamps[i-1])-10)

            test_itt_mean.append(np.mean(inter_trial_time))
            test_itt_q1.append(np.percentile(inter_trial_time, 25))
            test_itt_q2.append(np.percentile(inter_trial_time, 50)) #median
            test_itt_q3.append(np.percentile(inter_trial_time, 75))

            temp_correct_timestamps = []
            get_cts = ArrayParser(file, temp_correct_timestamps, 'J','L')
            get_cts.arraygrabber()
            test_cts.append([float(i) for i in temp_correct_timestamps[-1]])
            test_max_time.append(list(np.linspace(0,max(test_cts[-1]),len(test_cts[-1]))))

            temp_incorrect_timestamps = []
            get_its = ArrayParser(file, temp_incorrect_timestamps, 'L', 'NONE')
            get_its.endarraygrabber()
            test_its.append([float(i) for i in temp_incorrect_timestamps[-1]])

            itrr = []
            for i,x in enumerate(trial_timestamps):
                if i == 0:
                    itrr.append(available_increments[i]/((trial_timestamps[i]-1)/60))
                else:
                    itrr.append(available_increments[i]/((trial_timestamps[i] -trial_timestamps[i-1] - 5)/60))
            all_itrr.append(itrr)






    #All things FOOD dataframe
    food_df_maker = {'Subject': subjects,
                'Date': dates,
                'MSN': msn,
                'Day of paradigm': experiment,
                'Session Total Time (min)': total_time,
                'Max Allowed Presses': max_allowed,
                'Correct Presses': correct_presses,
                'First Press Latency': first_press_latency,
                'Move to test?': pass_check}


    food_df = pd.DataFrame(food_df_maker)
    food_df.sort_values(['Subject','Date'], ascending = (True,True), inplace= True)
    create_groups(food_df)
    day_numberer(food_df)

    food_df.set_index('Subject', inplace = True)


    #All things TEST dataframe
    test_df_maker = {'Subject': test_subjects,
                    'Date': test_dates,
                    'MSN': test_msns,
                    'Day of paradigm': test_experiments,
                    'Session Total Time (Min)': test_total_time,
                     'Last Completed Increment': test_last_completed_increment,
                     'Remainder after lst increment': test_remainder,
                    'Correct Presses': test_correct_presses,
                    'Response Rate (resp/min)': test_response_rate,
                    'Breaking Point': test_breakpoint,
                    'Incorrect Presses': test_incorrect_presses,
                    'ITT mean': test_itt_mean,
                    'ITT q1': test_itt_q1,
                    'ITT median': test_itt_q2,
                    'ITT q3': test_itt_q3,
                    'All ITRR': all_itrr}


    line_graph_df_maker = {'Subject': test_subjects,
                           'All correct responses': test_cts,
                            'Max Time': test_max_time}


    test_df = pd.DataFrame(test_df_maker)
    test_df.sort_values(['Subject','Date'], ascending = (True,True), inplace = True)
    create_groups(test_df)
    day_numberer(test_df)
    test_df.set_index('Subject', inplace = True)


    with pd.ExcelWriter(path_to_save + f'PR Data from {date.today()}.xlsx') as writer:
        food_df.to_excel(writer, sheet_name = 'FOOD')
        for i,x in test_df.groupby('Subject'):
            x.to_excel(writer, sheet_name = i)
        test_df.groupby('Group').mean().to_excel(writer, sheet_name = 'Group Means')
        test_df.groupby('Group').sem().to_excel(writer, sheet_name = 'Group SEMs')
        test_df.groupby(['Group', 'Day Number']).mean().to_excel(writer, sheet_name= 'By Day Averages')
        test_df.groupby(['Group', 'Day Number']).sem().to_excel(writer, sheet_name = 'By Day SEMs')
        

def parse_and_graph():
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


    test_subjects = []
    test_dates = []
    test_starttimes = []
    test_msns = []
    test_experiments = []
    test_total_time=  []
    test_correct_presses = []
    test_incorrect_presses = []
    test_breakpoint = []
    test_last_completed_increment = []
    test_remainder = []
    test_response_rate = []
    test_itt_mean = []
    test_itt_q1 = []
    test_itt_q2 = []
    test_itt_q3 = []
    test_cts = []
    test_max_time = []
    test_its = []
    test_trial_finishes = []

    all_itrr = []



    for i in os.listdir(path_to_data):
        print(i)
        file = path_to_data + i
        msn_check = MainInfoParser.msngrabber(file)
        if 'food' in msn_check.lower():
            main_info = MainInfoParser(file,dates,starttimes,subjects,msn,experiment)
            main_info.maininfograbber()
            total_presses_temp = []
            get_presses = ArrayParser(file, total_presses_temp, 'A','B')
            get_presses.arraygrabber()
            correct_presses.append(int(float(total_presses_temp[-1][0])))

            if correct_presses[-1] >= 50:
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



        else:
            test_main_info = MainInfoParser(file,test_dates,test_starttimes,test_subjects,test_msns,test_experiments)
            test_main_info.maininfograbber()


            #Grab the total correct lever presses
            total_presses_temp = []
            get_presses = ArrayParser(file, total_presses_temp, 'A','B')
            get_presses.arraygrabber()
            test_correct_presses.append(int(float(total_presses_temp[-1][0])))

            #Grab the total incorrect lever presses
            temp_incorrect = []
            get_incorrect = ArrayParser(file, temp_incorrect, 'B','D')
            get_incorrect.arraygrabber()
            test_incorrect_presses.append(int(float(temp_incorrect[-1][0])))

            #Grab the total time
            total_time_temp = []
            get_total_time = ArrayParser(file, total_time_temp, 'T', 'U')
            get_total_time.arraygrabber()
            test_total_time.append(int(float(total_time_temp[-1][0]))/60)

            #Grab the response rate per min
            test_response_rate.append(test_correct_presses[-1]/test_total_time[-1])


            #Create the increment slider (array F... the thing that allows you to move across the E array)
            temp_increment = []
            get_increment_mover = ArrayParser(file, temp_increment, 'F','G')
            get_increment_mover.arraygrabber()
            increment_slider = int(float(temp_increment[-1][0]))
            test_breakpoint.append(increment_slider) #this is the animal's progressive ratio breakpoint

            #Figure out what the last completed increment was
            temp_available_increments = []
            get_available_increments = ArrayParser(file, temp_available_increments, 'E','J')
            get_available_increments.arraygrabber()
            available_increments = [int(float(i)) for i in temp_available_increments[-1]]
            test_last_completed_increment.append(available_increments[increment_slider-1])

            #Remainder since last increment
            test_remainder.append(sum(available_increments[0:increment_slider+1]) - test_correct_presses[-1])

            #Avg. time spent per trial
            temp_trial_timestamps = []
            get_trial_timestamps = ArrayParser(file, temp_trial_timestamps, 'C', 'E')
            get_trial_timestamps.arraygrabber()
            trial_timestamps = [float(i) for i in temp_trial_timestamps[-1]]
            test_trial_finishes.append(trial_timestamps)
            inter_trial_time = []
            for i,x in enumerate(trial_timestamps):
                if i == 0:
                    inter_trial_time.append(x)
                elif i != 0:
                    inter_trial_time.append((x - trial_timestamps[i-1])-10)

            test_itt_mean.append(np.mean(inter_trial_time))
            test_itt_q1.append(np.percentile(inter_trial_time, 25))
            test_itt_q2.append(np.percentile(inter_trial_time, 50)) #median
            test_itt_q3.append(np.percentile(inter_trial_time, 75))

            temp_correct_timestamps = []
            get_cts = ArrayParser(file, temp_correct_timestamps, 'J','L')
            get_cts.arraygrabber()
            test_cts.append([float(i) for i in temp_correct_timestamps[-1]])
            test_max_time.append(list(np.linspace(0,max(test_cts[-1]),len(test_cts[-1]))))

            temp_incorrect_timestamps = []
            get_its = ArrayParser(file, temp_incorrect_timestamps, 'L', 'NONE')
            get_its.endarraygrabber()
            test_its.append([float(i) for i in temp_incorrect_timestamps[-1]])

            itrr = []
            for i,x in enumerate(trial_timestamps):
                if i == 0:
                    itrr.append(available_increments[i]/((trial_timestamps[i]-1)/60))
                else:
                    itrr.append(available_increments[i]/((trial_timestamps[i] -trial_timestamps[i-1] - 5)/60))
            all_itrr.append(itrr)





    #All things FOOD dataframe
    food_df_maker = {'Subject': subjects,
                'Date': dates,
                'MSN': msn,
                'Day of paradigm': experiment,
                'Session Total Time (min)': total_time,
                'Max Allowed Presses': max_allowed,
                'Correct Presses': correct_presses,
                'First Press Latency': first_press_latency,
                'Move to test?': pass_check}


    food_df = pd.DataFrame(food_df_maker)
    food_df.sort_values(['Subject','Date'], ascending = (True,True), inplace= True)
    create_groups(food_df)
    day_numberer(food_df)

    food_df.set_index('Subject', inplace = True)


    #All things TEST dataframe
    test_df_maker = {'Subject': test_subjects,
                    'Date': test_dates,
                    'MSN': test_msns,
                    'Day of paradigm': test_experiments,
                    'Session Total Time (Min)': test_total_time,
                     'Last Completed Increment': test_last_completed_increment,
                     'Remainder after lst increment': test_remainder,
                    'Correct Presses': test_correct_presses,
                    'Response Rate (resp/min)': test_response_rate,
                    'Breaking Point': test_breakpoint,
                    'Incorrect Presses': test_incorrect_presses,
                    'ITT mean': test_itt_mean,
                    'ITT q1': test_itt_q1,
                    'ITT median': test_itt_q2,
                    'ITT q3': test_itt_q3,
                    'All ITRR': all_itrr}


    line_graph_df_maker = {'Subject': test_subjects,
                           'All correct responses': test_cts,
                            'Max Time': test_max_time}


    test_df = pd.DataFrame(test_df_maker)
    test_df.sort_values(['Subject','Date'], ascending = (True,True), inplace = True)
    create_groups(test_df)
    day_numberer(test_df)
    test_df.set_index('Subject', inplace = True)


    with pd.ExcelWriter(path_to_save + f'PR Data from {date.today()}.xlsx') as writer:
        food_df.to_excel(writer, sheet_name = 'FOOD')
        for i,x in test_df.groupby('Subject'):
            x.to_excel(writer, sheet_name = i)
        test_df.groupby('Group').mean().to_excel(writer, sheet_name = 'Group Means')
        test_df.groupby('Group').sem().to_excel(writer, sheet_name = 'Group SEMs')
        test_df.groupby(['Group', 'Day Number']).mean().to_excel(writer, sheet_name= 'By Day Averages')
        test_df.groupby(['Group', 'Day Number']).sem().to_excel(writer, sheet_name = 'By Day SEMs')
    
    summary_graphs(df = test_df)
    individ_rr_graphs(df = test_df)
    the_dots_graph(test_subjects = test_subjects, 
                test_cts = test_cts, 
                test_its = test_its, 
                test_trial_finishes = test_trial_finishes,
                test_max_time = test_max_time)
    summary_by_day_graphs(df = test_df)
