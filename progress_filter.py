# -*- coding: utf-8 -*-
"""
This script would do the following:
    1. filter the course progress from codecademy to the list of names specified
    2. add the current progress to the master excel workbook for the given course
    
"""
import pandas as pd
import glob
import os
import json
names = r"C:\Users\AmaliTech\Documents\CourseProgress Processing\names.csv"

from common import INPUT_FOLDER, OUTPUT_FOLDER, COURSE_MAPPING_FILE, NAMES_FILE
from common import MASTER_FOLDER

with open(COURSE_MAPPING_FILE,'r') as inp:
    course_mapping = json.load(inp)


modes = {'y':'bulk','n':'single'}

#== Test data ================
progressfile = 'DS.S 01.csv'
#=============================

# the names in the data file are either names or emails. We want to:
"""
NB: A master template exist containing all names  and track information
1. create a new column that contains names names only
2. filter the data table to cotain only records specified in the names
3. add/update the column that indicates whether a person is enroled in a course or not

"""
def load_data(file):
    return pd.read_csv(file)
    
def load_names(file = NAMES_FILE):
    """
    Reads names in the names.csv
    """
    namesdf = pd.read_csv(file)
    namesdf['name'] = [name.strip() for name in namesdf.name]
    namesdf['email']= [email.strip() for email in namesdf.email]
    return namesdf

def course_code_to_name(course_code):
    """
    - should return the name of the course given the course code
    - the course code should be the same as the name of the file
    """
    for track in course_mapping:
        if course_code in course_mapping[track]:
            return course_mapping[track][course_code]

def course_name_to_code(course_name):
    for track in course_mapping:
        for key, value in course_mapping[track].items(): 
         if course_name.strip() == value: 
             return key 
  
    return "key doesn't exist"
    
    
    
def bulk_load_data():
    files = glob.glob(INPUT_FOLDER + "/*.csv")
    return files
            
def filter_names(progress_df,name_list = None,email_list = None):
    """
    - cleans the names for uniformity
    - filters names in progress file to match those in names.csv, who 
    are current trainees
    """
    
    # seperate the names in the so that those with emails provided as names
    # will be in a seprate list
    df = load_names()
    name_list = df.name.values
    email_list = df.email.values
    
    # get records with full names 
    names_as_fullnames = progress_df[progress_df.name.isin(name_list)]
    # get records having emails as full name
    names_as_emails = progress_df[progress_df.name.isin(email_list)]
    
    return names_as_fullnames, names_as_emails

def emails_to_names(names_df, email_names):
    """
    Using the names databse as reference, replaces the email names to proper 
    full names. This is is applied to the progress
    file where this is the case
    """
    email_to_name = {n.strip(): e.strip() for e,n in names_df[['name','email']].values}
    names_as_emails = email_names.assign(fullname = email_names.name.map(email_to_name))
    return names_as_emails

def save_output(final_df,output_file):
    """
    save output of cleaned data to output folder
    """
    output_file = os.path.join(OUTPUT_FOLDER,output_file)
    final_df.to_csv(output_file)
    print("Done saving **{}** to output folder".format(output_file))


def tag_enrollment(course_code,track):
    """
    Given a trainee name and their track, produce the enrolment
    status for the current course
    
    Sol: If this course is on the course list for the track 
    enrolled, then this person is enrolled in the course
    """
    track_courses = course_mapping.get(track,'')
    
    if course_code in track_courses:
        enrolled = 'Yes'
    else:
        enrolled = 'No'
    return enrolled

        

    
def process(names = NAMES_FILE, mode ='single' ):
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


   
    # read names
    namesdf = load_names()
    name_list = namesdf['name'].values.tolist()
    email_list = namesdf['email'].values.tolist()
    
    # read progress files
    bulk_files = bulk_load_data()
    #bulk_files =[course_name_to_code(item) for item in bulk_files]
    all_dataframes = []
    
    for file in bulk_files:
        df = pd.read_csv(file, index_col=None, header=0)
        all_dataframes.append((os.path.basename(file),df))
    
    
    # Now, process each file separately
    
    processed_dataframes = []
    print('===== Processing Progress Files ====',end='\n\n')
    for filename,datadf in all_dataframes:
        
        names_as_fullnames, names_as_emails = filter_names(datadf,name_list,email_list)
        names_as_emails = emails_to_names(namesdf,names_as_emails)
        
        # update name column with full names
        names_as_emails['name'] = names_as_emails.fullname.values
        names_as_emails.drop(columns =['fullname'],inplace = True)
              
        #== output table should have: ==
        # name, track, course, enroled, started, completed
        final_df = final_df = pd.concat((names_as_fullnames,names_as_emails),axis=0)
        
        # add column for track info
        name_track_map = dict(namesdf[['name','track']].values)
        final_df['track'] = final_df['name'].map(name_track_map)
    
        
                
        #1. Add a column for course in the df
        course_code = os.path.splitext(filename)[0]
        course_name = course_code_to_name(course_code)
        final_df['course'] = course_name
        
        # create columns for enrollment status
        temp =[]
        for record in final_df.to_dict(orient = 'record'):
            #check if the course name for current progress file
            # is in course list for thi record
            
            temp.append(tag_enrollment(track= record['track'], course_code = course_code))
        
        final_df['enrolled'] = temp
        
        # change the order of the columns
        final_df = final_df[['name','track','course','enrolled','started_at','percent_complete','completed_at']]
        processed_dataframes.append(final_df)
                
            
        
    output_df = pd.concat(processed_dataframes, axis=0, ignore_index=True)
    save_output(output_df,'current_progress.csv')
            
        
        
        

if __name__ == 'main':
    process()
else:
    process()
    
    

