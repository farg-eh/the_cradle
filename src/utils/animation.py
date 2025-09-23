import pygame
from .timer import Timer
from . import import_imgs


class Animation:
    def __init__(self, dir_path='', duration=1000, loop=False, imgs=[]):
        if imgs:
            self.imgs = imgs
        else:
            self.imgs = import_imgs(dir_path)
        self.duration = duration 
        self.loop = loop
        self.done = False
        self.curr_index = 0
        self.timer = Timer(duration=self.duration, 
                                 loop=self.loop)
        self.name = dir_path.split('/')[-1]
    def play(self):
        self.timer.activate()

    def curr_img(self):
        return self.imgs[self.curr_index]

    def update(self):
        self.timer.update()
        self.done = self.timer.done
        self.curr_index = round(self.timer.get_progress() * float(len(self.imgs) - 1))

    def add_img(self, img):
        self.imgs.append(img)


    def __getitem__(self, index):
        return self.imgs[index]

    def __setitem__(self,index, item):
        self.imgs[index] = item

