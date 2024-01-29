import os.path

import pandas as pd

data = pd.read_excel(r'D:\jx3_file\file_fire\10.12 九老洞资源数据采集\九老洞.xlsx')

# data['Count'] = data['File'].map(data['File'].value_counts())
# # 打印更新后的表格
# data.to_excel(r'D:\jx3_svn\Hook_g_OpenFile-master\hook_g_openfile\MonitorMsgLoopFrameLoop\logs\output.xlsx', index=False)



column_name = 'File'
duplicates = data[column_name].value_counts()

file_type = []
file_size = []
for i in duplicates.index:
    file_extension = os.path.splitext(i)[1]
    file_type.append(file_extension)

# 创建包含重复项和计数的数据框
df_duplicates = pd.DataFrame({'Value': duplicates.index, 'Count': duplicates.values, 'Type': file_type})

# 将数据框保存为新的.xlsx文件
df_duplicates.to_excel(
    r'D:\jx3_file\file_fire\10.12 九老洞资源数据采集\duplicates.xlsx', index=False)
