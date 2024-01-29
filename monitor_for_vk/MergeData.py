import pandas as pd

event_focus_list = [
    'CPU Frame',
    'KSO3UI::EndPaint',
    'KG3D_Window::BeginPaint',
    'KG3D_Window::_UpdateAll3DScene',
    'KG3D_Scene::_Update',
    'KG3D_SceneView::BeginRender',
    'KG3D_Window::EndPaint',
    'Frame Wait Timer',
    'KG3D_Window::_Present'
]


class MergeData(object):
    def __init__(self, file_path):
        self.file_path = file_path
        self.event_all = {}
        self.columns = ['EventName']

    def read_file(self):
        excel_data = pd.read_excel(self.file_path, sheet_name=None)
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

    def save(self):
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
                print(temp)
            write_data.append(temp)
        # 创建DataFrame,写入数据
        df_summary_sheet = pd.DataFrame(
            write_data,
            columns=self.columns
        )
        df_summary_focus_sheet = pd.DataFrame(
            write_data_focus,
            columns=self.columns
        )
        workbook_name = 'summary'
        with pd.ExcelWriter(self.file_path, mode='a', engine='openpyxl') as writer:
            if workbook_name in writer.book.sheetnames:
                writer.book.remove(writer.book[workbook_name])
            df_summary_sheet.to_excel(writer, sheet_name=workbook_name, index=False)
        workbook_name = 'summary_focus'
        with pd.ExcelWriter(self.file_path, mode='a', engine='openpyxl') as writer:
            if workbook_name in writer.book.sheetnames:
                writer.book.remove(writer.book[workbook_name])
            df_summary_focus_sheet.to_excel(writer, sheet_name=workbook_name, index=False)

    def run(self):
        self.read_file()
        self.save()


if __name__ == '__main__':
    xx = MergeData(r'D:\jx3_file\file_opt\每日性能监控\稻香村日常\HD_summary.xlsx')
    xx.run()
    xx = MergeData(r'D:\jx3_file\file_opt\每日性能监控\稻香村日常\BD_summary.xlsx')
    xx.run()
    print('done!')
