import asyncio
from collections import deque
from datetime import datetime
from functools import lru_cache
import json
import time
import logging
from typing import Union
from uuid import uuid4

import tango
from tango.asyncio import AttributeProxy, DeviceProxy
from pyparsing.exceptions import ParseException

from achtung.evaluator import AlarmEvaluator


# AlarmStates
#  'NORM' #Normal state
#  'RTNUN' #Active but returned to normal
#  'ACKED' #Acknowledged by operator
#  'ACTIVE' #UNACK alias
#  'UNACK' #Active and unacknowledged
#  'ERROR' #PyAlarm not working properly, exception on formula
#  'SHLVD' #Silenced, hidden, ignored, (DEBUG), temporary state
#  'DSUPR' #Disabled by a process condition (Enabled), failed not throwed
#  'OOSRV' #Unconditionally disabled, Enable = False, Device is OFF

# ACTIVE_STATES = 'ACTIVE','UNACK','ACKED','RTNUN'
# DISABLED_STATES = 'ERROR','SHLVD','OOSRV','DSUPR'

# SEVERITIES:
# 'DEBUG':0,
# 'INFO':1,
# 'WARNING':2,
# 'ALARM':3,
# 'ERROR':4,
# 'CONTROL':-1

class Alarm(object):
    ALARM_PRIORITIES = {
        "ALARM": 400,
        "ERROR": 400,
        "WARNING": 300,
        "INFO": 200,
        "DEBUG": 100,
    }

    def __init__(
            self,
            formula="",
            rawformula="",
            name="",
            severity="",
            desc="",
            receiver="",
            device="",
            actions=None,
            queue_length=10,
            autoreset=0.0,
            reset_retries=0,
            logger=None,
            checks_state=False,
    ):
        self.active = False
        self.instance = None  # Unique id for an alarm activation
        self.value = None
        self.subvalues = {}  # Values of attributes and values at last evaluation
        self.exception = None
        self.active_since = 0
        self.disabled_since = 0
        self.failed_since = 0
        self.counter = 0
        self.returned_since = None
        self.failed = False
        self.enabled = True
        self.acked = None
        self.reset_attempt = None
        self.reset_retries = reset_retries
        self.rawformula = rawformula
        self.formula = formula
        self.tag = name
        self.severity = severity
        self.priority = self.ALARM_PRIORITIES.get(severity, 0)
        self.description = desc
        self.receiver = receiver
        self.actions = actions or {}
        self.comment = ""
        self.reports = deque(maxlen=queue_length)
        self.device = device
        self.checks_state = checks_state
        if autoreset > 0.0:
            self.autoreset_time = autoreset
        else:
            self.autoreset_time = 315360000.0  # 10 years
        self.logger = logger or logging.getLogger(__name__)

    def __repr__(self):
        try:
            return ("Alarm(tag={tag}, severity={severity}, formula='{formula}', active={active}, enabled={enabled})"
                    .format(**self.__dict__))
        except Exception:
            self.logger.exception("Failed to create string representation for alarm %r", self.tag)

    @property
    def active_since_isoformat(self):
        return datetime.fromtimestamp(self.active_since).isoformat()

    @property
    def disabled_since_isoformat(self):
        return datetime.fromtimestamp(self.disabled_since).isoformat()

    @property
    def failed_since_isoformat(self):
        return datetime.fromtimestamp(self.failed_since).isoformat()

    def update(self, value: bool, subvalues, threshold: int = 0):
        self.value = value
        self.subvalues = subvalues
        self.failed = False
        actions = []

        if value:
            self.counter += 1
            if self.counter >= threshold:
                self.activate()
                if activate_actions := self.actions.get("activate"):
                    actions.extend(activate_actions)

            if self.active and self.reset_attempt is not None:
                # A reset is pending
                # Since the formula is true, it fails
                if self.reset_attempt <= self.reset_retries:
                    # Failed attempt, perhaps try again
                    self.reset_attempt += 1
                else:
                    # Stop trying
                    self.reset_attempt = None
                    self.reset_comment = None

        elif self.active:
            # Alarm formula is no longer true, but the alarm is active.
            if self.returned_since is None:
                self.returned_since = time.time()
            elif (time.time() - self.returned_since) > self.autoreset_time:
                # Auto-reset when alarm has been low for long enough
                self.active_since = 0
                self.active = False
                self.comment = "Autoreset"
                self.acked = None
                self._append_report("AUTORESET")
                self._append_report("RESET")
                self.logger.debug("Autoreset alarm %r", self.tag)
            if self.reset_attempt is not None:
                # A reset is pending
                if self.reset_attempt <= self.reset_retries:
                    self.reset()

        return actions

    # MESSAGE_TYPES = ['ACTIVE','ACKNOWLEDGED','RECOVERED','AUTORESET','RESET','DISABLED']
    def _append_report(self, message: str):
        tz = datetime.now().astimezone().tzinfo
        now = datetime.now(tz).isoformat()
        report = {
            "description": self.description,
            "timestamp": now,
            "priority": self.priority,
            "subvalues": self.subvalues,
            "device": self.device,
            "formula": self.rawformula,
            "alarm_tag": self.tag,
            "severity": self.severity,
            "message": message,
            "instance": self.instance,
        }
        if message == "ACTIVE":
            report["active_since"] = datetime.fromtimestamp(self.active_since, tz).isoformat()
        elif message == "RECOVERED":
            report["recovered_at"] = now
        elif message == "ACKNOWLEDGED":
            report["user_comment"] = self.comment
            report["recovered_at"] = now
            report["active_since"] = datetime.fromtimestamp(self.active_since, tz).isoformat()
        elif message == "RESET":
            report["user_comment"] = self.comment
        elif message == "DISABLED":
            report["user_comment"] = self.comment
        self.reports.append(report)

    def enable(self):
        if not self.enabled:
            self.enabled = True
            self.failed = False
            self.disabled_since = 0
            self.failed_since = 0
            self.acked = None
            self.counter = 0
            self.logger.debug("Enabled")

    def disable(self, comment):
        if self.enabled:
            self.enabled = False
            self.disabled_since = time.time()
            self.comment = comment
            self.acked = None
            self._append_report("DISABLED")
            self.counter = 0
            self.logger.debug("Disabled")

    def fail(self, exception=None):
        self.exception = exception
        if not self.failed:
            self.failed = True
            self.failed_since = time.time()
            self.comment = "Failed"
            self._append_report("FAILED")
            self.counter = 0
            self.logger.debug("Failed alarm %r", self.tag)
        if self.checks_state:
            # To imitate PyAlarm behavior, we activate the alarm if it checks
            # device state.
            self.activate()

    def activate(self):
        self.counter = 0

        if not self.active:
            self.active_since = time.time()
            self.returned_since = None
            self.active = True
            self.acked = False
            self.instance = str(uuid4())
            self._append_report("ACTIVE")
            self.logger.debug("Activated alarm %r", self.tag)

    def mark_reset(self, comment):
        """
        Mark the alarm as being reset. Next time it's updated, if it evaluates
        as false, the alarm will be reset.
        """
        self.reset_attempt = 0
        self.reset_comment = comment
        return self.actions.get("reset", [])

    def reset(self):
        # Reset the alarm
        self.counter = 0
        self.active_since = 0
        self.active = False
        self.comment = self.reset_comment
        self.reset_comment = None
        self.acked = None
        self._append_report("RESET")
        self.logger.debug("Reset alarm %r", self.tag)

    def acknowledge(self, comment):
        if not self.acked:
            self.acked = True
            self.comment = comment
            self._append_report("ACKNOWLEDGED")
            self.logger.debug("Acknowledged alarm %r", self.tag)

    def renounce(self):
        if self.acked:
            self.acked = False
            self.logger.debug("Denounced alarm %r", self.tag)

    @property
    def state(self):
        if self.failed:
            return "ERROR"
        elif not self.enabled:
            return "OOSRV"
        elif not self.active:
            return "NORM"
        elif self.active and self.value and not self.acked:
            return "UNACK"
        elif self.active and not self.value and not self.acked:
            return "RTNUN"
        elif self.active and self.acked:
            return "ACKED"
        else:
            return "ERROR"

    def get_reports(self):
        reports = self.reports
        self.reports = []
        return reports

    def get_exception_string(self) -> str:
        if self.exception:
            if isinstance(self.exception, tango.DevFailed):
                return self.exception.args[0].desc
            return str(self.exception)
        return ""

    async def perform_actions(self, place: str):
        self.logger.info(f"Performing {place} actions for {self}")
        actions = self.actions.get(place, [])
        self.logger.debug(f"Actions: {self.actions}")
        return await perform_actions(*actions)


