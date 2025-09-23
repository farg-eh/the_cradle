from abc import ABC, abstractmethod
from src.mouse_manager import MouseManager
from src.ui import Group

class State(ABC):  # defining State as abstract class
    def __init__(self, core,  state_name):
        self.state_name = state_name
        self.core = core
        self.switch_state = core.switch_state
        self.screen = core.screen
        self.display = core.display
        self.mouse = MouseManager()
        self.root = Group(pos=(0, 0), size=self.screen.get_size())

    @abstractmethod
    def handle_input(self, event):
        self.mouse.get_events(event) # dont forget

    @abstractmethod
    def update(self, dt):
        self.root.update(dt, self.mouse) # dont forget updating the root group
        self.mouse.update() # dont forget this should be at the end

    @abstractmethod
    def draw(self):
        self.root.draw(self.screen) # dont forget drawing the root group on the screen 
