import pygame
import math
import sys
from src.states.state import State
from src.utils import import_img, import_imgs, SoundManager, Animation, Timer, Pos, Rect, TextLoader, get_abs_path
from src.ui import Stretchable
from src.ui import Text
from src.utils.lerp import oscilating_lerp
from .book import BookBG
from src.settings import SW, SH, conf

class Menu(State):
    def __init__(self, core):
        super().__init__(core, 'menu')
        self.sound_mgr = None
        self.assets = self.load_assets()
        self.book_bg = BookBG(self, self.assets)
        self.okay = False


        # load music and play it 
        pygame.mixer.music.load(get_abs_path('assets/sound/music/m1.mp3'))
        pygame.mixer.music.set_volume(core._music_vol)
        pygame.mixer.music.play(-1)

        # the press anything to start text
        start_txt: str = TextLoader("menu").get("press_anything_to_start")
        # color
        self.start_txt_color = pygame.Color('white')
        self.curr_txt_color = self.start_txt_color
        self.end_text_color = pygame.Color((0, 0, 0, 0))
        # txt
        self.start_txt = Text(start_txt, lang=conf['LANG'], font_size='small', color='white')
        self.start_txt.move_to_by_center((SW//2, SH*0.89))
        self.root.add_child(self.start_txt)
        # timers
        self.start_txt_timer = Timer(1400, loop=True, autostart = True)
        self.tag_pulse_timer = Timer(5000, loop=True, autostart=True, func=self.book_bg.tags_mangaer.pulse)


    def load_assets(self):
        # import sounds
        self.sound_mgr = SoundManager([
                'sfx/page-flip',
                'sfx/scribble-long',
                'sfx/scribble-short',
                'sfx/erase-long',
                'sfx/erase-short'
            ], vol=self.core._sfx_vol)

        # import imgs 
        assets = {
                "book-open": Animation("assets/imgs/book/book-open", duration=800),
                "page-flip-left": Animation("assets/imgs/book/page-flip-left", duration=200),
                "page-flip-right": Animation("assets/imgs/book/page-flip-right", duration=200),
                "page-fliping-right": Animation("assets/imgs/book/page-flip-right", duration=185, loop=False),
                "page-fliping-left": Animation("assets/imgs/book/page-flip-left", duration=185, loop=False),
                "chaining-page-left": import_img("assets/imgs/book/chaining-page-left.png"),
                "chaining-page-right": import_img("assets/imgs/book/chaining-page-right.png"),
                }
        assets['page-fliping-right'][4] = assets['chaining-page-right']
        assets['page-fliping-left'][4] = assets['chaining-page-left']

        return assets

    def handle_input(self, event):
        super().handle_input(event)
        if event.type == pygame.KEYUP:
            # open the book
            if not self.book_bg.open:
                self.book_bg.open_book() 
                self.root.remove_child(self.start_txt)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                self.switch_state('game')
            if event.key == pygame.K_2:
                self.switch_state('editor')

        self.book_bg.handle_input(event)

    def update(self, dt):
        self.book_bg.update(dt, self.mouse)
        if not self.book_bg.open:
            self.start_txt_timer.update()
            self.curr_txt_color = self.start_txt_color.lerp(self.end_text_color, oscilating_lerp(0, 1,self.start_txt_timer.get_progress()**2))
            self.curr_txt_color.a = int(oscilating_lerp(255, 0, self.start_txt_timer.get_progress()))
            self.start_txt.surf.set_alpha(self.curr_txt_color.a)

            self.tag_pulse_timer.update()
        
        super().update(dt)

    def draw(self):
       self.display.fill('black')  # "#3C7275"

       self.book_bg.draw(self.display)
       self.screen.blit(pygame.transform.scale2x(self.display), (0, 0))
       self.book_bg.on_screen_draw(self.screen)
       super().draw()

