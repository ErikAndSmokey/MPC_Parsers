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

    def __init__(self, file, dates_list, starttimes_list, subjects_list, msns_list, paradigms_list, correct_list, incorrect_list,
                    omissions_list, streak_list, trials_list, checker_list, trialstocrit_list, righttrials_list, lefttrials_list,
                    persev_errors_list, regres_errors_list, never_rein_list, away_errors_list, toward_errors_list, vcmaxtrials_list,
                    vcmintrials_list):

        
        self.file = file
        self.dates = dates_list
        self.starttimes = starttimes_list
        self.subjects = subjects_list
        self.msns = msns_list
        self.paradigms = paradigms_list
        self.correct = correct_list
        self.incorrect = incorrect_list
        self.omissions = omissions_list
        self.streak = streak_list
        self.trials = trials_list
        self.checker = checker_list
        self.trialstocrit = trialstocrit_list
        self.righttrials = righttrials_list
        self.lefttrials = lefttrials_list
        self.persev_errors = persev_errors_list
        self.regres_errors = regres_errors_list
        self.never_rein = never_rein_list
        self.away_errors = away_errors_list
        self.toward_errors = toward_errors_list
        self.vcmaxtrials = vcmaxtrials_list
        self.vcmintrials = vcmintrials_list
        self.direction = []

        
        msn_check = self.msngrabber()
        if 'visual' in msn_check.lower() or 'bias shift' in msn_check.lower():
            self.maininfograbber()
            self.check_next()
        
    def check_next(self):
        if 'right' in self.msns[-1].lower():
            self.direction.append('R')
        elif 'left' in self.msns[-1].lower():
            self.direction.append('L')

        #Check to see what msn was run and decide which path to take from there
        if 'visual' in self.msns[-1].lower():
            self.visual_cue()
        elif 'bias shift' in self.msns[-1].lower():
            self.bias_shift()
            if self.streak[-1] >= 10:
                if 'rev' not in self.paradigms[-1].lower():
                    self.bias_errors()
                    self.away_errors.append(np.nan)
                    self.toward_errors.append(np.nan)
                elif 'rev' in self.paradigms[-1].lower():
                    self.bias_errors()
                    self.reversal_errors()

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


    #Random useful functions
    def trial_binner(self):
        for i in range(0,len(self.completed_trials_set)+1,16):
            yield list(self.completed_trials_set[i:i+16])

    def visual_cue(self):
        temp_vc = []
        correct = ArrayParser(self.file, temp_vc, 'A','B')
        correct.arraygrabber()
        self.correct.append(float(temp_vc[0][0]))
        temp_vc = []
        incorrect = ArrayParser(self.file, temp_vc, 'B','C')
        incorrect.arraygrabber()
        self.incorrect.append(float(temp_vc[0][0]))
        temp_vc = []
        omissions = ArrayParser(self.file, temp_vc, 'C','D')
        omissions.arraygrabber()
        self.omissions.append(float(temp_vc[0][0]))
        temp_vc = []
        streak = ArrayParser(self.file, temp_vc, 'D','E')
        streak.arraygrabber()
        self.streak.append(float(temp_vc[0][0]))
        temp_vc = []
        total_trials = ArrayParser(self.file, temp_vc, 'E','F')
        total_trials.arraygrabber()
        self.trials.append(float(temp_vc[0][0]))
        temp_vc = []
        max_criteria = ArrayParser(self.file , temp_vc, 'F','G')
        max_criteria.arraygrabber()
        self.vcmaxtrials.append(float(temp_vc[0][0]))
        temp_vc = []
        min_criteria = ArrayParser(self.file, temp_vc, 'L','M')
        min_criteria.arraygrabber()
        self.vcmintrials.append(float(temp_vc[0][0]))
        if self.vcmaxtrials[-1] == self.trials[-1] and self.streak[-1] != 10:
            self.trialstocrit.append('N/A')
            self.checker.append('Run day 2')
        elif self.streak[-1] == 10 and  self.trials[-1] >= self.vcmintrials[-1]:
            self.trialstocrit.append(self.trials[-1] - self.omissions[-1])
            self.checker.append('Move to shift!')
        else:
            self.trialstocrit.append('N/A')
            self.checker.append('Catch all rule- something may be wrong')

        self.persev_errors.append(np.nan)
        self.regres_errors.append(np.nan)
        self.never_rein.append(np.nan)
        self.away_errors.append(np.nan)
        self.toward_errors.append(np.nan)

    def bias_shift(self):
        temp_rb = []
        correct_rb = ArrayParser(self.file, temp_rb, 'A','B')
        correct_rb.arraygrabber()
        self.correct.append(float(temp_rb[0][0]))
        temp_rb = []
        incorrect_rb = ArrayParser(self.file, temp_rb, 'B', 'C')
        incorrect_rb.arraygrabber()
        self.incorrect.append(float(temp_rb[0][0]))
        temp_rb = []
        omissions_rb = ArrayParser(self.file, temp_rb, 'C','D')
        omissions_rb.arraygrabber()
        self.omissions.append(float(temp_rb[0][0]))
        temp_rb = []
        streak_rb = ArrayParser(self.file, temp_rb, 'D','E')
        streak_rb.arraygrabber()
        self.streak.append(float(temp_rb[0][0]))
        temp_rb = []
        trials_rb = ArrayParser(self.file, temp_rb, 'E','F')
        trials_rb.arraygrabber()
        self.trials.append(float(temp_rb[0][0]))
        if self.streak[-1] >= 10:
            self.trialstocrit.append(self.trials[-1] - self.omissions[-1])
            self.checker.append('PASSED')

    def bias_errors(self):
        if self.direction[-1] == 'R':
            correct_dir = 'L'
            incorrect_dir = 'R'
        elif self.direction[-1] =='L':
            correct_dir = 'R'
            incorrect_dir = 'L'
        self.trialtype = []
        temp_rb = []
        right_trials = ArrayParser(self.file, temp_rb, 'Q','None')
        right_trials.endarraygrabber()
        self.righttrials.append(list(int(float(i)) for i in temp_rb[0]))
        temp_rb = []
        left_trials = ArrayParser(self.file, temp_rb, 'O','Q')
        left_trials.arraygrabber()
        self.lefttrials.append(list(int(float(i)) for i in temp_rb[0]))
        #Begin making the trial type list... basically say which trial was L and which was R cue preceeded
        y = 0
        for i in range(1,int(self.trials[-1])+1):
            trialorder = ['L','R','R','L','R','L']
            self.trialtype.append(trialorder[y])
            y += 1
            if y == len(trialorder):
                y = 0
            else:
                pass
        self.press_dictionary = {correct_dir:self.lefttrials[-1], incorrect_dir:self.righttrials[-1]}        
        self.completed_trials = [i for i in self.righttrials[-1]]
        self.completed_trials.extend(self.lefttrials[-1])
        self.completed_trials.sort()
        self.completed_trials_set = list(set(self.completed_trials))
        self.trial_bins = list(self.trial_binner())
        pos = 0
        while pos <= len(self.trial_bins):
            for i in self.trial_bins[pos]:
                if i in self.press_dictionary[correct_dir]:
                    self.trial_bins[pos][self.trial_bins[pos].index(i)] = 'Pass'
                elif i in self.press_dictionary[incorrect_dir]:
                    if self.trialtype[i-1] == incorrect_dir:
                        self.trial_bins[pos][self.trial_bins[pos].index(i)] = 'I'
                    else:
                        self.trial_bins[pos][self.trial_bins[pos].index(i)] = 'NR'
            pos += 1
            if pos == len(self.trial_bins):
                break
            else:
                pass
        for i in self.trial_bins:
            if i.count('I') < 6:
                error_switch = self.trial_bins.index(i)    
        temp_persev_errors = 0
        temp_regres_errors = 0
        temp_nr_errors = 0
        temp_correct_trials = 0
        for i in self.trial_bins:
            if self.trial_bins.index(i) < error_switch:
                temp_persev_errors += i.count('I')
                temp_nr_errors += i.count('NR')
                temp_correct_trials += i.count('Pass')
            elif self.trial_bins.index(i) >= error_switch:
                temp_regres_errors += i.count('I')
                temp_nr_errors += i.count('NR')
                temp_correct_trials += i.count('Pass')
        self.persev_errors.append(temp_persev_errors)
        self.regres_errors.append(temp_regres_errors)
        self.never_rein.append(temp_nr_errors)


    def reversal_errors(self):
        temp_toward_distractor = 0
        temp_away_distractor = 0
        for i in self.completed_trials_set:
            if i in self.press_dictionary[incorrect_dir]:
                if self.trialtype[i-1] == incorrect_dir:
                    temp_toward_distractor += 1
                elif self.trialtype[i-1] == correct_dir:
                    pass
            else:
                pass
        for i in range(1,int(self.trials[-1])+1):
            if i not in self.completed_trials_set:
                if self.trialtype[i-1] == correct_dir:
                    temp_away_distractor += 1
                else:
                    pass
            else:
                pass
        self.away_errors.append(temp_away_distractor)
        self.toward_errors.append(temp_toward_distractor)



