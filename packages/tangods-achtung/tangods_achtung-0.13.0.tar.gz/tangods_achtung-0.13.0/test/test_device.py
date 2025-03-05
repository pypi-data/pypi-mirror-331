from datetime import datetime
import json
from time import time, sleep

import pytest
import tango

from . import achtung_context, build_achtung_info, DEFAULT_AUTORESET_TIME
from .fake_ps import PowerSupply


POWER_SUPPLIES_INFO = {
    "class": PowerSupply,
    "devices": [
        {"name": "test/supply/1"},
        {"name": "test/supply/2"},
    ]
}


# Note: all the tests in this module should run with both old and new evaluator!
@pytest.mark.parametrize("use_new_evaluator", [False, True])
def test_trivial_config(mocker, use_new_evaluator):
    achtung_info = build_achtung_info([("never", "False")],
                                      UseNewEvaluator=use_new_evaluator)

    with achtung_context(mocker, [achtung_info]) as context:
        achtung = context.get_device("test/achtung/1")

        # Check initial situation
        assert not achtung.never

        achtung.update()

        # Check expected situation
        assert achtung.State() == tango.DevState.ON
        assert not achtung.never
        assert not achtung.ActiveAlarms


@pytest.mark.parametrize("use_new_evaluator", [False, True])
def test_broken_property_causes_device_fault(mocker, use_new_evaluator):
    achtung_info = build_achtung_info([
        ("bad_alarm", "True"),
        ("fine_alarm2", "False"),
    ], UseNewEvaluator=use_new_evaluator)

    # Messing up the formatting of an alarm
    achtung_info["devices"][0]["properties"]["AlarmList"][0] = "bad_alarm;True"

    with achtung_context(mocker, [achtung_info]) as context:
        achtung = context.get_device("test/achtung/1")

        # Check expected situation
        assert achtung.State() == tango.DevState.FAULT
        status = achtung.Status()

        assert "AlarmList" in status
        assert "bad_alarm" in status
        assert "fine_alarm2" not in status

        with pytest.raises(tango.DevFailed) as e:
            achtung.ActiveAlarms
        assert e.value.args[0].reason == "API_AttrNotAllowed"


@pytest.mark.parametrize("use_new_evaluator", [False, True])
def test_broken_formula_causes_device_fault(mocker, use_new_evaluator):
    achtung_info = build_achtung_info([
        ("fine_alarm1", "True"),
        ("bad_alarm", "'''jiadj&%%%X"),  # Formula that can't be parsed
        ("fine_alarm2", "False"),
    ], UseNewEvaluator=use_new_evaluator)

    with achtung_context(mocker, [achtung_info]) as context:
        achtung = context.get_device("test/achtung/1")

        # Check expected situation
        assert achtung.State() == tango.DevState.FAULT
        status = achtung.Status()

        assert "fine_alarm1" not in status
        assert "bad_alarm" in status
        assert "fine_alarm2" not in status

        with pytest.raises(tango.DevFailed) as e:
            achtung.ActiveAlarms
        assert e.value.args[0].reason == "API_AttrNotAllowed"


@pytest.mark.parametrize("use_new_evaluator", [False, True])
def test_alarm_with_remote_attribute(mocker, use_new_evaluator):
    achtung_info = build_achtung_info([("ps_on", "test/supply/1/power == True")],
                                      UseNewEvaluator=use_new_evaluator)

    with achtung_context(mocker, [POWER_SUPPLIES_INFO, achtung_info]) as context:
        achtung = context.get_device("test/achtung/1")
        ps1 = context.get_device("test/supply/1")

        # Check initial situation
        assert not achtung.ps_on

        # Turn power on
        ps1.write_attribute("power", True)
        assert ps1.read_attribute("power").value

        achtung.update()

        # Check expected situation
        assert achtung.ps_on


