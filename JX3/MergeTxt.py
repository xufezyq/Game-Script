#!/usr/bin/env python
# -*- coding = utf-8 -*-
import os
import pandas as pd
from Process_xlsx import ProcessXlsx

if __name__ == '__main__':
    print("begin")
    directory = r"D:\jx3_file\file_fire\9.18 1080_pakv_HD巴陵梯田内存测试\1080_散文件_HD巴陵极致画质_0918\Res"
    file_list = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            # 获取文件的完整路径
            file_path = os.path.join(root, file)
            # 将文件路径添加到列表中
            file_list.append(file_path)
    keywords = ["MaterialInsPackData", "MeshResources", "ShaderTextureManagerResources", "DataManagerResources",
                "InitSingleActor", "TerrainInfo", "UITextureInfo"]
    # 定义一个空字典用于存储数据
    data_dict = {}
    name_dict = {
        "MaterialInsPackData": "material",
        "MeshResources": "mesh",
        "ShaderTextureManagerResources": "texture",
        "DataManagerResources": "DataManagerResources",
        "InitSingleActor": "InitSingleActor",
        "TerrainInfo": "TerrainInfo",
        "UITextureInfo": "UITextureInfo"}
    # 循环读取每个文件并保存到字典中
    for keyword in keywords:
        for file in file_list:
            if keyword in file:
                file_name = os.path.basename(file)
                data = pd.read_csv(file, encoding='gbk', sep="\t")
                # 获取文件名（作为表名）
                data_dict[name_dict[keyword]] = data
                break
    # 创建Excel写入器
    execl_name = os.path.join(directory, "Texture_Mesh_Manager.xlsx")
    writer = pd.ExcelWriter(execl_name)

    # 将字典中的数据写入不同的表格
    for table_name, data in data_dict.items():
        # 将数据写入Excel工作表
        data.to_excel(writer, sheet_name=table_name, index=False)

    # 保存Excel文件
    writer.close()

    # 保存Data Manager Resources
    data_type = {}
    data_type_summary = {}
    df = pd.read_excel(execl_name, 'DataManagerResources')
    for _, row in df.iterrows():
        if row['Type'] not in data_type.keys():
            data_type[row['Type']] = [[row['Name'], row['Size'], row['RefCount']]]
            data_type_summary[row['Type']] = int(row['Size'])
        else:
            data_type[row['Type']].append([row['Name'], row['Size'], row['RefCount']])
            data_type_summary[row['Type']] += int(row['Size'])
    filename = os.path.join(directory, "DataManagerResources.xlsx")
    write_data_type_summary = []
    with pd.ExcelWriter(filename) as writer:
        for key in data_type.keys():
            write_data_type = data_type[key]
            write_data_type_summary.append([key, round(data_type_summary[key] / 1024, 3), len(write_data_type)])
            df = pd.DataFrame(write_data_type, columns=['Name', 'Size', 'RefCount'])
            df.to_excel(writer, sheet_name=key, index=False)
        df = pd.DataFrame(write_data_type_summary, columns=['Type', 'Size(KB)', 'Count'])
        df.to_excel(writer, sheet_name='summary', index=False)
    print('done!')
