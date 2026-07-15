from core.processor import load_config

class ValidationEngine:
    def __init__(self, config: dict = None):
        self.config = config or load_config()
        self.rules = self.config['validation_rules']

    def validate(self, row: dict, state: str) -> dict:
        """
        Checks if observed telemetry matches what the state implies.
        Returns a result dict with passed, expected, observed, reason.
        """
        if state not in self.rules:
            return {
                'passed': True,
                'state': state,
                'expected': None,
                'observed': None,
                'reason': 'No validation rule for this state'
            }

        implies = self.rules[state]['implies']
        failures = []

        for rule, threshold in implies.items():
            observed_value, passed = self._check_rule(row, rule, threshold)
            if not passed:
                failures.append({
                    'rule': rule,
                    'threshold': threshold,
                    'observed': observed_value
                })

        if failures:
            return {
                'passed': False,
                'state': state,
                'expected': implies,
                'observed': {f['rule']: f['observed'] for f in failures},
                'reason': f"Validation failed: {failures}"
            }

        return {
            'passed': True,
            'state': state,
            'expected': implies,
            'observed': None,
            'reason': 'All rules passed'
        }

    def _check_rule(self, row: dict, rule: str, threshold: float):
        """
        Parses rule name into field + condition and checks it.
        Rule format: fieldname_min or fieldname_max
        """
        if rule.endswith('_min'):
            field = rule[:-4]
            value = row.get(field)
            return value, (value is not None and value >= threshold)

        if rule.endswith('_max'):
            field = rule[:-4]
            value = row.get(field)
            return value, (value is not None and value <= threshold)

        return None, True