@pytest.mark.parametrize("use_new_evaluator", [False, True])
def test_alarm_with_broken_attribute(mocker, use_new_evaluator):
    achtung_info = build_achtung_info([
        ("ps_on", "test/supply/7/power == True"),
        ("ps_state", "test/supply/7/state == RUNNING")
    ], UseNewEvaluator=use_new_evaluator)

    with achtung_context(mocker, [POWER_SUPPLIES_INFO, achtung_info]) as context:
        achtung = context.get_device("test/achtung/1")
        ps1 = context.get_device("test/supply/1")

        # Check initial situation
        assert not achtung.ps_on

        # Turn power on
        ps1.write_attribute("power", True)
        assert ps1.read_attribute("power").value

        achtung.update()

        # Check expected situation
        assert not achtung.ps_on
        assert len(achtung.ActiveAlarms) == 1
        assert len(achtung.FailedAlarms) == 2

        assert set(fa.split(":")[0] for fa in achtung.FailedAlarms) == {"ps_on", "ps_state"}
        assert "ps_state" in str(achtung.ActiveAlarms)

        assert "2 alarms could not be evaluated" in achtung.Status()


@pytest.mark.parametrize("use_new_evaluator", [False, True])
def test_failed_alarm_restored(mocker, use_new_evaluator):

    achtung_info = build_achtung_info([("exc", "test/supply/1/exception == True")],
                                      UseNewEvaluator=use_new_evaluator)

    with achtung_context(mocker, [POWER_SUPPLIES_INFO, achtung_info]) as context:
        achtung = context.get_device("test/achtung/1")
        ps1 = context.get_device("test/supply/1")

        achtung.update()
        assert not achtung.FailedAlarms

        ps1.toggle_exc()

        achtung.update()
        failed = achtung.FailedAlarms
        assert len(failed) == 1
        assert "exc" in failed[0]

        ps1.toggle_exc()
        achtung.update()

        assert not achtung.FailedAlarms


@pytest.mark.parametrize("use_new_evaluator", [False, True])
def test_alarm_with_variable(mocker, use_new_evaluator):
    achtung_info = build_achtung_info(
        [("voltage_too_high", "test/supply/1/voltage > maxvoltage")],
        # TODO weird... if the Variables property is spelled with different
        # casing (e.g. "variables" the test is broken. AFAIK property names
        # should be case insensitive..?
        variables=["maxvoltage:45"],
        UseNewEvaluator=use_new_evaluator
    )

    with achtung_context(mocker, [POWER_SUPPLIES_INFO, achtung_info]) as context:
        achtung = context.get_device("test/achtung/1")
        ps1 = context.get_device("test/supply/1")

        # Check initial situation
        ps1.write_attribute("power", True)
        achtung.update()
        assert not achtung.voltage_too_high

        ps1.write_attribute("voltage", 55)
        achtung.update()
        assert achtung.voltage_too_high


