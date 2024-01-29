# -*- coding: utf-8 -*-
import os

import pandas as pd

log_set = set()


def merge_log(log_filename):
    # log_filename = r'D:\jx3_file\file_log\JX3Client_2052-zhcn_2023_08_31_14_14_45.log'
    target_string = '[KG3DEngineAdapter] render thread load file'
    with open(log_filename, 'r', encoding='gbk', errors='ignore') as file:
        for line in file:
            if target_string in line:
                start_index = line.rfind('begin: ')
                if start_index == -1:
                    start_index = line.find('end: ') + len('end: ')
                    end_index = line.find(', succeed')
                    if line[start_index:end_index] not in log_set:
                        log_set.add(line[start_index:end_index])
                else:
                    start_index += len('begin: ')
                    if line[start_index:-1] not in log_set:
                        log_set.add(line[start_index:-1])


def read_log(log_file_list):
    log_file = ''
    for read_file in log_file_list:
        if read_file[-4:] == '.log':
            merge_log(read_file)
            log_file = read_file
            # print(read_file)
    output_file = r"D:\jx3_file\file_log\8.31日志\All_Log_Summary.xlsx"
    start_index = log_file.find("MachineLog3\\") + len("MachineLog3\\")
    last_backslash_index = log_file.rfind('\\')
    end_index = log_file.rfind('\\', 0, last_backslash_index)
    sheet_name = log_file[start_index:end_index] + '_' + log_file[end_index + 1:last_backslash_index]
    print(sheet_name)
    df = pd.DataFrame(log_set, columns=['File Name'])
    if os.path.exists(output_file):
        with pd.ExcelWriter(output_file, mode='a', engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    else:
        with pd.ExcelWriter(output_file) as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)


if __name__ == '__main__':
    directory = r'D:\jx3_file\file_log\8.31日志\MachineLog3'
    # 获取该目录下文件列表
    # 当dirs为空的时候，root就是目录，files就是文件
    count = 0
    for root, dirs, files in os.walk(directory):
        file_list = []
        if len(dirs) == 0 and '2023_08_31' in root:
            for file in files:
                # 获取文件的完整路径
                file_path = os.path.join(root, file)
                # 将文件路径添加到列表中
                file_list.append(file_path)
        if file_list:
            count += 1
            read_log(file_list)
        log_set.clear()
    print(count)
    print('done!!!')
