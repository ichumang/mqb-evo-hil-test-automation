# CI/CD Pipeline

## Overview

The test framework runs on a dedicated Jenkins controller (`jenkins.internal.local`)
with Windows-based agents connected to HiL test benches. All agents have
CANoe licenses, Vector hardware drivers, and Python 3.11 installed.

---

## Pipeline Stages

```
  ┌──────────┐   ┌────────┐   ┌──────────┐   ┌───────────┐   ┌────────────┐
  │  Checkout │──►│  Lint  │──►│  Unit    │──►│  Smoke    │──►│  Report    │
  │  + Setup  │   │ flake8 │   │  Tests   │   │  (subset) │   │  Allure    │
  │           │   │ mypy   │   │  47 pass │   │  30 tests │   │  + Slack   │
  └──────────┘   └────────┘   └──────────┘   └───────────┘   └────────────┘
       │
       │ (nightly trigger)
       ▼
  ┌──────────┐   ┌────────────┐   ┌───────────┐   ┌─────────┐   ┌──────────┐
  │  Setup   │──►│ Integration│──►│  System   │──►│  HiL    │──►│ Regress  │
  │  Bench   │   │  83 tests  │   │  62 tests │   │ 34 tests│   │ 156 tests│
  │  CANoe   │   │  single-ECU│   │  multi-ECU│   │ power   │   │ 6×26 var │
  └──────────┘   └────────────┘   └───────────┘   └─────────┘   └──────────┘
       │
       ▼
  ┌──────────────────────────────────────────────┐
  │  Post-Actions                                 │
  │  - Allure report publish                      │
  │  - Jira tickets for failures                  │
  │  - Slack notification (#mqb-evo-test)          │
  │  - Coverage matrix update (DOORS)             │
  └───────────────────────────────────────────────┘
```

## Trigger Schedules

| Trigger | Schedule | Scope | Duration |
|---------|----------|-------|----------|
| Commit push | On every push to `main` / `develop` | Lint + Unit + Smoke | ~3 min |
| Nightly | 02:00 CET, Mon–Fri | Full suite (422 tests) | ~45 min |
| Weekly HiL | Sunday 04:00 CET | HiL power + voltage + EMC | ~2 h |
| Release gate | Manual trigger | Full + extended soak | ~90 min |

## Jenkinsfile Structure

```groovy
pipeline {
    agent { label 'mqb-evo-bench-win' }

    triggers {
        cron('H 2 * * 1-5')    // nightly
    }

    stages {
        stage('Setup') {
            steps {
                bat 'python -m pip install -r requirements.txt'
                bat 'python -m pytest --collect-only -q'
            }
        }
        stage('Lint') {
            steps {
                bat 'python -m flake8 lib/ tests/ conftest.py'
                bat 'python -m mypy lib/ --ignore-missing-imports'
            }
        }
        stage('Unit') {
            steps {
                bat 'python -m pytest tests/unit/ -v --alluredir=reports/allure'
            }
        }
        // ... integration, system, hil, regression stages
    }

    post {
        always {
            allure includeProperties: false, results: [[path: 'reports/allure']]
        }
        failure {
            slackSend channel: '#mqb-evo-test', color: 'danger',
                message: "MQB-EVO nightly FAILED: ${env.BUILD_URL}"
        }
    }
}
```

## Agent Requirements

| Requirement | Details |
|-------------|---------|
| OS | Windows 10/11 (CANoe requires Windows) |
| Python | 3.11+ with pip |
| CANoe | V17+ with COM API license |
| Vector drivers | VN1640 CAN/LIN interface |
| Network | VW backend reachable (for backend tests) |
| HiL bench | Connected relay board + PSU (for HiL tests) |
| UART | USB-serial adapter for serial trace capture |

## Report Artifacts

| Artifact | Format | Location |
|----------|--------|----------|
| Allure report | HTML | `jenkins.internal.local/allure/mqb-evo/` |
| pytest HTML | `.html` | `reports/report.html` |
| Serial logs | `.log` | Attached to Allure per-test |
| CANoe traces | `.blf` | Archived per build |
| Coverage matrix | `.xlsx` | DOORS export, weekly |
