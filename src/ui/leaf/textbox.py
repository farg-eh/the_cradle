import pygame
from src.utils import import_font
from src.settings import conf
LANG = conf['LANG']

# NOTE: THIS CLASS GOT REPLACED WITH Text in text.py this will be kept here just for refrence just for refrence 
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

        self.font = import_font("assets/fonts/regular.ttf", size)
        if lang == "ar":
            self.font.set_script("Arab")
            self.font.set_direction(pygame.DIRECTION_RTL)
            self.font.align = pygame.FONT_RIGHT
        self.text_surf = self.font.render(text, False, color, wraplength=int(self.rect.width))

    def draw(self, surface):
        surface.blit(self.text_surf, self.rect.topleft)
