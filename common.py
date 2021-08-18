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
INPUT_FOLDER = os.path.join(os.getcwd(),'input')
OUTPUT_FOLDER = os.path.join(os.getcwd(),'output')
COURSE_MAPPING_FILE = os.path.join(os.getcwd(),'track_course_mapping.json')
NAMES_FILE = os.path.join(os.getcwd(),'names.csv')
MASTER_FOLDER = os.path.join(os.getcwd(),'master')
HISTORY_FOLDER = os.path.join(os.getcwd(),'history')

with open(COURSE_MAPPING_FILE,'r') as inp:
    TRACK_COURSE_MAPPING = json.load(inp)
#==============================



def bulk_load_data(source_folder = INPUT_FOLDER):
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