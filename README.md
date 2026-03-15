# MQB-EVO HiL/SiL Test Automation Framework

![Python 3.11](https://img.shields.io/badge/Python-3.11-blue)
![pytest 8.x](https://img.shields.io/badge/pytest-8.x-green)
![VW MQB-EVO](https://img.shields.io/badge/Platform-MQB--EVO-lightgrey)
![422 Tests](https://img.shields.io/badge/Tests-422-brightgreen)
![Jenkins CI](https://img.shields.io/badge/CI-Jenkins-red)
![Allure Reports](https://img.shields.io/badge/Reports-Allure-orange)

Enterprise-grade pytest framework for automated HiL, SiL, and bench-level
validation of **Volkswagen MQB-EVO platform ECUs** — infotainment (MIB3),
connectivity (OCU5), telematics (TCU), instrument cluster (Kombi), and body
control (BCM1). Built at [Previous Employer] for the VW Group test bench
infrastructure.

> **Note:** Test libraries (`lib/`) and test implementations (`tests/`) are
> proprietary. The public `conftest.py` and documentation demonstrate the
> framework architecture. See [NOTICE.md](NOTICE.md) for details.

---

## Test Architecture

```
  ┌──────────────────────────────────────────────────────────────────┐
  │                    Test Runner (pytest + Jenkins)                 │
  │  conftest.py → markers, fixtures, hooks, variant parametrize     │
  └────────────────────────────┬─────────────────────────────────────┘
                               │
  ┌────────────────────────────┴─────────────────────────────────────┐
  │                       Test Libraries (lib/)                       │
  │                                                                   │
  │  ┌─────────────┐  ┌──────────────┐  ┌────────────────────────┐  │
  │  │ canoe_api.py │  │ odis_diag.py │  │ serial_trace.py        │  │
  │  │ CANoe COM    │  │ UDS / DoIP   │  │ UART boot logs         │  │
  │  │ CAN, LIN,   │  │ DTC read/clr │  │ error pattern match    │  │
  │  │ Ethernet,    │  │ DID R/W      │  │ timestamp extraction   │  │
  │  │ BAP msgs     │  │ session mgmt │  │                        │  │
  │  └──────┬───────┘  └──────┬───────┘  └───────────┬────────────┘  │
  │         │                 │                       │               │
  │  ┌──────┴───────┐  ┌─────┴────────┐  ┌──────────┴────────────┐  │
  │  │ bap_codec.py │  │ cp_tool.py   │  │ ecu_power.py          │  │
  │  │ BAP encode/  │  │ CP variant   │  │ KL15/KL30 relay ctrl  │  │
  │  │ decode, LSG  │  │ coding,      │  │ voltage variation     │  │
  │  │ ID mapping   │  │ long coding  │  │ HiL bench interface   │  │
  │  └──────────────┘  └──────────────┘  └────────────────────────┘  │
  └──────────────────────────────────────────────────────────────────┘
                               │
  ┌────────────────────────────┴─────────────────────────────────────┐
  │                     Hardware / Bench Layer                        │
  │                                                                   │
  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────────────┐  │
  │  │ CANoe    │  │ Vector   │  │ Relay     │  │ Lab PSU         │  │
  │  │ (Vector) │  │ VN1640   │  │ Board     │  │ (Rohde&Schwarz) │  │
  │  │ COM API  │  │ CAN/LIN  │  │ KL15/30  │  │ 6–18V sweep     │  │
  │  └──────────┘  └──────────┘  └──────────┘  └─────────────────┘  │
  └──────────────────────────────────────────────────────────────────┘
```

---

## Test Categories

| Category | Tests | Scope | Marker |
|----------|-------|-------|--------|
| **Unit** | 47 | BAP encoding, config parsing, protocol helpers | `@pytest.mark.unit` |
| **Integration** | 83 | Single-ECU diagnostic sequences, DTC/DID read/write | `@pytest.mark.integration` |
| **System / E2E** | 62 | Multi-ECU flows: Bluetooth, WiFi, CarPlay, Android Auto, online services | `@pytest.mark.e2e` |
| **Regression** | 156 | 6 ECU variants × 26 test cases, parametrized matrix | `@pytest.mark.regression` |
| **HiL** | 34 | Power cycle, voltage variation (LV 124), boot time, EMC recovery | `@pytest.mark.hil` |
| **Backend** | 28 | OCU5 online connectivity, OTA update flow, SWaP backend | `@pytest.mark.backend` |
| **Performance** | 12 | Response latency, CAN bus load, cold/warm start timing | `@pytest.mark.performance` |
| **Total** | **422** | | |

---

## ECU Coverage

| ECU | Platform | Function | Test Scope |
|-----|----------|----------|------------|
| **MIB3 High** | MQB-EVO | Infotainment head unit, navigation, media | Diagnostics, BAP, CarPlay, Android Auto, BT audio |
| **MIB3 Entry** | MQB-EVO | Base infotainment, radio, phone | Diagnostics, BAP, BT phone |
| **OCU5** | MQB-EVO | Online connectivity unit, WiFi hotspot, LTE | Online services, OTA, backend, WiFi AP |
| **Kombi** | MQB-EVO | Instrument cluster, driver info display | CAN signals, DID reads, variant coding |
| **BCM1** | MQB-EVO | Body control module, comfort functions | KL15/KL30 power, sleep/wake, bus management |
| **Gateway** | MQB-EVO | Central gateway, CAN/LIN routing | Bus routing validation, diagnostic proxy |

---

## CI/CD Pipeline

```
  ┌──────────┐    ┌──────┐    ┌─────────────┐    ┌─────────┐    ┌────────────┐
  │  Commit  │───►│ Lint │───►│ Unit Tests  │───►│  Smoke  │───►│  Nightly   │
  │  Trigger │    │ flake8│    │ (47 tests)  │    │ (subset)│    │ Full Suite │
  └──────────┘    │ mypy │    └─────────────┘    └─────────┘    │ (422 tests)│
                  └──────┘                                      └────────────┘
                                                                      │
                                                               ┌──────┴──────┐
                                                               │   Reports   │
                                                               │ Allure HTML │
                                                               │ Jira ticket │
                                                               │ Slack alert │
                                                               └─────────────┘
```

- **On every commit:** lint + unit tests + smoke subset (~3 min)
- **Nightly (02:00 CET):** full regression suite across all 6 ECU variants (~45 min)
- **Weekly (Sunday 04:00):** HiL power cycle + voltage variation on bench (~2 h)
- **Reports:** Allure HTML served on `http://jenkins.internal.local/allure/mqb-evo`
- **Failure handling:** Auto-create Jira ticket in MQBEVO project, attach Allure link + serial log

---

## Framework Features

- **Custom pytest markers:** `@hil`, `@sil`, `@smoke`, `@regression`, `@backend`, `@performance`, `@e2e`
- **Fixture-based ECU lifecycle:** session-scoped CANoe connection, function-scoped diagnostic sessions
- **Parametrized variant matrix:** `@pytest.mark.parametrize("variant", ECU_VARIANTS)` across 6 ECU variants
- **Serial trace capture:** automatic UART log capture during test, attached to Allure report on failure
- **DOORS traceability:** test docstrings contain requirement IDs (`REQ-MQB-xxxx`), parsed into coverage matrix
- **Automatic Jira integration:** failed tests create MQBEVO Jira tickets with logs + screenshots
- **Power management:** KL15/KL30 fixture handles ECU power cycling, voltage sweeps per LV 124 / VW TL 80000
- **BAP protocol library:** encode/decode BAP telegrams, LSG ID mapping, opcode helpers

---

## Technology Stack

| Component | Version | Purpose |
|-----------|---------|---------|
| Python | 3.11 | Test runtime |
| pytest | 8.x | Test framework + fixtures |
| pytest-html | 4.x | HTML report generation |
| pytest-xdist | 3.x | Parallel test execution |
| pytest-timeout | 2.x | Test timeout enforcement |
| pytest-ordering | 0.6+ | Test execution order control |
| Allure | 2.x | Rich test reporting |
| python-can | 4.x | CAN bus interface |
| udsoncan | 1.x | UDS diagnostic client |
| doipclient | 1.x | DoIP transport layer |
| isotp | 2.x | ISO-TP framing |
| pyserial | 3.x | Serial trace capture |
| pandas | 2.x | Test data analysis |
| PyYAML | 6.x | Configuration files |
| Jinja2 | 3.x | Report templates |
| flake8 / mypy / black | latest | Code quality |

---

## Module Structure

```
├── conftest.py              — pytest fixtures, markers, hooks (PUBLIC)
├── config/
│   ├── bench_config.yaml    — HiL bench hardware mapping
│   ├── ecu_variants.yaml    — ECU variant definitions (HW/SW versions)
│   └── doors_mapping.yaml   — Requirement ID → test function mapping
├── lib/
│   ├── canoe_api.py         — CANoe COM automation wrapper
│   ├── odis_diag.py         — UDS/DoIP diagnostic client
│   ├── bap_codec.py         — BAP protocol encoder/decoder
│   ├── serial_trace.py      — Serial log capture + pattern matching
│   ├── ecu_power.py         — KL15/KL30 relay + PSU control
│   ├── cp_tool.py           — Variant coding / parameterization
│   ├── jira_client.py       — Automatic Jira ticket creation
│   └── report_utils.py      — Allure attachment helpers
├── tests/
│   ├── unit/                — BAP encoding, config parsing, helpers
│   ├── integration/         — Single-ECU diagnostic sequences
│   ├── system/              — Multi-ECU E2E scenarios
│   ├── regression/          — Parametrized variant matrix
│   ├── hil/                 — Power cycle, voltage, boot time
│   ├── backend/             — Online services, OTA, SWaP
│   └── performance/         — Latency, bus load, startup timing
├── ci/
│   ├── Jenkinsfile          — Multi-stage pipeline definition
│   └── run_tests.sh         — CLI wrapper for local/CI execution
├── reports/                 — Generated test reports (gitignored)
├── requirements.txt
└── pytest.ini
```

---

## Author

**Umang Panchal** — [GitHub](https://github.com/ichumang)

- GitHub: [github.com/ichumang](https://github.com/ichumang)

---

*This repository demonstrates the architecture and design of a production
automotive test framework. Test implementations and library code are
proprietary — see [NOTICE.md](NOTICE.md).*
