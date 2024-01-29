import csv
import os
import pandas as pd
from datetime import datetime
from collections import OrderedDict

filename_HD = 'D:/tab_file/长安站点/145938_1080长安站点_HD极致8.11.tab'
filename_BD = 'D:/tab_file/长安站点/150304_1080长安站点_BD极致8.11.tab'
data_summary = [
    ['file count', 'size(MB)', 'file count', 'size(MB)', 'file count', 'size(MB)']
]
open_data_all = [
    [0, 0], [0, 0], [0, 0]
]

write_data_open = [
    # ['File', 'Size', 'HD', 'BD', 'HD&BD', 'ONLY_HD', 'ONLY_BD']
]
data_open = {}
with open(filename_HD, 'r') as file:
    reader = csv.reader(file, delimiter='\t')
    for row in reader:
        # 替换分隔符和大小写
        row[3] = row[3].lower()
        row[3] = row[3].replace('/', '\\')
        row[3] = row[3].replace('\\\\', '\\')
        row[3] = row[3].replace('h:\\client\\', '')
        row[3] = row[3].replace('g:\\client\\', '')

        if row[4] == '-1':
            continue
        if row[2][:len('KGDetoursMgr::myOpenFile')] == 'KGDetoursMgr::myOpenFile':
            data_open[row[3]] = [row[4], '1', '0']  # filename size hd bd hd&bd onlyhd onlybd
            # write_data.append([row[3], row[4], '1', '0'])

with open(filename_BD, 'r') as file:
    reader = csv.reader(file, delimiter='\t')
    for row in reader:
        # 替换分隔符和大小写
        row[3] = row[3].lower()
        row[3] = row[3].replace('/', '\\')
        row[3] = row[3].replace('\\\\', '\\')
        row[3] = row[3].replace('h:\\client\\', '')
        row[3] = row[3].replace('g:\\client\\', '')

        if row[4] == '-1':
            continue
        if row[2][:len('KGDetoursMgr::myOpenFile')] == 'KGDetoursMgr::myOpenFile':
            if row[3] in data_open.keys():
                data_open[row[3]][2] = '1'
            else:
                data_open[row[3]] = [row[4], '0', '1']

for key in data_open.keys():
    HD_BD = '0'
    HD = '0'
    BD = '0'
    if data_open[key][1] == '1':
        if data_open[key][2] == '1':
            HD_BD = '1'
        else:
            HD = '1'
    else:
        if data_open[key][2] == '1':
            BD = '1'
    if HD_BD == '1':
        open_data_all[0][0] += 1
        open_data_all[0][1] += int(data_open[key][0])
    if HD == '1':
        open_data_all[1][0] += 1
        open_data_all[1][1] += int(data_open[key][0])
    if BD == '1':
        open_data_all[2][0] += 1
        open_data_all[2][1] += int(data_open[key][0])
    write_data_open.append([key, data_open[key][0], data_open[key][1], data_open[key][2], HD_BD, HD, BD])