@pytest.mark.parametrize("use_new_evaluator", [False, True])
def test_active_alarms(mocker, use_new_evaluator):
    """Test activation of alarms with manual reset"""

    achtung_info = build_achtung_info([
        ("ps_on", "test/supply/1/power == True"),
        ("ps_voltage_high", "test/supply/1/voltage > 300"),
        ("ps_voltage_low", "test/supply/1/power == True and test/supply/1/voltage < 5"),
    ], UseNewEvaluator=use_new_evaluator)

    with achtung_context(mocker, [POWER_SUPPLIES_INFO, achtung_info]) as context:
        achtung = context.get_device("test/achtung/1")
        ps1 = context.get_device("test/supply/1")

        # Check initial situation
        achtung.update()
        assert not achtung.ps_on
        assert not achtung.ps_voltage_high
        assert not achtung.ps_voltage_low
        assert not achtung.ActiveAlarms
        assert achtung.State() == tango.DevState.ON

        # Turn on
        ps1.write_attribute("power", True)
        ps1.write_attribute("voltage", 10)

        t0 = time()
        achtung.update()
        assert achtung.State() == tango.DevState.ALARM
        assert achtung.ps_on
        assert not achtung.ps_voltage_high
        assert not achtung.ps_voltage_low
        # ActiveAlarms have format "<tag>:<timestamp>:<formula>"
        active_tags = []
        timestamps = []
        assert achtung.ActiveAlarms
        for line in achtung.ActiveAlarms:
            # Since timestamps *also* contain ":" (thanks, PyAlarm) we
            # need to be careful splitting the lines.
            tag, rest = line.split(":", 1)
            active_tags.append(tag)
            timestamp, *_ = rest.rsplit(":", 1)
            timestamps.append(timestamp)

        # Check that timestamps make sense
        for ts in timestamps:
            t = datetime.fromisoformat(ts).timestamp()
            assert t0 < t < (t0 + 1)
        assert len(active_tags) == 1
        assert "ps_on" in active_tags

        # High voltage
        ps1.write_attribute("voltage", 500)

        achtung.update()
        assert achtung.State() == tango.DevState.ALARM
        assert achtung.ps_on
        assert achtung.ps_voltage_high
        assert not achtung.ps_voltage_low
        active_tags = {line.split(":")[0] for line in achtung.ActiveAlarms}
        assert len(active_tags) == 2
        assert "ps_on" in active_tags
        assert "ps_voltage_high" in active_tags

        # Low voltage
        ps1.write_attribute("voltage", 1)

        achtung.update()
        assert achtung.State() == tango.DevState.ALARM
        assert achtung.ps_on
        assert achtung.ps_voltage_high
        assert achtung.ps_voltage_low
        active_tags = {line.split(":")[0] for line in achtung.ActiveAlarms}
        assert len(active_tags) == 3
        assert "ps_on" in active_tags
        assert "ps_voltage_high" in active_tags
        assert "ps_voltage_low" in active_tags

        # Reset alarm whose formula is no longer true
        achtung.ResetAlarm(["ps_voltage_high", "Some comment here"])

        achtung.update()
        assert achtung.State() == tango.DevState.ALARM
        assert achtung.ps_on
        assert not achtung.ps_voltage_high
        assert achtung.ps_voltage_low
        active_tags = {line.split(":")[0] for line in achtung.ActiveAlarms}
        assert len(active_tags) == 2
        assert "ps_voltage_high" not in active_tags

        # Reset alarm whose formula is still true
        achtung.ResetAlarm(["ps_voltage_low", "Some other comment"])

        achtung.update()
        assert achtung.ps_on
        assert not achtung.ps_voltage_high
        assert achtung.ps_voltage_low
        active_tags = {line.split(":")[0] for line in achtung.ActiveAlarms}
        assert "ps_voltage_low" in active_tags

        # Turn off
        ps1.write_attribute("power", False)
        achtung.ResetAlarm(["ps_on", "..."])
        achtung.ResetAlarm(["ps_voltage_low", "..."])

        achtung.update()
        assert achtung.State() == tango.DevState.ON
        assert not achtung.ps_on
        assert not achtung.ps_voltage_high
        assert not achtung.ps_voltage_low
        assert not achtung.ActiveAlarms


@pytest.mark.parametrize("use_new_evaluator", [False, True])
def test_reset_alarm(mocker, use_new_evaluator):
    """Test manual reset of alarms"""

    achtung_info = build_achtung_info(
        [
            ("ps_voltage_high", "test/supply/1/voltage > 300"),

        ],
        # ResetActions="ps_voltage_high:write_attribute;test/supply/1/other;17",
        UseNewEvaluator=use_new_evaluator)

    with achtung_context(mocker, [POWER_SUPPLIES_INFO, achtung_info]) as context:
        achtung = context.get_device("test/achtung/1")
        ps1 = context.get_device("test/supply/1")

        # Turn set alarm conditions
        ps1.write_attribute("power", True)
        ps1.write_attribute("voltage", 1000)
        achtung.update()

        assert achtung.State() == tango.DevState.ALARM
        assert achtung.ps_voltage_high

        # Unset alarm condition
        ps1.write_attribute("voltage", 100)

        # Alarm still active since we haven't configured auto reset
        achtung.update()
        assert achtung.State() == tango.DevState.ALARM
        assert achtung.ps_voltage_high

        # Reset alarm
        achtung.ResetAlarm(["ps_voltage_high", "Some comment here"])

        achtung.update()
        assert achtung.State() == tango.DevState.ON
        assert not achtung.ps_voltage_high


