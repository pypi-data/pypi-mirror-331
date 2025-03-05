import asyncio
from unittest.mock import Mock

import pytest
from tango import AttrQuality, DevFailed, DevError, ConnectionFailed, DeviceAttribute
from tango.utils import CaselessDict

from achtung.evaluator2 import AlarmEvaluator, FormulaError


def make_devfailed(desc, exc_class=DevFailed):
    err = DevError()
    err.desc = desc
    return exc_class(err)


class _FakeDeviceProxy:
    "Just a completely fake device proxy"

    VALUES = CaselessDict({
        "sys/tg_test/2/ampli": (0, AttrQuality.ATTR_VALID, None, None),
        "sys/tg_test/2/boolean_scalar": (True, AttrQuality.ATTR_VALID, None, None),
        "sys/tg_test/2/string_scalar": ("Default string", AttrQuality.ATTR_VALID, None, None),
        "tango://a.b.c.d.e.f.g:10000/sys/tg_test/2/ampli": (0, AttrQuality.ATTR_VALID, None, None),
        "some/broken/device/attr": (None, None, None, make_devfailed("Oh no!")),
        "some/disconnected/device/attr": (None, None, make_devfailed("Oh no!", ConnectionFailed), None),
        "some/not/defined/device": (None, None, make_devfailed("blah API_DeviceNotDefined blah"), None),
        "s-w4/ctl/plc-21/w4_150nfa30dt001_am": (0, AttrQuality.ATTR_VALID, None, None),
        "r1-1/mag/crdip-01/CyclingState": (0, AttrQuality.ATTR_VALID, None, None),
        "r3-3/MAG/CRDIP-01/CyclingState": (0, AttrQuality.ATTR_VALID, None, None),
        "r3-a102011cab20/mag/psdi-01/Current": (0, AttrQuality.ATTR_VALID, None, None),
        "r3-a102011cab14/mag/psdf-01/Current": (0, AttrQuality.ATTR_VALID, None, None),
        "r1-d100101cab20/mag/psdj-01/Current": (0, AttrQuality.ATTR_VALID, None, None),
        "r1-d100101cab16/mag/psdh-01/Current": (0, AttrQuality.ATTR_VALID, None, None),
        "r1-d100101cab17/mag/psde": (0, AttrQuality.ATTR_VALID, None, None),
        "I-K08/RF/MOD-01/STATUS": ('Currently: Hv interlock 2', AttrQuality.ATTR_VALID, None, None),
    })

    def __init__(self, device):
        self.device = device
        self.calls = []

    async def read_attributes(self, attrs, extract_as=None):
        results = []
        for attr in attrs:
            mock = Mock(spec=DeviceAttribute)
            assert isinstance(mock, DeviceAttribute)
            full_name = f"{self.device}/{attr}"
            mock.value, mock.quality, raises_exc, attr_exc = self.VALUES[full_name]
            if raises_exc:
                raise raises_exc
            mock.has_failed = bool(attr_exc)
            results.append(mock)
        self.calls.append(attrs)
        return results

    def set_timeout_millis(self, timeout):
        pass


async def FakeDeviceProxy(dev):
    return _FakeDeviceProxy(dev)


