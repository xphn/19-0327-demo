import pandas as pd
import numpy as np
import datetime
from matplotlib import pyplot as plt
import glob
import os
import re

root = os.getcwd() #get the current working directory

if os.path.exists('summary_H2S.csv'): # check if the summary csv already exists
    print ('The program will not proceed if the summary_H2S csv file already exists') # check if the summary csv already exists
else:
    file_dir = glob.glob(root+'\\*.csv')
    summary_H2S= []
    for file_name in file_dir:
        table =[]
        Site_ID = os.path.basename(file_name).split('.')[0]

        with open(file_name,'r') as f:
            lines = f.readlines()
            for n in range(len(lines)):
                if 'Date' in lines[n] or 'Time Stamp' in lines[n]:
                    table_header =n
                if 'EVENTS' in lines[n]:
                    table_end = n
                lines[n] = lines[n].split(',')

        table =lines[table_header+1:table_end]
        columns = lines[table_header]

    # Replace the H2S () to H2S (PPM)
        for n, i in enumerate(columns):
            if i == 'H2S ()':
                columns[n] = 'H2S (PPM)'
            if i =='Time Stamp\n':
                columns[n] = 'Time Stamp'

        table_df = pd.DataFrame(table, columns=columns)
        table_df = table_df.replace(r'\n', '', regex=True)
        table_df['Time Stamp'] = pd.to_datetime(table_df['Time Stamp'])
        table_df['Site_ID'] = Site_ID
        table_df = table_df[['Time Stamp','H2S (PPM)','Site_ID']]

    # Considering the PPB scenario and remove the initial and last zeros
        if 'ppb' in Site_ID or 'PPB' in Site_ID:
            table_df['H2S (PPM)'] =table_df['H2S (PPM)'].astype('float64')*0.001
        else:
            none_zero_list =[] # obtain the list of the entries that are not zero
            for i in range(len(table_df)):
                if table_df['H2S (PPM)'][i] != '0':
                    none_zero_list.append(i)
            none_zero_st = min(none_zero_list) # the first none zero
            none_zero_ed = max(none_zero_list)  # the last none zero
            table_df = table_df[none_zero_st:none_zero_ed+1] # eleminating the first and last zeros in the dataframe

        pattern = r'\{.+\}'
        table_df['Site_ID'] = re.sub(pattern, '', Site_ID)
        table_df['Site_ID'] = table_df['Site_ID'].str.strip()

        summary_H2S.append(table_df) #combine all sites'data into a dataframe


    summary_H2S = pd.concat(summary_H2S, axis=0).reset_index().drop(columns=['index'])
    summary_H2S = summary_H2S.sort_values(['Site_ID','Time Stamp'], ascending=[True, True])
    summary_H2S.to_csv(root + '\\summary_H2S.csv', index=False)