@pytest.mark.parametrize("use_new_evaluator", [False, True])
def test_reset_active_alarm(mocker, use_new_evaluator):
    """Test manual reset of alarm with active condition"""

    achtung_info = build_achtung_info(
        [
            ("ps_voltage_high", "test/supply/1/voltage > 300"),

        ],
        # ResetActions="ps_voltage_high:write_attribute;test/supply/1/other;17",
        UseNewEvaluator=use_new_evaluator)

    with achtung_context(mocker, [POWER_SUPPLIES_INFO, achtung_info]) as context:
        achtung = context.get_device("test/achtung/1")
        ps1 = context.get_device("test/supply/1")

        # Turn set alarm conditions
        ps1.write_attribute("power", True)
        ps1.write_attribute("voltage", 1000)
        achtung.update()

        assert achtung.State() == tango.DevState.ALARM
        assert achtung.ps_voltage_high

        # Alarm still active since we haven't configured auto reset
        achtung.update()
        assert achtung.State() == tango.DevState.ALARM
        assert achtung.ps_voltage_high

        # Reset alarm
        achtung.ResetAlarm(["ps_voltage_high", "Some comment here"])

        # Alarm still active, condition still true
        achtung.update()
        assert achtung.State() == tango.DevState.ALARM
        assert achtung.ps_voltage_high


@pytest.mark.parametrize("use_new_evaluator", [False, True])
def test_reset_alarm_retry(mocker, use_new_evaluator):
    """Test activation of alarms with manual reset with retries"""

    achtung_info = build_achtung_info(
        [
            ("ps_voltage_high", "test/supply/1/voltage > 300"),

        ],
        # ResetActions="ps_voltage_high:write_attribute;test/supply/1/other;17",
        ResetRetries="2",
        UseNewEvaluator=use_new_evaluator)

    with achtung_context(mocker, [POWER_SUPPLIES_INFO, achtung_info]) as context:
        achtung = context.get_device("test/achtung/1")
        ps1 = context.get_device("test/supply/1")

        # Turn set alarm conditions
        ps1.write_attribute("power", True)
        ps1.write_attribute("voltage", 1000)
        achtung.update()

        assert achtung.State() == tango.DevState.ALARM
        assert achtung.ps_voltage_high

        achtung.ResetAlarm(["ps_voltage_high", "Some comment here"])

        # Alarm still active, since the condition still true
        achtung.update()
        assert achtung.State() == tango.DevState.ALARM
        assert achtung.ps_voltage_high

        # Still true
        achtung.update()
        assert achtung.State() == tango.DevState.ALARM
        assert achtung.ps_voltage_high

        # Unset alarm condition
        ps1.write_attribute("voltage", 100)

        # Alarm gets reset, after two retries
        achtung.update()
        assert achtung.State() == tango.DevState.ON
        assert not achtung.ps_voltage_high


@pytest.mark.parametrize("use_new_evaluator", [False, True])
def test_reset_alarm_retry_fail(mocker, use_new_evaluator):
    """Test reset runs out of retries"""

    achtung_info = build_achtung_info(
        [
            ("ps_voltage_high", "test/supply/1/voltage > 300"),

        ],
        # ResetActions="ps_voltage_high:write_attribute;test/supply/1/other;17",
        ResetRetries="1",
        UseNewEvaluator=use_new_evaluator)

    with achtung_context(mocker, [POWER_SUPPLIES_INFO, achtung_info]) as context:
        achtung = context.get_device("test/achtung/1")
        ps1 = context.get_device("test/supply/1")

        # Turn set alarm conditions
        ps1.write_attribute("power", True)
        ps1.write_attribute("voltage", 1000)
        achtung.update()

        assert achtung.State() == tango.DevState.ALARM
        assert achtung.ps_voltage_high

        achtung.ResetAlarm(["ps_voltage_high", "Some comment here"])

        # Alarm still active, since the condition still true
        achtung.update()
        assert achtung.State() == tango.DevState.ALARM
        assert achtung.ps_voltage_high

        # Still true after first (and last) retry
        achtung.update()
        assert achtung.State() == tango.DevState.ALARM
        assert achtung.ps_voltage_high

        # Unset alarm condition
        ps1.write_attribute("voltage", 100)

        # Alarm reset already failed, too late
        achtung.update()
        assert achtung.State() == tango.DevState.ALARM
        assert achtung.ps_voltage_high


