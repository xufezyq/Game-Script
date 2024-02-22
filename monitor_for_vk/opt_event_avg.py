import sys
import numpy as np
import pandas as pd

from robot import *
from util import *
from send_to_mongodb import send_to_mongodb
from opt_file_parser import OptFileParser
from scipy.stats import zscore
from collections import defaultdict


class OptEventAvg(OptFileParser):
    def __init__(self, input_path):
        super().__init__(input_path)
        self.frame = []
        self.stat = {}
        self.target_events = []
        self.config_exists = False
        self.config_path = "config.txt"
        self.frame_elapse = 0

    def read_config(self):
        try:
            with open(self.config_path, 'r') as file:
                # 如果文件存在，读取文件内存
                self.config_exists = True
                for line in file:
                    line = line.strip()
                    self.target_events.append(line)
        except FileNotFoundError:
            # 文件不存在
            self.config_exists = False

    def get_frames(self):
        """"存储每帧中的所有事件"""
        print(f"Frame Count: {self.cpu_frame_count}")
        for frame_index in range(self.cpu_frame_count):
            temp = {
                'frame_index': frame_index,
                'frame_events': []
            }
            for event in self.frame_events[frame_index]:
                event_elapse = get_round_time(event[1] - event[0])
                event_index = event[2]
                temp['frame_events'].append([event_index, event[0], event[1]])
            self.frame.append(temp)
            # print(temp)

    def merge_elapse(self):
        """合并同一帧中相同事件的耗时"""
        for frame in self.frame:
            events_intervals = defaultdict(list)
            merged_frame = []

            # 按事件id，把同属所有区间进行集合
            for event_index, event_start, event_end in frame['frame_events']:
                events_intervals[event_index].append((event_start, event_end))

            # 按照区间起始时间进行排序并计算总时长
            for event_index, intervals in events_intervals.items():
                sorted_intervals = sorted(intervals, key=lambda x: x[0])
                total_elapse = 0
                start_interval, end_interval = sorted_intervals[0]
                for current_start, current_end in sorted_intervals[1:]:
                    if current_start > end_interval:
                        # 区间断开，将前一个连接区间进行累加
                        total_elapse += end_interval - start_interval
                        start_interval = current_start
                    end_interval = max(end_interval, current_end)
                # 把最后一个区间进行累加
                total_elapse += end_interval - start_interval
                merged_frame.append([event_index, total_elapse])

            # update
            frame['frame_events'] = merged_frame
            # print(frame)

    def stat_data(self):
        """计算平均耗时"""
        frame_events_name = {}
        frame_events_elapse = defaultdict(list)

        # 每个函数名对应一个列表
        for i in range(len(self.event_descs)):
            frame_events_name[i] = self.event_descs[i].split('(')[0]

        # 提取每帧每事件的耗时
        for frame in self.frame:
            for event_index, total_elapse in frame['frame_events']:  # 事件下标
                frame_events_elapse[event_index].append(total_elapse)
                # if total_elapse > 10000:  # 排除0.01ms以下的
                #     frame_events_elapse[event_index].append(total_elapse)  # event[0]:event_key  event[1]:total_duration

        # 计算每事件的平均耗时
        for event_index, event_elapse in frame_events_elapse.items():
            data_array = np.array(event_elapse, dtype=np.int64)
            if not len(data_array):
                # 如果该事件未发生
                pass
            else:
                # 事件平均耗时(总耗时/帧数)
                avg_event_elapse = np.sum(data_array) / self.cpu_frame_count
                avg_event_elapse = round(avg_event_elapse / 1000000, 3)
                # 最大最小方差标准差
                max_event_elapse = round(np.max(data_array) / 1000000, 3)
                var_event_elapse = round(np.var(data_array) / 1000000 / 1000000, 3)

                # z_scores
                z_scores = zscore(data_array)
                threshold = 7  # 可根据情况适当修改
                outliers = np.where(np.abs(z_scores) > threshold)

                # outlier 存在离群值，或方差远大于平均数
                is_outlier = (len(outliers[0]) > 0 or var_event_elapse > (avg_event_elapse * 100))

                self.stat[event_index] = (frame_events_name[event_index], avg_event_elapse)
        # print(self.stat)

    def write_data(self):
        """把config标记的函数的提取出来"""
        extracted_data = []
        if self.config_exists:
            # target中包含event进行提取
            for event_index, stat in self.stat.items():  # event_name   avg_event_elapse
                # if stat[1] > 0 and stat[0] in self.target_events:
                #     extracted_data.append(stat)
                function_name = stat[0]
                for target_name in self.target_events:
                    if target_name in function_name:
                        extracted_data.append((target_name, stat[1]))

            # 没有的event默认0
            for event in self.target_events:
                if event not in extracted_data:
                    extracted_data.append((event, 0))

            # 排序extracted_data 根据target.txt的顺序进行排序
            extracted_data.sort(key=lambda x: self.target_events.index(x[0]))
        else:
            for event_index, stat in self.stat.items():
                if stat[1] > 0:
                    extracted_data.append(stat)
        return extracted_data

    def save(self):
        output_file = self.input_path[:-4] + '.xlsx'
        data_map = []
        data_writer_tmp = []

        # 写入数据
        data_writer = self.write_data()

        # 将data_writer中重复的元素，删除
        for data in data_writer:
            if data[0] not in data_map:
                data_writer_tmp.append(data)
                data_map.append(data[0])
        data_writer = data_writer_tmp

        # 保存并写入数据
        columns = ['Event Name', 'Avg Event Elapse(ms)']
        if os.path.exists(output_file):
            os.remove(output_file)
        with pd.ExcelWriter(output_file, mode='w', engine='openpyxl') as writer:
            pd.DataFrame(data_writer, columns=columns).to_excel(writer, index=False)

        # 发送数据
        # send_data_robot(self.stat, self.input_dir)
        send_to_mongodb(data_writer, self.input_dir)

    def run(self):
        self.read_opt_content()
        self.parse()
        self.read_config()
        self.get_frames()
        self.merge_elapse()
        self.stat_data()
        self.save()


def get_file_path():
    mylist = []
    for root, dirs, files in os.walk(directory):
        for f in files:
            # 获取文件的完整路径
            file_path = os.path.join(root, f)
            # 将文件路径添加到列表中
            mylist.append(file_path)
    return mylist


if __name__ == '__main__':
    if len(sys.argv) > 1:
        directory = sys.argv[1]

        # 获取该目录下文件列表
        file_list = get_file_path()

        # 处理所有.opt文件
        for file in file_list:
            if file[-4:] == '.opt':
                print(file)
                xx = OptEventAvg(file)
                xx.run()

        # 创建json数据并发送
        # create_json_data()
        print('done!')
    else:
        print("arguments wrong number!")
