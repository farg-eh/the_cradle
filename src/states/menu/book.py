import pygame
import math
import sys
from src.states.state import State
from src.utils import import_img, import_imgs, Animation, Timer, Pos, Rect, TextLoader
from src.ui import Stretchable
from src.ui import TextBox, CheckBox
from .page import Page, PageCheckBox, PageSlider, book_classes
from .tags import Tags
from src.ui.parse import mimlize
from src.settings import conf
import random


class BookBG:
    def __init__(self, menu, assets):
        self.assets = assets
        self.menu = menu
        self.l_page_rect = Rect(54, 30, 103, 138)  # not needed anymore
        self.r_page_rect = Rect(163, 30, 103, 138) # not needed anymore

        # ~~~~~~~~~(  TEXT  )~~~~~~~~~
        self.loader = TextLoader("book")
        book_content: dict = self.loader.get()
        self.tag_names = list(book_content.keys())
        # convert the pages into a {tag_name: list of Page s}  dict
        self.curr_tag = 'play'
        self.pages = {tag: [mimlize(self.loader.get(f"{tag}.pages.{i}"),
                                    book_classes) for i in range(len(book_content[tag]['pages']))] for tag in self.tag_names}    
        
        self.txt = TextLoader("book.about.pages")
        test2 = self.txt.get("0")
        test1 = self.txt.get('1')
        self.textbox = TextBox(self.l_page_rect, test2) 

        self.curr_animation = self.assets['book-open']
        self.page_visible = True

        # ~~~~~~~~~(  TAGS  )~~~~~~~~~
        self.tags_mangaer = Tags(self)

        # ~~~~~~~~~(  PAGES  )~~~~~~~~~
        self.rp_index = 1
        self.lp_index = 0
        self.l_page= self.pages[self.curr_tag][self.lp_index]
        self.r_page = self.pages[self.curr_tag][self.rp_index]
        self.apply_page_changes()

        # empty pages 
        self.empty_l_page = Page()
        self.empty_r_page = Page(page_type='right')


        # states
        self.open = False

        # this if for the fade in effect when the book opens 
        self.book_just_opened = False

        self.changing_sections = False
        self._sections_pages_to_flip = 0

        # book-open sfx issue solution
        self.book_open_sfx_last_index = -1

        # settings ui 
        self.settings_prepared = False

    def apply_page_changes(self):
        # select the new pages
        max_page_index = len(self.pages[self.curr_tag]) - 1
        lp = self.lp_index if self.lp_index < max_page_index else -1
        rp = self.rp_index if self.rp_index <= max_page_index else -1
        print(f'lp is {lp}, and rp is {rp}')
        self.l_page = self.pages[self.curr_tag][lp] if lp >= 0 else self.empty_l_page
        self.r_page = self.pages[self.curr_tag][rp] if rp >=0 else self.empty_r_page

        # remove current pages
        for kid in self.menu.root.children.copy():
            if isinstance(kid, Page):
                kid.reset_animation()
                self.menu.root.children.remove(kid)
        # add new ones
        self.menu.root.add_child(self.l_page)
        self.menu.root.add_child(self.r_page)

    def change_section(self, direction='left', sections_count=1):
        self._sections_pages_to_flip = sections_count * 3 
        self.changing_sections = True
        self.curr_animation = self.assets[f'page-fliping-{direction}']
        self.curr_animation.play()

    def change_section_pages(self, tag_name='play', too_many_flips = False):
        index_a = self.tag_names.index(tag_name)
        index_b = self.tag_names.index(self.curr_tag)
        dist = (index_b - index_a)
        sign = 1 if dist >= 0 else -1
        # clamp dist
        dist = dist if abs(dist) < 2 else  2 * sign
        # if we are on the same sectin we want to go just abort 
        if dist == 0: return 
        if too_many_flips:
            dist = 99 * sign

        # specify the correct animation to play
        direction = 'right' if dist > -1 else 'left'
        self.change_section(direction=direction, sections_count=abs(dist))
        
        # change curr section
        self.curr_tag = tag_name

        # re setting the pages 
        self.lp_index = 0
        self.rp_index = 1
        # applying the changes
        self.apply_page_changes()



    def flip(self, direction="left"):
        # no fliping if the book is closed
        if not self.open: return
        # if the current page is the first page in the list disable fliping to the left 
        max_page_index = len(self.pages[self.curr_tag]) - 1
        if self.lp_index == 0 and direction == 'right':
            return

        # change the current animation
        self.curr_animation = self.assets[f'page-flip-' + direction]
        self.curr_animation.timer.activate()


        # changing pages content
        x = -1 if direction=="right" else 1
        self.lp_index += 2  * x
        self.rp_index = self.lp_index + 1
        lp = self.lp_index if self.lp_index < max_page_index else -1
        rp = self.rp_index if self.rp_index <= max_page_index else -1
        print(f'lp is {lp}, and rp is {rp}')

        # applying the changes
        self.l_page = self.pages[self.curr_tag][lp] if lp >= 0 else self.empty_l_page
        self.r_page = self.pages[self.curr_tag][rp] if rp >=0 else self.empty_r_page
        self.apply_page_changes()

        # showing the new pages 
        self.l_page.fade_in()
        self.r_page.fade_in()
        print(len(self.menu.root.children))
        # paly a random sound
        #sn = random.choice(self.menu.assets['sounds']['pf'])
        #sn.play()
        self.menu.sound_mgr.play('page-flip', 'seq')

    def open_book(self):
        self.curr_animation = self.assets['book-open']
        self.curr_animation.play()
        self.book_just_opened = True
        self.open = True

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_LEFT:
                self.flip('left')
            if event.key == pygame.K_RIGHT:
                self.flip('right')
            if event.key == pygame.K_o:
                self.okay = True

            if event.key == pygame.K_j:
                self.r_page.fade_in()
            if event.key == pygame.K_k:
                self.r_page.fade_out()

            if event.key == pygame.K_p:
                self.tags_mangaer.pulse()

            if event.key == pygame.K_f:
                self.change_section()

    def draw(self, surface):
        surface.blit(self.curr_animation.curr_img(), (0, 0))
        self.tags_mangaer.draw(surface)

    def on_screen_draw(self, surface):
        
        pass


    def update(self, dt, mouse):
        # animation 
        self.curr_animation.update()
        # hide pages content if we are not at the last frame of the current animation 
        self.menu.root.get_child_by_name("page_left").hidden = False if self.curr_animation.done else True
        self.menu.root.get_child_by_name("page_right").hidden = False if self.curr_animation.done else True

        # tags update
        self.tags_mangaer.update(dt, mouse)

        # changing sections logic
        if self.changing_sections:
            if self.curr_animation.done:
                self._sections_pages_to_flip -= 1
                if self._sections_pages_to_flip > 1:
                    self.curr_animation.play()
                    # paly a random sound
                    self.menu.sound_mgr.play('page-flip', 'random-no-repeat')
                elif self._sections_pages_to_flip == 1:
                    self.curr_animation = self.assets[f"page-flip-{self.curr_animation.name.split('-')[-1]}"]
                    self.curr_animation.play()
                    # paly a random sound
                    self.menu.sound_mgr.play('page-flip', 'random-no-repeat')
                    #sn = random.choice(self.menu.assets['sounds']['pf'])
                    #sn.play()
                else:
                    self.changing_sections = False
                    self.l_page.fade_in()
                    self.r_page.fade_in()



        # show pages content when we open the book 
        if self.book_just_opened and self.curr_animation.done:
            self.l_page.fade_in()
            self.r_page.fade_in()
            self.book_just_opened = False

        # book open sounds
        if self.curr_animation == self.assets['book-open'] and self.curr_animation.curr_index != self.book_open_sfx_last_index:
            if self.curr_animation.curr_index in [3, 6, 9]:
                self.menu.sound_mgr.play('page-flip', 'seq')
                self.book_open_sfx_last_index = self.curr_animation.curr_index



    def prepare_ui_functions(self):
        if self.settings_prepared : return

        ui = self.menu.root.named_children
        print(ui)
        fullscreen_cbox = ui.get('fullscreen_cbox')[0]
        fullscreen_cbox.value = self.menu.core._fullscreen
        fullscreen_cbox.func = self._switch_fullscreen

        scaled_cbox = ui.get('scaled_cbox')[0]
        scaled_cbox.value = self.menu.core._scaled
        scaled_cbox.func = self._switch_scaled

        show_fps_cbox = ui.get('show_fps_cbox')[0]
        show_fps_cbox.value = self.menu.core._show_fps
        show_fps_cbox.func = self._show_fps_func 

        music_slider = ui.get('music_slider')[0]
        music_slider.set_value(self.menu.core._music_vol)
        music_slider.func = self._music_vol_func 

        sfx_slider = ui.get('sfx_slider')[0]
        sfx_slider.set_value(self.menu.core._sfx_vol)
        sfx_slider.func = self._sfx_vol_func

        ar_cbox = ui.get('ar_cbox')[0]
        en_cbox = ui.get('en_cbox')[0]
        ar_cbox.value = bool(conf['LANG']=='ar')
        en_cbox.value = bool(conf['LANG']=='en')
        ar_cbox.func = self._change_lang_2ar_func
        en_cbox.func = self._change_lang_2en_func
        
        
        self.settings_prepard = True

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~ tag click functions ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def play_tag_click(self):
        print('\033[93mplay tag pulled\033[0m')
        # tags index distance calculation
        self.change_section_pages('play')
        self.menu.switch_state('game')
    def editor_tag_click(self):
        print('\033[93meditor tag pulled\033[0m')
        self.change_section_pages('editor')
        self.menu.switch_state('editor')

    def multiplare_tag_click(self):
        print('\033[93mmultiplayer tag pulled\033[0m')
        self.change_section_pages('multiplayer')

    def settings_tag_click(self):
        print('\033[93msettings tag pulled\033[0m')
        self.change_section_pages('settings')
        self.prepare_ui_functions()

    def about_tag_click(self):
        print('\033[93mabout tag pulled\033[0m')
        self.change_section_pages('about')



    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~ throw away functions for settings ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def _switch_fullscreen(self, value):
        self.play_sound_for_checkbox(value)
        self.menu.core.switch_fullscreen(value)
        
    def _switch_scaled(self, value):
        self.play_sound_for_checkbox(value)
        self.menu.core.switch_scaled(value)

    def _show_fps_func(self, value):
        self.play_sound_for_checkbox(value)
        self.menu.core._show_fps = value

    def _music_vol_func(self, value, mouse=None):
        if value == self.menu.core._music_vol: return
        # play sound
        if value > self.menu.core._music_vol:
            self.menu.sound_mgr.play('scribble-long', 'seq')
        elif value < self.menu.core._music_vol:
            self.menu.sound_mgr.play('erase-long', 'seq')

        self.menu.core._music_vol = value
        pygame.mixer.music.set_volume(value)
        print(value)
        print(pygame.mixer.music.get_volume())
        
    def _sfx_vol_func(self, value, mouse=None):
        if value == self.menu.core._sfx_vol: return
        old_vol = self.menu.core._sfx_vol

        self.menu.core._sfx_vol = value
        self.menu.sound_mgr._vol = value
        print(value)
        print(self.menu.sound_mgr._vol)

        # play sound
        if value > old_vol:
            self.menu.sound_mgr.play('scribble-long', 'seq')
        elif value < old_vol:
            self.menu.sound_mgr.play('erase-long', 'seq')

    def _change_lang_2ar_func(self, value):
        self.play_sound_for_checkbox(value)
        if conf['LANG'] == 'ar': return
        conf['LANG'] = 'ar'
        self.menu.switch_state('menu')

    def _change_lang_2en_func(self, value):
        self.play_sound_for_checkbox(value)
        global LANG
        if conf['LANG'] == 'en': return
        conf['LANG'] = 'en'
        self.menu.switch_state('menu')

    def play_sound_for_checkbox(self, value):
            if value:
                self.menu.sound_mgr.play('scribble-short', 'seq')
            else:
                self.menu.sound_mgr.play('erase-short', 'seq')