@pytest.mark.parametrize("use_new_evaluator", [False, True])
def test_active_alarms_reset_all(mocker, use_new_evaluator):

    "Same as above, but using ResetAll command instead of individual resets"

    achtung_info = build_achtung_info([
        ("ps_on", "test/supply/1/power == True"),
        ("ps_voltage_high", "test/supply/1/voltage > 300"),
        ("ps_voltage_low", "test/supply/1/power == True and test/supply/1/voltage < 5"),
    ], UseNewEvaluator=use_new_evaluator)

    with achtung_context(mocker, [POWER_SUPPLIES_INFO, achtung_info]) as context:
        achtung = context.get_device("test/achtung/1")
        ps1 = context.get_device("test/supply/1")

        # Check initial situation
        achtung.update()
        assert not achtung.ps_on
        assert not achtung.ps_voltage_high
        assert not achtung.ps_voltage_low
        assert not achtung.ActiveAlarms

        # Turn on
        ps1.write_attribute("power", True)
        ps1.write_attribute("voltage", 10)

        achtung.update()
        assert achtung.ps_on
        assert not achtung.ps_voltage_high
        assert not achtung.ps_voltage_low

        # High voltage
        ps1.write_attribute("voltage", 500)

        achtung.update()
        assert achtung.ps_on
        assert achtung.ps_voltage_high
        assert not achtung.ps_voltage_low
        active_tags = {line.split(":")[0] for line in achtung.ActiveAlarms}
        assert len(active_tags) == 2
        assert "ps_on" in active_tags
        assert "ps_voltage_high" in active_tags

        # Low voltage
        ps1.write_attribute("voltage", 1)

        achtung.update()
        assert achtung.ps_on
        assert achtung.ps_voltage_high
        assert achtung.ps_voltage_low
        active_tags = {line.split(":")[0] for line in achtung.ActiveAlarms}
        assert len(active_tags) == 3
        assert "ps_on" in active_tags
        assert "ps_voltage_high" in active_tags
        assert "ps_voltage_low" in active_tags

        # This should reset alarms whose formula is no longer true
        achtung.ResetAll("Some comment here")

        achtung.update()
        assert achtung.ps_on
        assert not achtung.ps_voltage_high
        assert achtung.ps_voltage_low
        active_tags = {line.split(":")[0] for line in achtung.ActiveAlarms}
        assert len(active_tags) == 2
        assert "ps_voltage_high" not in active_tags

        assert achtung.ps_on
        assert not achtung.ps_voltage_high
        assert achtung.ps_voltage_low
        active_tags = {line.split(":")[0] for line in achtung.ActiveAlarms}
        assert "ps_voltage_low" in active_tags

        # Turn off
        ps1.write_attribute("power", False)
        achtung.update()
        achtung.ResetAll("...")

        achtung.update()
        assert not achtung.ps_on
        assert not achtung.ps_voltage_high
        assert not achtung.ps_voltage_low
        assert not achtung.ActiveAlarms


