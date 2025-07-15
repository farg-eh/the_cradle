from abc import ABC, abstractmethod


class State(ABC):  # defining State as abstract class
    def __init__(self, core,  state_name):
        self.state_name = state_name
        self.core = core
        self.switch_state = core.switch_state
        self.screen = core.screen
        self.display = core.display

    @abstractmethod
    def handle_input(self, event):
        pass

    @abstractmethod
    def update(self, dt):
        pass

    @abstractmethod
    def draw(self):
        pass
