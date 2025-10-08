import pygame
from abc import ABC, abstractmethod

from .panel import Panel
from src.utils import Pos, get_abs_pos


# abstract class 
class List(Panel, ABC):
    def __init__(self, pos=(0, 0), size=(0, 0), name='', parent=None, clickable=False, hoverable=True, scrollable=False,
                 max_width=0, max_height=0, fixed_size=False, v_gap=3, h_gap=3, show_border=False, hidden=False, border_width=1, border_color='white', border_radius=0, border_radius_list=[0, 0, 0, 0], bg_color=(0, 0, 0, 0),  padding=(0, 0), margin=(0, 0),
                 rtl=False) -> None:
        super().__init__(pos=pos, size=size, name=name, parent=parent, clickable=clickable, hoverable=hoverable, scrollable=scrollable,
                         show_border=show_border, hidden=hidden, border_width=border_width, border_color=border_color, padding=padding,
                         margin=margin, bg_color=bg_color, border_radius=border_radius, border_radius_list=border_radius_list)
        # basic properties
        self.max_width = max_width
        self.max_height = max_height
        self.fixed_size = fixed_size
        self.h_gap = h_gap
        self.v_gap = v_gap


        # stuff used for positioning and wraping
        self._last_child_index = 0
        self._max_w = 0
        self._max_h = 0
        self._progress_x = 0
        self._progress_y = 0

        # rtl for hlists TODO: apply for vlist when needed  
        self.rtl = rtl

    def add_child(self, ui_element):
        super().add_child(ui_element)
        self._update_last_child_pos_rtl() if self.rtl else self._update_last_child_pos()
        self._last_child_index += 1

    def remove_child(self, ui_element):
        super().remove_child(ui_element)
        self._last_child_index = len(self.children) - 1

    def _grow_rects(self, w_increase, h_increase):
        self.padding_rect.inflate_ip(w_increase, h_increase)
        if self.rect != self.padding_rect:
            self.rect.inflate_ip(w_increase, h_increase)
        if self.margin_rect != self.rect:
            self.margin_rect.inflate_ip(w_increase, h_increase)

        self.margin_rect.topleft = self.pos.x, self.pos.y
        self.rect.center = self.margin_rect.center
        self.padding_rect.center = self.rect.center

    def _resize_padding_rect(self, w, h):
        self.padding_rect.update(0, 0, w, h)
        if self.rect != self.padding_rect:
            self.rect.update(0, 0, w + self._padding[0]*2, h + self._padding[1]*2)
        if self.margin_rect != self.rect:
            self.margin_rect.update(0, 0, self.rect.width + self._margin[0]*2, self.rect.height + self._margin[1]*2)
        # now we position them correctly 
        self.margin_rect.topleft = self.pos.x, self.pos.y
        self.rect.center = self.margin_rect.center
        self.padding_rect.center = self.rect.center

        # lets resize the surface too 
        self.surf = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        self.surf.set_colorkey('black')

    def _reset_positioning_stuff(self):
        self._last_child_index = 0
        self._max_w = 0
        self._max_h = 0
        self._progress_x = 0
        self._progress_y = 0

    # this method is used to auto resize the container 
    @abstractmethod
    def _fit_kids(self):
        pass



    # here is where the list positions its children
    @abstractmethod
    def _update_last_child_pos(self):
        pass

    def _update_last_child_pos_rtl(self):
        pass


# TODO: do the max_height logic on the hlist
# NOTE: an idea is to re write the whole hlist logic and make it work as a 2d list to make positioning easier and more flexable i want to achieve flex box flexability in the future 
class HList(List):
    """this HList or Horizontal List auto positions elements inside it horizontally
    the inital size you specify will expand when needed  
    you can add a max_width to enable wraping 
    if you specify max_height too it will throw and error if you exceed the list size
    """

    # this method is used to auto resize the container 
    def _fit_kids(self):
        new_size = [0, 0]
        rect = self.padding_rect
        if self._progress_x > rect.width:
            new_size[0] = self._progress_x
        else:
            new_size[0] = rect.width # aka old width
        if self._max_h + self._progress_y > rect.height:
            new_size[1] = self._max_h + self._progress_y
        else:
            new_size[1] = rect.height # aka old height
        # now we resize
        self._resize_padding_rect(*new_size)

    def _update_last_child_pos(self):
        # shorter names to make it easier
        child = self.children[self._last_child_index]
        w = child.margin_rect.width
        h = child.margin_rect.height
        rect = self.padding_rect

        # the actual positionsing
        # updating max height (the height of the heighest element in the row)
        self._max_h = h if h > self._max_h else self._max_h


        #if the element is the first in the row then we position it without thinking much 
        if self._progress_x == 0:
            child.default_border_color = 'blue'
            #child.move_to(get_abs_pos(rect, (self._progress_x, self._progress_y)))
            child.move_to((self._progress_x, self._progress_y))
            self._progress_x += w 
            # now we resize if we should
            self._fit_kids()
            # and exit 
            return

        # now we are not the first element in the row
        # if we have a width limit (aka max_width is enabled)
        if self.max_width > 0:
            if self._progress_x + self.h_gap + w > self.max_width: # if no room
                # we go down a row
                self._progress_x = 0
                self._progress_y += self._max_h + self.v_gap
                self._max_h = h
                # positions the child
                #child.move_to(get_abs_pos(rect, (self._progress_x, self._progress_y)))
                child.move_to((self._progress_x, self._progress_y))
                self._progress_x += w
                # resize our rects 
                self._fit_kids()
                # exit
                return

        # if we have room or if there is no width limit
        self._progress_x += self.h_gap
        #child.move_to(get_abs_pos(rect, (self._progress_x, self._progress_y)))
        child.move_to((self._progress_x, self._progress_y))
        self._progress_x += w
        # resize our rects if we should
        self._fit_kids()
        # exit
        return
