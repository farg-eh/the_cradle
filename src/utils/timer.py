import pygame

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
        """resets the timer"""
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

    def __bool__(self):
        return self.active
