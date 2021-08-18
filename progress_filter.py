# -*- coding: utf-8 -*-
"""
This script would do the following:
    1. filter the course progress from codecademy to the list of names specified
    2. add the current progress to the master excel workbook for the given course
    
"""
import pandas as pd
import glob
import os

names = r"C:\Users\AmaliTech\Documents\CourseProgress Processing\names.csv"

from common import PROGRESS_FOLDER, OUTPUT_FOLDER, NAMES_FILE
from common import TRACK_COURSE_MAPPING
from common import course_name_to_code
from common import save_output
# with open(TRACK_COURSE_MAPPING_FILE,'r') as inp:
#     TRACK_COURSE_MAPPING = json.load(inp)



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
    for track in TRACK_COURSE_MAPPING:
        if course_code in TRACK_COURSE_MAPPING[track]:
            return TRACK_COURSE_MAPPING[track][course_code]


    
    
    
def bulk_load_data(source_folder):
    files = glob.glob(PROGRESS_FOLDER + "/*.csv")
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
    print('processing {}'.format(progress_file))
    
    namesdf = load_names()
    name_list = namesdf['name'].values.tolist()
    email_list = namesdf['email'].values.tolist()
    progress_df = load_data(progress_file)
    # seperate the correct full names from email names
    names_as_fullnames, names_as_emails = filter_names(progress_df,name_list,email_list)
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
    
    #get course name
    # course_code = os.path.splitext(progress_file)[0]
    # course_name = course_code_to_name(course_code)
    course_name = os.path.splitext(os.path.basename(progress_file))[0]
    course_code =  course_name_to_code(course_name)
    final_df['course'] = course_name
    
    # create columns for enrollment status
    temp =[]
    for record in final_df.to_dict(orient = 'records'):
        #check if the course name for current progress file
        # is in course list for thi record
        
        temp.append(tag_enrollment(track= record['track'], course_code = course_code))
    
    final_df['enrolled'] = temp
    #filter out those enrolled
    final_df = final_df[final_df.enrolled == 'Yes']
    
    # change the order of the columns
    final_df = final_df[['name','track','course','enrolled','started_at','percent_complete','completed_at']]
    save_output(final_df,course_name+'.csv')
    
    return final_df
    
def process(names = NAMES_FILE):
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
    progress_files = bulk_load_data(source_folder = PROGRESS_FOLDER)
   
    #progress_files =[course_name_to_code(item) for item in progress_files]
    all_dataframes = []
    
    for file in progress_files:
        progress_df = pd.read_csv(file, index_col=None, header=0)
        all_dataframes.append((os.path.basename(file),progress_df))
    
    
    # Now, process each file separately
    
    processed_dataframes = []
    print('===== Processing Progress Files ====',end='\n\n')
    for filename,datadf in all_dataframes:
        print('processing {}'.format(filename))
        
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
        for record in final_df.to_dict(orient = 'records'):
            #check if the course name for current progress file
            # is in course list for thi record
            
            temp.append(tag_enrollment(track= record['track'], course_code = course_code))
        
        final_df['enrolled'] = temp
        
        #filter out those enrolled
        final_df = final_df[final_df.enrolled == 'Yes']
        
        # change the order of the columns
        final_df = final_df[['name','track','course','enrolled','started_at','percent_complete','completed_at']]
        #processed_dataframes.append(final_df)
        #save_output(final_df, course_name)
                
            
        
    output_df = pd.concat(processed_dataframes, axis=0, ignore_index=True)
    save_output(output_df,'current_progress.csv')
            
        
        
        

if __name__ == 'main':
    process()
else:
    process()
    
    