# 获取文件目录
cut_index = filename_HD.rindex('/')
dir_path = f"{filename_HD[:cut_index]}{os.sep}"
# 获取当前时间戳
time_string = datetime.now().strftime("%m-%d")
# 创建文件
filename = dir_path + 'g_OpenFile_' + time_string + '.csv'
# 写入文件
with open(filename, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(write_data_open)

# -----------------------------------------------------------------------------------------------------------------------
# 处理create
create_data_all = [
    [0, 0], [0, 0], [0, 0]
]
create_only_data_all = [
    [0, 0], [0, 0], [0, 0]
]

write_data_create = [
    # ['File', 'Size', 'HD', 'BD', 'HD&BD', 'ONLY_HD', 'ONLY_BD', 'ONLY_CREATE']
]
data_create = {}
with open(filename_HD, 'r') as file:
    reader = csv.reader(file, delimiter='\t')
    for row in reader:
        # 替换分隔符和大小写
        row[3] = row[3].lower()
        row[3] = row[3].replace('/', '\\')
        row[3] = row[3].replace('\\\\', '\\')
        row[3] = row[3].replace('h:\\client\\', '')
        row[3] = row[3].replace('g:\\client\\', '')

        if row[4] == '-1':
            continue
        if row[2][:len('KGDetoursMgr::myCreateFile')] == 'KGDetoursMgr::myCreateFile':
            data_create[row[3]] = [row[4], '1', '0']
            # write_data.append([row[3], row[4], '1', '0'])

with open(filename_BD, 'r') as file:
    reader = csv.reader(file, delimiter='\t')
    for row in reader:
        # 替换分隔符和大小写
        row[3] = row[3].lower()
        row[3] = row[3].replace('/', '\\')
        row[3] = row[3].replace('\\\\', '\\')
        row[3] = row[3].replace('h:\\client\\', '')
        row[3] = row[3].replace('g:\\client\\', '')

        if row[4] == '-1':
            continue
        if row[2][:len('KGDetoursMgr::myCreateFile')] == 'KGDetoursMgr::myCreateFile':
            if row[3] in data_create.keys():
                data_create[row[3]][2] = '1'
            else:
                data_create[row[3]] = [row[4], '0', '1']

for key in data_create.keys():
    HD_BD = '0'
    HD = '0'
    BD = '0'
    ONLY_CREATE = '1'
    if data_create[key][1] == '1':
        if data_create[key][2] == '1':
            HD_BD = '1'
        else:
            HD = '1'
    else:
        if data_create[key][2] == '1':
            BD = '1'
    if key in data_open.keys():
        ONLY_CREATE = '0'
    if HD_BD == '1':
        if ONLY_CREATE == '1':
            create_only_data_all[0][0] += 1
            create_only_data_all[0][1] += int(data_create[key][0])
        else:
            create_data_all[0][0] += 1
            create_data_all[0][1] += int(data_create[key][0])
    if HD == '1':
        if ONLY_CREATE == '1':
            create_only_data_all[1][0] += 1
            create_only_data_all[1][1] += int(data_create[key][0])
        else:
            create_data_all[1][0] += 1
            create_data_all[1][1] += int(data_create[key][0])
    if BD == '1':
        if ONLY_CREATE == '1':
            create_only_data_all[2][0] += 1
            create_only_data_all[2][1] += int(data_create[key][0])
        else:
            create_data_all[2][0] += 1
            create_data_all[2][1] += int(data_create[key][0])
    write_data_create.append(
        [key, data_create[key][0], data_create[key][1], data_create[key][2], HD_BD, HD, BD, ONLY_CREATE])

filename = dir_path + 'CreateFile_' + time_string + '.csv'
with open(filename, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(write_data_create)
for i in range(len(open_data_all)):
    data_summary.append([open_data_all[i][0], round(int(open_data_all[i][1]) / 1048576, 3),
                         create_data_all[i][0], round(int(create_data_all[i][1]) / 1048576, 3),
                         create_only_data_all[i][0], round(int(create_only_data_all[i][1]) / 1048576, 3),
                         ])
    filename = dir_path + 'data_all_' + time_string + '.csv'
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data_summary)

df_openfile = pd.DataFrame(write_data_open, columns=['File', 'Size', 'HD', 'BD', 'HD&BD', 'ONLY_HD', 'ONLY_BD'])
df_create = pd.DataFrame(write_data_create,
                         columns=['File', 'Size', 'HD', 'BD', 'HD&BD', 'ONLY_HD', 'ONLY_BD', 'ONLY_CREATE'])
df_summary = pd.DataFrame(data_summary,
                          columns=['KGDetoursMgr_myOpenFile', '', 'KGDetoursMgr_myCreateFile', '', 'ONLY_CREATE', ''])
# data_openfile = OrderedDict()  # 有序字典
# data_create = OrderedDict()
# data_summary = OrderedDict()
# for line in list(df_openfile.columns):
#     data_openfile[line] = list(df_openfile[line])  # 构建excel格式
# for line in list(df_create.columns):
#     data_create[line] = list(df_create[line])  # 构建excel格式
# for line in list(df_summary.columns):
#     data_summary[line] = list(df_summary[line])  # 构建excel格式

filename = dir_path + 'Summary_' + time_string + '.xlsx'
with pd.ExcelWriter(filename) as writer:
    # obj_openfile = pd.DataFrame(data_openfile)
    # obj_create = pd.DataFrame(data_create)
    # obj_summary = pd.DataFrame(data_summary)
    # obj_openfile.to_excel(writer, sheet_name='g_Openfile', index=False)
    # obj_create.to_excel(writer, sheet_name='CreateFile', index=False)
    # obj_summary.to_excel(writer, sheet_name='summary', index=False)
    df_openfile.to_excel(writer, sheet_name='g_Openfile', index=False)
    df_create.to_excel(writer, sheet_name='createfile', index=False)
    df_summary.to_excel(writer, sheet_name='summary', index=False)
print("done")
