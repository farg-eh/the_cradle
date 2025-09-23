import pygame
import sys
from .state import State
from src.utils import import_font
from src.ui import UiElement, Group, Panel, ScrollablePanel, HList, Button, Text, CheckBox, Slider
from src.mouse_manager import MouseManager
from src.ui import mimlize, CLASSES

class TestYard(State):
    def __init__(self, core):
        super().__init__(core, 'testyard')
        self.mouse = MouseManager() 
        self.root = Group(size=self.screen.get_size(), name='root')
        self.root.show_border=True

        self.root.add_child(Text(text="Hello World!", color='yellow', font_size='big', pos=(230, 0)))


    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                self.switch_state('menu')
           

        self.mouse.get_events(event)

    def update(self, dt):
        self.root.update(dt, self.mouse)
        self.mouse.update()

      
    def close_game(self, mouse=None):
        pygame.quit()
        sys.exit()

    def draw(self):   
        self.screen.fill("#6C455F")
        self.root.draw(self.screen)


class DebugPanel(ScrollablePanel):
    def __init__(self, pos=(0, 0), size=(110, 110), name='', parent=None, 
                 clickable=True, hoverable=True, scrollable=False, padding=(0, 0), margin=(0, 0),
                 show_border=False, hidden=False, border_width=1, border_color='white', bg_color='orange' ):
        super().__init__( pos=pos, size=size, name=name, parent=parent, 
                 clickable=clickable, hoverable=hoverable, scrollable=scrollable, padding=padding, margin=margin,
                 show_border=show_border, hidden=hidden, border_width=border_width, border_color=border_color, bg_color=bg_color )


