#The Art Van DeLay imports/exports.... but more imports than exports... and that's the problem
import pandas as pd
import os
import re
from itertools import chain
from datetime import date
import smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import SS_SetAndShift

#The directory where the data files are that you want to analyze
main_folder = os.getcwd()
data_storage = main_folder + '\\Data\\'
xl_storage = main_folder + '\\XL Files\\'


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
    
        
#Food Training Lists
fddates = []
fdstarttimes = []
fdsubjects = []
fdmsns = []
fdparadigms = []
fd_r_presses = []
fd_l_presses = []
fd_total = []


#Lever training lists
levtrdates = []
levtrstarttimes = []
levtrsubjects = []
levtrmsns = []
levtrparadigms = []
levtr_llo = []
levtr_llr = []
levtr_lle = []
levtr_rlo = []
levtr_rlr = []
levtr_rle = []

#Lever bias lists
biasdates = []
biasstarttimes = []
biassubjects = []
biasmsns = []
biasparadigms = []
biastime = []
biasllr = []
biaslli = []
biasrlr = []
biasrli = []
biascomplete = []
biasfailed = []
biasresults = []



counter = 0
for i in os.listdir(data_storage):
    file = data_storage+i
    a_array = []
    c_array = []
    msn_check = MainInfoParser.msngrabber(file = file)
    y = MainInfoParser.dayofparadigm(file = file)
    if 'ass_food' in msn_check.lower():
        temp_fd_r_presses = []
        temp_fd_l_presses = []
        food_main  = MainInfoParser(file,fddates,fdstarttimes,fdsubjects,fdmsns,fdparadigms)
        food_main.maininfograbber()
        right_data = ArrayParser(file, temp_fd_r_presses, 'A','B')
        right_data.arraygrabber()
        fd_r_presses.append(float(temp_fd_r_presses[0][0])) #appends list with right lever totals
        left_data = ArrayParser(file, temp_fd_l_presses, 'B','C')
        left_data.arraygrabber()
        fd_l_presses.append(float(temp_fd_l_presses[0][0]))#Appens list with left lever totals
        #Now collect total session lever presses
        fd_total.append(float(temp_fd_l_presses[0][0]) + float(temp_fd_r_presses[0][0]))
    elif msn_check.upper() == 'ASS_LEVER_TRAINING':
        levtr_main = MainInfoParser(file, levtrdates, levtrstarttimes, levtrsubjects, levtrmsns, levtrparadigms)
        levtr_main.maininfograbber()
        temp_levtr = []
        llo = ArrayParser(file, temp_levtr, 'C','D')
        llo.arraygrabber()
        levtr_llo.append(float(temp_levtr[0][0]))
        temp_levtr = []
        llr = ArrayParser(file, temp_levtr, 'A','B')
        llr.arraygrabber()
        levtr_llr.append(float(temp_levtr[0][0]))
        temp_levtr = []
        lle = ArrayParser(file, temp_levtr, 'E','F')
        lle.arraygrabber()
        levtr_lle.append(float(temp_levtr[0][0]))
        temp_levtr = []
        rlo = ArrayParser(file, temp_levtr, 'D','E')
        rlo.arraygrabber()
        levtr_rlo.append(float(temp_levtr[0][0]))
        temp_levtr = []
        rlr = ArrayParser(file, temp_levtr, 'B','C')
        rlr.arraygrabber()
        levtr_rlr.append(float(temp_levtr[0][0]))
        temp_levtr = []
        rle = ArrayParser(file,temp_levtr,'F','G')
        rle.arraygrabber()
        levtr_rle.append(float(temp_levtr[0][0]))
    elif 'ass_bias' in msn_check.lower():
        bias_main = MainInfoParser(file, biasdates, biasstarttimes, biassubjects, biasmsns, biasparadigms)
        bias_main.maininfograbber()
        temp_bias = []
        lli = ArrayParser(file,temp_bias, 'F','G')
        lli.arraygrabber()
        biaslli.append(float(temp_bias[0][0]))
        temp_bias = []
        llr = ArrayParser(file, temp_bias, 'A','B')
        llr.arraygrabber()
        biasllr.append(float(temp_bias[0][0]))
        temp_bias = []
        rli = ArrayParser(file, temp_bias, 'G','H')
        rli.arraygrabber()
        biasrli.append(float(temp_bias[0][0]))
        temp_bias = []
        rlr = ArrayParser(file,temp_bias, 'B','F')
        rlr.arraygrabber()
        biasrlr.append(float(temp_bias[0][0]))
        temp_bias = []
        failed = ArrayParser(file, temp_bias, 'J', 'K')
        failed.arraygrabber()
        if float(temp_bias[0][0]) == 1.0:
            biasfailed.append('FAILED')
            biascomplete.append('FAILED TO PRESS LEVER')
            biasresults.append('FAILED TO PRESS LEVER')
        else:
            biasfailed.append('PASSED')
            temp_bias = []
            complete = ArrayParser(file,temp_bias, 'I', 'J')
            complete.arraygrabber()
            biascomplete.append(float(temp_bias[0][0]))
            if biasllr[-1] >= biasrlr[-1]*2:
                biasresults.append('Left Bias')
            elif biasrlr[-1] >= biasllr[-1]*2:
                biasresults.append('Right Bias')
            elif biasrli[-1] > biaslli[-1]:
                biasresults.append('Right Bias')
            elif biaslli[-1] > biasrli[-1]:
                biasresults.append('Left Bias')
            else:
                biasresults.append('Data inconclusive! Check!')
    counter += 1

        
