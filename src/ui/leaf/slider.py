import pygame
from src.ui import UiElement
from src.utils import Pos
class Slider(UiElement):
    def __init__(self, pos=(0, 0), size=(36, 10), clickable=True, name="Slider", margin=(0, 0), padding=(0, 0)):
        super().__init__(pos, size, clickable=clickable, name=name, padding=padding, margin=margin)
        self.hoverable = True
        self.value = 0.5
        self.func = None
        self.being_changed = False
        self.max_v = 1.0
        self.min_v = 0.0

    def draw(self, surf):
        pygame.draw.rect(surf, 'white', self.rect, border_radius=3)
        pygame.draw.line(surf, "#00000000", self.rect.midleft, (self.rect.right -1, self.rect.centery), 3)
        pygame.draw.rect(surf, 'white', self.rect, 3, 3)
        pygame.draw.circle(surf, '#00000000', (self.rect.left + self.rect.width * self.value, self.rect.centery), 4)

    def on_click(self, mouse=None):
        super().on_click(mouse)
        print('clicked')

    def on_hover(self, mouse=None):
        if not mouse: return
        if self.mouse_inside and mouse.l_down:
            self.being_changed = True
            pos_x = mouse.pos[0]
            if pos_x < self.rect.left:
                pos_x = self.rect.left
            elif pos_x > self.rect.right:
                pos_x = self.rect.right
            self.value = abs(self.rect.left - pos_x) / self.rect.width
            self.value = max(min(self.value, self.max_v), self.min_v)  # clamp the value so its never more than max_v or less than min_v
            if self.func:
                self.func(self.value, mouse)
            print(f"somthing {self.value}")
    #    if self.mouse_inside and mouse.l_up_once and self.being_changed:
    #        print(f'\033[91m something -{self.value}\033[0m')
    #        if self.func:
    #            self.func(self.value, mouse)
