# Notice — Public / Private Code Policy

This repository uses a **public README + private code** model for portfolio
demonstration purposes.

## What is public

| Path | Content |
|------|---------|
| `README.md` | Project overview, architecture, test metrics |
| `docs/*.md` | Test architecture, CI/CD pipeline, ECU coverage matrix |
| `conftest.py` | Root pytest configuration — fixtures, markers, hooks |
| `CONTRIBUTING.md` | Contribution guidelines |
| `LICENSE` | Proprietary license terms |

## What is private

| Path | Content |
|------|---------|
| `lib/` | Test libraries — CANoe API, UDS diagnostics, BAP codec, serial trace, ECU power control |
| `tests/` | 422 test cases across unit, integration, system, regression, HiL, backend, and performance categories |
| `config/` | Bench hardware configuration, ECU variant definitions |

Private directories contain `NOTICE.md` files explaining their proprietary status.

## Author

Umang Panchal — github.com/ichumang
