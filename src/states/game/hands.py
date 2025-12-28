import pygame
from copy import deepcopy
from src.utils import Rect, Pos

class Hands:
    def __init__(self, human, color=None):
        self.human = human
        self.assets = human.game.assets['hands'].copy() # get it from player player get it from game

        self.change_color(color)

        # ~~~~~~~~~~~
        self.tool = 'empty' # other options are sword and bow
        self.state = 'idle' # there is action too and running is currently optional

        self.front_img = self.assets[f"{self.tool}-{self.state}-front_hand"][0]
        self.back_img = self.assets[f"{self.tool}-{self.state}-back_hand"][0]
        self.image_rect = self.front_img.get_frect(center=human.image_rect.center)

        # this works only for some items
        self.rotate = 0

        self.animation_index = 0
        self.animation_speed = 12

        # actions things
        self.finished_cycle = False
        self.performing_action = False
        self.hold_action = False

    def change_color(self, color=None):
        # change hands color
        try:
            skin_color = self.human.image.get_at((16, 9)) if color is None else color
        except IndexError:
            skin_color = pygame.Color("brown")
        assets = self.assets
        self.assets = {}
        for key, animation in deepcopy(assets).items():
            self.assets[key] = animation.change_color_copy(pygame.Color("white"), skin_color)

    def change_tool(self, new_tool):
        self.animation_index = 0
        self.tool = new_tool
        self.front_img = self.assets[f"{self.tool}-{self.state}-front_hand"][0]
        self.back_img = self.assets[f"{self.tool}-{self.state}-back_hand"][0]
        self.image_rect = self.front_img.get_frect(center=self.human.image_rect.center)

    def get_back_surf(self):
        # a surface to draw behind
        return pygame.transform.flip(self.back_img, self.human.flip, False)

    def get_front_surf(self):
        # a surface to draw infront of the player
        if self.human.is_aiming:
            return self.front_img
        return pygame.transform.flip(self.front_img, self.human.flip, False)

    def get_between_tick_rect(self, t):
        rect = self.image_rect.copy()
        rect.center = self.human.get_between_tick_rect(t).center
        return rect

    def update_animation(self, tdt):
        back_frames = self.assets[f"{self.tool}-{self.state}-back_hand"]
        front_frames = self.assets[f"{self.tool}-{self.state}-front_hand"]
        # manually updating the animation
        if back_frames:
            self.animation_index += self.animation_speed * tdt
            if self.animation_index >= len(back_frames):
                self.animation_index = 0
                self.finished_cycle = True
            self.back_img = back_frames[int(self.animation_index)]
            self.front_img = front_frames[int(self.animation_index)]

    def have_finished_cycle(self):
        if self.finished_cycle:
            self.finished_cycle = False
            return True
        return False

    def update(self, tdt):
        self.update_animation(tdt)

