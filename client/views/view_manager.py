from __future__ import annotations
from typing import Callable
from client.views.base_view import BaseView
from client.views.view_action import ViewAction


class ViewManager:
    """
    Owns the active view, the view registry, and context factories.

    Usage:
        vm = ViewManager()
        vm.register(ViewAction.GOTO_HOME, home_view, lambda: {"ws_client": ws, ...})
        vm.switch(ViewAction.GOTO_HOME)

        # in the app loop:
        action = vm.current.handle_click(x, y)
        if action:
            vm.switch(action)
        vm.current.render(canvas)
    """

    def __init__(self):
        self._views:    dict[ViewAction, BaseView]            = {}
        self._contexts: dict[ViewAction, Callable[[], dict]] = {}
        self._current:  BaseView | None = None

    def register(self, action: ViewAction, view: BaseView,
                 context_factory: Callable[[], dict] = None) -> None:
        self._views[action]    = view
        self._contexts[action] = context_factory or (lambda: {})

    @property
    def current(self) -> BaseView | None:
        return self._current

    def init(self, view: BaseView, context: dict = None) -> None:
        """Bootstrap the first view before any action-driven transition."""
        self._current = view
        self._current.on_enter(context or {})

    def switch(self, action: ViewAction, extra: dict = None) -> None:
        if action == ViewAction.QUIT:
            if self._current:
                self._current.on_exit()
            self._current = None
            return

        view = self._views.get(action)
        if view is None:
            raise KeyError(f"No view registered for {action}")

        if self._current is not None:
            self._current.on_exit()

        ctx = self._contexts[action]()
        if extra:
            ctx.update(extra)

        self._current = view
        self._current.on_enter(ctx)

    def handle_server_message(self, msg) -> ViewAction | None:
        if self._current is None:
            return None
        return self._current.handle_server_message(msg)
