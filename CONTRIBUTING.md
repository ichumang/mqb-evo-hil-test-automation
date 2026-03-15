# Contributing

This repository is a **portfolio showcase** of the MQB-EVO HiL/SiL test
automation framework developed at [Previous Employer]. External contributions
are not accepted at this time.

## For [Previous Employer] Team Members

1. **Branch from `develop`** — never push directly to `main`.
2. **Follow pytest conventions** — use markers, fixtures from `conftest.py`,
   and parametrize across ECU variants where applicable.
3. **Require DOORS traceability** — every test docstring must include a
   `REQ-MQB-xxxx` reference.
4. **Run the full smoke suite** before opening a merge request:
   ```bash
   pytest -m smoke -v --alluredir=reports/allure
   ```
5. **Allure report** must show no regressions.
6. **Code review** by at least one team member with HiL bench access.

## Test Quality Standards

| Metric | Requirement |
|--------|-------------|
| Smoke suite pass rate | 100% |
| Nightly regression pass rate | ≥ 98% |
| New test must have | marker, docstring, REQ-MQB ref |
| Flaky tests | Must be marked `@pytest.mark.xfail(reason="known_flaky")` |
