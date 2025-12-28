import pygame
from src import ui
from src.ui import Group, UiElement
from src.utils import get_rel_pos, Rect, Pos
from src.utils.lerp import smooth_step_lerp

class Panel(Group):
    """this branch element doesnt order its children in any specifc way they are positioned using their positions
    however this branch element uses relative positioning and draws things on its own surface meaning elements will be positioned
    relatively and they wont show or be interactive with when outside of the Panel"""

    def __init__(self, pos=(0, 0), size=(110, 110), name='', parent=None, 
                 clickable=True, hoverable=True, scrollable=False, padding=(0, 0), margin=(0, 0),
                 show_border=False, hidden=False, border_width=1, border_color='white',border_radius=0, border_radius_list=[0, 0, 0, 0], bg_color=(0, 0, 0, 0)):
        super().__init__( pos=pos, size=size, name=name, parent=parent, 
                 clickable=clickable, hoverable=hoverable, scrollable=scrollable, padding=padding, margin=margin,
                 show_border=show_border, hidden=hidden, border_width=border_width, border_color=border_color )
        self.border_radius_list = [border_radius, border_radius, border_radius, border_radius] if border_radius else border_radius_list

        self.surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        self.bg_color = pygame.Color(bg_color)

    def set_opacity(self, value=1):
        self.surf.set_alpha(int(255*value))

    def add_child(self, ui_element):
        super().add_child(ui_element)

    def handle_mouse(self, mouse, _mouse_offset=(0, 0)):
        # change mouse pos to relative
        mouse_org_pos = mouse.pos
        mouse_rel_pos = get_rel_pos(self.rect, mouse_org_pos) 
        mouse.pos = mouse_rel_pos[0] + _mouse_offset[0], mouse_rel_pos[1] + _mouse_offset[1]
        # set our rects pos temporarily to (0, 0)
        org_rect_pos = self.margin_rect.topleft
        self.move_to((-self._margin[0]+_mouse_offset[0], -self._margin[1]+_mouse_offset[1]))
        # apply mouse handling logic
        returned = super().handle_mouse(mouse)

        # reset mouse pos & rect pos
        mouse.pos = mouse_org_pos
        self.move_to(org_rect_pos)
        
        return returned

    # TODO: start using dirty flags to optmize perfromance 
    def draw(self, surf):
        if self.hidden: return
        brs = self.border_radius_list

        self.surf.fill((0, 0, 0, 0))
        pygame.draw.rect(self.surf, self.bg_color, (0, 0, self.rect.width, self.rect.height),
                             border_top_left_radius=brs[0], border_top_right_radius=brs[1],
                             border_bottom_right_radius=brs[2], border_bottom_left_radius=brs[3])

        for child in self.children:
            child.draw(self.surf)

        if self.show_border:
            pygame.draw.rect(self.surf, self.border_color, (0, 0, self.rect.width, self.rect.height), self.border_width,
                             border_top_left_radius=brs[0], border_top_right_radius=brs[1],
                             border_bottom_right_radius=brs[2], border_bottom_left_radius=brs[3])

        surf.blit(self.surf, self.margin_rect)

class ScrollablePanel(Panel):
    """like Panel but allows scrolling"""
    def __init__(self, pos=(0, 0), size=(110, 110), name='', parent=None, 
                 clickable=True, hoverable=True, scrollable=False, padding=(0, 0), margin=(0, 0),
                 show_border=False, hidden=False, border_width=1, border_color='white', bg_color=(0, 0, 0, 0), border_radius=0):
        super().__init__( pos=pos, size=size, name=name, parent=parent, 
                 clickable=clickable, hoverable=hoverable, scrollable=True, padding=padding, margin=margin,
                 show_border=show_border, hidden=hidden, border_width=border_width, border_color=border_color, bg_color=bg_color, border_radius=border_radius )

        self.content_rect = Rect(0, 0, 0, 0)  
        self.content_surf = pygame.Surface((0, 0), pygame.SRCALPHA)
        self.offset = Pos(0, 0)
        self.lerp_offset = Pos(0, 0)
        self.scroll_speed = 25

    def _lerp_scroll(self, dt):
        # TODO: this is dum optimize it please
        if self.lerp_offset.x == self.offset.x and self.lerp_offset.y == self.offset.y: return

        dist = self.lerp_offset.distance_to(self.offset)
        if dist < 1:
            self.lerp_offset.x, self.lerp_offset.y = self.offset.x, self.offset.y
            return
        # now we will use a smooth step function to map distance to speed
        max_speed = 350
        min_speed = 25
        #k = 0.8
        max_dist = 55 
        t = pygame.math.clamp( dist/max_dist, 0, 1)
        move_amount = smooth_step_lerp(min_speed, max_speed, t)
        self.lerp_offset.move_towards_ip(self.offset, move_amount*dt)

    def on_scroll(self, mouse):
        super().on_scroll(mouse)
        # print(f"mouse wheel_dir = {mouse.wheel_dir}\noffsety: {self.offset.y}, crect width: {self.content_rect.height}")
        self.offset.y += mouse.wheel_dir * self.scroll_speed
        # FIXME please optmize T - T stop making hacks this solves 
        self.calc_content_surf()
        if self.offset.y > self.content_surf.height - self.surf.height + self._padding[1] + 4:  # FIXME please remove the 4
           self.offset.y = self.content_surf.height - self.surf.height + self._padding[1] + 4
        elif self.offset.y < 0:
           self.offset.y = 0

    def calc_content_rect(self):
        rect = self.rect.copy()
        self.content_rect = rect.unionall([x.margin_rect for x in self.children] + [self.rect])
        self.content_rect.topleft = self.rect.topleft

    def calc_content_surf(self):
        self.calc_content_rect()
        self.content_surf = pygame.Surface(self.content_rect.size, pygame.SRCALPHA)

    def add_child(self, ui_element):
         super().add_child(ui_element)
         self.calc_content_surf()

    def handle_mouse(self, mouse, _mouse_offset=(0, 0)):
        return super().handle_mouse(mouse, (self.offset))

    def draw(self, surf):
        if self.hidden: return
        self.content_surf.fill(self.bg_color)

        for child in self.children:
            child.draw(self.content_surf)
        self.surf.fill((0, 0, 0, 0))
        self.surf.blit(self.content_surf, -self.lerp_offset)

        if self.show_border:
            pygame.draw.rect(self.surf, self.border_color, (0, 0, self.rect.width, self.rect.height), self.border_width, border_radius=self.border_radius_list[0])

        surf.blit(self.surf, self.rect)

        #UiElement.draw(self, surf)

    def update(self, dt, mouse=None):
        self._lerp_scroll(dt)
        super().update(dt, mouse)
        # print(f"{self.name}: {self.content_surf.size}, r{self.content_rect.size}, sr{self.rect.size}")

    
