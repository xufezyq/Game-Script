import pandas as pd

# 读取两个 Excel 文件
file1 = '烂柯山_5005_屏蔽前.xlsx'  # 改
file2 = '烂柯山_6758_屏蔽后.xlsx'  # 改
df1 = pd.read_excel(file1)
df2 = pd.read_excel(file2)

# 根据某一列的数值查找相同和不同的值
common_values = pd.merge(df1, df2, on='MeshPath')  # 改
different_values_in_file1 = df1[~df1['MeshPath'].isin(df2['MeshPath'])]  # 改
different_values_in_file2 = df2[~df2['MeshPath'].isin(df1['MeshPath'])]  # 改

# 输出到不同的工作簿
with pd.ExcelWriter('output.xlsx') as writer:
    common_values.to_excel(writer, sheet_name='Common_Values', index=False)
    different_values_in_file1.to_excel(writer, sheet_name='Different_Values_in_File1', index=False)
    different_values_in_file2.to_excel(writer, sheet_name='Different_Values_in_File2', index=False)
