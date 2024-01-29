import json
import os
from test_robot import request_post
from datetime import datetime
import pandas as pd

event_focus_list = [
    'CPU Frame',
    'Frame Wait Timer',
    'KG3D_Window::BeginPaint',
    'KG3D_Window::EndPaint',
    'KG3D_Window::_Present'
]


class MergeData(object):
    def __init__(self):
        self.file_path = []
        self.event_all = {}
        self.columns = ['EventName']
        self.post_data = {}
        self.sub_data = {}
        self.data = {}
        self.url = 'https://xz.wps.cn/api/v1/webhook/send?key=700f5b7d6ec17818105a95378e4c4caf'

    def get_file(self):
        current_directory = os.getcwd()
        for file in os.listdir(current_directory):
            if file.endswith('.xlsx'):
                self.file_path.append(file)
        print(self.file_path)

    def process_file(self):
        current_time = datetime.now().date()

        self.data = {
            "msgtype": "markdown",
            "markdown": {
                "text": f"# 《剑网3重制版》{current_time}稻香村监控数据：\n\n"
            }
        }
        for file in self.file_path:
            self.read_file(file)
            self.save(file)
        self.data['markdown']['text'] += "<at user_id=\"1518675131\"></at>"
        json_data = json.dumps(self.data)
        response = request_post(self.url, json_data)
        print(response.status_code)
        print(response.json())

    def read_file(self, file):
        excel_data = pd.read_excel(file, sheet_name=None)
        # 每个工作簿，每行数据存入
        for key in excel_data.keys():
            if key == 'summary' or key == 'summary_focus':
                continue
            self.columns.append(key)
            df_sheet = excel_data[key]
            for _, row in df_sheet.iterrows():
                event_name = row['EventName']
                event_elapse = row['Avg Event Elapse(ms)']
                if event_name not in self.event_all.keys():
                    self.event_all[event_name] = [event_elapse]
                else:
                    self.event_all[event_name].append(event_elapse)

    def save(self, file):
        write_data = []
        write_data_focus = []

        # 把数据都写入write_data
        for key in self.event_all.keys():
            events = self.event_all[key]
            temp = [key]
            for event in events:
                temp.append(event)
            # 提取特殊event
            if key in event_focus_list:
                write_data_focus.append(temp)
            write_data.append(temp)

        # 创建DataFrame,写入数据
        df_summary_sheet = pd.DataFrame(
            write_data,
            columns=self.columns
        )
        write_data_focus = sorted(write_data_focus, key=lambda x: event_focus_list.index(x[0]))
        for data in write_data_focus:
            self.post_data[data[0]] = data[len(data) - 1]
            self.sub_data[data[0]] = round(data[len(data) - 1] - data[len(data) - 2], 3)
        df_summary_focus_sheet = pd.DataFrame(
            write_data_focus,
            columns=self.columns
        )
        workbook_name = 'summary'
        with pd.ExcelWriter(file, mode='a', engine='openpyxl') as writer:
            if workbook_name in writer.book.sheetnames:
                writer.book.remove(writer.book[workbook_name])
            df_summary_sheet.to_excel(writer, sheet_name=workbook_name, index=False)
        workbook_name = 'summary_focus'
        with pd.ExcelWriter(file, mode='a', engine='openpyxl') as writer:
            if workbook_name in writer.book.sheetnames:
                writer.book.remove(writer.book[workbook_name])
            df_summary_focus_sheet.to_excel(writer, sheet_name=workbook_name, index=False)

        if 'HD' in file:
            self.data['markdown']['text'] += f"## 画质：HD极致\n\n"
        else:
            self.data['markdown']['text'] += f"## 画质：BD电影\n\n"
        self.data['markdown']['text'] += (f"- CPU Frame: **<font color='green'>{self.post_data['CPU Frame']}</font>**"
                                          f"<font color='red'>({self.sub_data['CPU Frame']})</font>\n"
                                          f"- Frame Wait Timer: **<font color='green'>{self.post_data['Frame Wait Timer']}</font>**"
                                          f"<font color='red'>({self.sub_data['Frame Wait Timer']})</font>\n"
                                          f"- KG3D_Window::BeginPaint: **<font color='green'>{self.post_data['KG3D_Window::BeginPaint']}</font>**"
                                          f"<font color='red'>({self.sub_data['KG3D_Window::BeginPaint']})</font>\n"
                                          f"- KG3D_Window::EndPaint: **<font color='green'>{self.post_data['KG3D_Window::EndPaint']}</font>**"
                                          f"<font color='red'>({self.sub_data['KG3D_Window::EndPaint']})</font>\n"
                                          f"- KG3D_Window::_Present: **<font color='green'>{self.post_data['KG3D_Window::_Present']}</font>**"
                                          f"<font color='red'>({self.sub_data['KG3D_Window::_Present']})</font>\n\n")

    def run(self):
        self.get_file()
        self.process_file()

# if __name__ == '__main__':
#     xx = MergeData(r'D:\jx3_file\file_opt\每日性能监控\稻香村日常\HD_summary.xlsx')
#     xx.run()
#     xx = MergeData(r'D:\jx3_file\file_opt\每日性能监控\稻香村日常\BD_summary.xlsx')
#     xx.run()
#     print('done!')
