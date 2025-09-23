import pygame
from src.ui import UiElement


class CheckBox(UiElement):
    def __init__(self, pos=(0, 0), size=(15, 15), name="", text="", color='white'):
        super().__init__(pos, size, clickable=True, name=name)
        self.value = False
        self.color = color
        self.func = None

#    def __bool__(self):
#        return self.value

    def on_click(self, mouse):
        super().on_click(mouse)
        self.value = not self.value
        if self.func:
            self.func(self.value)

    def draw(self, surf):
        super().draw(surf)
        if self.value:
            pygame.draw.rect(surf, self.color, self.rect, border_radius=3)
        else:
            pygame.draw.rect(surf, self.color, self.rect, 2, 3)
