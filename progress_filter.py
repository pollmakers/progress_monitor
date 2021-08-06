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

input_folder = os.path.join(os.getcwd(),'input')
output_folder = os.path.join(os.getcwd(),'output')

modes = {'y':'bulk','n':'single'}

#== Test data ================
namesfile = 'names.csv'
progressfile = 'progress.csv'
#=============================

# the names in the data file are either names or emails. We want to:
"""
NB: A master template exist containing all names  and track information
1. create a new column that contains names names only
2. filter the data table to cotain only records specified in the names

"""
def load_data(file):
    return pd.read_csv(file)
    
def load_names(file = namesfile):
    """
    Reads names in the names.csv
    """
    namesdf = pd.read_csv(file)
    names = [name.strip() for name in namesdf.name]
    emails = [email.strip() for email in namesdf.email]
    return namesdf,names,emails
    
def bulk_load_data():
    files = glob.glob(input_folder + "/*.csv")
    return files
            
def filter_names(progress_df,name_list = None,email_list = None):
    """
    filters names in progress file to mathc those in names.csv
    """
    
    # seperate the names in the so that those with emails provided as names
    # will be in a seprate list
    
    _,name_list,email_list = load_names()
    names_as_fullnames = progress_df[progress_df.name.isin(name_list)]
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
    output_file = os.path.join(output_folder,output_file)
    final_df.to_csv(output_file)
    print("Done saving **{}** to output folder".format(output_file))
    
def process(names = namesfile, mode ='single' ):
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
    
    
    response = input("Do you want to process multiple files? Y/N:  ")
    
    mode = modes[response.lower()]
    if mode == 'single':
        print()
        print("Make sure the file specified is in the `input` folder")
        print("The output will be in the `output` folder with the same name")
        input_file = input("What is the name of the progress file (without the extension)?   ")
        #output_file = input("What do you want to call the output file: e.g output.csv  ")
        
        
        namesdf = load_names()[0]
        name_list = load_names()[1]
        email_list = load_names()[2]
        
        # Read progress file
        input_file += ".csv"
        datadf = pd.read_csv('databases.csv')#(input_file)
        
        # Create filter to isolate names in name list by name and by email
        # filter1 contains full names, filter 2 contains emails
        names_as_fullnames, names_as_emails = filter_names(datadf,name_list,email_list)
        
        # change email names to full names
        names_as_emails = emails_to_names(namesdf,names_as_emails)
        
        # for uniformity, and easier join add a fullname column to the 
        #names_as_fullnames = names_as_fullnames.assign(fullname = names_as_fullnames.name)
        
        #Replace the data in the name column with then full name column and 
        # drop the full name column
        
        names_as_emails['name'] = names_as_emails.fullname.values
        names_as_emails.drop(columns =['fullname'],inplace = True)
        
        # Join the two filtered tables
        final_df = pd.concat((names_as_fullnames,names_as_emails),axis=0)
        #final_df.drop(columns = ['fullname'],inplace = True)
        
        # create a new column that contains only names: Current file contains name/email
        # for name column
        save_output(final_df,input_file)
        
    elif mode == 'bulk':
        # read names
        namesdf = load_names()[0]
        name_list = load_names()[1]
        email_list = load_names()[2]
        
        # read progress files
        bulk_files = bulk_load_data()
        all_dataframes = []
        
        for file in bulk_files:
            df = pd.read_csv(file, index_col=None, header=0)
            all_dataframes.append((os.path.basename(file),df))
        
        #datadf = pd.concat(all_dataframes, axis=0, ignore_index=True)
        # Now, process each file separately
        for filename,datadf in all_dataframes:
            names_as_fullnames, names_as_emails = filter_names(datadf,name_list,email_list)
            names_as_emails = emails_to_names(namesdf,names_as_emails)
            
            # update name column with full names
            names_as_emails['name'] = names_as_emails.fullname.values
            names_as_emails.drop(columns =['fullname'],inplace = True)
            
            #names_as_fullnames = names_as_fullnames.assign(fullname = names_as_fullnames.name)
            
            
            final_df = pd.concat((names_as_fullnames,names_as_emails),axis=0)
            save_output(final_df,filename)
            
        
        
        

if __name__ == 'main':
    process()
else:
    process()
    
    

