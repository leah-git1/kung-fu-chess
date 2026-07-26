"""
Tests for client/app_state.py and client/views/view_manager.py
"""
import sys, os
_ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.insert(0, _ROOT)
sys.path.insert(0, os.path.join(_ROOT, "client"))

import pytest
from unittest.mock import MagicMock, call
from client.app_state import AppState
from client.views.view_manager import ViewManager
from client.views.view_action import ViewAction
from client.views.base_view import BaseView
from shared.enums import Color


# ══ AppState ══════════════════════════════════════════════════════════════════

def test_app_state_stores_init_values():
    s = AppState("alice", "pw", False, 1400)
    assert s.player_name == "alice"
    assert s.password    == "pw"
    assert s.register    is False
    assert s.rating      == 1400


def test_app_state_defaults():
    s = AppState("x", "", False, 1200)
    assert s.white_name == "White"
    assert s.black_name == "Black"
    assert s.room_id    == ""


def test_app_state_color_default_is_white():
    s = AppState("x", "", False, 1200)
    assert s.color == Color.WHITE


def test_app_state_mutable():
    s = AppState("x", "", False, 1200)
    s.player_name = "bob"
    s.rating      = 1500
    assert s.player_name == "bob"
    assert s.rating      == 1500


# ══ ViewManager ═══════════════════════════════════════════════════════════════

def _view():
    v = MagicMock(spec=BaseView)
    return v


def test_view_manager_current_none_initially():
    vm = ViewManager()
    assert vm.current is None


def test_view_manager_init_sets_current():
    vm = ViewManager()
    v = _view()
    vm.init(v, {"x": 1})
    assert vm.current is v
    v.on_enter.assert_called_once_with({"x": 1})


def test_view_manager_init_empty_context():
    vm = ViewManager()
    v = _view()
    vm.init(v)
    v.on_enter.assert_called_once_with({})


def test_view_manager_switch_calls_on_exit_on_current():
    vm = ViewManager()
    old = _view()
    new = _view()
    vm.init(old)
    vm.register(ViewAction.GOTO_HOME, new)
    vm.switch(ViewAction.GOTO_HOME)
    old.on_exit.assert_called_once()


def test_view_manager_switch_calls_on_enter_on_new():
    vm = ViewManager()
    vm.init(_view())
    new = _view()
    vm.register(ViewAction.GOTO_HOME, new, lambda: {"k": "v"})
    vm.switch(ViewAction.GOTO_HOME)
    new.on_enter.assert_called_once_with({"k": "v"})


def test_view_manager_switch_extra_merged_into_context():
    vm = ViewManager()
    vm.init(_view())
    new = _view()
    vm.register(ViewAction.GOTO_HOME, new, lambda: {"base": 1})
    vm.switch(ViewAction.GOTO_HOME, extra={"extra": 2})
    new.on_enter.assert_called_once_with({"base": 1, "extra": 2})


def test_view_manager_switch_updates_current():
    vm = ViewManager()
    vm.init(_view())
    new = _view()
    vm.register(ViewAction.GOTO_HOME, new)
    vm.switch(ViewAction.GOTO_HOME)
    assert vm.current is new


def test_view_manager_switch_quit_sets_current_none():
    vm = ViewManager()
    vm.init(_view())
    vm.switch(ViewAction.QUIT)
    assert vm.current is None


def test_view_manager_switch_quit_calls_on_exit():
    vm = ViewManager()
    v = _view()
    vm.init(v)
    vm.switch(ViewAction.QUIT)
    v.on_exit.assert_called_once()


def test_view_manager_switch_unknown_action_raises():
    vm = ViewManager()
    vm.init(_view())
    with pytest.raises(KeyError):
        vm.switch(ViewAction.GOTO_GAME)


def test_view_manager_handle_server_message_delegates_to_current():
    vm = ViewManager()
    v = _view()
    v.handle_server_message.return_value = ViewAction.GOTO_HOME
    vm.init(v)
    result = vm.handle_server_message("some_msg")
    v.handle_server_message.assert_called_once_with("some_msg")
    assert result == ViewAction.GOTO_HOME


def test_view_manager_handle_server_message_none_when_no_current():
    vm = ViewManager()
    assert vm.handle_server_message("msg") is None


def test_view_manager_context_factory_called_at_switch_time():
    vm = ViewManager()
    vm.init(_view())
    counter = {"n": 0}
    def factory():
        counter["n"] += 1
        return {}
    vm.register(ViewAction.GOTO_HOME, _view(), factory)
    vm.switch(ViewAction.GOTO_HOME)
    vm.switch(ViewAction.GOTO_HOME)
    assert counter["n"] == 2
