import csv
import os
from datetime import datetime

filename_HD = 'D:/tab_file/成都站点/143050_1080成都站点_HD极致7.5.tab'
write_data_open = [
    ['File', 'Size', 'HD', 'BD', 'HD&BD', 'ONLY_HD', 'ONLY_BD']
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

        if row[4] == '-1':
            continue
        if row[2][:len('KGDetoursMgr::myOpenFile')] == 'KGDetoursMgr::myOpenFile':
            data_open[row[3]] = [row[4], '1', '0']  # filename size hd bd hd&bd onlyhd onlybd
            # write_data.append([row[3], row[4], '1', '0'])

for key in data_open.keys():
    write_data_open.append([key, data_open[key][0], data_open[key][1], data_open[key][2]])

cut_index = filename_HD.rindex('/')
dir_path = f"{filename_HD[:cut_index]}{os.sep}"
current_time = datetime.now()
time_string = current_time.strftime("%Y-%m-%d-%H-%M-%S")
filename = dir_path + 'KGDetoursMgr_myOpenFile' + time_string + '.csv'
with open(filename, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(write_data_open)

print('done!')
