import pygame
from copy import deepcopy
from src.utils import Pos, Rect

class UiElement:
    def __init__(self, pos=(0, 0), size=(0, 0), name='', parent=None, 
                 clickable=True, hoverable=True, scrollable=False, padding=(0, 0), margin=(0, 0),
                 show_border=False, hidden=False, border_width=1, border_color='white' ):
        # basic element info
        self.pos = Pos(*pos)
        self.rect = Rect(*pos, *size)
        self.name = name
        self.parent = parent
        self.root = self
        
        # element interactivitya
        self.clickable = clickable
        self.hoverable = hoverable
        self.scrollable = scrollable

        # borders 
        self.default_border_color = border_color
        self.border_color = self.default_border_color
        self.border_width = border_width
        self.show_border = show_border

        # padding and margin
        self.padding_rect = self.rect
        self.margin_rect = self.rect
        self._padding = padding
        self._margin = margin
        self.set_padding(*self._padding)
        self.set_margin(*self._margin)

        # status
        self.mouse_inside = False
        self.hidden = hidden
        
    def move_to(self, new_pos):
        self.pos = Pos(*new_pos)
        self.margin_rect.topleft = new_pos
        self.rect.center = self.margin_rect.center
        self.padding_rect.center = self.margin_rect.center

    def move_to_by_center(self, new_pos):
        self.margin_rect.center = new_pos
        self.rect.center = new_pos
        self.padding_rect.center = new_pos
        self.pos = Pos(self.margin_rect.x, self.margin_rect.y)

    def copy(self):
        return deepcopy(self)

    def set_padding(self, left_right, top_down):
        self._padding = (left_right, top_down)
        self.padding_rect = self.rect.inflate(-left_right*2, -top_down*2) 
        self.padding_rect.center = self.rect.center

    def set_margin(self, left_right, top_down):
        self._margin = (left_right, top_down)
        self.margin_rect = self.rect.inflate(left_right*2, top_down*2)
        self.margin_rect.topleft = self.rect.topleft
        self.rect.center = self.margin_rect.center
        self.padding_rect.center = self.rect.center

    def on_hover(self, mouse):
        if self.mouse_inside:
            name = self.name if self.name else self.__str__()
            self.border_color = "pink"
        else:
            self.border_color = self.default_border_color

    def on_click(self, mouse):
        pass

    def on_scroll(self, mouse):
        pass

    def handle_mouse(self, mouse):
        if not self.hoverable: return 
        if self.rect.collidepoint(mouse.pos):
            self.mouse_inside = True
            if self.root.mouse_stack[-1] != self:
                self.root.mouse_stack.append(self)
        
        self.on_hover(mouse)
        m_in = self.mouse_inside
        self.mouse_inside = False
        return m_in

    def draw(self, surf):
        if self.hidden: return
        if self.show_border: 
            pygame.draw.rect(surf, self.border_color, self.rect, self.border_width)

    def update(self, dt, mouse):
        pass

        
    def __str__(self):
        return self.name if self.name else f"({self.__class__.__name__})"



