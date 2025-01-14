import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.graphics.tsaplots import plot_acf
from statsmodels.graphics.tsaplots import plot_pacf


def load_and_prepare_data(file_path):
    # Read Excel file
    df = pd.read_excel(file_path)
    
    # Create dictionaries to store data for each contract
    data_dict = {
        'train': ['TL2312', 'TL2403'],
        'val': ['TL2406'],
        'test': ['TL2409']
    }
    
    # Initialize scaler
    scaler = MinMaxScaler()
    
    # Prepare data for each split
    datasets = {}
    for split, contracts in data_dict.items():
        split_data = df[df['contract'].isin(contracts)].copy()
        
        # Sort by datetime
        split_data = split_data.sort_values('datetime')
        
        # Scale the features
        features = ['open', 'high', 'low', 'close', 'volume']
        split_data[features] = scaler.fit_transform(split_data[features])
        
        # Create sequences using past data to predict future
        lookback_window = 20  # Number of past timeframes to use
        forecast_horizon = 1  # Number of timeframes ahead to predict
        X, y = [], []

        for i in range(len(split_data) - lookback_window - forecast_horizon + 1):
            # Past data for input
            past_sequence = split_data[features].values[i:i+lookback_window]
            X.append(past_sequence)
            
            # Future price for target
            current_open = split_data['open'].values[i+lookback_window-1]  # Last timeframe's open
            future_close = split_data['close'].values[i+lookback_window+forecast_horizon-1]  # Next timeframe's close
            
            # Calculate future direction
            price_change = future_close - current_open
            y.append(1 if price_change > 0 else -1)  # 1 for up, -1 for down/flat
                
        datasets[split] = {
            'X': np.array(X),
            'y': np.array(y)
        }
    
    return datasets

def main():
    file_path = '/Users/daiwangtao/Documents/Data/TL5Minutes.xlsx'
    datasets = load_and_prepare_data(file_path)
    
    # Print shapes of resulting datasets
    for split, data in datasets.items():
        print(f"{split} data shapes:")
        print(f"X: {data['X'].shape}")
        print(f"y: {data['y'].shape}")
        
        fig, axs = plt.subplots(1, 2)
        plot_acf(data['y'], lags=50,ax=axs[0])
        axs[0].set_title('Autocorrelation Function (ACF)')
        plot_pacf(data['y'], lags=50, ax=axs[1])
        axs[1].set_title('Partial Autocorrelation Function (PACF)')
        plt.tight_layout()
        plt.show()
        
    return datasets

if __name__ == "__main__":
    datasets = main()