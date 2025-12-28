import pygame
from src.settings import SCALE
class Pos(pygame.Vector2):
    def __init__(self, x, y):
        super().__init__(x, y)

    def display2screen(self):
        return Pos(self.x * SCALE, self.y * SCALE)

    def screen2display(self):
        return Pos(self.x / SCALE, self.y / SCALE)

    # TODO enable drawing as a surfaces
    # NOTE drawing as a surface doesnt work currently
    # enabls draw as surf if ur drawing directly on the main screen and you want to use a color with alpha value
    def draw(self, surface, color=pygame.Color('white'), thickness=1, draw_as_surf=False):
        if not draw_as_surf:
            pygame.draw.circle(surface, color, self, thickness)
        else:
            pass


class Rect(pygame.FRect):
    def __init__(self, x, y, width, height):
        super().__init__(x, y , width, height)

    @classmethod
    def from_2pos(cls, pos1, pos2):
        p1x = pos1[0] if pos1[0] < pos2[0] else pos2[0]
        p1y = pos1[1] if pos1[1] < pos2[1] else pos2[1]
        p2x = pos1[0] if pos1[0] > pos2[0] else pos2[0]
        p2y = pos1[1] if pos1[1] > pos2[1] else pos2[1]
        return Rect(p1x, p1y, p2x - p1x, p2y - p1y)

    def get_surf(self, color=pygame.Color('#00000000'), border_color=None, border_width=1, radius=0):
        surf = pygame.Surface(self.size, pygame.SRCALPHA)
        Rect(0, 0, *self.size).draw(surface=surf, color=color, border_color=border_color, border_width=border_width, radius=radius, draw_as_surf=False)
        return surf

    # enable draw as surf if ur drawing directly on the main screen and you want to use a color with alpha value
    def draw(self, surface, color=pygame.Color("white"), border_color=None, border_width=1, radius=0,draw_as_surf=False):        
        if not draw_as_surf:
            pygame.draw.rect(surface, color, self, border_radius=radius)
            if border_color:
                pygame.draw.rect(surface, border_color, self, border_width, border_radius=radius)
        else:
            surf = self.get_surf(color=color, border_color=border_color, border_width = border_width, radius=radius)
            surface.blit(surf, self)



    def display2screen(self):
        return Rect(self.x * SCALE, self.y * SCALE, self.width * SCALE, self.height * SCALE)
