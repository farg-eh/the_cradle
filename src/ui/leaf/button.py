import pygame
from src.ui import UiElement
from . import Text

class Button(UiElement):
    def __init__(self, pos=(0,0),size=(34, 16), name='btn', text="btn", func=None, fore_color='white', back_color='black', border_color=None, border_width=2, border_radius=8, font_size='small'):
        super().__init__(pos, size, clickable=True, name=name)
        self.hoverable = True
        self.border_color = border_color
        self.border_width = border_width
        self.border_radius = border_radius
        self._c1 = fore_color
        self._c2 = back_color
        self.background_color = self._c2
        self.foreground_color = self._c1
        self.text_color = self._c2
        txt = text if text else name
        self.btn_text = Text(text=txt, color="white", font_size=font_size)
        self.btn_text.move_to_by_center(self.rect.center)
        self.show_border = False
        self.always_hover_checking = True
        self.func=func

    def on_click(self, mouse):
        super().on_click(mouse)
        if self.func:
            self.func()



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
        pygame.draw.rect(surf, self.background_color, self.rect, border_radius=self.border_radius)
        if not self.border_color:
            pygame.draw.rect(surf, self.foreground_color, self.rect, self.border_width, self.border_radius)
        else:
            pygame.draw.rect(surf, self.border_color, self.rect, self.border_width, self.border_radius)

        self.btn_text.draw(surf)
        if self.show_border:
            pygame.draw.rect(surf, 'red', self.rect, 1)
            pygame.draw.rect(surf, 'green', self.margin_rect, 1)
            pygame.draw.rect(surf, 'red', self.padding_rect, 1)

        # FIXME: this means that the method is gonna be called for every thing that is being drawn its not a good idea performance wise but it solves the bug where if the mouse leaves the child and the parent it doesnt get the chance to call the else part of the on_hover method
        # FIXME FIXME FIXME
        if self.always_hover_checking:
            self.on_hover()
    
    def update(self, dt, mouse=None):
        super().update(dt, mouse)
        # TODO: fix this mess ( WHY DOES THIS NEED TO HAPPED EVERY FRAME )
        self.btn_text.move_to_by_center(self.rect.center)
