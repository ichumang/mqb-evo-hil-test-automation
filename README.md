# mqb-evo-hil-test-automation

> A pytest-based Hardware-in-the-Loop (HiL) and Software-in-the-Loop (SiL) test automation framework for automotive embedded infotainment systems — 422 test cases, Jenkins CI/CD pipeline, coverage growth from 62% to 91%.

![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)
![pytest](https://img.shields.io/badge/pytest-HiL%2FSiL-0C8590?logo=pytest&logoColor=white)
![Jenkins](https://img.shields.io/badge/Jenkins-CI%2FCD-D24939?logo=jenkins&logoColor=white)
![Automotive](https://img.shields.io/badge/Automotive-ASPICE%20%7C%20ISO%2026262-blue)
![License](https://img.shields.io/badge/License-MIT-blue)

---

## Overview

This repository demonstrates the architecture and methodology of a professional HiL/SiL test automation framework built for an automotive infotainment platform. The framework uses **pytest** as its test runner with custom fixtures for hardware abstraction, enabling the same test cases to execute against real hardware (HiL) and simulated environments (SiL) without modification.

---

## Framework Architecture

```
╔══════════════════════════════════════════════════════════════════════╗
║               MQB-EVO HiL/SiL Test Framework                        ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  ┌──────────────────────────────────────────────────────────────┐    ║
║  │                  pytest Test Suite  (422 tests)              │    ║
║  │                                                              │    ║
║  │  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐    │    ║
║  │  │  Unit tests │  │ Integration  │  │ E2E / Regression  │    │    ║
║  │  │  (SiL only) │  │   tests      │  │  (HiL + SiL)     │    │    ║
║  │  └──────┬──────┘  └──────┬───────┘  └────────┬──────────┘    │    ║
║  └─────────┼────────────────┼──────────────────┼────────────────┘    ║
║            └────────────────┼──────────────────┘                     ║
║                             ▼                                         ║
║  ┌──────────────────────────────────────────────────────────────┐    ║
║  │           Hardware Abstraction Layer  (pytest fixtures)      │    ║
║  │                                                              │    ║
║  │   ┌─────────────────┐            ┌─────────────────┐        │    ║
║  │   │  HiL Backend    │            │  SiL Backend    │        │    ║
║  │   │  (CANoe COM)    │            │  (Mock / Stub)  │        │    ║
║  │   └────────┬────────┘            └────────┬────────┘        │    ║
║  └────────────┼──────────────────────────────┼─────────────────┘    ║
║               │                              │                       ║
║  ┌────────────▼────────────┐    ┌────────────▼────────────┐         ║
║  │  Physical HiL Bench     │    │  Simulation Environment  │         ║
║  │  • ECU (target HW)      │    │  • Python stubs          │         ║
║  │  • CANoe (VN1640A)      │    │  • CAPL script replays   │         ║
║  │  • Power supply control │    │  • UDS response tables   │         ║
║  └─────────────────────────┘    └─────────────────────────┘         ║
╚══════════════════════════════════════════════════════════════════════╝
```

---

## CI/CD Pipeline

```
  Developer commits
        │
        ▼
  ┌─────────────────┐
  │    Git push     │
  └────────┬────────┘
           │
           ▼
  ┌─────────────────────────────────────────┐
  │            Jenkins Pipeline             │
  │                                         │
  │  Stage 1: Static analysis (flake8)      │
  │       │                                 │
  │       ▼                                 │
  │  Stage 2: SiL test run  (422 tests)     │
  │       │   └─ No hardware required       │
  │       ▼                                 │
  │  Stage 3: Coverage report generation    │
  │       │   └─ pytest-cov HTML artifact   │
  │       ▼                                 │
  │  Stage 4: HiL regression set            │
  │       │   └─ Requires bench connection  │
  │       ▼                                 │
  │  Stage 5: DOORS traceability export     │
  └─────────────────────────────────────────┘
           │
           ▼
  PASS: merge gate cleared
  FAIL: build blocked + Jira ticket auto-created
```

---

## Coverage Growth

```
Test Coverage (%)
100 ┤
 91 ┤                                    ████████████  91% ← After framework
 80 ┤                        ████████████
 70 ┤            ████████████
 62 ┤ ████████████  ← Baseline (manual testing only)
    └────┬──────────────┬────────────────┬──────────── Sprint
         0             +3               +6
```

| Metric | Before | After |
|---|---|---|
| Automated test cases | 0 | 422 |
| Test coverage | 62% (manual) | 91% (automated) |
| Regression cycle time | ~3 days | ~4 hours |
| Variant coverage | Ad-hoc | 6-variant systematic matrix |

---

## Test Categories

| Category | Count | Description |
|---|---|---|
| Unit tests | 87 | Function-level SiL verification |
| Integration tests | 143 | Multi-component interaction (CAN + UDS + BAP) |
| E2E regression | 118 | Full workflow from user action to CAN output |
| HiL voltage tests | 38 | Supply voltage variation sweep (8 V – 16 V) |
| Negative / boundary | 36 | Error injection, timeout, invalid input |

---

## Technology Stack

| Component | Technology |
|---|---|
| Test runner | pytest (custom fixtures, parameterised test matrix) |
| HiL interface | CANoe COM API (Vector) via Python win32com |
| Diagnostics | ODIS / UDS over DoIP (ISO 14229) |
| Protocol tracing | BAP (Bedien- und Anzeige-Protokoll) |
| CI/CD | Jenkins (Declarative Pipeline) |
| Requirements tracing | Jira + DOORS bidirectional link |
| Coverage | pytest-cov + HTML / XML export |

---

## Key Design Patterns

| Pattern | Implementation |
|---|---|
| **HiL/SiL parity** | All tests use abstract fixtures; backend selected by `pytest.ini` marker at runtime |
| **Parameterised regression matrix** | 6 vehicle variants × full test suite via `pytest.mark.parametrize` |
| **Self-healing fixtures** | CANoe connection fixtures auto-reconnect on timeout; test continues rather than failing entire suite |
| **Structured test IDs** | DOORS requirement ID embedded in test name for automatic traceability export |
| **Parallel SiL execution** | SiL-only tests run with `pytest-xdist` across 4 workers for ~3× speedup |

---

## Repository Structure

```
mqb-evo-hil-test-automation/
├── tests/
│   ├── unit/               # Function-level SiL tests
│   ├── integration/        # Multi-component tests
│   ├── e2e/                # End-to-end regression suite
│   └── hil/                # HiL-specific voltage + stress tests
├── fixtures/
│   ├── canoe_fixture.py    # CANoe COM abstraction
│   ├── uds_fixture.py      # UDS / DoIP session management
│   └── bap_fixture.py      # BAP protocol trace fixture
├── utils/
│   ├── coverage.py         # Coverage merge + HTML report
│   └── doors_export.py     # Jira / DOORS traceability export
├── jenkins/
│   └── Jenkinsfile         # Declarative CI/CD pipeline
└── docs/
    └── test-strategy.md    # Coverage strategy and variant matrix
```

---

## ASPICE / V-Model Alignment

This framework supports ASPICE Level 2 evidence generation:

- **SWE.4** — Unit verification (87 unit tests with MC/DC targets)
- **SWE.5** — Integration verification (143 integration tests with interface coverage)
- **SWE.6** — System testing (118 E2E + 38 HiL tests with requirements traceability)

---

## Market Context

HiL/SiL test automation is now mandatory under ISO 26262 and ASPICE for automotive software development. The shift toward software-defined vehicles (SDV) and decoupled E/E architectures is driving demand for engineers who can **build and maintain** test infrastructure — not just run manual tests.

This framework approach is transferable to:
- ADAS / AD system test automation
- Automotive cybersecurity testing (ISO 21434)
- AUTOSAR stack integration testing
- Industrial embedded systems (IEC 61508 verification)

---

## License

MIT — see [LICENSE](./LICENSE)

> **Note:** This repository contains the test framework architecture and methodology only. No production ECU calibration data, vehicle-specific parameters, or proprietary diagnostic routines are included.
