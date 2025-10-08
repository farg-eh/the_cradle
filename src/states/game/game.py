import pygame
import sys
from src.states import State
from src.utils import import_imgs, get_abs_path, import_img, Animation
from .entities import Player
from src.tiles.tilemap import Tilemap

class Game(State):
    def __init__(self, core):
        super().__init__(core, 'menu')
        self.assets = self.load_assets()
        self.movement = [False, False, False, False]

        self.tilemap = Tilemap(self, tile_size=16)
        self.tilemap.load('map3.json')

        self.scroll = [0, 0]

        self.player = Player(self, (50, 50), (8, 15))
        
        self.tilemap = Tilemap(self, tile_size=16)
        self.tilemap.load('map3.json')

    def load_assets(self):
        assets = {
            "decor": import_imgs("assets/imgs/tiles/decor"),
            "large_decor": import_imgs("assets/imgs/tiles/large_decor"),
            'dark_grass': import_imgs("assets/imgs/tiles/dark_grass"),
            'grass_water': import_imgs("assets/imgs/tiles/grass_water"),
            'sand': import_imgs("assets/imgs/tiles/sand"),
            #'player': import_img('assets/imgs/entities/player.png'),
            'player/idle': Animation('assets/imgs/entities/human2/idle', duration=1800, loop=True, autostart=True),
            'player/run': Animation('assets/imgs/entities/human2/run', duration=600, loop=True, autostart=True)
            #'player/jump': Animation(import_imgs('data/images/entities/player/jump')),
            #'player/slide': Animation(import_imgs('data/images/entities/player/slide')),
            #'player/wall_slide': Animation(import_imgs('data/images/entities/player/wall_slide'))
        }

        return assets
        
    def handle_input(self, event):
        super().handle_input(event)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                self.switch_state('menu') 

            if event.key == pygame.K_LEFT:
                self.movement[0] = True
            if event.key == pygame.K_RIGHT:
                self.movement[1] = True

            if event.key == pygame.K_DOWN:
                self.movement[3] = True
            if event.key == pygame.K_UP:
                self.movement[2] = True

            if event.key == pygame.K_x:
                self.player.dash()

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                self.movement[0] = False
            if event.key == pygame.K_RIGHT:
                self.movement[1] = False
            if event.key == pygame.K_DOWN:
                self.movement[3] = False
            if event.key == pygame.K_UP:
                self.movement[2] = False

            if event.key == pygame.K_e:
                self.assets['player/idle'] = Animation(import_imgs('data/images/entities/human2/idle'), img_dur=6)
                self.assets['player/run'] = Animation(import_imgs('data/images/entities/human2/run'), img_dur=4)
            if event.key == pygame.K_t:
                self.assets['player/idle'] = Animation(import_imgs('data/images/entities/human1/idle'), img_dur=6)
                self.assets['player/run'] = Animation(import_imgs('data/images/entities/human1/run'), img_dur=4)
    def update(self, dt):
        
        self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) / 30
        self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1]) / 30
        render_scroll = (int(self.scroll[0]), int(self.scroll[1]))
        
        
        
        self.player.update(self.tilemap, (self.movement[1] - self.movement[0], self.movement[3] - self.movement[2]))

        self.tilemap.render(self.display,self.player, offset=render_scroll)
        
        #self.player.render(self.display, offset=render_scroll)
        
        super().update(dt)

    def draw(self):
       self.screen.fill("#CC2828")
       
       self.screen.blit(pygame.transform.scale2x(self.display), (0, 0))

       self.display.fill("black")
       super().draw()
