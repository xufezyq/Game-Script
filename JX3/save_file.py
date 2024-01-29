import pandas as pd
from collections import OrderedDict

# !/usr/bin/env python
# -*- coding:utf-8 -*-


df_openfile = pd.read_csv('D:/tab_file/长安站点/g_OpenFile  08-14.csv', encoding='gbk')
df_create = pd.read_csv('D:/tab_file/长安站点/CreateFile  08-14.csv', encoding='gbk')
df_summary = pd.read_csv('D:/tab_file/长安站点/data_all  08-14.csv', encoding='gbk')
data_openfile = OrderedDict()  # 有序字典
data_create = OrderedDict()
data_summary = OrderedDict()
for line in list(df_openfile.columns):
    data_openfile[line] = list(df_openfile[line])  # 构建excel格式
for line in list(df_create.columns):
    data_create[line] = list(df_create[line])  # 构建excel格式
for line in list(df_summary.columns):
    data_summary[line] = list(df_summary[line])  # 构建excel格式

with pd.ExcelWriter('summary.xlsx') as writer:
    obj_openfile = pd.DataFrame(data_openfile)
    obj_create = pd.DataFrame(data_create)
    obj_summary = pd.DataFrame(data_summary)
    obj_openfile.to_excel(writer, sheet_name='g_Openfile', index=False)
    obj_create.to_excel(writer, sheet_name='CreateFile', index=False)
    obj_summary.to_excel(writer, sheet_name='summary', index=False)
print('done!')
