import os

import pandas as pd

# df1 = pd.read_excel(r'D:\jx3_file\file_log\MachineLog3\All_Log_Summary.xlsx', sheet_name='81-laptopBVT_2023_09_04')
# df2 = pd.read_excel(r'D:\jx3_file\file_log\8.31日志\All_Log_Summary.xlsx', sheet_name='81-laptopBVT_2023_08_31')
#
# common_rows = pd.merge(df1, df2, on='File Name')
# common_rows.to_excel(r'D:\jx3_file\file_log\8.31日志\81-laptopBVT.xlsx', index=False)

folder_path = r'D:\jx3_file\file_log\8.31日志\sum'

merged_data = pd.DataFrame()
output_file = r'D:\jx3_file\file_log\8.31日志\sum\merged.xlsx'

for filename in os.listdir(folder_path):
    if filename.endswith('.xlsx'):
        print(filename)
        sheet_name = os.path.splitext(filename)[0]
        file_path = os.path.join(folder_path, filename)
        df = pd.read_excel(file_path)
        if os.path.exists(output_file):
            with pd.ExcelWriter(output_file, mode='a', engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name=sheet_name, index=False)
        else:
            with pd.ExcelWriter(output_file) as writer:
                df.to_excel(writer, sheet_name=sheet_name, index=False)


# output_file = r'D:\jx3_file\file_log\8.31日志\sum\merged.xlsx'
# merged_data.to_excel(output_file, index=False)
