# core/processor.py
import pandas as pd
import yaml
import os

RAW_PATH = os.path.join('data', 'raw', 'discharge_data.csv')
PROCESSED_PATH = os.path.join('data', 'processed', 'processed_data.csv')
CONFIG_PATH = os.path.join('config', 'rules.yaml')

def load_config(config_path: str = CONFIG_PATH) -> dict:
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def prepare_data(raw_path: str = RAW_PATH) -> pd.DataFrame:
    df = pd.read_csv(raw_path)
    cols = ['cycle', 'time', 'voltage_measured',
            'current_measured', 'temperature_measured', 'capacity']
    df = df[cols]
    df = df.sort_values(['cycle', 'time']).reset_index(drop=True)
    df['current_abs'] = df['current_measured'].abs()
    df['capacity_pct'] = (df['capacity'] / df['capacity'].max()) * 100
    return df

def save_processed(df: pd.DataFrame,
                   path: str = PROCESSED_PATH):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)
    print(f"Saved processed data to {path}")

def load_data(processed_path: str = PROCESSED_PATH) -> pd.DataFrame:
    return pd.read_csv(processed_path)

def get_cycle_ids(df: pd.DataFrame) -> list:
    return sorted(df['cycle'].unique().tolist())

def get_cycle(df: pd.DataFrame, cycle_id: int) -> pd.DataFrame:
    return df[df['cycle'] == cycle_id].reset_index(drop=True)