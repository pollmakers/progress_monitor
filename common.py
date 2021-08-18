# -*- coding: utf-8 -*-
"""
Created on Mon Aug 16 11:14:35 2021

@author: AmaliTech
"""
import glob
import os
import pandas as pd
import json
#=========== CONSTANTS ========
PROGRESS_FOLDER = os.path.join(os.getcwd(),'progress_reports')
OUTPUT_FOLDER = os.path.join(os.getcwd(),'output')
COURSE_MAPPING_FILE = os.path.join(os.getcwd(),'track_course_mapping.json')
NAMES_FILE = os.path.join(os.getcwd(),'names.csv')
MASTER_FOLDER = os.path.join(os.getcwd(),'master')
HISTORY_FOLDER = os.path.join(os.getcwd(),'history')


namesfile = 'names.csv'
trainee_df = pd.read_csv(namesfile)
trainee_df['name'] = trainee_df['name'].apply(lambda x: x.strip()) 
trainee_list = trainee_df.to_dict(orient = 'records')

with open(COURSE_MAPPING_FILE,'r') as inp:
    TRACK_COURSE_MAPPING = json.load(inp)
    

ALL_COURSES = {}
for track in TRACK_COURSE_MAPPING:
    ALL_COURSES.update(TRACK_COURSE_MAPPING[track])

#==============================

def get_course_enrolment(course):
    """
    Returns the list of trainees enrolled in this course

    Parameters
    ----------
    course : TYPE
        DESCRIPTION.

    Returns
    -------
    enrolled : TYPE
        DESCRIPTION.

    """
    
    enrolled = []
            
    for trainee in trainee_list:
        
        track_courses = TRACK_COURSE_MAPPING.get(trainee['track'])
        if track_courses:
            if course in track_courses.values():
                enrolled.append(trainee['name'])
        else:
            continue
    return enrolled


def course_name_to_code(course_name):
    """
    Returns the course code given a course name

    Parameters
    ----------
    course_name : TYPE
        DESCRIPTION.

    Returns
    -------
    TYPE
        DESCRIPTION.

    """
    for track in TRACK_COURSE_MAPPING:
        for key, value in TRACK_COURSE_MAPPING[track].items(): 
         if course_name.strip() == value: 
             return key 
  
    return "key doesn't exist"

def bulk_load_data(source_folder = PROGRESS_FOLDER):
    files = glob.glob(source_folder + "/*.csv")
    return files

def load_data(file):
    return pd.read_csv(file)

def get_progress_data(file_name):
    
    try:
        progress_file = file_name if file_name.endswith(".csv") else file_name + ".csv"
        progress_data = load_data(progress_file)
    except FileNotFoundError:
        print("{} does not exist in master folder".format(file_name))
    
    return progress_file, progress_data

def save_output(final_df,output_file):
    """
    save output of cleaned data to output folder
    """
    output_file = os.path.join(OUTPUT_FOLDER,output_file)
    final_df.to_csv(output_file)
    print("Done saving **{}** to output folder".format(output_file))