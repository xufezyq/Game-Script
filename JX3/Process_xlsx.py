import csv
import os
import pandas as pd
from datetime import datetime


class ProcessXlsx(object):
    def __init__(self, filename_hd, filename_bd):
        self.filename_hd = filename_hd
        self.filename_bd = filename_bd
        self.data_texture = {}
        self.data_mesh = {}
        self.data_material = {}
        self.all_texture = [[0, 0], [0, 0], [0, 0]]
        self.all_mesh = [[0, 0], [0, 0], [0, 0]]
        self.all_material = [[0, 0], [0, 0], [0, 0]]
        self.texture = [[0, 0], [0, 0], [0, 0]]
        self.mesh = [[0, 0], [0, 0], [0, 0]]
        self.material = [[0, 0], [0, 0], [0, 0]]
        self.write_data_texture = []
        self.write_data_mesh = []
        self.write_data_material = []
        self.data_summary = []

    def read_texture(self):
        # 读取hd文件
        df_hd = pd.read_excel(self.filename_hd, 'texture')
        for _, row in df_hd.iterrows():
            self.data_texture[row['File']] = [row['Size(KB)'], '1', '0', '-1']
        df_bd = pd.read_excel(self.filename_bd, 'texture')
        for _, row in df_bd.iterrows():
            if row['File'] in self.data_texture.keys():
                self.data_texture[row['File']][2] = '1'
                if self.data_texture[row['File']][0] != row['Size(KB)']:
                    self.data_texture[row['File']][3] = row['Size(KB)']
            else:
                self.data_texture[row['File']] = [row['Size(KB)'], '0', '1', '-1']
        # 处理并写入data
        for key in self.data_texture.keys():
            hd_bd = '0'
            hd = '0'
            bd = '0'
            find_bd = '0'
            if key.lower().find("bd") != -1:
                find_bd = '1'
            if self.data_texture[key][1] == '1':  # HD
                if self.data_texture[key][2] == '1':  # BD
                    hd_bd = '1'
                else:  # only hd
                    hd = '1'
            else:
                if self.data_texture[key][2] == '1':  # only bd
                    bd = '1'
            if hd_bd == '1':
                self.all_texture[0][0] += 1
                self.all_texture[0][1] += int(self.data_texture[key][0])
            if hd == '1':
                self.all_texture[1][0] += 1
                self.all_texture[1][1] += int(self.data_texture[key][0])
            if bd == '1':
                self.all_texture[2][0] += 1
                self.all_texture[2][1] += int(self.data_texture[key][0])
            if self.data_texture[key][1] == '1':  # File one
                self.texture[0][0] += 1
                self.texture[0][1] += int(self.data_texture[key][0])
            if self.data_texture[key][2] == '1':  # File Two
                self.texture[1][0] += 1
                self.texture[1][1] += int(self.data_texture[key][0])

            # 写入write_data_texture
            self.write_data_texture.append(
                [key, self.data_texture[key][0], self.data_texture[key][1], self.data_texture[key][2],
                 self.data_texture[key][3], hd_bd, hd, bd, find_bd]
            )

    def read_mesh(self):
        # 读取hd文件
        df_hd = pd.read_excel(self.filename_hd, 'mesh')
        for _, row in df_hd.iterrows():
            self.data_mesh[row['Name']] = [row['Size'], '1', '0', '-1']
        df_bd = pd.read_excel(self.filename_bd, 'mesh')
        for _, row in df_bd.iterrows():
            if row['Name'] in self.data_mesh.keys():
                self.data_mesh[row['Name']][2] = '1'
                if self.data_mesh[row['Name']][0] != row['Size']:
                    self.data_mesh[row['Name']][3] = row['Size']
            else:
                self.data_mesh[row['Name']] = [row['Size'], '0', '1', '-1']
        # 处理并写入data
        for key in self.data_mesh.keys():
            hd_bd = '0'
            hd = '0'
            bd = '0'
            find_bd = '0'
            if key.lower().find("bd") != -1:
                find_bd = '1'
            if self.data_mesh[key][1] == '1':  # HD
                if self.data_mesh[key][2] == '1':  # BD
                    hd_bd = '1'
                else:  # only hd
                    hd = '1'
            else:
                if self.data_mesh[key][2] == '1':  # only bd
                    bd = '1'
            if hd_bd == '1':
                self.all_mesh[0][0] += 1
                self.all_mesh[0][1] += int(self.data_mesh[key][0])
            if hd == '1':
                self.all_mesh[1][0] += 1
                self.all_mesh[1][1] += int(self.data_mesh[key][0])
            if bd == '1':
                self.all_mesh[2][0] += 1
                self.all_mesh[2][1] += int(self.data_mesh[key][0])
            if self.data_mesh[key][1] == '1':  # File one
                self.mesh[0][0] += 1
                self.mesh[0][1] += int(self.data_mesh[key][0])
            if self.data_mesh[key][2] == '1':  # File two
                self.mesh[1][0] += 1
                self.mesh[1][1] += int(self.data_mesh[key][0])
            self.write_data_mesh.append(
                [key, self.data_mesh[key][0] / 1024, self.data_mesh[key][1], self.data_mesh[key][2],
                 self.data_mesh[key][3], hd_bd, hd, bd, find_bd])

    def read_material(self):
        # 读取hd文件
        df_hd = pd.read_excel(self.filename_hd, 'material')
        for _, row in df_hd.iterrows():
            self.data_material[row['Name']] = ['1', '0']
        df_bd = pd.read_excel(self.filename_bd, 'material')
        for _, row in df_bd.iterrows():
            if row['Name'] in self.data_material.keys():
                self.data_material[row['Name']][1] = '1'
            else:
                self.data_material[row['Name']] = ['0', '1']
        # 处理并写入data
        for key in self.data_material.keys():
            hd_bd = '0'
            hd = '0'
            bd = '0'
            find_bd = '0'
            if key.lower().find("bd") != -1:
                find_bd = '1'
            if self.data_material[key][0] == '1':  # HD
                if self.data_material[key][1] == '1':  # BD
                    hd_bd = '1'
                else:  # only hd
                    hd = '1'
            else:
                if self.data_material[key][1] == '1':  # only bd
                    bd = '1'
            if hd_bd == '1':
                self.all_material[0][0] += 1
            if hd == '1':
                self.all_material[1][0] += 1
            if bd == '1':
                self.all_material[2][0] += 1
            if self.data_material[key][0] == '1':  # File one
                self.material[0][0] += 1
            if self.data_material[key][1] == '1':
                self.material[1][0] += 1
            self.write_data_material.append(
                [key, self.data_material[key][0], self.data_material[key][1], hd_bd, hd, bd, find_bd]
            )

    def save_file(self):
        self.data_summary.append(['file count', 'size(MB)', 'file count', 'size(MB)', 'file count', 'size(MB)'])
        for i in range(2):
            self.data_summary.append([
                self.texture[i][0], round(int(self.texture[i][1]) / 1024, 3),
                self.mesh[i][0], round(int(self.mesh[i][1]) / 1024 / 1024, 3),
                self.material[i][0], 0
            ])
        self.data_summary.append([
            self.texture[1][0] - self.texture[0][0],
            round((int(self.texture[1][1]) - int(self.texture[0][1])) / 1024, 3),
            self.mesh[1][0] - self.mesh[0][0],
            round((int(self.mesh[1][1]) - int(self.mesh[0][1])) / 1024 / 1024, 3),
            self.material[1][0] - self.material[0][0], 0
        ])
        df_texture = pd.DataFrame(
            self.write_data_texture,
            columns=['FileName', 'Size(KB)', 'FileOne', 'FileTwo', 'DIFF_SIZE', 'One&Two', 'Only_One', 'Only_Two',
                     'Find_BD'])
        df_mesh = pd.DataFrame(
            self.write_data_mesh,
            columns=['FileName', 'Size(KB)', 'FileOne', 'FileTwo', 'DIFF_SIZE', 'One&Two', 'Only_One', 'Only_Two',
                     'Find_BD'])
        df_material = pd.DataFrame(
            self.write_data_material,
            columns=['FileName', 'FileOne', 'FileTwo', 'One&Two', 'Only_One', 'Only_Two', 'Find_BD'])
        df_summary = pd.DataFrame(
            self.data_summary,
            columns=['texture', '', 'mesh', '', 'material', '']
        )

        # 获取文件目录
        cut_index = self.filename_bd.rindex('\\')
        dir_path = f"{self.filename_bd[:cut_index]}{os.sep}"
        # 获取文件时间戳
        time_string = datetime.now().strftime("%m-%d")
        # 保存至文件
        filename = dir_path + 'Summary_' + time_string + '.xlsx'
        with pd.ExcelWriter(filename) as writer:
            df_texture.to_excel(writer, sheet_name='texture', index=False)
            df_mesh.to_excel(writer, sheet_name='mesh', index=False)
            df_material.to_excel(writer, sheet_name='material', index=False)
            df_summary.to_excel(writer, sheet_name='summary', index=False, startcol=1)
            data = {"Column": ['', 'File One', 'File Two', 'Two-One']}
            df = pd.DataFrame(data)
            df.to_excel(writer, sheet_name='summary', index=False, startrow=0, startcol=0)

    def run(self):
        self.read_texture()
        self.read_mesh()
        self.read_material()
        self.save_file()


if __name__ == '__main__':
    xx = ProcessXlsx(r'D:\jx3_file\file_fire\刀宗内存定点测试\0823\MX350_简约_TestResSpy\8.23刀宗.xlsx',
                     r'D:\jx3_file\file_fire\刀宗内存定点测试\刀宗内存测试 8.28\8.28MX350\Res\Texture_Mesh_Manager.xlsx')
    xx.run()
    print('done!')
