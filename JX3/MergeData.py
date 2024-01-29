import pandas as pd


class MergeData(object):
    def __init__(self, file_path):
        self.file_path = file_path
        self.event_all = {}
        self.columns = ['EventName']

    def read_file(self):
        excel_data = pd.read_excel(self.file_path, sheet_name=None)
        # 每个工作簿，每行数据存入
        for key in excel_data.keys():
            if key == 'summary':
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
        # 把数据都写入write_data
        for key in self.event_all.keys():
            events = self.event_all[key]
            temp = [key]
            for event in events:
                temp.append(event)
            write_data.append(temp)
        # 创建DataFrame,写入数据
        df_summary_sheet = pd.DataFrame(
            write_data,
            columns=self.columns
        )
        workbook_name = 'summary'
        with pd.ExcelWriter(self.file_path, mode='a', engine='openpyxl') as writer:
            if workbook_name in writer.book.sheetnames:
                writer.book.remove(writer.book[workbook_name])
            df_summary_sheet.to_excel(writer, sheet_name=workbook_name, index=False)

    def run(self):
        self.read_file()
        self.save()


if __name__ == '__main__':
    xx = MergeData(r'D:\jx3_file\file_opt\每日性能监控\稻香村日常\HD_summary.xlsx')
    xx.run()
    xx = MergeData(r'D:\jx3_file\file_opt\每日性能监控\稻香村日常\BD_summary.xlsx')
    xx.run()
    print('done!')