# TODO: merge with the above method to avoid code duplication
    def _update_last_child_pos_rtl(self):
        # shorter names to make it easier
        child = self.children[self._last_child_index]
        w = child.margin_rect.width
        h = child.margin_rect.height
        rect = self.padding_rect

        # the actual positionsing
        # updating max height (the height of the heighest element in the row)
        self._max_h = h if h > self._max_h else self._max_h


        #if the element is the first in the row then we position it without thinking much 
        if self._progress_x == 0:
            child.default_border_color = 'blue' # TODO: this shouldnt exist i think
            child.move_to(get_abs_pos(rect, (self._progress_x, self._progress_y)))
            self._progress_x += w 
            # now we resize if we should
            self._fit_kids()
            # and exit 
            return 

        # now we are not the first element in the row
        # if we have a width limit (aka max_width is enabled)
        if self.max_width > 0:
            if abs(self._progress_x) + self.h_gap + w > self.max_width: # if no room
                # we go down a row
                self._progress_x = 0
                self._progress_y += self._max_h + self.v_gap
                self._max_h = h
                # positions the child
                child.move_to(get_abs_pos(rect, (self._progress_x, self._progress_y)))
                self._progress_x += w
                # resize our rects 
                self._fit_kids()
                # exit
                return

        # here is most of the logic
        # if we have room or if there is no width limit
        self._progress_x += self.h_gap
        child.move_to(get_abs_pos(rect, (0, self._progress_y)))
        self._progress_x += w
        # resize our rects if we should
        self._fit_kids()
        # re position (move) all children having the same y coords as the child 
        move_amount = abs(w + self.h_gap)
        for kid in self.children:
            if kid == child:
                continue
            if kid.margin_rect.top == child.margin_rect.top:
                kid.move_to_by_center((kid.rect.centerx+move_amount , kid.rect.centery))

        # exit
        return

    def draw(self, surf):
        super().draw(surf)
        okay = False # useful with debugging 
        if okay:
            pygame.draw.rect(surf, 'white', self.padding_rect, 1)
            for child in self.children:
                pygame.draw.rect(surf, 'red', child.margin_rect.move_to(topleft=get_abs_pos(self.rect, child.pos)), 1)


# TODO: do the max_width logic
class VList(List):
    """this VList or Vertical list auto positions elements inside it vertically
    the inital size you specify will expand when needed  
    you can add a max_height to enable wraping 
    if you specify max_width too it will throw and error if you exceed the list size
    """
    # this method is used to auto resize the container 
    def _fit_kids(self):
        new_size = [0, 0]
        rect = self.padding_rect
        if self._progress_y > rect.height:
            new_size[1] = self._progress_y
        else:
            new_size[1] = rect.height # aka old height
        if self._max_w + self._progress_x > rect.width:
            new_size[0] = self._max_w + self._progress_x
        else:
            new_size[0] = rect.width # aka old width
        # now we resize
        self._resize_padding_rect(*new_size)

    def _update_last_child_pos(self):
        # shorter names to make it easier
        child = self.children[self._last_child_index]
        w = child.margin_rect.width
        h = child.margin_rect.height
        rect = self.padding_rect

        # the actual positionsing
        # updating max width (the width of the widest element in the row)
        self._max_w = w if w > self._max_w else self._max_w


        #if the element is the first in the column then we position it without thinking much 
        if self._progress_y == 0:
            child.move_to(get_abs_pos(rect, (self._progress_x, self._progress_y)))
            self._progress_y += h 
            # now we resize if we should
            self._fit_kids()
            # and exit 
            return

        # now we are not the first element in the cloumn
        # if we have a height limit (aka max_height is enabled)
        if self.max_height > 0:
            if self._progress_y + self.v_gap + h > self.max_height: # if no room
                # we go right opening a new col
                self._progress_y = 0
                self._progress_x += self._max_w + self.h_gap
                self._max_w = w
                # positions the child
                child.move_to(get_abs_pos(rect, (self._progress_x, self._progress_y)))
                self._progress_y += h
                # resize our rects 
                self._fit_kids()
                # exit
                return

        # if we have room or if there is no width limit
        self._progress_y += self.v_gap
        child.move_to(get_abs_pos(rect, (self._progress_x, self._progress_y)))
        self._progress_y += h
        # resize our rects if we should
        self._fit_kids()
        # exit
        return

    def draw(self, surf):
        super().draw(surf)
        if self.show_border:
            pygame.draw.rect(surf, self.border_color, self.rect, width=1)
        okay = False
        if okay:
            pygame.draw.rect(surf, 'white', self.padding_rect, 1)
            for child in self.children:
                pygame.draw.rect(surf, 'red', child.margin_rect.move_to(topleft=get_abs_pos(self.rect, child.pos)), 1)


