import os

import pandas as pd

log_set = set()
load_time_list = []
load_file_list = []


def merge_log(log_filename):
    target_string = '[KG3DEngineAdapter] render thread load file'
    index = log_filename.rfind('\\')
    log_name = log_filename[index + 1:]
    with open(log_filename, 'r', errors='ignore') as reader:
        for line in reader:
            load_time = ''
            if target_string in line:
                time_index = line.find(',')
                load_time = line[:time_index]
                start_index = line.find('begin: ')
                if start_index == -1:  # end的处理
                    start_index = line.find('end: ') + len('end: ')
                    end_index = line.find(', succeed')
                    if line[start_index:end_index] not in log_set:
                        log_set.add(line[start_index:end_index])
                        load_time_list.append([load_time])
                        load_file_list.append(log_name)
                else:
                    start_index += len('begin: ')  # begin的处理
                    if line[start_index:-1] not in log_set:
                        log_set.add(line[start_index:-1])
                        load_time_list.append([load_time])
                        load_file_list.append(log_name)

    # log_data = []
    # for i in range(len(log_set)):
    #     log_data.append([line, ])
    # df = pd.DataFrame(log_set, columns=['File Name'])
    # with pd.ExcelWriter(output_file) as writer:
    #     df.to_excel(writer, index=False)


if __name__ == '__main__':
    directory = r'D:\jx3_file\file_log\9.7 101日志\2023_09_07'
    file_list = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            file_list.append(file_path)
    for file in file_list:
        merge_log(file)

    output_file = r'D:\jx3_file\file_log\9.7 101日志\2023_09_07\log.xlsx'
    log_data = []
    i = 0
    for load_file in log_set:
        log_data.append([load_file, load_time_list[i], load_file_list[i]])
        i += 1
    print(log_data)
    print(len(log_set))
    print(len(load_time_list))
    print(len(load_file_list))
    df = pd.DataFrame(log_data, columns=['file name', 'load time', 'log name'])
    with pd.ExcelWriter(output_file) as writer:
        df.to_excel(writer, index=False)
