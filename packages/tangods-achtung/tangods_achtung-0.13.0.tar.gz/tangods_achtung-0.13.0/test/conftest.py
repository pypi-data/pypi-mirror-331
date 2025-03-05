import logging
import os
import subprocess
import sys
import time

import pytest
import tango

from . import PYTANGO_TANGO_HOST, PYTANGO_DATABASE_NAME

logging.basicConfig(level=logging.DEBUG)


@pytest.fixture(scope="function")
def pytango_db():
    """
    Runs a pytango database server that we can run the tests against.
    This eliminates the need for MySQL etc.
    Also creates and starts a test device.
    """
    # TODO get a free port
    os.environ["TANGO_HOST"] = PYTANGO_TANGO_HOST
    try:

        databaseds = subprocess.Popen(
            [sys.executable, "-m", "databaseds.database", "2"],
            env={
                "TANGO_HOST": PYTANGO_TANGO_HOST,
                "PYTANGO_DATABASE_NAME": PYTANGO_DATABASE_NAME,
            },
        )

        waited = 0
        dt = 0.3
        while True:
            time.sleep(dt)
            waited += dt
            if databaseds.poll() is not None:
                raise RuntimeError(f"Database stopped: {databaseds.returncode}")
            try:
                db = tango.Database()
                db.get_info()
                break
            except tango.DevFailed as e:
                if waited > 10:
                    raise RuntimeError("Tired of waiting for database...") from e
            except AssertionError:
                pass

        device = "test/supply/1"
        dev_info = tango.DbDevInfo()
        dev_info.name = device
        dev_info._class = "PowerSupply"
        dev_info.server = "fake_ps/1"
        db.add_server(dev_info.server, dev_info, with_dserver=True)
        db.put_device_property(device, {"graphql_test": ["abc", "def"]})

        # Start our dummy device

        dummy = subprocess.Popen(
            [sys.executable, "test/fake_ps.py", "1"], stderr=subprocess.PIPE
        )
        waited = 0
        dt = 0.3
        while True:
            time.sleep(dt)
            waited += dt
            if dummy.poll() is not None:
                stderr = dummy.stderr.read().decode()
                print(stderr)
                raise RuntimeError(f"Dummy device stopped: {dummy.returncode}")
            try:
                proxy = tango.DeviceProxy(
                    device, green_mode=tango.GreenMode.Synchronous
                )
                proxy.ping()
                if proxy.read_attribute("State").value == tango.DevState.RUNNING:
                    break
            except tango.DevFailed as e:
                if waited > 10:
                    raise RuntimeError("Tired of waiting for device proxy...") from e
            except AssertionError:
                pass

        yield device

    finally:
        # Clean up
        try:
            dummy.kill()
            db.delete_server(dev_info.server)
        except Exception:
            pass
        try:
            databaseds.kill()
        except Exception:
            pass

        del os.environ["TANGO_HOST"]
