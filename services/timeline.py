# services/timeline.py

class TimelineService:
    def __init__(self):
        self.events = []
        self._prev_state = None

    def update(self, row: dict, state: str, 
               anomalies: list, validation: dict):
        """
        Records an event only when something changes:
        - state transition
        - anomaly detected
        - validation failure
        """
        event = None

        # State transition
        if state != self._prev_state:
            event = {
                'time': row['time'],
                'cycle': row['cycle'],
                'type': 'STATE_CHANGE',
                'description': f"{self._prev_state} → {state}",
                'voltage': round(row['voltage_measured'], 3),
                'temperature': round(row['temperature_measured'], 1),
                'capacity_pct': round(row['capacity_pct'], 1)
            }
            self._prev_state = state
            self.events.append(event)

        # Anomaly
        if anomalies:
            for a in anomalies:
                self.events.append({
                    'time': row['time'],
                    'cycle': row['cycle'],
                    'type': f"ANOMALY_{a['type']}",
                    'description': a['reason'],
                    'severity': a['severity'],
                    'voltage': round(row['voltage_measured'], 3),
                    'temperature': round(row['temperature_measured'], 1),
                    'capacity_pct': round(row['capacity_pct'], 1)
                })

        # Validation failure
        if not validation['passed']:
            self.events.append({
                'time': row['time'],
                'cycle': row['cycle'],
                'type': 'VALIDATION_FAILURE',
                'description': validation['reason'],
                'voltage': round(row['voltage_measured'], 3),
                'temperature': round(row['temperature_measured'], 1),
                'capacity_pct': round(row['capacity_pct'], 1)
            })

    def get_events(self) -> list:
        return self.events

    def reset(self):
        self.events = []
        self._prev_state = None