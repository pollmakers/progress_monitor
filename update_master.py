# -*- coding: utf-8 -*-
"""
Created on Thu Jul 29 13:57:14 2021

@author: AmaliTech

=====================================
This module is for updating the master files for each course.
In the end, a single master file will be created by appending all
the updates to a single file.

1. read the progress file
2. select the percent_complete column
3. append the data to the coresponding name in the master sheet.

NB: Need to make sure that names are correctly matched
- the recommended file naming convention for progress reports is to use the course code
- however it might be easier naming them by the exac course names
- if course names are used, they must be exact as those in the courselist.csv
"""
import datetime
from openpyxl import load_workbook
import pandas as pd
import os
import glob 
import shutil

from common import PROGRESS_FOLDER, OUTPUT_FOLDER, COURSE_MAPPING_FILE, NAMES_FILE, TRACK_COURSE_MAPPING
from common import MASTER_FOLDER, HISTORY_FOLDER

from common import bulk_load_data,get_progress_data, load_data
from common import get_course_enrolment

#========= Test Data ===
#progress_file = r"C:\Users\AmaliTech\Documents\CourseProgress Processing\output\current_progress.csv"
#master_workbook = load_workbook(os.path.join(MASTER_FOLDER,'course_progress.xlsx'))
#=======================

# list available courses
course_df = pd.read_csv('courselist.csv')
namesfile = 'names.csv'

#get the people enrolled
names_df = pd.read_csv(namesfile)
names_df['name'] = names_df['name'].apply(lambda x: x.strip()) 

trainee_list = names_df.to_dict(orient='record')
num_enrolled = len(trainee_list)

# psheet = master_workbook['progress']

l = []
#==============================================================================
# STEPS:
"""
- GET THE PROGRESS DATA FOR EACH COURSE
- GET THE CORRESPONDING MASTER FILES
- UPDATE THE RECORDS FOR LEARNERS IN THAT TRACK
- APPEND THE OUTPUT TO A TEMPORARY Storage
- JOIN THE OUTPUT AND STORE IN A SINGLE FILE
"""
#==============================================================================
# 1
def load_progress_files():
    """
    Loads progress files
    Returns
    -------
    None.

    """
    files = bulk_load_data()
    
    
    return files

#2
def load_master_files():
    """
    constructs the path for all master files for progress files provided

    Returns
    -------
    csv files

    """
    progress_files = load_progress_files()
    
    for progress_file in progress_files:
        progress_file = os.path.splitext(os.path.basename(progress_file))[0]+'.xlsx'
        yield "{}".format(os.path.join(MASTER_FOLDER,progress_file))
    

#3   
def load_master_data(file_name):
    try:
        master_wb = load_workbook(file_name)
    except FileNotFoundError:
        print("{} does not exist in master folder".format(file_name))
    
    except Exception:
        print("Unable to open {}. Make sure it's a valid file".format(file_name))
        return
    
    return master_wb


def update_progress_sheet(course_name,progress_data,master_workbook):
    """
    This function handles the task of updating the master sheet with the 
    latest progress figures.
    
    It creates a new column with with the date the progress data is read
    and add the progress reading
    
    To Do:
        Add a function that checks and update the Started At column
    """
    # Get enrollment for this course
    
    enrollment = get_course_enrolment(course_name)
    
    # Get the correct sheets
    master_progress_sheet = master_workbook['progress']
    summary_sheet = master_workbook['summary']
    
    # Ge the colum to update the next values
    last_column = master_progress_sheet.max_column
    next_column = last_column + 1
    
    #create a new column with header as current date
    master_progress_sheet.cell(1,next_column).value = datetime.datetime.today().date()
    
    
    # filter out people not enrolled in the course
    progress_data = progress_data[progress_data.name.isin(enrollment)]
    
    # create dictionary mapings to ease out name search
    name_progress_dict = { name.strip():progress for name,progress in list(progress_data[['name','percent_complete']].values)}
    name_date_started_dict = { name.strip():started for name,started in list(progress_data[['name','started_at']].values)}
    name_date_completed_dict = { name.strip():started for name,started in list(progress_data[['name','completed_at']].values)}
    
    # get each record in mastersheet and update them 
    for row in range(2, master_progress_sheet.max_row+1):
        
        # get the name of current learner in the master sheet
        name = master_progress_sheet.cell(row = row, column=1).value
        name = name.strip() if name is not None else name
        
        # find corresponding value and update the progress
        if name in enrollment:
            master_progress_sheet.cell(row = row, column=next_column).value = name_progress_dict.get(name,0)
            
            # if Started_At column is empty, update it
            if summary_sheet.cell(row = row, column=3).value is None:
               summary_sheet.cell(row = row, column=3).value = name_date_started_dict.get(name,'')
               summary_sheet.cell(row = row, column=4).value = name_date_completed_dict.get(name,'')
        #return master_progress_sheet