@pytest.mark.parametrize("use_new_evaluator", [False, True])
def test_disable_alarms(mocker, use_new_evaluator):
    achtung_info = build_achtung_info([
        ("ps_on", "test/supply/1/power == True"),
        ("ps_voltage_high", "test/supply/1/voltage > 300"),
        ("ps_voltage_low", "test/supply/1/power == True and test/supply/1/voltage < 5"),
    ], UseNewEvaluator=use_new_evaluator)

    with achtung_context(mocker, [POWER_SUPPLIES_INFO, achtung_info]) as context:
        achtung = context.get_device("test/achtung/1")
        ps1 = context.get_device("test/supply/1")

        # Check initial situation
        achtung.update()
        assert not achtung.ps_on
        assert not achtung.ps_voltage_high
        assert not achtung.ps_voltage_low
        assert not achtung.ActiveAlarms

        # Turn on
        ps1.write_attribute("power", True)
        ps1.write_attribute("voltage", 8000)

        achtung.update()
        assert achtung.ps_on
        assert achtung.ps_voltage_high

        # Disable alarm
        achtung.Disable(["ps_voltage_high", "Some reason"])
        achtung.update()
        disabled_tags = {line.split(":")[0] for line in achtung.DisabledAlarms}
        assert "ps_voltage_high" in disabled_tags
        assert achtung.ps_on
        assert not achtung.ps_voltage_high

        # Enable again
        achtung.Enable("ps_voltage_high")
        achtung.update()
        assert not achtung.DisabledAlarms
        assert achtung.ps_on
        assert achtung.ps_voltage_high


@pytest.mark.parametrize("use_new_evaluator", [False, True])
def test_autoreset_alarms(mocker, use_new_evaluator):
    achtung_info = build_achtung_info([
        ("ps_on", "test/supply/1/power"),
        ("ps_voltage_high", "test/supply/1/voltage > 300"),
        ("ps_voltage_low", "test/supply/1/power == True and test/supply/1/voltage < 5"),
    ], UseNewEvaluator=use_new_evaluator)

    with achtung_context(mocker, [POWER_SUPPLIES_INFO, achtung_info]) as context:
        achtung = context.get_device("test/achtung/1")
        ps1 = context.get_device("test/supply/1")

        # Check initial situation
        achtung.update()
        assert not achtung.ps_on
        assert not achtung.ps_voltage_high
        assert not achtung.ps_voltage_low
        assert not achtung.ActiveAlarms

        # Trigger some alarms
        ps1.write_attribute("power", True)
        ps1.write_attribute("voltage", 500)
        achtung.update()
        assert achtung.ps_on
        assert achtung.ps_voltage_high
        assert not achtung.ps_voltage_low

        # Back to normal condition
        ps1.write_attribute("voltage", 50)

        # Alarm does not immediately reset
        achtung.update()
        assert achtung.ps_on
        assert achtung.ps_voltage_high

        # Wait more than the autoreset time
        sleep(DEFAULT_AUTORESET_TIME * 1.5)

        # Now the alarm should autoreset
        achtung.update()
        assert achtung.ps_on
        assert not achtung.ps_voltage_high


@pytest.mark.parametrize("use_new_evaluator", [False, True])
def test_alarm_threshold(mocker, use_new_evaluator):
    achtung_info = build_achtung_info([
        ("ps_on", "test/supply/1/power"),
        ("ps_voltage_high", "test/supply/1/voltage > 300"),
        ("ps_voltage_low", "test/supply/1/power == True and test/supply/1/voltage < 5"),
    ], AlarmThreshold=3, UseNewEvaluator=use_new_evaluator)

    with achtung_context(mocker, [POWER_SUPPLIES_INFO, achtung_info]) as context:
        achtung = context.get_device("test/achtung/1")
        ps1 = context.get_device("test/supply/1")

        # Check initial situation
        achtung.update()
        assert not achtung.ps_on
        assert not achtung.ps_voltage_high
        assert not achtung.ps_voltage_low
        assert not achtung.ActiveAlarms

        # Trigger some alarms
        ps1.write_attribute("power", True)
        ps1.write_attribute("voltage", 500)

        # Alarms don't activate since we're below AlarmThreshold
        achtung.update()
        assert not achtung.ps_on
        assert not achtung.ps_voltage_high
        assert not achtung.ps_voltage_low

        achtung.update()
        assert not achtung.ps_on
        assert not achtung.ps_voltage_high
        assert not achtung.ps_voltage_low

        # After three times, the alams activate
        achtung.update()
        assert achtung.ps_on
        assert achtung.ps_voltage_high
        assert not achtung.ps_voltage_low


