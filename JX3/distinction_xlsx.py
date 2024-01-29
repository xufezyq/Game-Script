import pandas as pd

# 读取两个Excel文件
df1 = pd.read_excel('屏蔽前.xlsx')
df2 = pd.read_excel('屏蔽后.xlsx')

# 使用merge函数将两个表格合并，设置indicator参数为True以标识每行的来源
merged_df = df1.merge(df2, on=df1.columns[0], how='outer', indicator=True)

# 根据来源标识创建新列
merged_df['source'] = merged_df['_merge'].map({'left_only': 'table1', 'right_only': 'table2', 'both': 'both'})

# 将结果保存到新的Excel文件
merged_df.to_excel('differences_with_source.xlsx', index=False)
