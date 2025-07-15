import pygame
import sys
from .state import State
from src.utils import import_img, import_imgs, Animation, Timer


class Menu(State):
    def __init__(self, core):
        super().__init__(core, 'menu')
        self.assets = self.load_assets()
        self.book_bg = BookBG(self.assets)

    def load_assets(self):
        assets = {
                "book-open": Animation("assets/imgs/book/book-open", duration=800),
                "page-flip-left": Animation("assets/imgs/book/page-flip-left", duration=200),
                "page-flip-right": Animation("assets/imgs/book/page-flip-right", duration=200),

                }
        return assets

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                self.switch_state('game')
            if event.key == pygame.K_2:
                self.switch_state('editor')
            if event.key == pygame.K_SPACE:
                self.assets['book-open'].timer.activate()
            if event.key == pygame.K_LEFT:
                self.book_bg.flip('left')
            if event.key == pygame.K_RIGHT:
                self.book_bg.flip('right')

    def update(self, dt):
        self.book_bg.update(dt)

    def draw(self):
       self.display.fill('black')  # "#3C7275"
       self.book_bg.draw(self.display)
       self.screen.blit(pygame.transform.scale2x(self.display), (0, 0))

class BookBG:
    def __init__(self, assets):
        self.assets = assets
        self.curr_animation = self.assets['book-open']
    def flip(self, direction="left"):
        self.curr_animation = self.assets[f'page-flip-' + direction]
        self.curr_animation.timer.activate()

    def draw(self, surface):
        surface.blit(self.curr_animation.curr_img(), (0, 0))

    def update(self, dt):
        self.curr_animation.update()
