"""
Tests that need a Tango database.
We use the pytango-db project for this, so that we don't require a
full Tango installation.
"""

import time

import pytest
import tango

from . import build_achtung_props, start_achtung


def test_no_reset_action(mocker, pytango_db):
    """Test manual reset of alarm without reset action"""

    achtung_props = dict(
        UseNewEvaluator=True,
        **build_achtung_props([
            ("ps_voltage_high", "test/supply/1/voltage > 300"),
        ]),
        logging_level="DEBUG",
    )

    with start_achtung(achtung_props) as achtung:
        ps1 = tango.get_device_proxy("test/supply/1")

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

        # Alarm has not been reset, condition is still true
        achtung.update()
        assert achtung.State() == tango.DevState.ALARM
        assert achtung.ps_voltage_high


def test_reset_action(mocker, pytango_db):
    """Test manual reset of alarm with reset action"""

    achtung_props = dict(
        # This action will change the PS voltage when the alarm is reset
        # so that it's under the alarm limit
        Actions="ps_voltage_high:reset:write_attribute:test/supply/1/voltage:200",
        UseNewEvaluator=True,
        **build_achtung_props([
            ("ps_voltage_high", "test/supply/1/voltage > 300"),
        ]),
        logging_level=["DEBUG"],
    )

    with start_achtung(achtung_props) as achtung:
        ps1 = tango.get_device_proxy("test/supply/1")

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

        # Alarm has been reset, because the action changed the condition
        achtung.update()
        assert achtung.State() == tango.DevState.ON
        assert not achtung.ps_voltage_high


def test_reset_action_resetall(mocker, pytango_db):
    """Test manual reset of alarm with reset action"""

    achtung_props = dict(
        # This action will change the PS voltage when the alarm is reset
        # so that it's under the alarm limit
        Actions="ps_voltage_high:reset:write_attribute:test/supply/1/voltage:200",
        UseNewEvaluator=True,
        **build_achtung_props([
            ("ps_voltage_high", "test/supply/1/voltage > 300"),
        ]),
        logging_level=["DEBUG"],
    )

    with start_achtung(achtung_props) as achtung:
        ps1 = tango.get_device_proxy("test/supply/1")

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
        achtung.ResetAll("Some comment here")

        # Alarm has been reset, because the action changed the condition
        achtung.update()
        assert achtung.State() == tango.DevState.ON
        assert not achtung.ps_voltage_high


def test_reset_actions_multiple_resetall(mocker, pytango_db):

    achtung_props = dict(
        Actions=[
            # This action will change the PS voltage when the alarm is reset
            # so that it's under the alarm limit
            "ps_voltage_high:reset:write_attribute:test/supply/1/voltage:200",
            "ps_voltage_low:reset:write_attribute:test/supply/1/other:true",
        ],
        UseNewEvaluator=True,
        **build_achtung_props([
            ("ps_voltage_high", "test/supply/1/voltage > 300"),
            ("ps_voltage_low", "test/supply/1/voltage < -100"),
        ]),
        logging_level=["DEBUG"],
    )

    with start_achtung(achtung_props) as achtung:
        ps1 = tango.get_device_proxy("test/supply/1")

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
        achtung.ResetAll("Some comment here")

        # Alarm has been reset, because the action changed the condition
        achtung.update()
        assert achtung.State() == tango.DevState.ON
        assert not achtung.ps_voltage_high

        # The second reset action did not run, it's for another alarm
        assert ps1.other is False

        # Now activate the second alarm
        ps1.write_attribute("voltage", -1000)
        achtung.update()
        assert achtung.ps_voltage_low

        # Then reset it
        ps1.write_attribute("voltage", 0)
        achtung.ResetAll("Some comment here")
        achtung.update()
        assert not achtung.ps_voltage_low

        # The second alarm's reset action ran
        assert ps1.other is True


def test_reset_actions_multiple_on_same_alarm_resetall(mocker, pytango_db):

    achtung_props = dict(
        Actions=[
            # This action will change the PS voltage when the alarm is reset
            # so that it's under the alarm limit
            "ps_voltage_high:reset:write_attribute:test/supply/1/voltage:200",
            "ps_voltage_high:reset:write_attribute:test/supply/1/other:true",
        ],
        UseNewEvaluator=True,
        **build_achtung_props([
            ("ps_voltage_high", "test/supply/1/voltage > 300"),
            ("ps_voltage_low", "test/supply/1/voltage < -100"),
        ]),
        logging_level=["DEBUG"],
    )

    with start_achtung(achtung_props) as achtung:
        ps1 = tango.get_device_proxy("test/supply/1")

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
        achtung.ResetAll("Some comment here")

        # Alarm has been reset, because the first action changed the condition
        achtung.update()
        assert achtung.State() == tango.DevState.ON
        assert not achtung.ps_voltage_high
        assert ps1.other is True  # second action also ran


def test_reset_actions_resetall_failure(mocker, pytango_db):
    """Test manual reset of alarms with a failing reset action"""

    achtung_props = dict(
        # This action will change the PS voltage when the alarm is reset
        # so that it's under the alarm limit
        Actions=[
            "ps_voltage_high:reset:write_attribute:test/supply/1/voltage:200",
            "ps_voltage_high:reset:write_attribute:test/supply/1/other:17",  # bad value, bool attr
        ],
        UseNewEvaluator=True,
        **build_achtung_props([
            ("ps_voltage_high", "test/supply/1/voltage > 300"),
        ]),
        logging_level=["DEBUG"],
    )

    with start_achtung(achtung_props) as achtung:
        ps1 = tango.get_device_proxy("test/supply/1")

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
        with pytest.raises(tango.DevFailed):
            achtung.ResetAll("Some comment here")

        # Alarm has been reset, because the action changed the condition
        achtung.update()
        assert achtung.State() == tango.DevState.ON
        assert not achtung.ps_voltage_high

        # The second reset action failed
        assert ps1.other is False


def test_activate_action(mocker, pytango_db):
    """Test manual reset of alarm with reset action"""

    achtung_props = dict(
        # This action will change the PS voltage when the alarm is reset
        # so that it's under the alarm limit
        Actions="ps_voltage_high:activate:write_attribute:test/supply/1/other:true",
        **build_achtung_props([
            ("ps_voltage_high", "test/supply/1/voltage > 300"),
        ]),
        logging_level=["DEBUG"],
    )

    with start_achtung(achtung_props) as achtung:
        ps1 = tango.get_device_proxy("test/supply/1")
        assert ps1.other is False

        # Turn set alarm conditions
        ps1.write_attribute("power", True)
        ps1.write_attribute("voltage", 1000)
        achtung.update()
        time.sleep(0.01)  # Actions run async, so

        # The activate action should have run at this point
        assert achtung.State() == tango.DevState.ALARM
        assert achtung.ps_voltage_high
        assert ps1.other is True
