import os
import pandas as pd

data_file_folder = './excel'

df = []

for file in os.listdir(data_file_folder):
    if file.endswith('.xls'):
        print('Loading file {0}...'.format(file))
        df.append(pd.read_excel(os.path.join(data_file_folder, file), sheet_name='Sheet 1'))

print(len(df))

df_master = pd.concat(df, axis=0)
df_master.to_excel('master_excel.xls', index=False)