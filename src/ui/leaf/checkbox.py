import pygame
from src.ui import UiElement


# TODO: handle the text attribute or remove it from the miml code in the langauge json
class CheckBox(UiElement):
    def __init__(self, pos=(0, 0), size=(15, 15), name="", text="", color='white', margin=(0, 0), padding=(0, 0)):
        super().__init__(pos, size, clickable=True, name=name, margin=margin, padding=padding)
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

        print('\033[91mClick!\033[0m')

    def draw(self, surf):
        super().draw(surf)
        if self.value:
            pygame.draw.rect(surf, self.color, self.rect, border_radius=3)
        else:
            pygame.draw.rect(surf, self.color, self.rect, 2, 3)
