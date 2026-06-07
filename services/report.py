# services/report.py
import json
import csv
import os
from collections import Counter

class ReportGenerator:
    def __init__(self):
        self.reset()

    def reset(self):
        self.state_durations = {}
        self.anomaly_counts = Counter()
        self.validation_failures = 0
        self.total_rows = 0
        self.cycles_processed = set()
        self._prev_row = None
        self._prev_state = None

    def update(self, row: dict, state: str,
               anomalies: list, validation: dict):
        self.total_rows += 1
        self.cycles_processed.add(row['cycle'])

        # Track state durations
        if self._prev_state is not None and self._prev_row is not None:
            dt = row['time'] - self._prev_row['time']
            if dt > 0:
                self.state_durations[self._prev_state] = \
                    self.state_durations.get(self._prev_state, 0) + dt

        # Track anomalies
        if anomalies:
            for a in anomalies:
                self.anomaly_counts[a['type']] += 1

        # Track validation failures
        if not validation['passed']:
            self.validation_failures += 1

        self._prev_row = row
        self._prev_state = state

    def generate(self) -> dict:
        total_duration = sum(self.state_durations.values())
        return {
            'cycles_processed': sorted(list(self.cycles_processed)),
            'total_cycles': len(self.cycles_processed),
            'total_rows': self.total_rows,
            'total_duration_seconds': round(total_duration, 1),
            'state_durations_seconds': {
                k: round(v, 1) 
                for k, v in self.state_durations.items()
            },
            'state_duration_pct': {
                k: round((v / total_duration) * 100, 1)
                for k, v in self.state_durations.items()
            },
            'anomaly_counts': dict(self.anomaly_counts),
            'total_anomalies': sum(self.anomaly_counts.values()),
            'validation_failures': self.validation_failures
        }

    def save_json(self, path: str = 'reports/report.json'):
        os.makedirs('reports', exist_ok=True)
        report = self.generate()
        with open(path, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"Report saved to {path}")
        return report

    def save_csv(self, path: str = 'reports/report.csv'):
        os.makedirs('reports', exist_ok=True)
        report = self.generate()
        with open(path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['metric', 'value'])
            writer.writerow(['total_cycles', report['total_cycles']])
            writer.writerow(['total_rows', report['total_rows']])
            writer.writerow(['total_duration_seconds', 
                           report['total_duration_seconds']])
            writer.writerow(['total_anomalies', report['total_anomalies']])
            writer.writerow(['validation_failures', 
                           report['validation_failures']])
            for state, duration in report['state_durations_seconds'].items():
                writer.writerow([f'duration_{state}', duration])
            for atype, count in report['anomaly_counts'].items():
                writer.writerow([f'anomaly_{atype}', count])
        print(f"Report saved to {path}")
        return report