EVALUATE_FORMULAS = [

    # These are used for parametrizing tests below. Each line is a
    # formula and the expected result after evaluation.

    # Basic math
    ("25", 25),
    ("abs(-17.5)", 17.5),
    ("(17.5-7.5)", 10),
    ("round(3.14)-2.3", 0.7),
    ("(1.0-2.0)*2", -2.0),
    ("-2", -2),
    ("1-2", -1),
    ("sin(pi) < 0.01", True),
    ("2**2 == 4", True),
    ("exp(1) > 2 and exp(1) < 3", True),
    ("10E-5 > -10e-4", True),
    ("10**5 > 10**-6", True),
    ("7.92e-4 > 6.48e-4", True),

    # Other types
    ("sys/tg_test/2/string_scalar == 'Default string'", True),
    ("'fault' in sys/tg_test/2/string_scalar", True),
    ('"flepp" in sys/tg_test/2/string_scalar', False),

    # Logic
    ("True or False", True),
    ("True and False", False),
    ("not True and False", False),
    ("not (True and False)", True),
    ("(not True) and False", False),
    ("not False", True),
    ("True and False and True and False", False),

    # Tango attributes
    ("sys/tg_test/2/ampli == 3", False),
    ("sys/tg_test/2/ampli < 5", True),
    ("sys/tg_test/2/ampli >= 5", False),
    ("sys/tg_test/2/ampli == sys/tg_test/2/ampli", True),
    ("sys/tg_test/2/ampli != sys/tg_test/2/ampli", False),
    ("not sys/tg_test/2/boolean_scalar", False),
    ("sys/tg_test/2/ampli == 3 and sys/tg_test/2/boolean_scalar == False", False),
    ("sys/tg_test/2/ampli/2 == 0", True),
    ("tango://a.b.c.d.e.f.g:10000/sys/tg_test/2/ampli/2 == 0", True),

    ("sys/tg_test/2/boolean_scalar.quality == ATTR_VALID", True),

    ("some/disconnected/device/attr.not_accessible", True),
    ("some/not/defined/device.not_accessible", True),
    ("some/broken/device/attr.not_readable", True),
    ("some/disconnected/device/attr.exception", True),
    ("some/not/defined/device.exception", True),
    ("some/broken/device/attr.exception", True),
    ("sys/tg_test/2/ampli.exception == False", True),
    ("sys/tg_test/2/ampli.not_readable", False),
    ("sys/tg_test/2/ampli.not_accessible", False),

    # Variables
    ("apa==4", True),
    ("sys/tg_test/2/ampli/2 + apa == 4", True),
    ("apa - sys/tg_test/2/ampli == 4", True),
    ("xyz == 3", True),
    ("sys/tg_test/2/ampli < xyz", True),
    ("some_device/ampli > 4", False),
    ("some_attribute > 4", False),

    # Complex
    ("1 + 2 + 3 > 5", True),
    ("sys/tg_test/2/ampli<2.0 and bepa2<0 and apa < 6", True),
    ("((sys/tg_test/2/ampli<2.0 and bepa2<0) or (apa < 6 and False))", True),
    ("((s-w4/ctl/plc-21/w4_150nfa30dt001_am<21.7 and (not r1-1/mag/crdip-01/CyclingState and not r3-3/MAG/CRDIP-01/CyclingState) and ((r3-a102011cab20/mag/psdi-01/Current>600 and r3-a102011cab14/mag/psdf-01/Current>330) or (r1-d100101cab20/mag/psdj-01/Current>600 and r1-d100101cab16/mag/psdh-01/Current>350 and r1-d100101cab17/mag/psde>280))) or s-w4/ctl/plc-21/w4_150nfa30dt001_am<21.2)", True),
    ("all(True for _ in range(4))", True),
    ("arr[3] == 4", True),
    ("arr[2:4] == [3, 4]", True),
    ("any([x in I-K08/RF/MOD-01/STATUS for x in ['Hv interlock 2', 'State: Standby']])", True),

    # Weird
    ("datetime(2014, 10, 10, 2, 12, 14) - datetime(2014, 10, 10, 1, 12, 14) == timedelta(hours=1)", True),
    ("3 <= randint(3, 5) <= 5", True),
    ("time() > 0", True),
    ("'a' or 'b'", 'a'),
    ("'' or 'b'", 'b'),

    # PyAlarm compatibility - not implemented in new evaluator
    # ("ce_PA == False", True),
    # ("ce_PA == false", True),
    # ("ce_PA == FALSE", True),
    # ("ce_PA != True", True),
    # ("ce_PA != true", True),
    # ("ce_PA != TRUE", True),
    # ("2^2 == 4", True),
    # ("!True", False)
]

VARIABLES = {
    "apa": "4",
    "bepa2": "-10",
    "ce_PA": "False",
    "xyz": "1 + 2",  # Variables are also formulas
    "arr": "[1, 2, 3, 4, 5]",
    "some_device": "sys/tg_test/2",
    "some_attribute": "sys/tg_test/2/ampli",
}


@pytest.mark.parametrize("formula,expected", EVALUATE_FORMULAS)
@pytest.mark.asyncio
async def test_evaluate_formula(formula, expected):
    "Evaluate each test formula separately, and check their result"
    evaluator = AlarmEvaluator(get_device_proxy=FakeDeviceProxy)
    name = "test"
    for varname, varval in VARIABLES.items():
        evaluator.add_variable(f"{varname}:{varval}")
    evaluator.add_formula(f"{name}:{formula}")

    result, sub_results = await evaluator.evaluate(name)

    assert expected == pytest.approx(result), \
        f"Formula '{formula}' gave unexpected result {result}; expected {expected}."