def cleanup():
    """
    Deletes all the progress files from the input and output folders
    - input files are backed up in the history folder with subfolders by the date of update
    - files in output folders are deleted completely
    
    1. Get updated progress files
    2. Move them to history
    """
    current_date = str(datetime.datetime.today().date())
    
    # load progress files used
    progress_files_folder = os.path.join(os.getcwd(),'input')
    updated_files = bulk_load_data(progress_files_folder)
    
    # create a new folder and move items into it
    destination_folder = os.path.join(HISTORY_FOLDER,current_date)
    
    if not os.path.exists(destination_folder):
        os.mkdir(destination_folder)
        
    for file in updated_files:
        file_name = os.path.basename(file)
        shutil.move(file,os.path.join(destination_folder,file_name))
        
    # Cleanup files in the output folder in parent directory
    for file in bulk_load_data(PROGRESS_FOLDER):
        os.remove(file)
    
    
    
    
    
    
    
"""
TO DO
- Add function to add the date started in the summary sheet each time 
master file is updated for those leaeners whose entries are empty
"""    


def process(course_name,progress_file, master_file):
    """
    Function to chain all the steps together for a single progress file
    and a single master file

    Returns
    -------
    None.

    """
        
    # 1. Get progress Data
    
    progress_data = load_data(progress_file)
    
    # 2. Get master file
    master_wb = load_master_data(file_name = master_file) 
    
    # 3. update progress sheet in master workbook
    update_progress_sheet(
        course_name = course_name,
        progress_data = progress_data,
        master_workbook = master_wb
        
        )
        
    
    # 4. Save workbook
    master_wb.save(os.path.join(MASTER_FOLDER,master_file + '_copy.xlsx'))
    print("Done updating **{}** in master  folder".format(master_file))
        

    
    
#         #master_wb.save(os.path.join(MASTER_FOLDER,master_file + '_copy.xlsx'))
#     elif mode == 'bulk':
#         bulk_files = bulk_load_data()
        
#         for file in bulk_files:
#             # 1. Get progress Data
#             progress_file, progress_data = get_progress_data(file_name = file )
        
#             try:
#                 # 2. Get master file
#                 master_file, master_wb = get_master_data(file_name = progress_file)
               
            
                
                
#                # 3. update progress sheet in master workbook
#                 update_progress_sheet(progress_data = progress_data,
#                                   master_workbook= master_wb,
#                                   )
                
#                 # 4. Save workbook
#                 master_wb.save(os.path.join(MASTER_FOLDER,master_file + '_copy.xlsx'))
#                 print("Done updating **{}** in master  folder".format(master_file))
        
#             except TypeError:
#                 continue
        
#         cleanup()



def run():
    progress_files = load_progress_files()
    master_fiiles = load_master_files()
    
    for progress_file, master_file in zip(progress_files,master_fiiles):
        course_name = os.path.splitext(os.path.basename(progress_file))[0]
        process(course_name,progress_file,master_file)
        

if __name__ == 'main':
    run()
else:
    run()
    