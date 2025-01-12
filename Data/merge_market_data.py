import os
import pandas as pd

input_directory = '/Users/daiwangtao/Documents/Data/TL5minData'
output_file = '/Users/daiwangtao/Documents/Data/TL5Minutes.xlsx'

def process_dataframe(df):
    return df.rename(columns={
        '证券代码': 'contract',
        '交易时间': 'datetime',
        '开盘价': 'open',
        '最高价': 'high',
        '最低价': 'low',
        '收盘价': 'close',
        '成交量': 'volume'
    })[['contract', 'datetime', 'open', 'high', 'low', 'close', 'volume']].assign(
        datetime=lambda x: pd.to_datetime(x['datetime'])
    ).dropna(how='any')  # Remove rows with any missing values

def main():
    dataframes = []
    for file in [f for f in os.listdir(input_directory) if f.endswith('.xlsx')]:
        try:
            df = process_dataframe(pd.read_excel(os.path.join(input_directory, file)))
            if not df.empty:  # Only append if dataframe is not empty after cleaning
                dataframes.append(df)
        except Exception:
            continue
    
    if dataframes:
        merged_df = pd.concat(dataframes, ignore_index=True)
        merged_df = merged_df[merged_df['volume'] > 0]  # Remove rows with zero volume
        merged_df.to_excel(output_file, index=False)

if __name__ == "__main__":
    main()
