import pygame

class MouseManager:
    def __init__(self):
        self.r_down = False
        self.l_down = False
        self.l_down_once = False
        self.l_up_once = False
        self.r_up = False
        self.l_up = True
        self.r_click = False
        self.l_click = False
        self.wheel_dir = 0
        self.pos = pygame.mouse.get_pos()
        self.is_moving = False
        self.drag = pygame.Vector2()
        # holding the mouse 
        self.is_being_held = False
        self.hold_time = 300
        self.pressed_time = 0
        self.hold_progress = 0  # 0 to 1 value 

        self.show_pos = False

    def get_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # left button pressed
                if not self.l_down:
                    self.l_down_once = True
                self.l_down = True
                self.l_up = False
                self.pressed_time = pygame.time.get_ticks()
            elif event.button == 2:  # middle button pressed
                pass
            elif event.button == 3:  # right button pressed
                self.r_down = True
                self.r_up = False
            elif event.button == 4:  # scroll up
                self.wheel_dir = -1
            elif event.button == 5:  # scroll down 
                self.wheel_dir = 1

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # left button up
                self.l_down = False
                if not self.l_up:
                    self.l_up_once = True
                self.l_up = True
                self.l_click = True
                # disable holding 
                self.is_being_held = False
                self.hold_progress = 0
            elif event.button == 2:  # middle button up
                pass
            elif event.button == 3:  # right button up
                self.r_down = False
                self.r_up = True
                self.r_click = True
        if event.type == pygame.MOUSEMOTION:
            self.pos = pygame.mouse.get_pos()



    # call this at the end of executions loop
    def update(self):
        self.wheel_dir = 0
        self.r_click = False
        self.l_click = False 
        self.l_down_once = False
        self.l_up_once = False
        self.drag = pygame.Vector2()
        if not self.is_being_held and self.l_down:
            time_diff = pygame.time.get_ticks() - self.pressed_time
            self.hold_progress = min(time_diff/self.hold_time, 1.0)
            if time_diff > self.hold_time:
                self.is_being_held = True