@lru_cache(1)
def get_database():
    return tango.Database()


class Action:
    """
    An "action" can either write an attribute or run a command on some tango device.
    The syntax is e.g.
       run_command;sys/tg_test/1/switchstates  # No argument
       run_command;sys/tg_test/1/some_command;["a", "b", "c"]  # Argument, as JSON
       write_attribute;sys/tg_test/1/double_scalar;56.2  # Also JSON
    """

    WRITE_ATTRIBUTE = 0
    RUN_COMMAND = 1
    action_types = {
        "write_attribute": WRITE_ATTRIBUTE,
        "run_command": RUN_COMMAND,
    }
    keywords = {
        "false": False,
        "true": True,
    }

    def __init__(self, type_: str, target: str, args: object, logger=None):
        self.action_type = type_  # E.g. write_attribute
        self.target = target  # E.g. an attribute name
        self.args = args  # JSON compatible value, e.g. 19, or ["foo", "bar"]
        self.logger = logger or logging.getLogger(__name__)

    def __hash__(self):
        return hash((self.action_type, self.target, json.dumps(self.args)))

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __repr__(self):
        return f"Action: {self.get_action_name(self.action_type)} Target: {self.target} Args: {self.args}"

    async def execute(self) -> None:
        self.logger.debug(f"Running action {self}")
        try:
            if self.action_type == Action.RUN_COMMAND:
                device, command = self.target.rsplit("/", 1)
                proxy = await DeviceProxy(device)
                if self.args:
                    await proxy.command_inout(command, self.args)
                else:
                    await proxy.command_inout(command)
            elif self.action_type == Action.WRITE_ATTRIBUTE:
                proxy = await AttributeProxy(self.target)
                await proxy.write(self.args)
        except Exception as e:
            self.logger.error(f"Failed to run action {self}: {e}")
            raise

    @classmethod
    def from_string(cls, string, sep=":", logger=None):
        try:
            action_type, target, *args = [
                word.strip() for word in string.split(sep, 2)
            ]
        except ValueError:
            msg = f"bad format '{string}'. Expected <action>{sep}<name_of_attribute/command>[{sep}<args_as_JSON>]"
            raise ValueError(msg)

        try:
            args = json.loads(args[0]) if args else None
        except ValueError as e:
            raise ValueError(f"bad args '{args}'. Could not parse args as JSON: {e}")

        try:
            action_type = Action.action_types[action_type.lower()]
        except KeyError:
            msg = f"bad action name '{string}'. Expected {', '.join(Action.action_types)}"
            raise ValueError(msg)

        target = Action._verify_target(target)

        return cls(action_type, target, args, logger)

    @staticmethod
    def _verify_target(target):
        try:
            parsed = AlarmEvaluator.attribute.parseString(target)
        except ParseException:
            raise ValueError(f"bad action target '{target}'; it is not a valid Tango name")
        device, element = parsed[0].rsplit("/", 1)
        try:
            DeviceProxy(device)
        except tango.DevFailed as e:
            raise ValueError(f"bad action target device '{device}'; {e.args[0].desc}")
        return target

    @staticmethod
    def get_action_name(action_number):
        return list(Action.action_types.keys())[action_number]


async def perform_actions(*actions: Action) -> list[Union[None, Exception]]:
    """
    Perform the given actions, ensuring that identical actions are only done once.
    """
    unique_actions = set(actions)
    if unique_actions:
        coros = (action.execute() for action in unique_actions)
        return await asyncio.gather(*coros, return_exceptions=True)
    return []
