# -*- coding: utf-8 -*-
"""
This script would do the following:
    1. filter the course progress from codecademy to the list of names specified
    2. add the current progress to the master excel workbook for the given course
    
"""
import pandas as pd
import glob
import os

from common import PROGRESS_FOLDER, OUTPUT_FOLDER, NAMES_FILE
from common import TRACK_COURSE_MAPPING
from common import course_name_to_code
from common import save_output
from common import load_names
from common import load_data

from common import bulk_load_data
from common import get_course_enrolment
from common import load_progress_files

# the names in the data file are either names or emails. We want to:
"""
NB: A master template exist containing all names  and track information
1. create a new column that contains names names only
2. filter the data table to cotain only records specified in the names
3. add/update the column that indicates whether a person is enroled in a course or not

"""

#===== CODE NEEDING TO RUN ONLY ONE TIME ======
names_df = load_names()
progress_df = load_data(os.path.join(PROGRESS_FOLDER,'Analyze Data with Python.csv'))

#==============================================    

def clean_names_column(progress_df,names_df = names_df):
    """
    Return the progress data with the names cleaned and a few more columns
    added
    
    Note: Some of the names in the progess file are not trainees.
    They will be left out.
    
    Anyone left out means names are not spelt consistently

    Parameters
    ----------
    progress_df : pandas df
        progress dataframe for a single course.
    names_df : pandas df
        names of all trainees.

    Returns
    -------
    None.

    """
    name_list = [name.strip() for name in names_df.name.values]
    email_list =[email.strip() for email in names_df.email.values]
    
    email_name_map = {email:name for name,email in names_df[['name','email']].values}
    
    # pick out the names that are emails and replace them accordingly
    clean = progress_df[progress_df.name.isin(name_list)]
    to_correct = progress_df[progress_df.name.isin(email_list)]
    
    to_correct['name'] = to_correct['name'].map(email_name_map)
    # update name column with full names
    
    cleaned_df = pd.concat([clean,to_correct])
        
    return cleaned_df


def emails_to_names(names_df, email_names):
    """
    Using the names databse as reference, replaces the email names to proper 
    full names. This is is applied to the progress
    file where this is the case
    """
    email_to_name = {n.strip(): e.strip() for e,n in names_df[['name','email']].values}
    names_as_emails = email_names.assign(fullname = email_names.name.map(email_to_name))
    return names_as_emails




def tag_enrollment(course_code,track):
    """
    Given a trainee name and their track, produce the enrolment
    status for the current course
    
    Sol: If this course is on the course list for the track 
    enrolled, then this person is enrolled in the course
    """
    track_courses = TRACK_COURSE_MAPPING.get(track,'')
    
    if course_code in track_courses:
        enrolled = 'Yes'
    else:
        enrolled = 'No'
    return enrolled

        
def clean_progress_file(progress_file):
    """
    Code for cleaning up the raw progress file.
    

    Parameters
    ----------
    progress_file : file name being name of the course
        DESCRIPTION.

    Returns
    -------
    None.

    """
    #print('processing {}'.format(progress_file))
    
    #== output table should have: ==
    # name, track, course, enroled, started, completed
    
    # load progress data
    progress_data = load_data(progress_file)
    
    # correct name errors 
    cleaned_df =  clean_names_column(progress_df = progress_data)
    
    
    
    # add column for track info
    name_track_map = dict(names_df[['name','track']].values)
    cleaned_df['track'] = cleaned_df['name'].map(name_track_map)
    
    
    # Get course name
    course_name = os.path.splitext(os.path.basename(progress_file))[0]
    course_code =  course_name_to_code(course_name)
    cleaned_df['course'] = course_name
    
    # create new column for enrollment status
    temp =[]
    for record in cleaned_df.to_dict(orient = 'records'):
        temp.append(tag_enrollment(track= record['track'], course_code = course_code))
    
    cleaned_df['enrolled'] = temp
    #Keep only records for those enrolled in course
    cleaned_df = cleaned_df[cleaned_df.enrolled == 'Yes']
    
    # change the order of the columns
    cleaned_df = cleaned_df[['name','track','course','enrolled','started_at','percent_complete','completed_at']]
    
    return cleaned_df
    
def process(progress_file, names = NAMES_FILE):
    """
    Sets up the sequence for processing all relevant files
    
    STEPS:
        1. Determine mode of peration
        2. Load names
        3. Read progress file(s)
        4. Filter the data to match the names
        5. Add addtional columns as needed
        6. Save the cleaned file. 
        Note: only the percent_complete column will be appended to the master sheet
    """

    
    
    # course_name = os.path.splitext(os.path.basename(progress_file))[0]
    
    # correct errors in name columns and add additional columns
    cleaned_df = clean_progress_file(progress_file)
    cleaned_df.reset_index(drop=True,inplace=True)
    
          
    output_file_name = os.path.splitext(os.path.basename(progress_file))[0] 
    output_file_name += '.csv'  
    cleaned_df.to_csv(os.path.join(OUTPUT_FOLDER,output_file_name))       

            

def run():
    """
    Apply cleaning and formatting to all progress files

    Returns
    -------
    None.

    """
    progress_files = load_progress_files()
    
    msg_template = """
    ***********************************************
    Beginning to Process {} Progress Files 
    ************************************************
    {}
    """
    success_msg = []
    
    #print(msg_template.format(len(progress_files)))
    for progress_file in progress_files:
        process(progress_file)
        file_name = os.path.basename(progress_file)
        success_msg.append("Cleaning... {}. File succefully saved".format(file_name))
    
    msg = '\n'.join(success_msg)
    print(msg_template.format(len(progress_files),msg))            
        
        

if __name__ == 'main':
    run()
else:
    run()
    
    

