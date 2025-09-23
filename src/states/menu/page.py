import pygame
from src.ui import Panel, Slider, CheckBox, Button, Text, HList, CLASSES
from src.utils import Rect, Pos, get_rel_pos
from src.settings import conf
from src.utils import Timer

class Page(Panel):
    def __init__(self, page_type='left', parent=None):
        posx = 54 if page_type == 'left' else 163
        posy = 30
        width = 103
        height = 138
        rect = Rect(posx, posy, width, height).display2screen()
        padding = (4, 6)
        margin = (0, 0)
        super().__init__(pos=(rect.x, rect.y), size=(rect.width, rect.height), name=f"page_{page_type}", parent=parent, padding=padding, margin=margin)

        # animations and effects
        self.trans_in_dur = 1400
        self.trans_out_dur = 200
        self.transition_timer = Timer(self.trans_in_dur)
        self.animation_status = ''
        self.surf.set_alpha(0)  # the page will be transparent at first u need to show in with fade_in


    def is_animating(self):
        return bool(self.transition_timer)

    def reset_animation(self):
        self.transition_timer.deactivate()
        self.animation_status = ''
        self.surf.set_alpha(0)


    def fade_out(self):
        if not self.transition_timer:
            self.animation_status = 'fade_out'
            self.transition_timer.duration = self.trans_out_dur
            self.transition_timer.activate()

    def fade_in(self):
        if not self.transition_timer:
            self.animation_status = 'fade_in'
            self.transition_timer.duration = self.trans_in_dur
            self.transition_timer.activate()


    def draw(self, surf):
        if self.hidden: return
        self.surf.fill((255, 255, 255, 255))
        super().draw(surf)
    
    def update(self, dt, mouse=None):
        self.transition_timer.update()
        if self.transition_timer:
            if self.animation_status == 'fade_in':
                self.surf.set_alpha(round(255 * self.transition_timer.get_progress()))

            elif self.animation_status == 'fade_out':
                self.surf.set_alpha(round(255 * (1 - self.transition_timer.get_progress())))
        #else:  # only update when there is no animations being played 
        #    super().update(dt, mouse)
        super().update(dt, mouse)


# ~~~~~~~~~~~~~~~~~~~~~~~ custom classes for page ui ~~~~~~~~~~~~~~~~~~~~~~~~~~~
class PageSlider(Slider):
    def __init__(self, pos=(0,0), name="page-slider", text='موسيقى', lang=None):
        lang = conf['LANG'] if lang == None else lang
        # pre super init calculations
        margin = (0, 0)
        padding = (0, 0)

        font_size = 'mid' if lang == 'ar' else 'big'
        self.text_y_offset = -2 if lang == 'ar' else -5
        self.text_x_offset = -3 if lang == 'ar' else 3
        if lang == 'ar':
            self.prog_rect = Rect(0, 0, 66, 10)
            self.name_rect = Rect(*self.prog_rect.topright, 27, 10)
        else:
            self.name_rect = Rect(0, 0, 27, 10)
            self.prog_rect = Rect(*self.name_rect.topright, 66, 10)
        self.mrg_rect = self.name_rect.union(self.prog_rect)
        
        # super init
        super().__init__(pos=pos, size=self.mrg_rect.scale_by(2).size, clickable=True, name=name, margin=margin, padding=padding)

        # text
        self.text = Text(pos=(pos[0]+self.text_x_offset, pos[1] + self.text_y_offset), text=text, color="#EEC39A", font_size=font_size, lang=lang)
        if lang == 'ar':
            self.text.move_to(((self.pos[0]+self.rect.width-self.text.rect.width)+self.text_x_offset, self.pos[1] + self.text_y_offset)) 

        # colors
        self.body_color = "#DD936E"
        self.prog_color = "#B86C49"
        self.focus_body_color = "#DF6262"
        self.focus_prog_color = "#BA3636"

        # surfaces
        self.surf = pygame.Surface(self.mrg_rect.size, pygame.SRCALPHA) # main surface
        self.name_surf = pygame.Surface(self.name_rect.size, pygame.SRCALPHA)
        self.body = self.surf.copy()
        self.focus_body = self.surf.copy()

        # drawing 
        self.body.fill(self.body_color)
        self._chop_corners(self.body, self.mrg_rect)
        self.holes = self._chop_holes(self.body, self.prog_rect)

        self.focus_body.fill(self.focus_body_color)
        self._chop_holes(self.focus_body, self.prog_rect)
        self._chop_corners(self.focus_body, self.mrg_rect)

        # state
        self.in_focus = False
        if lang == 'ar':
            self.prog_mouse_rect = self.prog_rect.scale_by(2,0).move_to(topleft=(self.rect.x + 16, self.rect.y)) # abs pos version of prog_rect
        else:
            self.prog_mouse_rect = self.prog_rect.scale_by(2,0).move_to(topleft=(self.rect.x + self.name_rect.width*2, self.rect.y)) # abs pos version of prog_rect
        self.value_in_points = 3 # 6 points for a slider
        
        self.lang = lang

    def _chop_corners(self, surf, rect):
        surf.set_at(rect.topleft, (0, 0, 0, 0))
        surf.set_at((rect.x, rect.height-1), (0, 0, 0, 0))
        surf.set_at((rect.right-1, rect.y), (0, 0, 0, 0))
        surf.set_at((rect.right-1, rect.height-1), (0, 0, 0, 0))

    def _chop_holes(self, surf, prog_rect):
        holes_center_points = []
        x = prog_rect.x + 1
        y = prog_rect.centery
        c = (0, 0, 0, 0) # transparent color 
        for i in range( 6):
            pygame.draw.circle(surf, c, (x+4, y), 4)
            holes_center_points.append([x+4, y])
            x += 8 + 3

        return holes_center_points

    def on_click(self, mouse=None):
        super().on_click(mouse)
        self.in_focus = True if not self.in_focus else False
        if self.func and not self.in_focus:
            self.func(self.value, mouse)

    def set_value(self, value):
        self.value = value
        self.value_in_points = round(self.value * 6)

    def on_hover(self, mouse=None):
        if mouse == None: return  
        rect = self.prog_mouse_rect
        x = min(max(rect.left, mouse.pos[0]), rect.right)
        if self.mouse_inside :
            if self.in_focus:
                self.value = abs(rect.left - x) / rect.width
                if self.lang == 'ar':
                    self.value = abs(1 - self.value)
                self.value_in_points = round(self.value * 6)
                self.value = self.value_in_points/6

        #print(f'\033[94m {self.value} \033[0m')
                

    def draw(self, surf):
        body = self.body if not self.in_focus else self.focus_body
        prog_color = self.prog_color if not self.in_focus else self.focus_prog_color
        self.surf.fill((0, 0, 0, 0))
        self.surf.blit(body, (0, 0))
        
        # draw holes
        for hole_index in range(self.value_in_points):
            if self.lang == 'ar':
                pygame.draw.circle(self.surf, prog_color, self.holes[len(self.holes) - 1 - hole_index], 3)
            else:
                pygame.draw.circle(self.surf, prog_color, self.holes[hole_index], 3)
        
        
        surf.blit(pygame.transform.scale2x(self.surf), self.margin_rect)
        #self.text.move_to(self.rect.topleft)
        self.text.draw(surf)

    def move_to(self, new_pos):
        super().move_to(new_pos)
        if self.lang == 'ar':
            self.text.move_to(((self.pos[0]+self.rect.width-self.text.rect.width)+self.text_x_offset, self.pos[1] + self.text_y_offset)) 
        else:
            self.text.move_to((self.pos[0]+self.text_x_offset, self.pos[1] + self.text_y_offset))

    def update(self, dt, mouse=None):
        if not mouse: print('no mouse')
        if not self.parent: print('no parent')
        # TODO : this should be removed and the focus should be handled in the Group class by the root mouse handle logic
        if mouse.l_click and self.in_focus and not self.rect.collidepoint(get_rel_pos(self.parent.parent.rect, mouse.pos)): 
            # the above line make the slider only works if its a child of a paper and the paper is a child of the root
            self.in_focus = False

