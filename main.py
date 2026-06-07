# main.py
from core.processor import load_data, get_cycle_ids
from core.replay import ReplayEngine
from core.classifier import StateClassifier
from core.validator import ValidationEngine
from core.anomaly import AnomalyDetector
from services.timeline import TimelineService
from services.report import ReportGenerator

def run_cycle(df, cycle_id):
    engine = ReplayEngine(df, speed=10000.0)
    classifier = StateClassifier()
    validator = ValidationEngine()
    detector = AnomalyDetector()
    timeline = TimelineService()
    report = ReportGenerator()

    for row in engine.stream(cycle_id=cycle_id):
        state = classifier.classify(row)
        validation = validator.validate(row, state)
        anomalies = detector.detect(row)
        timeline.update(row, state, anomalies, validation)
        report.update(row, state, anomalies, validation)

    report.save_json(f'reports/cycle_{int(cycle_id)}_report.json')
    return report.generate()

if __name__ == '__main__':
    df = load_data()
    for cycle_id in get_cycle_ids(df):
        print(f"Processing cycle {int(cycle_id)}...")
        summary = run_cycle(df, cycle_id)
        print(f"  Anomalies: {summary['total_anomalies']} "
              f"Failures: {summary['validation_failures']}")