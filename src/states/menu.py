import pygame
import math
import sys
from .state import State
from src.utils import import_img, import_imgs, Animation, Timer, Pos, Rect, TextLoader
from src.ui import Stretchable
from src.ui import TextBox

class Menu(State):
    def __init__(self, core):
        super().__init__(core, 'menu')
        self.assets = self.load_assets()
        self.book_bg = BookBG(self, self.assets)
        self.okay = False

    def load_assets(self):
        assets = {
                "book-open": Animation("assets/imgs/book/book-open", duration=800),
                "page-flip-left": Animation("assets/imgs/book/page-flip-left", duration=200),
                "page-flip-right": Animation("assets/imgs/book/page-flip-right", duration=200),

                }
        return assets

    def handle_input(self, event):
        super().handle_input(event)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                self.switch_state('game')
            if event.key == pygame.K_2:
                self.switch_state('editor')
            if event.key == pygame.K_SPACE:
                self.assets['book-open'].play()
                self.book_bg.curr_animation = self.assets['book-open']
            if event.key == pygame.K_LEFT:
                self.book_bg.flip('left')
            if event.key == pygame.K_RIGHT:
                self.book_bg.flip('right')
            if event.key == pygame.K_o:
                self.okay = True

    def update(self, dt):
        self.book_bg.update(dt)
        super().update(dt)

    def draw(self):
       self.display.fill('black')  # "#3C7275"
       self.book_bg.draw(self.display)
       self.screen.blit(pygame.transform.scale2x(self.display), (0, 0))
       self.book_bg.on_screen_draw(self.screen)

class BookBG:
    def __init__(self, menu, assets):
        self.assets = assets
        self.menu = menu
        self.txt = TextLoader("book.about.pages")
        self.l_page_rect = Rect(54, 30, 103, 138)
        self.r_page_rect = Rect(163, 30, 103, 138)

        test = "Hello World \nmy name is Jenn and im making this cool game about\
                ancient arabic stories this test\
                is to see how much text my current page can handle ?"
        test2 = self.txt.get("0")
        self.textbox = TextBox(self.l_page_rect, test2) 
        self.curr_animation = self.assets['book-open']

        # testing the stretcher thingy
        self.stretched_list = []
        self.test = Stretchable(surf = self.curr_animation.imgs[-1],
                                stretch_area = Rect(273, 47, 3, 10),
                                moving_area = Rect(276, 47, 11, 10))
        self.test_list1 = [ Stretchable(self.curr_animation.imgs[-1], Rect(273, 47+(i*16), 1, 14),
                                                     Rect(274, 47+(i*16), 14, 14))
                                          for i in range(5) ]
        self.test_list2 = [ Stretchable(self.curr_animation.imgs[0], Rect(217, 47+(i*16), 1, 14),
                                                     Rect(218, 47+(i*16), 14, 14))
                                          for i in range(5) ]
        self.test_list = self.test_list2
        self.stretch_length = 7
        self.test_angle = 0
    def flip(self, direction="left"):
        self.curr_animation = self.assets[f'page-flip-' + direction]
        self.curr_animation.timer.activate()

    def draw(self, surface):
        surface.blit(self.curr_animation.curr_img(), (0, 0))
        for t in self.test_list:
            t.draw(surface)

        if self.curr_animation.done and self.stretched_list:
            surface.blit(self.stretched_list[0], self.stretched_list[1])
            surface.blit(self.stretched_list[2], self.stretched_list[3])
           # pygame.draw.rect(surface, "green",  self.stretched_list[1], 1)
           # pygame.draw.rect(surface, "blue", self.stretched_list[3], 1)
    def on_screen_draw(self, surface):
        if self.curr_animation.done:
            self.textbox.draw(surface)
 

    def update(self, dt):
        self.curr_animation.update()

        self.test_angle += 7 * dt;
        for i, t in enumerate(self.test_list):
            t.set_stretch_x((self.stretch_length * math.sin(self.test_angle + i*0.5) )+ self.stretch_length)
        self.menu.okay = False
        if self.curr_animation == self.assets['book-open'] and self.curr_animation.curr_index == 0:
            self.test_list = self.test_list2
        else:
            self.test_list = self.test_list1