class PageCheckBox(CheckBox):
    def __init__(self, pos=(0, 0), name="page_cbox"):
        # pre super init calculations
        size = 10*2, 10*2
        margin = (0, 4)
        padding = (0, 0)
        super().__init__(pos=pos, size=size, name=name, margin=margin)

        # colors
        self.color = "#B86C49"
        self.focus_color = "#BA3636"

    def on_click(self, mouse=None):
        super().on_click(mouse=mouse)
        print('\033[92mClick!\033[0m')

    def draw(self, surf):

        pygame.draw.rect(surf, self.color, self.rect, 2, 2)
        if self.value:
            pygame.draw.rect(surf, self.color, self.rect.inflate(-8, -8), border_radius=2)
        else:
            pass

        #print(self.value)
class PageText(Text):
    def __init__(self, text='', font_size='small', color='#B86C49', pos=(0, 0), name='', parent=None, lang=None, align=None):
        lang = conf['LANG'] if lang == None else lang
        if align == None:
            align = 'left' if lang == 'en' else 'right'
        super().__init__(text=text, color=color, font_size=font_size, wrap_width=190, pos=pos, name=name, parent=parent, clickable=False, hoverable=False, scrollable=False, lang=lang, align=align)
class PageTitle(Text):
    def __init__(self, text='', font_size='small', color='#B86C49', pos=(0, 0), name='', parent=None, lang=None):
        lang = conf['LANG'] if lang == None else lang
        super().__init__(text=text, color=color, font_size=font_size, wrap_width=190, pos=pos, name=name, parent=parent, clickable=False, hoverable=False, scrollable=False, lang=lang, align='mid')

    def draw(self, surf):
        super().draw(surf)
        p1 = Pos(*self.rect.bottomleft) + Pos(30, -4)
        p2 = Pos(*self.rect.bottomright) + Pos(-30, -4)
        pygame.draw.line(surf, self.color, p1, p2, 2)
        
        

book_classes = CLASSES.copy()
book_classes['>miml<'] = Page
book_classes['>slider<'] = PageSlider
book_classes['>checkbox<'] = PageCheckBox
book_classes['>txt<'] = PageText
book_classes['>title<'] = PageTitle

