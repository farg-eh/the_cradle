import pygame
import sys

from src.settings import FONTS, SW, SH
from src.ui.branch.list import VList
from .state import State
from src.utils import  Rect, import_imgs, import_imgs_as_dict
from src.ui import UiElement, Group, Panel, ScrollablePanel, HList, Button, Text, CheckBox, Slider, TextField, NumberField, PopPanel, RadioList, ImageBox
from src.mouse_manager import MouseManager
from src.ui import mimlize, CLASSES




class TestYard(State):
    def __init__(self, core):
        super().__init__(core, 'testyard')#
        self.mouse = MouseManager() 
        self.root = Group(size=self.screen.get_size(), name='root')
        self.root.show_border=True
        self.t = Text(text="Hello World!", color='yellow', font_size='mid', pos=(230, 0))
        pp = self.root
        #self.root.add_child(pp)
        #pp.add_child(self.t)
        #tf = TextField(placeholder='Your name')
        #tf.func = lambda: self.t.change_text(tf.value) 
        #pp.add_child(tf)
        #tf2 = NumberField(pos=(tf.pos[0], tf.pos[1] + tf.rect.height + 20))
        #pp.add_child(tf2)
        #pp.add_child(confirm_popup_gen('Hmmmm',"are you sure you want to exit without saving ?  ", None))
        #pp.add_child(PopPanel.with_confirm_popup("Wait", "are you sure you want to exit without saving first ?"))
        #rl = RadioList(pos=(200, 200), options=["blue", "green", "red"])
        #pp.add_child(rl)
        self.assets = self.load_assets()
        self.tile_variant = 0
        self.tile_list = [key for key in self.assets if key not in ['icons']]
        self.tile_group = 0

        self.imgbox = ImageBox(img=self.assets['large_decor'][1], size=(140, 140), pos=(100, 100), fit_type="contain")
        self.imgbox.show_border = True
        pp.add_child(self.imgbox)
        self.imgbox = ImageBox(img=self.assets['large_decor'][1], size=(100, 100), pos=(310, 100),fit_type="contain")
        self.imgbox.show_border = True
        pp.add_child(self.imgbox)
        self.imgbox = ImageBox(img=self.assets['large_decor'][1], size=(20, 20), pos=(100, 310),fit_type="contain")
        self.imgbox.show_border = True
        pp.add_child(self.imgbox)
        self.imgbox = ImageBox(img=self.assets['large_decor'][1], size=(30, 20), pos=(130, 310),fit_type="contain")
        self.imgbox.show_border = True
        pp.add_child(self.imgbox)

    def load_assets(self):
        # import imgs 
        assets = {
                'dark_grass': import_imgs("assets/imgs/tiles/dark_grass"),
                'grass_water': import_imgs("assets/imgs/tiles/grass_water"),
                "decor": import_imgs("assets/imgs/tiles/decor"),
                "large_decor": import_imgs("assets/imgs/tiles/large_decor"),
                'sand': import_imgs("assets/imgs/tiles/sand"),
                'icons': import_imgs_as_dict("assets/imgs/icons")
                }

        return assets

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                self.switch_state('menu')

            if event.key == pygame.K_a:
                pass
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:
                self.tile_variant = (self.tile_variant + 1) % len(self.assets[self.tile_list[self.tile_group]])
                for child in self.root.children:
                    if isinstance(child, ImageBox):
                        child.change_image(self.assets[self.tile_list[self.tile_group]][self.tile_variant])

            if event.button == 5:
                self.tile_group = (self.tile_group + 1) % len(self.tile_list)
                self.tile_variant = 0
                for child in self.root.children:
                    if isinstance(child, ImageBox):
                        child.change_image(self.assets[self.tile_list[self.tile_group]][self.tile_variant])


        super().handle_input(event)
           

        self.mouse.get_events(event)

    def update(self, dt):
        super().update(dt)

      
    def close_game(self, mouse=None):
        pygame.quit()
        sys.exit()

    def draw(self):   
        self.screen.fill("#6C455F")
        self.root.draw(self.screen)
        

