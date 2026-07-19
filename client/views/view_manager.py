from __future__ import annotations
from client.views.base_view import BaseView
from client.views.view_action import ViewAction


class ViewManager:
    """
    Owns the currently active view and the registry of all views.

    Usage:
        vm = ViewManager()
        vm.register(ViewAction.GOTO_HOME, HomeView())
        vm.switch(ViewAction.GOTO_HOME)

        # in the app loop:
        action = vm.current.handle_click(x, y)
        if action:
            vm.switch(action, context={...})
        vm.current.render(canvas)
    """

    def __init__(self):
        self._views: dict[ViewAction, BaseView] = {}
        self._current: BaseView | None = None

    def register(self, action: ViewAction, view: BaseView) -> None:
        self._views[action] = view

    @property
    def current(self) -> BaseView | None:
        return self._current

    def switch(self, action: ViewAction, context: dict = None) -> None:
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

        self._current = view
        self._current.on_enter(context or {})

    def handle_server_message(self, msg) -> None:
        if self._current is None:
            return
        action = self._current.handle_server_message(msg)
        if action:
            self.switch(action)
