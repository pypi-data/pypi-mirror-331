"""
This is a different implementation of the evaluator, that uses the
normal python parser to execute formulas. This seems quite a bit
faster, and enables much more elaborate syntax in formulas (basically
full python expressions). It's also reading attributes in batches per
device instead if individually, which can be a lot more efficient if
many alarms read attributes on the same device.

The main drawback is that it uses eval() which is usually considered a
security hazard.  However, we do restrict what's available to use in
formulas quite a bit. Also, PyAlarm uses eval() anyway, as far as I can
tell, so it should not be worse.
"""

import asyncio
from collections import defaultdict
from datetime import datetime, timedelta
from functools import partial, cache, lru_cache
from itertools import count, groupby
import logging
import math
from operator import itemgetter
from random import random, randint
from time import time, perf_counter
from typing import MutableMapping, Any, Sequence
from types import CodeType
import re

import tango  # type: ignore
from tango.utils import CaselessDict
from tango.asyncio import DeviceProxy  # type: ignore
from .util import Timer, FormulaError


ATTRIBUTE_PREFIX_RE = r"tango://[^:]+:\d+/"
ATTRIBUTE_NAME_RE = r"[\-\w.@_]+/[\-\w.@_]+/[\-\w.@_]+/[\-\w@_]+"
ATTRIBUTE_RE = fr"(({ATTRIBUTE_PREFIX_RE})?{ATTRIBUTE_NAME_RE})(\.[_a-z]+)?"
STATE_ATTRIBUTE_RE = fr"(({ATTRIBUTE_PREFIX_RE})?[\-\w.@_]+/[\-\w.@_]+/[\-\w.@_]+/state)(\.[_a-z]+)?"


class AttrData:
    """
    This class is used for "resolving" attribute data when a formula evaluates.
    Depending on the result of the attribute read, it will contain different
    results, and accessing the various properties on it will yield different
    effects.
    """

    def __init__(self, name: str, result: tango.DeviceAttribute | tango.DevFailed):
        self.__name = name
        self.__result = result

    @property
    def value(self) -> Any:
        "Get the value of the attribute, if available, else raises DevFailed."
        if isinstance(self.__result, tango.DeviceAttribute):
            if self.__result.has_failed:
                raise RuntimeError(f"Failed to read attribute {self.__name}")
            return self.__result.value
        raise self.__result

    @property
    def safe_value(self) -> Any:
        "Get the value or None, never raises."
        if isinstance(self.__result, tango.DeviceAttribute):
            return self.__result.value

    @property
    def quality(self) -> bool:
        "Get quality if available, raises DevFailed otherwise."
        if isinstance(self.__result, tango.DeviceAttribute):
            if self.__result.has_failed:
                raise RuntimeError(f"Failed to read attribute {self.__name}")
            return self.__result.quality
        raise self.__result

    def __is_connection_error(self):
        return (
            isinstance(self.__result, tango.ConnectionFailed)
            or "API_DeviceNotDefined" in str(self.__result)
        )

    @property
    def not_readable(self) -> bool:
        """
        Returns whether the attribute could not be read, if the
        device was otherwise reachable. Otherwise, raises.
        """
        if isinstance(self.__result, tango.DeviceAttribute):
            return self.__result.has_failed
        if not self.__is_connection_error():
            return True
        raise self.__result

    @property
    def not_accessible(self) -> bool:
        """
        Returns whether the device could be reached.
        TODO this seems confusing... is it really correct?
        """
        if isinstance(self.__result, tango.DeviceAttribute):
            if self.__result.has_failed:
                raise RuntimeError(f"Failed to read attribute {self.__name}")
            else:
                return False
        if self.__is_connection_error():
            return True
        raise self.__result

    @property
    def exception(self) -> bool:
        """
        Returns whether an exception was raised. Doesn't raise exceptions,
        so it should never cause the alarm to fail.
        """
        return isinstance(self.__result, tango.DevFailed) or self.__result.has_failed

    def __repr__(self):
        return f"AttrData({self.__name}, {self.safe_value})"


