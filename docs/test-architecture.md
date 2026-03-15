# Test Architecture

## Overview

The framework follows a layered architecture that decouples test logic from
hardware interfaces. Tests never interact with hardware directly — they use
library abstractions that can be swapped between real HiL bench and simulated
SiL environment.

---

## Layer Model

```
  ┌─────────────────────────────────────────────────────────────┐
  │  Layer 4: Test Cases                                        │
  │  tests/unit/ integration/ system/ regression/ hil/ backend/ │
  │  Pure pytest — assert-based, parametrized, marked           │
  └────────────────────────────┬────────────────────────────────┘
                               │ uses fixtures
  ┌────────────────────────────┴────────────────────────────────┐
  │  Layer 3: conftest.py — Fixtures & Hooks                    │
  │  Session/function scope, ECU lifecycle, report enrichment   │
  └────────────────────────────┬────────────────────────────────┘
                               │ instantiates
  ┌────────────────────────────┴────────────────────────────────┐
  │  Layer 2: Test Libraries (lib/)                              │
  │  canoe_api, odis_diag, bap_codec, serial_trace, ecu_power  │
  └────────────────────────────┬────────────────────────────────┘
                               │ calls
  ┌────────────────────────────┴────────────────────────────────┐
  │  Layer 1: Hardware / Simulation                              │
  │  CANoe COM, Vector VN1640, Relay board, Lab PSU, UART       │
  └─────────────────────────────────────────────────────────────┘
```

## Fixture Scoping

| Fixture | Scope | Purpose |
|---------|-------|---------|
| `canoe_app` | session | CANoe COM application — expensive to start, shared across all tests |
| `canoe_measurement` | module | Start/stop measurement per test module |
| `diag_session` | function | UDS diagnostic session — fresh per test |
| `serial_logger` | function | Serial trace capture — auto-attached to Allure on failure |
| `ecu_power` | function | KL15/KL30 control — resets ECU between HiL tests |
| `bench_config` | session | YAML bench hardware config — loaded once |
| `ecu_variant` | parametrize | Current ECU variant under test (from variant matrix) |

## Data Flow — Integration Test Example

```
  test_read_vin()
       │
       ▼
  diag_session fixture
       │ creates UDS client via doipclient
       ▼
  odis_diag.read_did(0xF190)
       │ UDS ReadDataByIdentifier
       ▼
  doipclient → DoIP TCP → ECU → UDS response
       │
       ▼
  assert vin.startswith("WVW")
       │
       ▼
  serial_logger fixture
       │ on failure: attach UART log to Allure
       ▼
  Allure report
```

## Marker Hierarchy

Tests can carry multiple markers. The CI pipeline filters by marker:

```
  @pytest.mark.smoke         — subset for commit-triggered runs
  @pytest.mark.regression    — nightly full suite
  @pytest.mark.hil           — requires physical HiL bench
  @pytest.mark.sil           — can run on SiL (simulated ECU)
  @pytest.mark.backend       — requires VW backend connectivity
  @pytest.mark.performance   — timing-sensitive, run in isolation
  @pytest.mark.e2e           — multi-ECU end-to-end
```

## Variant Matrix

The regression suite is parametrized across ECU variants:

| Variant ID | ECU | HW Version | SW Version | Market |
|------------|-----|------------|------------|--------|
| `MIB3_HIGH_EU` | MIB3 High | H50 | 0783 | EU/ROW |
| `MIB3_HIGH_NAR` | MIB3 High | H50 | 0783 | NAR |
| `MIB3_ENTRY_EU` | MIB3 Entry | H30 | 0612 | EU/ROW |
| `OCU5_EU` | OCU5 | H10 | 0341 | EU/ROW |
| `KOMBI_EU` | Kombi | H20 | 0455 | EU/ROW |
| `BCM1_EU` | BCM1 | H15 | 0298 | EU/ROW |

Each regression test runs once per variant, producing a 6 × 26 = 156 test
matrix. Variant-specific expected values (DID content, DTC lists) are loaded
from `config/ecu_variants.yaml`.

---

## Error Handling Strategy

| Failure Type | Action |
|--------------|--------|
| Test assertion failure | Mark FAIL, capture serial log + CANoe trace, create Jira ticket |
| ECU no-response (timeout) | Retry once after KL15 power cycle, then FAIL |
| CANoe COM error | Restart CANoe application, retry test module |
| Bench hardware fault | Skip remaining HiL tests, alert Slack channel |
| Flaky test detected | Mark XFAIL with `reason="known_flaky"`, log to tracking sheet |
