from abc import ABC, abstractmethod
from src.mouse_manager import MouseManager
from src.ui import Group
from src.utils import Timer
import pygame

class State(ABC):  # defining State as abstract class
    def __init__(self, core,  state_name):
        self.state_name = state_name
        self.core = core
        self.switch_state = core.switch_state
        self.screen = core.screen
        self.display = core.display
        self.mouse = MouseManager()
        self.root = Group(pos=(0, 0), size=self.screen.get_size())

        # delete and backspace things
        self.key_held = False
        self.keypress_timer = Timer(60) # adjust this for character deletion speed
        self.hold_del_key_timer = Timer(duration=400, func=lambda: setattr(self, 'key_held', True)) # how long to hold the backspace or the delete key to start deleting them fast 

    def _handle_del_bspce_keys(self):
        # handle the backspace and delete continous deletion
        self.keypress_timer.update()
        self.hold_del_key_timer.update()
        keys = pygame.key.get_pressed()
        if self.key_held and (keys[pygame.K_BACKSPACE] or keys[pygame.K_DELETE]) and not self.keypress_timer.active:
            self.root.handle_keyboard('\b')
            self.keypress_timer.activate()

    @abstractmethod
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            self.root.handle_keyboard(event.unicode)
            if event.key == pygame.K_BACKSPACE or event.key == pygame.K_DELETE:
                self.hold_del_key_timer.activate()
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_BACKSPACE or event.key == pygame.K_DELETE:
                self.key_held = False
                self.hold_del_key_timer.deactivate()

        self.mouse.get_events(event) # dont forget

    @abstractmethod
    def update(self, dt):
        self._handle_del_bspce_keys()
        self.root.update(dt, self.mouse) # dont forget updating the root group
        self.mouse.update() # dont forget this should be at the end

    def fixed_update(self, tick_dt):
        pass

    @abstractmethod
    def draw(self):
        self.root.draw(self.screen) # dont forget drawing the root group on the screen 
