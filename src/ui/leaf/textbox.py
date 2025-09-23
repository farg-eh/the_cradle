import pygame
from src.utils import import_font
from src.settings import LANG
class TextBox:
    def __init__(self, rect, text='', color="#9D775E", size=10,
                 lang=LANG, scroll=False, padding=10,
                 use_screen_pos=True):
        self.rect = rect
        if use_screen_pos:
            self.rect = self.rect.display2screen()
        self.rect.inflate_ip(-padding, -padding)
        self.txt = text
        self.color = color
        self.size = size
        self.lang = lang
        self.scroll = scroll
        self.padding = padding

        self.font = import_font("assets/fonts/PixelAE-Regular.ttf", size)
        if lang == "ar":
            self.font.set_script("Arab")
            self.font.set_direction(pygame.DIRECTION_RTL)
            self.font.align = pygame.FONT_RIGHT
        self.text_surf = self.font.render(text, False, color, wraplength=self.rect.width)

    def draw(self, surface):
        surface.blit(self.text_surf, self.rect.topleft)
