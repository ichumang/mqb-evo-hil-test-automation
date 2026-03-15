"""
MQB-EVO HiL/SiL Test Automation — Root conftest.py

Central pytest configuration for the MQB-EVO test framework.
Provides session-scoped hardware fixtures (CANoe, serial), function-scoped
diagnostic sessions, custom markers, and report enrichment hooks.

Author: Umang Panchal (github.com/ichumang)
"""

import logging
import os
from datetime import datetime
from pathlib import Path

import pytest
import yaml

log = logging.getLogger("mqb_evo")

# ──────────────────────────── Paths ──────────────────────────────

ROOT_DIR = Path(__file__).parent
CONFIG_DIR = ROOT_DIR / "config"
REPORTS_DIR = ROOT_DIR / "reports"


# ──────────────────────────── ECU Variants ───────────────────────

ECU_VARIANTS = [
    "MIB3_HIGH_EU",
    "MIB3_HIGH_NAR",
    "MIB3_ENTRY_EU",
    "OCU5_EU",
    "KOMBI_EU",
    "BCM1_EU",
]


# ──────────────────────────── Markers ────────────────────────────

def pytest_configure(config):
    """Register custom markers used across the test suite."""
    config.addinivalue_line("markers", "hil: requires physical HiL bench")
    config.addinivalue_line("markers", "sil: can run on simulated ECU")
    config.addinivalue_line("markers", "smoke: fast subset for commit checks")
    config.addinivalue_line("markers", "regression: full nightly regression")
    config.addinivalue_line("markers", "e2e: multi-ECU end-to-end scenario")
    config.addinivalue_line("markers", "backend: requires VW backend access")
    config.addinivalue_line("markers", "performance: timing-sensitive test")
    config.addinivalue_line("markers", "unit: offline unit test")
    config.addinivalue_line("markers", "integration: single-ECU diagnostic")


# ──────────────────────────── Bench Config ───────────────────────

@pytest.fixture(scope="session")
def bench_config():
    """Load HiL bench hardware configuration from YAML.

    Returns a dict with keys like 'canoe_cfg_path', 'doip_ip',
    'serial_port', 'relay_board_ip', 'psu_ip', etc.
    Falls back to defaults if config file is missing (SiL mode).
    """
    cfg_path = CONFIG_DIR / "bench_config.yaml"
    if cfg_path.exists():
        with open(cfg_path, "r") as fh:
            return yaml.safe_load(fh)
    # sensible defaults for SiL / CI without bench hardware
    return {
        "canoe_cfg_path": r"C:\CANoe\MQB_EVO\mqb_evo.cfg",
        "doip_ip": "172.20.0.10",
        "doip_port": 13400,
        "serial_port": "COM4",
        "serial_baud": 115200,
        "relay_board_ip": "172.20.0.50",
        "psu_ip": "172.20.0.60",
        "kl30_voltage_nom": 13.5,
    }


# ──────────────────────────── CANoe ──────────────────────────────

@pytest.fixture(scope="session")
def canoe_app(bench_config):
    """Session-scoped CANoe COM application.

    Opens CANoe, loads the MQB-EVO configuration, and starts
    measurement. Yields the application handle. Tears down
    measurement and quits CANoe at session end.
    """
    from lib.canoe_api import CANoeApplication

    cfg_path = bench_config["canoe_cfg_path"]
    log.info("Starting CANoe with config: %s", cfg_path)

    app = CANoeApplication()
    app.open(cfg_path)
    app.start_measurement()
    yield app

    log.info("Stopping CANoe measurement")
    app.stop_measurement()
    app.quit()


@pytest.fixture(scope="module")
def canoe_measurement(canoe_app):
    """Module-scoped measurement restart.

    Stops and restarts measurement between test modules to ensure
    a clean bus state. Cheaper than restarting the whole application.
    """
    canoe_app.stop_measurement()
    canoe_app.start_measurement()
    yield canoe_app
    # measurement stays running — next module fixture handles restart


# ──────────────────────────── Diagnostics ────────────────────────

@pytest.fixture(scope="function")
def diag_session(bench_config):
    """Function-scoped UDS diagnostic session via DoIP.

    Creates a fresh UDS client connected to the target ECU.
    Opens an extended diagnostic session (0x03) and yields
    the client. Closes session on teardown.
    """
    from lib.odis_diag import create_uds_client

    client = create_uds_client(
        ip=bench_config["doip_ip"],
        port=bench_config["doip_port"],
    )
    # open extended diagnostic session
    client.change_session(0x03)
    yield client

    # attempt graceful return to default session
    try:
        client.change_session(0x01)
    except Exception:
        pass
    client.close()


# ──────────────────────────── Serial Trace ───────────────────────

@pytest.fixture(scope="function")
def serial_logger(bench_config, request):
    """Function-scoped serial trace capture.

    Opens the UART port, captures all output during the test, and
    on failure attaches the log to the Allure report.
    """
    from lib.serial_trace import SerialLogger

    port = bench_config.get("serial_port", "COM4")
    baud = bench_config.get("serial_baud", 115200)

    logger = SerialLogger(port=port, baudrate=baud)
    logger.start()
    yield logger

    log_data = logger.stop()
    # attach to allure on failure
    if request.node.rep_call and request.node.rep_call.failed:
        try:
            import allure
            allure.attach(
                log_data,
                name="serial_trace.log",
                attachment_type=allure.attachment_type.TEXT,
            )
        except ImportError:
            pass  # allure not installed in this env


# ──────────────────────────── ECU Power ──────────────────────────

@pytest.fixture(scope="function")
def ecu_power(bench_config):
    """Function-scoped ECU power control (KL15/KL30).

    Provides methods to toggle ignition (KL15), cut battery (KL30),
    and set voltage via the lab PSU. Resets to nominal on teardown.
    """
    from lib.ecu_power import ECUPowerController

    ctrl = ECUPowerController(
        relay_ip=bench_config["relay_board_ip"],
        psu_ip=bench_config["psu_ip"],
        nominal_voltage=bench_config["kl30_voltage_nom"],
    )
    yield ctrl

    # restore nominal power state
    ctrl.set_voltage(bench_config["kl30_voltage_nom"])
    ctrl.kl15_on()


# ──────────────────────────── Variant Parametrize ────────────────

@pytest.fixture(scope="session")
def variant_config():
    """Load ECU variant definitions for parametrized regression tests.

    Returns a dict keyed by variant ID with expected DID values,
    DTC lists, SW/HW versions, etc.
    """
    cfg_path = CONFIG_DIR / "ecu_variants.yaml"
    if cfg_path.exists():
        with open(cfg_path, "r") as fh:
            return yaml.safe_load(fh)
    return {}


def pytest_generate_tests(metafunc):
    """Auto-parametrize tests that request the 'ecu_variant' fixture."""
    if "ecu_variant" in metafunc.fixturenames:
        metafunc.parametrize("ecu_variant", ECU_VARIANTS, scope="session")


# ──────────────────────────── Report Hooks ───────────────────────

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Store test result on the request node for use by fixtures."""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


def pytest_html_report_title(report):
    """Set HTML report title."""
    report.title = "MQB-EVO Test Report"


def pytest_html_results_summary(prefix, summary, postfix):
    """Add metadata to HTML report header."""
    prefix.extend([
        f"<p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>",
        f"<p>Platform: VW MQB-EVO</p>",
        f"<p>Variants: {', '.join(ECU_VARIANTS)}</p>",
    ])