@pytest.mark.asyncio
async def test_evaluate_many_formulas():
    "Evaluate all the test formulas in one call and check results"

    evaluator = AlarmEvaluator(get_device_proxy=FakeDeviceProxy)
    for varname, varval in VARIABLES.items():
        evaluator.add_variable(f"{varname}:{varval}")
    names = []
    for i, (formula, _) in enumerate(EVALUATE_FORMULAS):
        name = f"formula{i}"
        evaluator.add_formula(f"{name}:{formula}")
        names.append(name)

    results = await evaluator.evaluate_many(names)

    for (formula, expected), result in zip(EVALUATE_FORMULAS, results):
        value, attrs = result
        assert expected == pytest.approx(value), \
            f"Formula '{formula}' gave unexpected result {result}; expected {expected}."
    for device, fake_proxy in evaluator._device_proxies.items():
        # All attributes read in one single call, if any
        assert len(fake_proxy.calls) <= 1, f"Proxy {device} used too many times!"


@pytest.mark.asyncio
async def test_dangerous_formula():
    evaluator = AlarmEvaluator(get_device_proxy=FakeDeviceProxy)
    evaluator.add_formula("test:open('/some/secret/file.txt').read()")
    with pytest.raises(NameError) as ei:
        await evaluator.evaluate("test")
    assert "'open' is not defined" in str(ei.value)


@pytest.mark.asyncio
async def test_evaluate_nonexistent_device():

    error_desc = "I am an error!"

    async def raise_devfailed(_):
        raise make_devfailed(error_desc)

    evaluator = AlarmEvaluator(get_device_proxy=raise_devfailed)
    name = "test"

    evaluator.add_formula(f"{name}:{'some/nonexistent/device/attr == 118'}")
    with pytest.raises(DevFailed) as ei:
        await evaluator.evaluate(name)
    assert ei.value.args[0].desc == error_desc


@pytest.mark.asyncio
async def test_evaluate_broken_attribute():
    evaluator = AlarmEvaluator(get_device_proxy=FakeDeviceProxy)
    name = "test"

    evaluator.add_formula(f"{name}:some/broken/device/attr == 7")
    with pytest.raises(RuntimeError):
        await evaluator.evaluate(name)


@pytest.mark.asyncio
async def test_evaluate_bad_boolean():
    evaluator = AlarmEvaluator(get_device_proxy=FakeDeviceProxy)
    name = "test"

    evaluator.add_formula(f"{name}:sys/tg_test/2/ampli == true")
    with pytest.raises(NameError):
        await evaluator.evaluate(name)


@pytest.mark.asyncio
async def test_evaluate_bad_suffix():
    evaluator = AlarmEvaluator(get_device_proxy=FakeDeviceProxy)
    name = "test"

    with pytest.raises(FormulaError) as e:
        evaluator.add_formula(f"{name}:some/broken/device/attr.badbadbad == 67")
    assert "Bad suffix" in str(e.value)


@pytest.mark.asyncio
async def test_evaluate_broken_attribute_not_readable():
    evaluator = AlarmEvaluator(get_device_proxy=FakeDeviceProxy)
    name = "test"
    evaluator.add_formula(f"{name}:{'some/broken/device/attr.not_readable'}")
    assert await evaluator.evaluate(name)


@pytest.mark.asyncio
async def test_evaluate_disconnected_attribute_not_readable():
    evaluator = AlarmEvaluator(get_device_proxy=FakeDeviceProxy)
    name = "test"

    # device is not accessible and .not_readable doesn't catch connection errors
    evaluator.add_formula(f"{name}:{'some/disconnected/device/attr.not_readable'}")
    with pytest.raises(DevFailed):
        await evaluator.evaluate(name)


@pytest.mark.asyncio
async def test_evaluate_disconnected_attribute_not_accessible():
    evaluator = AlarmEvaluator(get_device_proxy=FakeDeviceProxy)
    name = "test"

    evaluator.add_formula(f"{name}:{'some/disconnected/device/attr.not_accessible'}")
    assert await evaluator.evaluate(name)


