from abc import ABC, abstractmethod


class Command(ABC):

    @classmethod
    @abstractmethod
    def from_parameters(cls, parts: list):
        pass

    @abstractmethod
    def execute(self, game, controller=None):
        pass