@pytest.mark.parametrize("use_new_evaluator", [False, True])
def test_eval_timeout(mocker, use_new_evaluator):
    achtung_info = build_achtung_info([
        # ("ps_on", "test/supply/1/power"),
        # ("ps_voltage_high", "test/supply/1/voltage > 300"),
        ("ps_slow", "test/supply/1/slow"),
    ], EvalTimeout=0.1, UseNewEvaluator=use_new_evaluator)

    print("t", time())

    with achtung_context(mocker, [POWER_SUPPLIES_INFO, achtung_info]) as context:
        achtung = context.get_device("test/achtung/1")
        ps1 = context.get_device("test/supply/1")

        # Check initial situation
        achtung.update()
        assert not achtung.ps_slow
        assert not achtung.ActiveAlarms
        assert not achtung.FailedAlarms

        # Trigger slowness
        ps1.write_attribute("power", True)

        achtung.update()
        assert "ps_slow:" in achtung.FailedAlarms[0]
        assert not achtung.ActiveAlarms

        status = achtung.Status()
        assert "ps_slow" in status

        sleep(0.2)  # prevent the fake_ps from segfaulting :/


@pytest.mark.parametrize("use_new_evaluator", [False, True])
def test_bad_http_consumer(mocker, use_new_evaluator):
    achtung_info = build_achtung_info(
        [
            ("ps_on", "test/supply/1/power"),
            ("ps_voltage_high", "test/supply/1/voltage > 300"),
        ],
        HttpConsumers=["http://this.doesnt.exist/almost/certainly/1982/"],
        PollingPeriod=0.1, UseNewEvaluator=use_new_evaluator
    )

    with achtung_context(mocker, [POWER_SUPPLIES_INFO, achtung_info]) as context:
        achtung = context.get_device("test/achtung/1")
        assert achtung.State() == tango.DevState.FAULT
        assert "HttpConsumers" in achtung.Status()


@pytest.mark.parametrize("use_new_evaluator", [False, True])
def test_http_consumer_receives_alarm_reports(mocker, httpserver, use_new_evaluator):
    achtung_info = build_achtung_info(
        [
            ("ps_on", "test/supply/1/power"),
            ("ps_voltage_high", "test/supply/1/voltage > 300"),
        ],
        HttpConsumers=[httpserver.url_for("/alarms")],
        ReportExtras=json.dumps({"a_little_extra": "something"}),
        PollingPeriod=0.1, UseNewEvaluator=use_new_evaluator
    )

    httpserver.expect_oneshot_request("/alarms", method="GET").respond_with_data()  # Ping
    httpserver.expect_request("/alarms", method="POST").respond_with_data()

    with achtung_context(mocker, [POWER_SUPPLIES_INFO, achtung_info]) as context:
        achtung = context.get_device("test/achtung/1")
        ps1 = context.get_device("test/supply/1")

        achtung.update()

        ps1.write_attribute("power", True)

        achtung.update()
        assert achtung.ps_on

        ps1.write_attribute("power", False)

        achtung.update()
        achtung.ResetAlarm(["ps_on", "no comment"])
        achtung.update()

        assert not achtung.ps_on

        # Wait for several periods, to ensure that we don't send more stuff
        sleep(1)

    httpserver.check_assertions()
    assert len(httpserver.log) == 3

    # First access is just a check, at startup
    request0, _ = httpserver.log[0]
    assert request0.method == "GET"

    # Alarm activated
    request1, _ = httpserver.log[1]
    report1 = request1.get_json()
    assert len(report1) == 1
    assert report1[0]["alarm_tag"] == "ps_on"
    assert report1[0]["message"] == "ACTIVE"
    assert report1[0]["active_since"]
    assert report1[0]["timestamp"]
    assert report1[0]["a_little_extra"] == "something"

    # Alarm reset
    request2, _ = httpserver.log[2]
    report2 = request2.get_json()
    assert len(report2) == 1
    assert report2[0]["alarm_tag"] == "ps_on"
    assert report2[0]["message"] == "RESET"
    assert not report2[0].get("active_since")
    assert report1[0]["a_little_extra"] == "something"


