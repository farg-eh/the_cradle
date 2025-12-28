import pygame
from .timer import Timer
from . import import_imgs


class Animation:
    def __init__(self, dir_path='', duration=1000, loop=False, imgs=None, autostart=False):
        if imgs != None:
            self.imgs = imgs
        else:
            self.imgs = import_imgs(dir_path)
        self.dir_path = dir_path
        self.duration = duration 
        self.loop = loop
        self.done = False
        self.curr_index = 0
        self.timer = Timer(duration=self.duration, 
                                 loop=self.loop)
        self.name = dir_path.split('/')[-1]
        self.autostart = autostart
        if autostart:
            self.play()
        
    def copy(self):
        imgs = [img.copy() for img in self.imgs]
        return Animation(dir_path=self.dir_path, imgs=imgs, duration=self.duration, loop=self.loop, autostart=self.autostart)

    def change_color_copy(self, old_color, new_color):
        animation = self.copy()
        for frame in animation.imgs:
            pxl_array = pygame.PixelArray(frame)
            pxl_array.replace(old_color, new_color)
            del pxl_array
        return animation
        
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

    def __len__(self):
        return len(self.imgs)

