from core.processor import load_config

class StateClassifier:
    def __init__(self, config: dict = None):
        self.config = config or load_config()
        self.states = self.config['states']

    def classify(self, row: dict) -> str:
        voltage = row['voltage_measured']
        current_abs = row['current_abs']
        temperature = row['temperature_measured']
        capacity = row['capacity']

        # Order matters — most severe first
        if capacity <= self.states['EOL']['capacity_max']:
            return 'EOL'

        if capacity <= self.states['DEGRADED']['capacity_max']:
            return 'DEGRADED'

        if temperature >= self.states['THERMAL_WARNING']['temperature_min']:
            return 'THERMAL_WARNING'

        if voltage <= self.states['LOW_BATTERY']['voltage_max']:
            return 'LOW_BATTERY'

        if current_abs >= self.states['NOMINAL']['current_max']:
            return 'HIGH_LOAD'

        return 'NOMINAL'