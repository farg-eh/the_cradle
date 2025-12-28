import pygame
from src.ui import UiElement
from src.settings import FONTS, conf

# TODO: padding is broken here it should be fixed by adding a another surface that is separate from the text surface and place the text surface relativly on the new base surface
class Text(UiElement):
    def __init__(self, text='', color='white', font_size='small', wrap_width=0, pos=(0, 0), name='', parent=None,
                 clickable=False, hoverable=False, scrollable=False, padding=(0, 0), margin=(0, 0),
                 show_border=False, hidden=False, border_width=1, border_color='white', lang='en', align='left', colorkey=None, line_size=0):
        # check if fonts are loaded 
        if not FONTS:
            raise RuntimeError("your trying to create a text element before loading ur fonts from main.py into src/settings.py")
        # setup font 
        self.font: pygame.font.Font = FONTS[font_size+"-"+lang]
        self._align(align)
        if line_size:
            self.font.set_linesize(line_size)


        super().__init__( pos=pos, name=name, parent=parent, 
                 clickable=clickable, hoverable=hoverable, scrollable=scrollable, padding=padding, margin=margin,
                 show_border=show_border, hidden=hidden, border_width=border_width, border_color=border_color )
        # changing defualt element settings
        self.clickable = False
        self.hoverable = False
        self.scrollable = False
        self.text = text
        self.wrap_width = wrap_width
        self.color = color
        self.lang = lang


        # creating surf and updating rects
        self.wrap_width = int(self.wrap_width)
        self.surf = self.font.render(text, False, color, wraplength=self.wrap_width)
        if colorkey:
            self.surf.set_colorkey(colorkey)
        self._margin = margin
        self._padding = padding
        self._update_element_size()

    def _align(self, alignment='left'):
        match alignment:
            case 'left':
                self.font.align = pygame.FONT_LEFT
            case 'right': 
                self.font.align = pygame.FONT_RIGHT
            case 'mid':
                self.font.align = pygame.FONT_CENTER



    def _update_element_size(self):
        self.rect = self.surf.get_rect(topleft=self.pos)
        self.set_padding(*self._padding)
        self.set_margin(*self._margin)
        self.size = self.margin_rect.size

    def change_color(self, color):
        if color == self.color: return
        self.surf = self.font.render(self.text, False, color, wraplength=self.wrap_width)
        self.color = color

    def change_text(self, new_text, wrap_width=-1):
        if self.text == new_text: return

        wrap_width = self.wrap_width if wrap_width == -1 else wrap_width

        self.surf = self.font.render(new_text, False, self.color, wraplength=wrap_width)
        self.text = new_text
        self._update_element_size()

    def get_size(self):
        return self.rect.size

    def draw(self, surf):
        if self.hidden: return
        super().draw( surf)
        surf.blit(self.surf, self.rect.move(*self._margin))

    def get_surf(self):
        return self.surf


class H1(Text):
    def __init__(self, text='', color='white', font_size='mid', wrap_width=0, pos=(0,0), name='', parent=None, clickable=False, hoverable=False, scrollable=False, padding=(0,0), margin=(0,0), show_border=False, hidden=False, border_width=1, border_color='white'):
        super().__init__(text, color, font_size, wrap_width, pos, name, parent, clickable, hoverable, scrollable, padding, margin, show_border, hidden, border_width, border_color)

