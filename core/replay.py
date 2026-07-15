import time
import pandas as pd
from core.processor import load_data

class ReplayEngine:
    def __init__(self, df: pd.DataFrame, speed: float = 1.0):
        self.df = df.sort_values(['cycle', 'time']).reset_index(drop=True)
        self.speed = speed
        self.is_running = False

    def set_speed(self, speed: float):
        self.speed = speed

    def stream(self, cycle_id: int = None):
        """
        Generator — yields one row at a time with simulated delay.
        If cycle_id given, replays only that cycle.
        Otherwise replays entire dataset.
        """
        self.is_running = True
        prev_time = None
        prev_cycle = None

        data = self.df if cycle_id is None else \
               self.df[self.df['cycle'] == cycle_id]

        for _, row in data.iterrows():
            if not self.is_running:
                break

            # Reset timer on new cycle
            if row['cycle'] != prev_cycle:
                prev_time = None
                prev_cycle = row['cycle']

            if prev_time is not None:
                delay = (row['time'] - prev_time) / self.speed
                time.sleep(min(delay, 1.0))  # cap at 1s

            prev_time = row['time']
            yield row.to_dict()

    def stop(self):
        self.is_running = False