food_info_df = {'Date':fddates,
               'Start Time': fdstarttimes,
               'Subject': fdsubjects,
               'MSN':fdmsns,
               'Day of Food': fdparadigms,
               'Right Lever Presses':fd_r_presses,
               'Left Lever Presses': fd_l_presses,
               'Total Lever Presses': fd_total}

levtr_info_df = {'Date': levtrdates,
                'Start Time': levtrstarttimes,
                'Subject': levtrsubjects,
                'MSN': levtrmsns,
                'Day of Lever Training': levtrparadigms,
                'LL Extensions': levtr_lle,
                'LL Responses': levtr_llr,
                'LL Omissions': levtr_llo,
                'RL Extensions': levtr_rle,
                'RL Responses': levtr_rlr,
                'RL Omissions': levtr_rlo}

bias_info_df = {'Date': biasdates,
               'Start Time': biasstarttimes,
               'Subject': biassubjects,
               'MSN': biasmsns,
               'Left Lever Initiations': biaslli,
               'Right Lever Initiations': biasrli,
               'Left Lever Responses': biasllr,
               'Right Lever Responses': biasrlr,
               'Failed?': biasfailed,
               'Total Trials': biascomplete,
               'Results': biasresults}


food_df = pd.DataFrame(food_info_df)
levtr_df = pd.DataFrame(levtr_info_df)
bias_df = pd.DataFrame(bias_info_df)
levtr_df_sort = levtr_df.sort_values(['Subject','Date'],ascending = (True,True))
bias_df_sort = bias_df.sort_values(['Subject','Date'], ascending = (True,True))
food_df_sort = food_df.sort_values(['Subject','Date'], ascending = (True,True))



#Code for assigning a group type to each animal
dfgroups = pd.ExcelFile(main_folder + '\\Group Identifier.xlsx').parse() #FILE PATH!
control_name = dfgroups.keys()[0] #Handles group ID name changes
experimental_name = dfgroups.keys()[1] #Handles group ID name changes
listofcontrols = [str(i).upper() for i in dfgroups[control_name]] #Because df to df comparisons weren't working...
listofexps = [str(i).upper() for i in dfgroups[experimental_name]] #Because df to df comparisons weren't working...



levtr_group_column = [] #making your list of shit...
for i in levtr_df_sort['Subject']:
    if i.upper() in listofcontrols:
        levtr_group_column.append(dfgroups.columns[0]) #You can change the names of the columns to match the study!
    elif i.upper() in listofexps:
        levtr_group_column.append(dfgroups.columns[1]) #You can change the names of the columns to match the study!
    else:
        levtr_group_column.append('NaN') #Because we need to match the df lengths
        print(f'{i} is not in your Group Identifier spreadsheet!!!! Please Check!!!')
levtr_df_sort['Subject Group'] = levtr_group_column

bias_group_column = [] #making your list of shit...
for i in bias_df_sort['Subject']:
    if i.upper() in listofcontrols:
        bias_group_column.append(dfgroups.columns[0]) #You can change the names of the columns to match the study!
    elif i.upper() in listofexps:
        bias_group_column.append(dfgroups.columns[1]) #You can change the names of the columns to match the study!
    else:
        bias_group_column.append('NaN') #Because we need to match the df lengths
        print(f'{i} is not in your Group Identifier spreadsheet!!!! Please Check!!!')
bias_df_sort['Subject Group'] = bias_group_column

food_group_column = [] #making your list of shit...
for i in food_df_sort['Subject']:
    if i.upper() in listofcontrols:
        food_group_column.append(dfgroups.columns[0]) #You can change the names of the columns to match the study!
    elif i.upper() in listofexps:
        food_group_column.append(dfgroups.columns[1]) #You can change the names of the columns to match the study!
    else:
        food_group_column.append('NaN') #Because we need to match the df lengths
        print(f'{i} is not in your Group Identifier spreadsheet!!!! Please Check!!!')
food_df_sort['Subject Group'] = food_group_column


path_to_xl = xl_storage + f'SS Data from {date.today()}.xlsx'

with pd.ExcelWriter(path_to_xl) as writer:
    food_df_sort.to_excel(writer, sheet_name = 'Food Training')
    levtr_df_sort.to_excel(writer, sheet_name = 'Lever Training')
    bias_df_sort.to_excel(writer, sheet_name = 'Bias Test')

SS_SetAndShift.main()