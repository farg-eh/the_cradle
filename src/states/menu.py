import pygame
import sys
from .state import State

class Menu(State):
    def __init__(self, core):
        super().__init__(core, 'menu')
        
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                self.switch_state('game')
            if event.key == pygame.K_2:
                self.switch_state('editor')

    def update(self, dt):
        pass

    def draw(self):
       self.screen.fill("#3C7275")
