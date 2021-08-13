# -*- coding: utf-8 -*-
"""
Created on Fri Aug 13 09:28:18 2021

@author: AmaliTech

This module maps the traks to their courses in json file.
The source file is the excel courselist file
"""

import pandas as pd
import json

df = pd.read_excel('courselist.xlsx',sheet_name = 0)
BE_courses = dict(df[df.BE==1][['code','name']].values)
FE_courses = dict(df[df.FE==1][['code','name']].values)
DS_courses = dict(df[df.DS==1][['code','name']].values)
FS_courses = dict(df[df.FS==1][['code','name']].values)

track_course_map = {
    "Data Science":DS_courses,
    "Front End": FE_courses,
    "Back End": BE_courses,
    "Full Stack": FS_courses,
    }

with open('track_course_mapping.json','w') as out:
    json.dump(track_course_map,out,indent=4)
    
    
# generate course code mappings

    
    
    