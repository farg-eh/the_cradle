import pygame
from src.ui import UiElement
from . import Text

class Button(UiElement):
    def __init__(self, pos=(0,0),size=(34, 16), name='btn', text="btn", fore_color='white', back_color='black'):
        super().__init__(pos, size, clickable=True, name=name)
        self.hoverable = True
        self._c1 = fore_color
        self._c2 = back_color
        self.background_color = self._c2
        self.foreground_color = self._c1
        self.text_color = self._c2
        txt = text if text else name
        self.btn_text = Text(text=txt, color="white")
        self.btn_text.move_to_by_center(self.rect.center)
        self.show_border = False



    def on_hover(self, mouse=None):
        if self.mouse_inside:
            self.background_color = self._c1
            self.foreground_color = self._c1
            self.btn_text.change_color(self._c2)
        else: 
            self.background_color = self._c2
            self.foreground_color = self._c1
            self.btn_text.change_color(self._c1)


    def draw(self, surf):
        pygame.draw.rect(surf, self.background_color, self.rect, border_radius=8)
        pygame.draw.rect(surf, self.foreground_color, self.rect, 3, 3)
        self.btn_text.draw(surf)
        if self.show_border:
            pygame.draw.rect(surf, 'red', self.rect, 1)
            pygame.draw.rect(surf, 'green', self.margin_rect, 1)
            pygame.draw.rect(surf, 'red', self.padding_rect, 1)
    
    def update(self, dt, mouse=None):
        super().update(dt, mouse)
        # TODO: fix this mess ( WHY DOES THIS NEED TO HAPPED EVERY FRAME )
        self.btn_text.move_to_by_center(self.rect.center)
