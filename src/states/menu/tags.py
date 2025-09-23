import pygame
import math
from src.states.state import State
from src.utils import import_img, import_imgs, Animation, Timer, Pos, Rect, TextLoader
from src.ui import Stretchable
from src.ui import TextBox, CheckBox
from .page import Page, PageCheckBox, PageSlider, book_classes
from src.ui.parse import mimlize
from src.utils import Pos, oscilating_lerp
class Tags:
    def __init__(self, book):
        self.book = book

        self.tags_book_open = [ Stretchable(self.book.curr_animation.imgs[-1], Rect(273, 47+(i*16), 1, 14),
                                                     Rect(274, 47+(i*16), 14, 14))
                                          for i in range(5) ]
        self.tags_book_closed = [ Stretchable(self.book.curr_animation.imgs[0], Rect(217, 47+(i*16), 1, 14),
                                                     Rect(218, 47+(i*16), 14, 14))
                                          for i in range(5) ]

        self.tags  = self.tags_book_open
        self.max_stretch_length = 10
        # pulse effect
        self.pulse_effect_angles = [0.0*i for i in range(len(self.tags))]
        self.pulse_speed = 610
        self.pulsing = False
        self._pulses_count = 0
        # hover and click
        self.hovered_tag = None
        self.pull_timer = None
        self.pulled_tag = None
        self.pull_length = 9


    def draw(self, surface):
        for tag in self.tags:
            tag.draw(surface)

    def pulse(self, count=1):
        if self.pulsing:
            return
        self.pulsing = True
        self._pulses_count = count
        # sets the angle to run again if the are 0 they wont run 
        for i in range(len(self.pulse_effect_angles)):
            self.pulse_effect_angles[i] = 0.01

    def pull_tag(self, tag_index):
        funcs = [self.book.play_tag_click, self.book.editor_tag_click, self.book.multiplare_tag_click,
                                self.book.settings_tag_click, self.book.about_tag_click]
        self.pull_timer = Timer(400, autostart=True, func=funcs[tag_index])
        self.pulled_tag = self.tags[tag_index]



    def update(self, dt, mouse):
        # pulse effect
        if self.pulsing:
            for i, pulse_effect_angle in enumerate(self.pulse_effect_angles):
                tag = self.tags[i]
                # increase the angle first
                
                
                if self.pulse_effect_angles[i] != 0:
                    self.pulse_effect_angles[i] += (self.pulse_speed - i*75) * dt
                
                # limit the angle to 360
                if self.pulse_effect_angles[i] >= 360:
                    self.pulse_effect_angles[i] = 0

                # set the stretch amount
                # print(f"angle : {pulse_effect_angle}, radians:{math.radians(pulse_effect_angle)}")
                tag.set_stretch_x((self.max_stretch_length/2 * math.cos(math.radians(pulse_effect_angle + 180))) + self.max_stretch_length/2)
            if all([not bool( angle) for angle in self.pulse_effect_angles]):
                self._pulses_count -= 1
                if self._pulses_count <= 0:
                    self.pulsing = False
                    self._pulses_count = 0
                else:
                    # sets the angles to run again 
                    for i in range(len(self.pulse_effect_angles)):
                        self.pulse_effect_angles[i] = 0.01
        # hover and click handling                 
        elif self.book.open:
            for i, tag in enumerate(self.tags):
                if tag.rect.collidepoint(Pos(*mouse.pos).screen2display()):
                    self.hovered_tag = i
                    if self.pulse_effect_angles[i] < 180:
                        self.pulse_effect_angles[i] += self.pulse_speed * 1.2 * dt
                    # limit the angle to 360
                    if self.pulse_effect_angles[i] >= 180:
                        self.pulse_effect_angles[i] = 180
                    if mouse.l_click:
                        print('tag clicked')
                        self.pull_tag(i)
                # if its not a hovered tag
                else:
                    if self.pulse_effect_angles[i] > 0:
                        self.pulse_effect_angles[i] -= self.pulse_speed * 1.2 * dt
                    else:
                        self.pulse_effect_angles[i] = 0

                tag.set_stretch_x((self.max_stretch_length/2 * math.cos(math.radians(self.pulse_effect_angles[i] + 180))) + self.max_stretch_length/2)






        # change tags position based on framse
        if self.book.curr_animation == self.book.assets['book-open'] and self.book.curr_animation.curr_index == 0:
            self.tags = self.tags_book_closed
        else:

            self.tags = self.tags_book_open

     
            

        # click timer update
        if self.pull_timer != None:
            if not self.pull_timer.done:
                #self.pulled_tag.set_stretch_x(self.max_stretch_length + self.pull_length * self.pull_timer.get_progress())
                self.pulled_tag.set_stretch_x(oscilating_lerp(self.max_stretch_length, self.max_stretch_length + self.pull_length, self.pull_timer.get_progress()**2))
            self.pull_timer.update()
