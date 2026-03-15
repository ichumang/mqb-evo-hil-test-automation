# ECU Coverage Matrix

## Overview

This matrix maps test categories to ECU functions across all supported
MQB-EVO variants. Coverage is tracked against DOORS requirements.

---

## MIB3 High (Infotainment Head Unit)

| Function | Unit | Integration | System | Regression | HiL |
|----------|------|-------------|--------|------------|-----|
| Diagnostics (UDS) | — | DTC R/W, DID read, session mgmt | — | 26 tests × 2 variants | — |
| BAP messaging | encode/decode | LSG subscribe, response | — | — | — |
| Bluetooth audio | — | BT module ready | pairing, A2DP stream | — | — |
| CarPlay | — | — | USB detect, projection, audio | — | — |
| Android Auto | — | — | USB detect, projection, audio | — | — |
| Navigation | — | — | GPS fix, route calc | — | — |
| Boot time | — | — | — | — | cold/warm start |
| Power cycle | — | — | — | — | KL15 cycle, rapid cycle |
| Voltage variation | — | — | — | — | 9V/16V/cranking dip |

## MIB3 Entry (Base Infotainment)

| Function | Unit | Integration | System | Regression | HiL |
|----------|------|-------------|--------|------------|-----|
| Diagnostics (UDS) | — | DTC R/W, DID read | — | 26 tests × 1 variant | — |
| BAP messaging | encode/decode | LSG subscribe | — | — | — |
| Bluetooth phone | — | BT module ready | HFP call, phonebook | — | — |
| Radio | — | — | FM/DAB tune, station list | — | — |
| Boot time | — | — | — | — | cold start |

## OCU5 (Online Connectivity Unit)

| Function | Unit | Integration | System | Regression | Backend | HiL |
|----------|------|-------------|--------|------------|---------|-----|
| Diagnostics | — | DTC, DID | — | 26 tests × 1 variant | — | — |
| WiFi hotspot | — | AP init | SSID broadcast, clients | — | — | — |
| LTE registration | — | — | cell attach, signal | — | backend verify | — |
| Online services | — | — | NTP sync, weather | — | SWaP auth | — |
| OTA update | — | — | — | — | download, install, verify | — |
| Boot time | — | — | — | — | — | cold start |

## Kombi (Instrument Cluster)

| Function | Unit | Integration | Regression | HiL |
|----------|------|-------------|------------|-----|
| Diagnostics | — | DTC, DID, variant coding | 26 tests × 1 variant | — |
| CAN signal display | — | speed, RPM, fuel | — | — |
| Warning indicators | — | — | — | power cycle recovery |

## BCM1 (Body Control Module)

| Function | Unit | Integration | Regression | HiL |
|----------|------|-------------|------------|-----|
| Diagnostics | — | DTC, DID | 26 tests × 1 variant | — |
| KL15/KL30 power | — | ignition on/off | — | cycle, sleep/wake |
| Bus sleep entry | — | — | — | NM timeout, wake |
| Comfort functions | — | window, mirror, lock | — | — |

---

## Requirement Traceability

Tests link to DOORS requirements via docstring annotations:

```python
def test_mib3_read_vin(diag_session):
    """REQ-MQB-1042: ECU shall respond to DID F190 with valid VIN."""
    response = diag_session.read_did(0xF190)
    assert len(response) == 17
```

The CI pipeline extracts `REQ-MQB-xxxx` patterns and generates a traceability
matrix exported to DOORS weekly.

| Metric | Value |
|--------|-------|
| Total requirements tracked | 312 |
| Requirements with automated tests | 287 (92%) |
| Requirements pending automation | 25 (8%) |
| Requirements without test (justified) | 0 |

---

## Test Count Summary

| ECU | Unit | Integration | System | Regression | HiL | Backend | Perf | Total |
|-----|------|-------------|--------|------------|-----|---------|------|-------|
| MIB3 High | 32 | 38 | 28 | 52 | 14 | — | 6 | 170 |
| MIB3 Entry | 8 | 15 | 12 | 26 | 4 | — | 2 | 67 |
| OCU5 | 4 | 12 | 14 | 26 | 4 | 28 | 2 | 90 |
| Kombi | 2 | 10 | 4 | 26 | 4 | — | 1 | 47 |
| BCM1 | 1 | 8 | 4 | 26 | 8 | — | 1 | 48 |
| **Total** | **47** | **83** | **62** | **156** | **34** | **28** | **12** | **422** |
