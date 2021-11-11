**Welcome to the Attentional Set Shift Parser folder!**

**Here's how to use the parser:**

1) Download the .py files, .bat files, and 'Group Identifier.xlsx'

2) Put all the parser files in the same root folder (ex. 'C:\\Users\\JoeSchmo\\Desktop\\Set Shift')

3) Run the .bat file ('Make Folders') by double-clicking. This will create the folders in the directory that are necessary for the program.
   
4) You will be required to add your own subjects (and their group names!) to the 'Group Identifier.xlsx' spreadsheet. Add those before running any of the other .bat files.

5) Add the data to be analyzed to the 'Data' folder that you made. This is the folder where it knows to look for files.

6) Once all this is setup, the SS_Analyzer.py script (the main script) can be run by double-clicking the 'Run SS Analyzer.bat' file (if you only want the spreadsheet of data). A file should be saved in your 'XL Files' folder everytime, and graphs saved to the 'Figures' folder if you choose to have the graphs made (**Graphs are in development at this time).

7) That's it! Do not forget to update your spreadsheet as you add animals to your study!


**AS FOR THE MPCs**

This code ***ONLY*** works if you use the accompanying MPCs. This program is designed to read the MPC MSNs, thus you will have to use the same naming conventions as are used here.

*For clarity*
The 'SS_Right Bias Shift' and 'SS_Left Bias Shift' tasks are named based the animal's bias, and thus run that particular shift task. For example, if an animal has a left bias (as determined during the bias test) then run the 'SS_Left Bias Shift' MPC. Animals with a right bias should get the opposite. Get it?
