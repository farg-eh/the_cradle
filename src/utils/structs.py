import pygame
from src.settings import SCALE
class Pos(pygame.Vector2):
    def __init__(self, x, y):
        super().__init__(x, y)

    def display2screen(self):
        return Pos(self.x * SCALE, self.y * SCALE)

    def screen2display(self):
        return Pos(self.x / SCALE, self.y / SCALE)


class Rect(pygame.Rect):
    def __init__(self, x, y, width, height):
        super().__init__(x, y , width, height)


    def display2screen(self):
        return Rect(self.x * SCALE, self.y * SCALE, self.width * SCALE, self.height * SCALE)
