# -*- coding: utf-8 -*-
"""
Created on Thu Aug  5 15:27:18 2021

@author: AmaliTech

For creating master files

====================================
This module is for automatically creating mater files 
corresponding to the courses available

1. read the courselist.csv file
2. for each course in the course list, creat a master excel file
    and save to master folder
"""
import openpyxl
from openpyxl import load_workbook,Workbook
import pandas as pd
import os
import glob 

master_folder = os.path.join(os.getcwd(),'master')

course_df = pd.read_csv('courselist.csv')
course_list = [ '-'.join(name.strip().split()) for name in course_df.name.values]

# duplicate names file for each course
namesfile = 'names.csv'

#ge the people enrolled
names_df = pd.read_csv(namesfile)
names_df['name'] = names_df['name'].apply(lambda x: x.strip()) 

people_enrolled = names_df.values
num_enrolled = len(people_enrolled)
# create a workbook 


def process():
    for course in course_list:
        wb = Workbook()
        summary = wb.active
        summary.title = 'summary'
        progression = wb.create_sheet(title = 'progression')
        
        # Create the sheet headers
        summary.cell(row = 1,column = 1).value = 'Name'
        summary.cell(row = 1,column = 2).value = 'Track'
        summary.cell(row = 1,column = 3).value = 'Started At'
        summary.cell(row = 1,column = 4).value = 'Completed At'
        summary.cell(row = 1,column = 5).value = 'Time Taken(Days)'
        
        # Create progression sheet headers
        progression.cell(row = 1,column = 1).value = 'Name'
        progression.cell(row = 1,column = 2).value = 'Track'
        
        # populate summary sheet with data
        for row, person in enumerate(people_enrolled,2):
            name, email, track = person
            summary.cell(row = row, column = 1).value = name
            summary.cell(row = row, column = 2).value = track
            
            # insert formala for days calculation
            summary.cell(row = row, column = 5).value = "=DAYS(D{},C{})".format(row,row)
            
            progression.cell(row = row, column = 1).value = name
            progression.cell(row = row, column = 2).value = track
        
        
        # save file
        output_file = os.path.join(master_folder,course +'.xlsx')
        if not os.path.exists(output_file):
            wb.save(output_file)
    
    
    
    
if __name__ == 'main':
    process()
else:
    process()
    
    

