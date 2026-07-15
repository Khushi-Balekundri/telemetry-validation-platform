from core.processor import load_config

class AnomalyDetector:
    def __init__(self, config: dict = None):
        self.config = config or load_config()
        self.thresholds = self.config['anomaly_thresholds']
        self._prev_row = None

    def detect(self, row: dict) -> dict:
        """
        Deterministic anomaly detection.
        Returns anomaly dict or None if no anomaly.
        """
        anomalies = []

        if self._prev_row is not None:
            # Voltage drop
            v_prev = self._prev_row['voltage_measured']
            v_curr = row['voltage_measured']
            v_drop_pct = ((v_prev - v_curr) / v_prev) * 100
            if v_drop_pct >= self.thresholds['voltage_drop_pct']:
                anomalies.append({
                    'type': 'VOLTAGE_DROP',
                    'reason': f"Voltage dropped {v_drop_pct:.1f}% "
                              f"({v_prev:.3f}V → {v_curr:.3f}V)",
                    'severity': 'HIGH' if v_drop_pct > 20 else 'MEDIUM'
                })

            # Temperature spike
            t_prev = self._prev_row['temperature_measured']
            t_curr = row['temperature_measured']
            t_delta = t_curr - t_prev
            if t_delta >= self.thresholds['temperature_spike']:
                anomalies.append({
                    'type': 'TEMPERATURE_SPIKE',
                    'reason': f"Temperature jumped {t_delta:.1f}°C "
                              f"({t_prev:.1f} → {t_curr:.1f}°C)",
                    'severity': 'HIGH' if t_delta > 8 else 'MEDIUM'
                })

            # Current spike
            c_prev = self._prev_row['current_abs']
            c_curr = row['current_abs']
            c_delta = abs(c_curr - c_prev)
            if c_delta >= self.thresholds['current_spike']:
                anomalies.append({
                    'type': 'CURRENT_SPIKE',
                    'reason': f"Current changed {c_delta:.3f}A "
                              f"({c_prev:.3f} → {c_curr:.3f}A)",
                    'severity': 'MEDIUM'
                })

        self._prev_row = row

        return anomalies if anomalies else None

    def reset(self):
        """Call this between cycles."""
        self._prev_row = None