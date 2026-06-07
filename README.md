# Telemetry Operations & Validation Platform

A telemetry replay, monitoring, and validation platform designed to demonstrate systems engineering, operational monitoring, and telemetry analysis concepts.

The platform is domain-agnostic and can be adapted to telemetry streams from aerospace systems, industrial equipment, robotics platforms, energy systems, and IoT devices.

---

## Overview

Most monitoring systems focus on visualizing telemetry.

This platform goes a step further by validating telemetry against expected operational behavior.

Given a telemetry stream, the platform:

* Processes and standardizes raw telemetry data
* Replays historical telemetry as a configurable real-time stream
* Classifies operational states using configurable rules
* Validates whether observed measurements are consistent with expected state behavior
* Detects explainable anomalies using deterministic logic
* Generates an operational timeline of state transitions and events
* Produces mission summary reports and operational statistics

---

## Architecture

```text
Raw Telemetry
      │
      ▼
Telemetry Processor
      │
      ├── Schema Validation
      ├── Timestamp Normalization
      ├── Unit Conversion
      ├── Interpolation
      └── Feature Engineering
      │
      ▼
Replay Engine
      │
      ├──────────────────────┐
      ▼                      ▼
State Classifier      Validation Engine
      │                      │
      └──────────┬───────────┘
                 ▼
          Anomaly Detector
                 │
                 ▼
          Timeline Service
                 │
                 ▼
          Report Generator
                 │
                 ▼
         Streamlit Dashboard
```

---

## Dataset

The platform uses the NASA Battery Dataset containing lithium-ion battery discharge cycles collected for prognostics and health management research.

Dataset characteristics:

* Multiple battery cells operated through repeated charge-discharge cycles
* Voltage measurements
* Current measurements
* Temperature measurements
* Capacity degradation over lifecycle

The dataset provides realistic telemetry suitable for demonstrating operational monitoring, state classification, anomaly detection, and lifecycle analysis.

---
## Data Setup

Download the NASA Battery Dataset from the official source:

- **Kaggle mirror** (easier): [NASA Battery Dataset on Kaggle](https://www.kaggle.com/datasets/patrickfleith/nasa-battery-dataset)
- **Official NASA source**: [NASA PCoE Datasets](https://www.nasa.gov/content/prognostics-center-of-excellence-data-set-repository)

After downloading, extract the discharge CSV and place it at:
---

## Data Processing Pipeline

Before replay, telemetry is processed through a preparation pipeline:

### Schema Validation

Validates required telemetry channels and data quality requirements.

### Timestamp Normalization

Converts timestamps into a standardized internal format.

### Unit Standardization

Converts measurements into consistent engineering units.

Examples:

* Current: mA → A
* Temperature: °F → °C
* Voltage: standardized to V

### Interpolation

Handles missing samples and irregular sampling intervals through resampling and interpolation.

### Feature Engineering

Derives additional operational metrics such as:

* Power consumption
* Temperature rate of change
* Voltage drop rate

---

## Operational States

Operational states are defined through configurable rules stored in `rules.yaml`.

| State           | Example Condition              |
| --------------- | ------------------------------ |
| NOMINAL         | Normal operating conditions    |
| HIGH_LOAD       | Elevated current draw          |
| LOW_BATTERY     | Low voltage condition          |
| THERMAL_WARNING | Elevated temperature           |
| DEGRADED        | Reduced battery capacity       |
| EOL             | End-of-life capacity threshold |

State definitions can be modified without changing application code.

---

## Validation Engine

The validation engine verifies that observed telemetry is consistent with the classified operational state.

Example:

```text
State: THERMAL_WARNING

Expected:
Temperature ≥ 35°C

Observed:
Temperature = 36.2°C

Result:
PASS
```

```text
State: THERMAL_WARNING

Expected:
Temperature ≥ 35°C

Observed:
Temperature = 28.1°C

Result:
FAIL
```

This capability transforms the platform from a monitoring tool into a telemetry validation system.

---

## Explainable Anomaly Detection

Anomaly detection is deterministic and rule-based.

Each detected anomaly includes an explicit explanation.

Examples:

| Anomaly           | Description                                        |
| ----------------- | -------------------------------------------------- |
| VOLTAGE_DROP      | Rapid decrease in voltage                          |
| TEMPERATURE_SPIKE | Rapid increase in temperature                      |
| CURRENT_SPIKE     | Sudden change in current draw                      |
| SENSOR_FREEZE     | Sensor value remains unchanged for extended period |

Example output:

```text
CURRENT_SPIKE

Current increased by 2.01 A
between consecutive samples.
```

---

## Event Timeline

The platform generates a chronological operational timeline.

Example:

```text
10:00  REPLAY_STARTED

10:02  HIGH_LOAD

10:05  TEMPERATURE_SPIKE

10:06  THERMAL_WARNING

10:08  VALIDATION_FAILURE

10:10  LOW_BATTERY

10:12  DEGRADED
```

Events are visualized directly on telemetry charts using annotations and timeline markers.

---

## Dashboard

The Streamlit dashboard provides:

### Live Telemetry

* Voltage
* Current
* Temperature
* Derived Power

### Operational Status

* Current State
* Validation Status
* Active Anomalies

### Annotated Timeline Visualization

Interactive charts displaying:

* Telemetry trends
* State transitions
* Validation failures
* Anomaly events

### Mission Summary

* Total anomalies
* Validation failures
* State transitions
* Replay statistics

---

## Project Structure

```text
telemetry-platform/

├── data/
│   └── raw/
│
├── processed/
│
├── config/
│   └── rules.yaml
│
├── preprocessing/
│   ├── schema_validator.py
│   ├── timestamp_normalizer.py
│   ├── unit_converter.py
│   ├── interpolator.py
│   ├── feature_engineering.py
│   └── telemetry_processor.py
│
├── replay/
│   └── replay_engine.py
│
├── services/
│   ├── state_classifier.py
│   ├── validation_engine.py
│   ├── anomaly_detector.py
│   ├── timeline_service.py
│   └── report_generator.py
│
├── dashboard/
│   ├── app.py
│   └── charts.py
│
├── outputs/
│   ├── reports/
│   └── timelines/
│
└── README.md
```

---

## Design Principles

### Configuration-Driven Rules

State definitions, thresholds, and validation logic are externalized to configuration files.

### Explainability

Every anomaly and validation result includes a human-readable explanation.

### Separation of Concerns

Replay, classification, validation, anomaly detection, reporting, and visualization are implemented as independent modules.

### Extensibility

The platform can be adapted to different telemetry domains by modifying telemetry schemas and rule definitions.

---

## Example Applications

The underlying architecture is applicable to:

* Telemetry and operations monitoring
* Industrial equipment monitoring
* Energy and battery systems
* Robotics and autonomous systems
* IoT telemetry analysis
* Operational event analysis
* Infrastructure and sensor monitoring

---

## Technology Stack

* Python
* Pandas
* Streamlit
* Plotly
* PyYAML

---
## How To Run

1. Install dependencies
```bash
pip install -r requirements.txt
```

2. Prepare data
```bash
python -c "from core.processor import prepare_data, save_processed; save_processed(prepare_data())"
```

3. Launch dashboard
```bash
streamlit run dashboard/app.py
```

4. Select a cycle, set replay speed, click ▶ Run Replay
---

## Future Enhancements

* Failure injection framework
* FastAPI service layer
* MQTT/WebSocket telemetry ingestion
* Multi-source telemetry support
* Automated alerting
* Historical replay comparison

```
```