@pytest.mark.parametrize("use_new_evaluator", [False, True])
def test_startup_delay(mocker, use_new_evaluator):
    achtung_info = build_achtung_info(
        [
            ("ps_on", "test/supply/1/power"),
            ("ps_voltage_high", "test/supply/1/voltage > 300"),
        ],
        StartupDelay=60
    )

    with achtung_context(mocker, [POWER_SUPPLIES_INFO, achtung_info]) as context:
        achtung = context.get_device("test/achtung/1")
        assert achtung.State() == tango.DevState.DISABLE
        assert "Waiting 60.0 seconds" in achtung.Status()


@pytest.mark.parametrize("use_new_evaluator", [False, True])
def test_alarm_checking_state_active_on_failure(mocker, use_new_evaluator):
    """
    Check that behavior matches PyAlarm's handling of failed alarms
    that check state.
    """
    achtung_info = build_achtung_info(
        [
            ("ps_state_on", "test/supply/17/state == ON"),
            ("ps_something_else", "test/supply/17/voltage < 73"),
        ], UseNewEvaluator=use_new_evaluator
    )
    with achtung_context(mocker, [achtung_info]) as context:
        achtung = context.get_device("test/achtung/1")
        achtung.update()
        assert achtung.State() == tango.DevState.ALARM
        assert achtung.ps_state_on  # Alarm active because it reads State
        assert not achtung.ps_something_else  # not active because it doesn't


@pytest.mark.parametrize("use_new_evaluator", [False, True])
def test_report_log(mocker, tmp_path, use_new_evaluator):
    report_logfile = tmp_path / "alarm_log.ndjson"
    achtung_info = build_achtung_info(
        [("always", "True")],
        ReportLogfile=str(report_logfile),
        ReportExtras=json.dumps({"hello": 53}),
        UseNewEvaluator=use_new_evaluator
    )

    with achtung_context(mocker, [achtung_info]) as context:
        achtung = context.get_device("test/achtung/1")
        achtung.update()

        assert achtung.State() == tango.DevState.ALARM

        # A report should be written to the logfile
        assert report_logfile.exists()
        content = report_logfile.open().readlines()
        assert len(content) == 1
        report = json.loads(content[0])
        assert report["alarm_tag"] == "always"
        assert report["message"] == "ACTIVE"
        assert report["hello"] == 53


@pytest.mark.parametrize("use_new_evaluator", [False, True])
def test_report_log_instance(mocker, tmp_path, use_new_evaluator):
    report_logfile = tmp_path / "alarm_log.ndjson"
    achtung_info = build_achtung_info(
        [("ps_on", "test/supply/1/power")],
        ReportLogfile=str(report_logfile),
        UseNewEvaluator=use_new_evaluator
    )

    with achtung_context(mocker, [POWER_SUPPLIES_INFO, achtung_info]) as context:
        achtung = context.get_device("test/achtung/1")
        ps1 = context.get_device("test/supply/1")
        achtung.update()

        # Activate
        ps1.write_attribute("power", True)
        achtung.update()
        assert achtung.State() == tango.DevState.ALARM

        # Reset
        ps1.write_attribute("power", False)
        achtung.ResetAlarm(["ps_on", "..."])
        achtung.update()
        assert achtung.State() == tango.DevState.ON

        # Activate again
        ps1.write_attribute("power", True)
        achtung.update()
        assert achtung.State() == tango.DevState.ALARM

        assert report_logfile.exists()
        content = report_logfile.open().readlines()
        assert len(content) == 3
        reports = [json.loads(line) for line in content]
        assert reports[0]["message"] == "ACTIVE"
        assert reports[1]["message"] == "RESET"

        # The first two reports should be the same instance id, since
        # they concern the same activation
        instance = reports[0]["instance"]
        assert instance == reports[1]["instance"]

        # Last report should be a new instance
        assert reports[2]["message"] == "ACTIVE"
        assert reports[2]["instance"] != instance