class AlarmEvaluator:
    """
    Handles parsing and evaluation of alarms.

    Assumptions:
    - Variables are added before any formulas using them
    - All formulas are added before any formulas are evaluated

    These are mainly due to caching and might be lifted if necessary.
    """

    # Restricting what is available to formulas, for safety reasons
    # This is probably not 100% safe against an evil attacker, but should be
    # enough to prevent bad mistakes
    GLOBALS = {
        # Allowing only a subset of builtins
        "__builtins__": {
            "int": int,
            "float": float,
            "bool": bool,
            "abs": abs,
            "round": round,
            "all": all,
            "any": any,
            "zip": zip,
            "range": range,
        },

        # Some useful standard library stuff
        **math.__dict__,
        "datetime": datetime,
        "timedelta": timedelta,
        "time": time,
        "random": random,
        "randint": randint,

        # Tango conveniences
        "ATTR_VALID": tango._tango.AttrQuality.ATTR_VALID,
        "ATTR_ALARM": tango._tango.AttrQuality.ATTR_ALARM,
        "ATTR_INVALID": tango._tango.AttrQuality.ATTR_INVALID,
        "ATTR_CHANGING": tango._tango.AttrQuality.ATTR_CHANGING,
        "ATTR_WARNING": tango._tango.AttrQuality.ATTR_WARNING,
        "ALARM": tango.DevState.ALARM,
        "EXTRACT": tango.DevState.EXTRACT,
        "INSERT": tango.DevState.INSERT,
        "ON": tango.DevState.ON,
        "STANDBY": tango.DevState.STANDBY,
        "CLOSE": tango.DevState.CLOSE,
        "FAULT": tango.DevState.FAULT,
        "MOVING": tango.DevState.MOVING,
        "OPEN": tango.DevState.OPEN,
        "UNKNOWN": tango.DevState.UNKNOWN,
        "DISABLE": tango.DevState.DISABLE,
        "INIT": tango.DevState.INIT,
        "OFF": tango.DevState.OFF,
        "RUNNING": tango.DevState.RUNNING,
    }

    ATTRIBUTE_SUFFIXES = ".value", ".quality", ".not_readable", ".not_accessible", ".exception"

    def __init__(self, logger=None, get_device_proxy=None, timeout: float = 1):
        self.logger = logger or logging.getLogger(__name__)
        self.timeout = timeout
        self._get_device_proxy = get_device_proxy or DeviceProxy

        self.formulas: MutableMapping[str, CodeType] = {}
        self.variables: MutableMapping[str, str] = {}
        self.timers: MutableMapping[str, Timer] = defaultdict(Timer)
        self._device_proxies: MutableMapping[str, DeviceProxy] = {}
        self._attr_ids = count()
        self._attr_placeholders = CaselessDict()
        self._formula_attributes: MutableMapping[str, list[str]] = defaultdict(list)
        self._formula_variables: MutableMapping[str, list[str]] = defaultdict(list)
        self._variable_attributes: MutableMapping[str, list[str]] = defaultdict(list)
        self.logger.info("Created new evaluator")

    def _replace_formula_attribute(
            self, formula_name: str, match: re.Match, variable=False):
        attr_name = match.group(1).lower()
        i = next(self._attr_ids)
        if attr_name in self._attr_placeholders:
            # This attribute already has a placeholder, re-use
            placeholder = self._attr_placeholders[attr_name]
        else:
            # New placeholder
            placeholder = f"__achtung_attr_{i}__"
            self._attr_placeholders[attr_name] = placeholder
        if variable:
            self._variable_attributes[formula_name].append(attr_name)
        else:
            self._formula_attributes[formula_name].append(attr_name)
        suffix = match.group(3) or ".value"  # Use read value by default
        if suffix not in self.ATTRIBUTE_SUFFIXES:
            # E.g. sys/tg_test/1/ampli.quality where .quality is the suffix
            # TODO I think '.' is allowed in tango attribute names, though it seems
            # like a bad idea for many reasons. This will break in that case.
            # This convention with suffixes is a PyAlarm invention I think, we
            # could support some other syntax.
            raise FormulaError(
                f"Bad suffix; should be one of {','.join(self.ATTRIBUTE_SUFFIXES)}")

        return f"{placeholder}{suffix}"

    def add_variable(self, name_and_formula: str):
        """
        Add a single variable, given as <name>:<value>"

        Variables may contain any syntax that formulas support, since
        they will simply be inserted into the formulas using them.

        Note: you must add variables *before* adding formulas using them.
        Otherwise the formulas will fail at evaluation time.
        """
        try:
            name, formula = name_and_formula.split(":", 1)
        except IndexError:
            raise FormulaError("Variables must be specified as <name>:<formula>")
        if name in self.GLOBALS:
            raise FormulaError("Bad variable name; collides with builtin")

        # Substitute any attribute names with placeholders. See
        # add_formula for more details.
        formula_subbed = re.sub(
            ATTRIBUTE_RE,
            partial(self._replace_formula_attribute, name, variable=True),
            formula)
        # # Skipping the "sanity check" for now. It breaks for some legitimate
        # # use cases, e.g. putting a device name in a variable. The value
        # # is limited since we check the final formulas anyway.
        # try:
        #     # Sanity check the formula syntax
        #     compile(formula_subbed, "<string>", "eval")
        # except (SyntaxError, ValueError) as e:
        #     raise FormulaError(f"Invalid variable formula: {e}") from e
        self.variables[name] = formula_subbed
        self.logger.debug("Added variable %r", name_and_formula)

    @cache
    def _get_variable_regex(self):
        # This regex should match any variable name, but only if
        # it is written separately (surrounded by "non word" chars)
        return r"\b(" + "|".join(
            fr"{variable}"
            for variable in self.variables
        ) + r")\b"

    def _replace_formula_variable(self, formula_name: str, match: re.Match):
        var_name = match.group(1).lower()
        formula = self.variables[var_name]
        variable_attributes = self._variable_attributes.get(var_name)
        if variable_attributes:
            # Add the variable's attributes to the formula, so that they get read
            # before the formula is evaluated.
            self._formula_attributes[formula_name].extend(variable_attributes)
        return formula

    def add_formula(self, name_and_formula: str):
        """
        Add a single formula, given as <name>:<formula>

        Since attribute names (e.g. 'sys/tg_test/1/ampli' can be given in formulas,
        the raw formulas aren't python code. Therefore we replace them with
        placeholder variables like '__achtung_attr_7__'. At evaluation time
        these will be AttrData instances with the latest read data.

        Variables are substituted with whatever they contain before compilation.
        Since variables can also be arbitrary expressions, this is a simple way
        of making them work transparently.

        This is a bit of a "hack". The main benefit is that we avoid
        complexity by re-using the python parser and executor. But a more
        sophisticated way than simple regex replacement would be nice...
        """

        start = perf_counter()
        name, formula = name_and_formula.split(":", 1)
        # Insert attribute placeholders. This also prevents variables from
        # accidentally replacing parts of an attribute name.
        # TODO this syntax is too ambiguous. We should consider using something
        # easier to parse, e.g. $variable or {sys/tg_test/1/ampli}. At least
        # optionally?
        formula_subbed = re.sub(ATTRIBUTE_RE,
                                partial(self._replace_formula_attribute, name),
                                formula)
        if self.variables:
            # Replace any variables that point to attributes
            # with the attribute name, to be handled normally
            # TODO this is quite crude string replacements. Most likely
            # there are corner cases... Look into using AST instead?
            formula_variable_subbed = re.sub(self._get_variable_regex(),
                                             partial(self._replace_formula_variable, name),
                                             formula_subbed)
            # Replace attributes again; a variable substitution could have completed
            # an attribute name. E.g. by containing a device name.
            formula_subbed = re.sub(ATTRIBUTE_RE,
                                    partial(self._replace_formula_attribute, name),
                                    formula_variable_subbed)

        self.logger.debug("Subbed formula: %r", formula_subbed)
        try:
            code = compile(formula_subbed, "<string>", "eval")
        except (SyntaxError, ValueError) as e:
            self.logger.error(f"Failed to parse formula {name}: {e}")
            error = str(e)
            raise FormulaError(error) from e
        self.logger.debug("Formula parse '{}' took {}s".format(formula, perf_counter() - start))
        self.formulas[name] = code
        state_attrs = re.findall(STATE_ATTRIBUTE_RE, formula)
        return state_attrs

    async def _read_attributes(self, device: str, attrs: list[str]) -> tuple[str, list[str], tango.DeviceAttribute | Exception]:
        """Read any number of attributes on one device"""
        t0 = perf_counter()

        # Get a proxy
        if device not in self._device_proxies:
            try:
                proxy = await self._get_device_proxy(device)
                proxy.set_timeout_millis(int(self.timeout * 1000))
                self._device_proxies[device] = proxy
            except tango.DevFailed as e:
                self.logger.error(f"Failed to create proxy to {device}: {e.args[-1].desc}")
                self._device_proxies[device] = e
                return device, attrs, e
        else:
            maybe_proxy = self._device_proxies[device]
            if isinstance(maybe_proxy, tango.DevFailed):
                return device, attrs, maybe_proxy
            proxy = maybe_proxy

        # Read attribute values
        try:
            # TODO seems the tango client timeout does not work here, why?
            results = await asyncio.wait_for(
                proxy.read_attributes(attrs, extract_as=tango.ExtractAs.List),
                timeout=self.timeout * 1.1
            )
            dt = perf_counter() - t0
            self.timers[device].add(dt)
            return device, attrs, results
        except tango.DevFailed as e:
            self.logger.error(f"Failed to read attributes on {device}: {e.args[0].desc}")
            return device, attrs, e
        except (TimeoutError, asyncio.TimeoutError) as e:
            # Until Python 3.11, asyncio.TimeoutError was raised.
            # Remove later when support is dropped.
            self.logger.warn("Attribute read on %s exceeded timeout!", device)
            return device, attrs, e
        else:
            self.logger.debug(f"Successfully read {len(attrs)} on {device}")

    async def _batch_read(self, attribute_names: Sequence[str]) -> Sequence[tango.DeviceAttribute]:
        """
        Read the given attributes, by making one read call per device.
        Returns the results in the same order as the argument.
        """
        self.logger.debug("_batch_read(%r)", attribute_names)
        device_attr = (name.rsplit("/", 1) for name in attribute_names)
        by_device = groupby(device_attr, key=itemgetter(0))
        reads = (
            self._read_attributes(device, [attr for _, attr in group])
            for device, group in by_device
        )
        results = await asyncio.gather(*reads, return_exceptions=True)
        results_by_name = {}
        for device, attrs, result in results:
            if isinstance(result, Exception):
                for attr in attrs:
                    name = f"{device}/{attr}"
                    results_by_name[name] = AttrData(name, result)
            else:
                for attr, data in zip(attrs, result):
                    name = f"{device}/{attr}"
                    results_by_name[name] = AttrData(name, data)
        return [results_by_name[name] for name in attribute_names]

    async def evaluate(self, name: str):
        """
        Evaluate a single formula by name, returning the result.
        """
        # Read attributes used by the formula
        attr_names = self._formula_attributes.get(name, [])
        data = await self._batch_read(attr_names)

        # Evaluate
        code = self.formulas[name]
        placeholder_values = {
            self._attr_placeholders[name]: result
            for name, result in zip(attr_names, data)
        }
        # Note: we could put the locals in a third eval argument and save some
        # work merging the dicts. However this doesn't work as expected for all
        # expressions in Python <3.12. See PEP 709.
        globals_ = {**self.GLOBALS, **placeholder_values}
        result = eval(code, globals_)

        # Also return the values of each attribute, if available
        attr_values = dict(zip(attr_names, [d.safe_value for d in data]))
        return result, attr_values

    def _try_eval(self, name, code, globals_, attr_values) -> tuple[str, dict[str, object]] | Exception:
        """Evaluate and return result or exception"""
        try:
            return (
                eval(code, globals_),
                {
                    attr_name: attr_values.get(attr_name).safe_value
                    for attr_name in self._formula_attributes[name]
                }
            )
        except Exception as e:
            self.logger.error(f"Error evaluating {name}: {e}")
            return e

    @lru_cache(1)
    def _get_attribute_names(self, names: tuple[str]):
        # This is just a minor optimization, to avoid having to sort the same
        # list over and over again. So we cache the latest value. The list of
        # formulas to evaluate should rarely change in practice.
        return sorted(set().union(
            *(
                self._formula_attributes.get(name, [])
                for name in names
            )
        ))

    async def evaluate_many(self, names: Sequence[str]):
        """
        Evaluate any number of alarms by name. Returns results in the same order.
        """
        # Get all attributes involved in any of the formulas
        # Read all those attributes
        attr_names = self._get_attribute_names(tuple(names))
        data = await self._batch_read(attr_names)

        # Evaluate formulas
        attr_values = dict(zip(attr_names, data))
        placeholder_values = {
            self._attr_placeholders[name]: attr_data
            for name, attr_data in attr_values.items()
        }
        globals_ = {**self.GLOBALS, **placeholder_values}
        return [
            self._try_eval(name, self.formulas[name], globals_, attr_values)
            for name in names
        ]


async def main():
    evaluator = AlarmEvaluator(logger=logging.getLogger())
    names = []
    evaluator.add_variable("foo:1")
    evaluator.add_variable("bar:[1,2,3]")
    evaluator.add_variable("baz:sys/tg_test/1/ampli")
    for i, formula in enumerate(sys.argv[1:]):
        print(evaluator.add_formula(f"test{i}:{formula}"))
        names.append(f"test{i}")
    for name in names:
        print(await evaluator.evaluate(name))
    print(await evaluator.evaluate_many(names))


if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.DEBUG)

    asyncio.run(main())
