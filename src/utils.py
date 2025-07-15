import os
import pygame

def get_abs_path(rel_path: str) -> str:
    """
    returns the absolute path of an input path

    Args:
        rel_path (str): relative path starting from the root directory of the project

    Returns:
        str: the absolute path 
    """
    p = os.path.abspath(os.path.dirname(__file__))
    rel_path_list = rel_path.split("/")
    return os.path.abspath(os.path.join(p, "..", *rel_path_list))

def import_img(path):
    img = pygame.image.load(get_abs_path(path)).convert()
    img.set_colorkey('black')  # color to be filled with transparency
    return img

def import_imgs(path):
    images = []
    img_names = sorted(os.listdir(get_abs_path(path)))
    for img_name in img_names:
        images.append(import_img(path + '/' + img_name))
    return images

class Animation:
    def __init__(self, dir_path, duration=1000, loop=False):
        self.imgs = import_imgs(dir_path)
        self.duration = duration 
        self.loop = loop
        self.done = False
        self.curr_index = 0
        self.timer = Timer(duration=self.duration, 
                                 loop=self.loop)

    def curr_img(self):
        return self.imgs[self.curr_index]

    def update(self):
        self.timer.update()
        if self.timer.get_progress() == 1 and not self.loop:
            self.done = True
        self.curr_index = round(self.timer.get_progress() * float(len(self.imgs) - 1))


    def __getitem__(self, index):
        return self.imgs[index]

    def __setitem__(self,index, item):
        self.imgs[index] = item



class Timer:
    def __init__(self, duration, loop=False, autostart=False, func=None):
        self.duration = duration
        self.loop = loop
        self.func = func

        self.active = False
        self.done = False
        self.start_time = 0

        if autostart:
            self.activate()

    def activate(self):
        self.active = True
        self.start_time = pygame.time.get_ticks()
        self.done = False

    def deactivate(self):
        self.active = False
        self.start_time = 0
        if self.loop:
            self.activate()
        else:
            self.done = True
    
    def get_progress(self) -> float:
        if self.done: 
            return 1
        elif self.start_time == 0: 
            return 0

        diff = pygame.time.get_ticks() - self.start_time
        return min(diff/self.duration, 1.0)

    def update(self):
        if self.active: 
            curr_time = pygame.time.get_ticks()
            diff = curr_time - self.start_time
            if diff >= self.duration:
                if self.func and self.start_time != 0:
                    self.func()
                self.deactivate()
            print(self.get_progress())

    def __bool__(self):
        return self.active

