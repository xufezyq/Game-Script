import pandas as pd


def compare_tables(file1, file2, column):
    # 读取Excel文件
    df1 = pd.read_excel(file1)
    df2 = pd.read_excel(file2)

    # 合并两个表格根据指定列进行匹配
    merged_df = pd.merge(df1, df2, on=column, how='outer', suffixes=('_file1', '_file2'), indicator=True)
    merged_df_same = pd.merge(df1, df2, on=column, suffixes=('_file1', '_file2'))

    # 获取只存在于一个表格中的行
    unique_rows = merged_df.loc[(merged_df['_merge'] == 'left_only') | (merged_df['_merge'] == 'right_only')]
    same_data = merged_df_same.dropna(subset=[column])  # 删除缺省值
    same_data.drop_duplicates(subset=column, inplace=True)  # 删除重复行

    # 写出数据到新的Excel文件
    with pd.ExcelWriter(
            r'G:\jx3_file\file_opt\XGame\diff_actor.xlsx') as writer:
        unique_rows.to_excel(writer, sheet_name='Unique Rows', index=False)
        same_data.to_excel(writer, sheet_name='Same Data', index=False)


# 使用示例
compare_tables(r'G:\jx3_file\file_opt\XGame\11.2楚州定点.xlsx',
               r'G:\jx3_file\file_opt\XGame\11.2楚州定点看天空.xlsx', 'EventName')

print("done!!!")