@pytest.mark.asyncio
async def test_evaluate_broken_attribute_not_accessible():
    evaluator = AlarmEvaluator(get_device_proxy=FakeDeviceProxy)
    name = "test"

    # device has broken attribute and .not_accessible catches only connection related errors
    evaluator.add_formula(f"{name}:{'some/broken/device/attr.not_accessible'}")
    with pytest.raises(RuntimeError):
        await evaluator.evaluate(name)


# Commented out because we don't validate variables any more. Remove if this
# decision stays.
# @pytest.mark.asyncio
# async def test_add_variable_broken():
#     evaluator = AlarmEvaluator(get_device_proxy=FakeDeviceProxy)
#     name = "test"
#     formula = "dsad'232+p(()"  # Very bad syntax
#     with pytest.raises(FormulaError) as e:
#         evaluator.add_variable(f"{name}:{formula}")
#     assert "unterminated" in str(e)


@pytest.mark.asyncio
async def test_add_variable_attribute():
    evaluator = AlarmEvaluator(get_device_proxy=FakeDeviceProxy)
    name = "test"
    formula = "sys/tg_test/1/ampli"
    evaluator.add_variable(f"{name}:{formula}")


@pytest.mark.asyncio
async def test_add_variable_device():
    evaluator = AlarmEvaluator(get_device_proxy=FakeDeviceProxy)
    name = "test"
    formula = "sys/tg_test/1"
    evaluator.add_variable(f"{name}:{formula}")


@pytest.mark.asyncio
async def test_evaluate_missing_variable():
    evaluator = AlarmEvaluator(get_device_proxy=FakeDeviceProxy)
    name = "test"
    formula = "missing_var == 5"
    evaluator.add_formula(f"{name}:{formula}")
    with pytest.raises(NameError) as e:
        await evaluator.evaluate(name)
        assert "missing_var" in str(e)


@pytest.mark.asyncio
async def test_evaluate_many():
    evaluator = AlarmEvaluator(get_device_proxy=FakeDeviceProxy)
    names = ["test1", "test2", "test3", "test4"]
    formulas = [
        "56",
        "sys/tg_test/2/ampli == 4",
        "some/broken/device/attr == 7",
        "True",
    ]
    for name, formula in zip(names, formulas):
        evaluator.add_formula(f"{name}:{formula}")

    results = await evaluator.evaluate_many(names)

    assert results[0][0] == 56
    assert results[1][0] is False
    assert isinstance(results[2], RuntimeError)
    assert results[3][0] is True


@pytest.mark.asyncio
async def test_evaluate_many__nonexistent_device():

    error_desc = "I am an error!"

    called_times = 0

    async def raise_devfailed(_):
        nonlocal called_times
        called_times += 1
        raise make_devfailed(error_desc)

    evaluator = AlarmEvaluator(get_device_proxy=raise_devfailed)

    evaluator.add_formula(f"test1:{'some/nonexistent/device/attr == 118'}")
    evaluator.add_formula(f"test2:{'some/nonexistent/device/attr == 118'}")
    results = await evaluator.evaluate_many(["test1", "test2"])
    assert isinstance(results[0], DevFailed)
    assert results[0].args[0].desc == error_desc
    assert isinstance(results[1], DevFailed)
    assert results[1].args[0].desc == error_desc

    assert called_times == 1


@pytest.mark.asyncio
async def test_get_device_proxy():
    device_name = "sys/tg_test/2"
    fake_proxy = _FakeDeviceProxy(device_name)
    delay = 0.1

    called_times = 0

    async def slow_get_proxy(_):
        "Fake proxy getter that is also quite slow"
        # Should get called only once; the caching returns the same proxy twice
        nonlocal called_times
        called_times += 1
        await asyncio.sleep(delay)
        return fake_proxy

    evaluator = AlarmEvaluator(get_device_proxy=slow_get_proxy)

    evaluator.add_formula(f"test1:{'sys/tg_test/2/ampli == 118'}")
    evaluator.add_formula(f"test2:{'sys/tg_test/2/boolean_scalar == True'}")

    results = await evaluator.evaluate_many(["test1", "test2"])

    # Evaluation succeeded
    assert not isinstance(results[0], DevFailed)
    assert not isinstance(results[1], DevFailed)

    # Both evaluations had to wait for the same proxy
    assert evaluator.timers["sys/tg_test/2"].total_time >= delay

    # Only one proxy used for both attributes
    assert called_times == 1
