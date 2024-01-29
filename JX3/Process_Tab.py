import csv
import os
import pandas as pd
from datetime import datetime


def replace_sep(row):
    row[3] = row[3].lower()
    row[3] = row[3].replace('/', '\\')
    row[3] = row[3].replace('\\\\', '\\')
    row[3] = row[3].replace('g:\\client\\', '')
    row[3] = row[3].replace('h:\\client\\', '')


class ProcessTab(object):
    def __init__(self, filename_hd, filename_bd):
        self.filename_HD = filename_hd
        self.filename_BD = filename_bd
        self.data_open = {}
        self.data_create = {}
        self.write_data_open = []
        self.write_data_create = []
        self.data_summary = []
        self.open_data_all = [[0, 0], [0, 0], [0, 0]]
        self.create_data_all = [[0, 0], [0, 0], [0, 0]]
        self.create_only_data_all = [[0, 0], [0, 0], [0, 0]]

    def read_tab_open_file(self):
        # 读取hd的文件
        with open(self.filename_HD, 'r') as file:
            reader = csv.reader(file, delimiter='\t')
            for row in reader:
                # 替换分隔符和大小写
                replace_sep(row)
                # 文件大小为-1跳过
                if row[4] == '-1':
                    continue
                # 是openfile写入data_open
                if row[2][:len('KGDetoursMgr::myOpenFile')] == 'KGDetoursMgr::myOpenFile':
                    self.data_open[row[3]] = [int(row[4]), '1', '0']  # filename size hd bd hd&bd onlyhd onlybd
        # 读取bd的文件
        with open(self.filename_BD, 'r') as file:
            reader = csv.reader(file, delimiter='\t')
            for row in reader:
                # 替换分隔符和大小写
                replace_sep(row)
                # 文件大小为-1跳过
                if row[4] == '-1':
                    continue
                if row[2][:len('KGDetoursMgr::myOpenFile')] == 'KGDetoursMgr::myOpenFile':
                    if row[3] in self.data_open.keys():
                        self.data_open[row[3]][2] = '1'
                    else:
                        self.data_open[row[3]] = [int(row[4]), '0', '1']
        # 处理并写入data_open
        for key in self.data_open.keys():
            hd_bd = '0'
            hd = '0'
            bd = '0'
            find_bd = '0'
            if key.find('bd') != -1:
                find_bd = '1'
            if self.data_open[key][1] == '1':
                if self.data_open[key][2] == '1':
                    hd_bd = '1'
                else:
                    hd = '1'
            else:
                if self.data_open[key][2] == '1':
                    bd = '1'
            if hd_bd == '1':
                self.open_data_all[0][0] += 1
                self.open_data_all[0][1] += int(self.data_open[key][0])
            if hd == '1':
                self.open_data_all[1][0] += 1
                self.open_data_all[1][1] += int(self.data_open[key][0])
            if bd == '1':
                self.open_data_all[2][0] += 1
                self.open_data_all[2][1] += int(self.data_open[key][0])
            self.write_data_open.append(
                [key, self.data_open[key][0], self.data_open[key][1], self.data_open[key][2], hd_bd, hd, bd, find_bd])

    def read_tab_create_file(self):
        with open(self.filename_HD, 'r') as file:
            reader = csv.reader(file, delimiter='\t')
            for row in reader:
                # 替换分隔符和大小写
                replace_sep(row)
                # 文件大小为-1跳过
                if row[4] == '-1':
                    continue
                if row[2][:len('KGDetoursMgr::myCreateFile')] == 'KGDetoursMgr::myCreateFile':
                    self.data_create[row[3]] = [int(row[4]), '1', '0']
        with open(self.filename_BD, 'r') as file:
            reader = csv.reader(file, delimiter='\t')
            for row in reader:
                # 替换分隔符和大小写
                replace_sep(row)
                # 文件大小为-1跳过
                if row[4] == '-1':
                    continue
                if row[2][:len('KGDetoursMgr::myCreateFile')] == 'KGDetoursMgr::myCreateFile':
                    if row[3] in self.data_create.keys():
                        self.data_create[row[3]][2] = '1'
                    else:
                        self.data_create[row[3]] = [int(row[4]), '0', '1']
        for key in self.data_create.keys():
            hd_bd = '0'
            hd = '0'
            bd = '0'
            only_create = '1'
            find_bd = '0'
            if key.find('bd') != -1:
                find_bd = '1'
            if self.data_create[key][1] == '1':
                if self.data_create[key][2] == '1':
                    hd_bd = '1'
                else:
                    hd = '1'
            else:
                if self.data_create[key][2] == '1':
                    bd = '1'
            if key in self.data_open.keys():
                only_create = '0'
            if hd_bd == '1':
                if only_create == '1':
                    self.create_only_data_all[0][0] += 1
                    self.create_only_data_all[0][1] += int(self.data_create[key][0])
                self.create_data_all[0][0] += 1
                self.create_data_all[0][1] += int(self.data_create[key][0])
            if hd == '1':
                if only_create == '1':
                    self.create_only_data_all[1][0] += 1
                    self.create_only_data_all[1][1] += int(self.data_create[key][0])
                self.create_data_all[1][0] += 1
                self.create_data_all[1][1] += int(self.data_create[key][0])
            if bd == '1':
                if only_create == '1':
                    self.create_only_data_all[2][0] += 1
                    self.create_only_data_all[2][1] += int(self.data_create[key][0])
                self.create_data_all[2][0] += 1
                self.create_data_all[2][1] += int(self.data_create[key][0])
            self.write_data_create.append(
                [key, self.data_create[key][0], self.data_create[key][1], self.data_create[key][2], hd_bd, hd, bd,
                 only_create, find_bd])

    def save_file(self):
        self.data_summary.append(['file count', 'size(MB)', 'file count', 'size(MB)', 'file count', 'size(MB)'])
        for i in range(3):
            self.data_summary.append([
                self.open_data_all[i][0], round(int(self.open_data_all[i][1]) / 1048576, 3),
                self.create_data_all[i][0], round(int(self.create_data_all[i][1]) / 1048576, 3),
                self.create_only_data_all[i][0], round(int(self.create_only_data_all[i][1]) / 1048576, 3),
            ])
        df_open_file = pd.DataFrame(
            self.write_data_open,
            columns=['File', 'Size', 'File_One', 'File_Two', 'One&Two', 'Only_One', 'Only_Two', 'Find_BD'])
        df_create = pd.DataFrame(
            self.write_data_create,
            columns=['File', 'Size', 'File_One', 'File_Two', 'One&Two', 'Only_One', 'Only_Two', 'ONLY_CREATE',
                     'Find_BD'])
        df_summary = pd.DataFrame(
            self.data_summary,
            columns=['KGDetoursMgr_myOpenFile', '', 'KGDetoursMgr_myCreateFile', '', 'ONLY_CREATE', ''])
        # 获取文件目录
        cut_index = self.filename_HD.rindex('\\')
        dir_path = f"{self.filename_HD[:cut_index]}{os.sep}"
        # 获取文件时间戳
        time_string = datetime.now().strftime("%m-%d")
        # 保存至文件
        filename = dir_path + 'Summary_' + time_string + '.xlsx'
        with pd.ExcelWriter(filename) as writer:
            df_open_file.to_excel(writer, sheet_name='g_Openfile', index=False)
            df_create.to_excel(writer, sheet_name='CreateFile', index=False)
            df_summary.to_excel(writer, sheet_name='Summary', index=False)

    def run(self):
        self.read_tab_open_file()
        self.read_tab_create_file()
        self.save_file()


if __name__ == '__main__':
    xx = ProcessTab(r'D:\file_jx3\file_xlsx\个人重测 7.5 纯阳\7.5.tab',
                    r'D:\file_jx3\file_xlsx\个人重测 8.20 纯阳\8.20.tab')
    xx.run()
    print('done!')
