from collections import defaultdict


class EventBus:
    def __init__(self):
        self._listeners = defaultdict(list)

    def subscribe(self, event_type, listener):
        self._listeners[event_type].append(listener)

    def unsubscribe(self, event_type, listener):
        self._listeners[event_type].remove(listener)

    def publish(self, event):
        for listener in list(self._listeners[type(event)]):
            listener(event)
