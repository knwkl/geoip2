import pandas as pd
import os

input_file = 'ipinfo_lite.csv'

if not os.path.exists(input_file):
    print(f"错误: 未找到文件 {input_file}")
else:
    df = pd.read_csv(input_file)
    print("列名如下：")
    print(df.columns.tolist())
    print("前3行数据：")
    print(df.head(3))
