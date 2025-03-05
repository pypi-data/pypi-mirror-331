import pytest
import tango

from achtung.alarm import Action, perform_actions

ARGS = [
    ("", None),
    ("0", 0),
    ("1", 1),
    ("true", True),
    ("false", False),
    ("1.2", 1.2),
    ("0.2", 0.2),
    ("-0.2", -0.2),
    ("1e5", 100000),
    ("1e-3", 0.001),
    ('"test"', "test"),
    ("[1, 2, 3]", [1, 2, 3]),
    ('["a"]', ["a"]),

    ("test", ValueError),
    ("test23113", ValueError),
    ("1,2", ValueError),
    (":::::", ValueError),
]


class FakeProxy:

    def __init__(self, *args, **kwargs):
        self.calls = []
        self.last_call = ()

    async def write(self, arg):
        call = "write", arg
        self.last_call = call
        self.calls.append(call)

    async def command_inout(self, command, arg=[]):
        call = ("command_inout", command, arg)
        self.last_call = call
        self.calls.append(call)


@pytest.mark.asyncio(loop_scope="session")
async def test_execute(monkeypatch):
    fake_device_proxy = FakeProxy()
    monkeypatch.setattr(tango.device_proxy, 'DeviceProxy', lambda *args, **kwargs: fake_device_proxy)
    fake_attr_proxy = FakeProxy()
    monkeypatch.setattr(tango.attribute_proxy, 'AttributeProxy', lambda *args, **kwargs: fake_attr_proxy)

    command_with_args = Action(Action.RUN_COMMAND, "sys/tg_test/11/switchstates", [0])
    command_without_args = Action(Action.RUN_COMMAND, "sys/tg_test/11/switchstates", [])
    write_attribute = Action(Action.WRITE_ATTRIBUTE, "sys/tg_test/11/double_scalar", 12.12)

    await command_with_args.execute()
    assert fake_device_proxy.last_call == ("command_inout", "switchstates", [0])

    await command_without_args.execute()
    assert fake_device_proxy.last_call == ("command_inout", "switchstates", [])

    await write_attribute.execute()
    assert fake_attr_proxy.last_call == ("write", 12.12)


@pytest.mark.parametrize("arg,expected", ARGS)
def test_attribute_from_string(arg, expected, monkeypatch):
    fake_device_proxy = FakeProxy()
    monkeypatch.setattr(tango.device_proxy, 'DeviceProxy', lambda *args, **kwargs: fake_device_proxy)
    s = "write_attribute: sys/tg_test/1/boolean_spectrum"
    if arg:
        s += (":" + arg)
    if expected != ValueError:
        action = Action.from_string(s)
        assert action.action_type == Action.WRITE_ATTRIBUTE
        assert action.target == "sys/tg_test/1/boolean_spectrum"
        assert action.args == expected
    else:
        with pytest.raises(ValueError):
            Action.from_string(s)


@pytest.mark.parametrize("arg,expected", ARGS)
def test_command_from_string(arg, expected, monkeypatch):
    fake_device_proxy = FakeProxy()
    monkeypatch.setattr(tango.device_proxy, 'DeviceProxy', lambda *args, **kwargs: fake_device_proxy)
    s = "run_command: sys/tg_test/1/switchstates"
    if arg:
        s += (":" + arg)
    if expected != ValueError:
        action = Action.from_string(s)
        assert action.action_type == Action.RUN_COMMAND
        assert action.target == "sys/tg_test/1/switchstates"
        assert action.args == expected
    else:
        with pytest.raises(ValueError, match=".*bad args.*"):
            Action.from_string(s)


def test_bad_format_type_from_string():
    s = "this is just a string"
    with pytest.raises(ValueError, match=".*bad format.*"):
        Action.from_string(s)


def test_bad_action_type_from_string():
    s = "run_bananas: sys/tg_test/1/switchstates: 56"
    with pytest.raises(ValueError, match=".*bad action.*"):
        Action.from_string(s)


def test_bad_target_from_string(monkeypatch):
    fake_device_proxy = FakeProxy()
    monkeypatch.setattr(tango.device_proxy, 'DeviceProxy', lambda *args, **kwargs: fake_device_proxy)
    s = "run_command:notatangodevice:56"
    with pytest.raises(ValueError, match=".*bad action target.*"):
        Action.from_string(s)


def test_identical_actions_look_the_same():
    action1 = Action(Action.RUN_COMMAND, "sys/tg_test/11/switchstates", [0])
    action2 = Action(Action.RUN_COMMAND, "sys/tg_test/11/switchstates", [0])
    assert action1 == action2
    assert len(set([action1, action2])) == 1


def test_different_actions_dont_look_the_same(monkeypatch):
    fake_device_proxy = FakeProxy()
    monkeypatch.setattr(tango.device_proxy, 'DeviceProxy', lambda *args, **kwargs: fake_device_proxy)
    action1 = Action(Action.RUN_COMMAND, "sys/tg_test/11/switchstates", [0])
    action2 = Action(Action.RUN_COMMAND, "sys/tg_test/12/switchstates", [0])
    assert action1 != action2
    assert len(set([action1, action2])) == 2


@pytest.mark.asyncio(loop_scope="session")
async def test_perform_actions_deduplicates(monkeypatch):
    fake_proxy = FakeProxy()
    monkeypatch.setattr(tango.device_proxy, 'DeviceProxy',
                        lambda *args, **kwargs: fake_proxy)
    # Two of three actions are identical, and should only be performed once
    action1 = Action(Action.RUN_COMMAND, "sys/tg_test/11/switchstates", [7])
    action2 = Action(Action.RUN_COMMAND, "sys/tg_test/12/bananas", [8])
    action3 = Action(Action.RUN_COMMAND, "sys/tg_test/11/switchstates", [7])
    result = await perform_actions(action1, action2, action3)
    assert not any(result)
    assert len(fake_proxy.calls) == 2