def main():
    dates = []
    starttimes = []
    subjects = []
    msns = []
    paradigms = []
    correct = []
    incorrect = []
    omissions = []
    streak = []
    trials = []
    checker = []
    trialstocrit = []
    righttrials = []
    lefttrials = []
    persev_errors = []
    regres_errors = []
    never_rein = []
    away_errors = []
    toward_errors = []
    vcmaxtrials = []
    vcmintrials = []



    for i in os.listdir(data_folder):
        file = data_folder + i

        Analyze(file = file, dates_list = dates, starttimes_list = starttimes,
            subjects_list = subjects, msns_list = msns, paradigms_list = paradigms,
            correct_list= correct, incorrect_list = incorrect, omissions_list = omissions,
            streak_list=  streak, trials_list = trials, checker_list = checker,
            trialstocrit_list = trialstocrit, righttrials_list = righttrials, lefttrials_list = lefttrials,
            persev_errors_list = persev_errors, regres_errors_list = regres_errors, never_rein_list = never_rein,
            away_errors_list = away_errors, toward_errors_list = toward_errors, vcmaxtrials_list = vcmaxtrials,
            vcmintrials_list = vcmintrials)




    shift_info = {'Subject': subjects,
            'Date': dates,
           'Start Time': starttimes,
           'MSN':msns,
            'Day of shift task': paradigms,
            'Total Number of Trials': trials,
           'Correct Responses': correct,
           'Incorrect Responses': incorrect,
           'Omissions': omissions,
           'Last Streak': streak,
           'Trials to criteria?': trialstocrit,
           'What to do next?': checker,
           'Perseverative Errors': persev_errors,
           'Regressive Errors': regres_errors,
           'Never Reinforced Errors': never_rein,
            'Toward Distractor Errors': toward_errors,
             'Away from Distractor Errors': away_errors}


    shift_df = pd.DataFrame(shift_info)

    shift_df['Date'] = pd.to_datetime(shift_df.Date) #Uniformly format the date for sorting purposes
    shift_df['Subject']= [i.upper().replace(' ','') for i in shift_df['Subject']] #Uniformly format the subject names
    shift_df.sort_values(['Subject','Date'],inplace=True)

    range_by_animal = [] #This is a list for collecting all the day numbers- needs to be after the sort
    for i in shift_df.groupby('Subject'):
        x = range(1,len(i[1])+1)
        for num in x:
            range_by_animal.append(num)
    shift_df['Day Number'] = range_by_animal #in essence, sort by date and then use the sorting to create a list of day nums based on date
    shift_df.set_index('Day Number', inplace = True)

    #Code for assigning a group type to each animal
    dfgroups = pd.ExcelFile(main_folder + '\\Group Identifier.xlsx').parse() #FILE PATH!
    control_name = dfgroups.keys()[0] #Handles group ID name changes
    experimental_name = dfgroups.keys()[1] #Handles group ID name changes
    listofcontrols = [str(i).upper() for i in dfgroups[control_name]] #Because df to df comparisons weren't working...
    listofexps = [str(i).upper() for i in dfgroups[experimental_name]] #Because df to df comparisons weren't working...


    rbgroup_column = []
    for i in shift_df['Subject']:
        if i.upper() in listofcontrols:
            rbgroup_column.append(dfgroups.columns[0]) #You can change the names of the columns to match the study!
        elif i.upper() in listofexps:
            rbgroup_column.append(dfgroups.columns[1]) #You can change the names of the columns to match the study!
        else:
            rbgroup_column.append('NaN') #Because we need to match the df lengths
            print(f'{i} is not in your Group Identifier spreadsheet!!!! Please Check!!!')
    shift_df['Subject Group'] = rbgroup_column


    data_save = xl_storage + f'SS Data from {date.today()}.xlsx'
    book = load_workbook(data_save)
    with pd.ExcelWriter(data_save, engine = 'openpyxl') as writer:
        writer.book = book
        writer.sheets = {worksheet.title:worksheet for worksheet in book.worksheets}
        for i,x in shift_df.groupby('MSN'):
            x.to_excel(writer, sheet_name = i)
        shift_df.groupby(['Subject Group', 'Day of shift task']).mean().to_excel(writer, sheet_name = 'AVERAGES')
        shift_df.groupby(['Subject Group', 'Day of shift task']).sem().to_excel(writer, sheet_name = 'SEM')