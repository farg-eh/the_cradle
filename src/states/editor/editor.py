import pygame
import sys
from src.states import State
from src.utils import import_imgs, get_abs_path, Pos, import_imgs_as_dict
from src.tiles import Tilemap
from src.settings import SCALE, TILE_SIZE
from .camera import Tilemap2, Camera
from .overlay import Overlay

class Editor(State):
    def __init__(self, core):
        super().__init__(core, 'menu')
        self.assets = self.load_assets()
        self.camera = Camera()
        
        # tile map load
        self.tilemap = Tilemap2(self)
        self.current_layer = list(self.tilemap.layers.keys())[0]
        
        try:
            self.tilemap.load('testmap')
        except FileNotFoundError:
            pass

        
        self.scroll = [0, 0]
        
        self.tile_list = ['dark_grass', 'grass_water', 'decor', 'large_decor', 'sand']
        self.tile_group = 0
        self.tile_variant = 0
        
        self.clicking = False
        self.right_clicking = False
        self.shift = False
        self.ctrl = False
        self.ongrid = True
        self.mpos = (0, 0)

        # size
        size_info = self.tilemap.calculate_size()
        self.map_size = size_info[0]     
        self.min_point = size_info[1]

        # grid
        self.show_grid = True
        self.grid_surf = pygame.Surface(self.screen.size, pygame.SRCALPHA)

        # overlay
        self.overlay = Overlay(self)

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
        super().handle_input(event)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                self.switch_state('menu') 

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.clicking = True
                # add tile
               # if not self.ongrid:
               #     self.tilemap.offgrid_tiles.append({'type': self.tile_list[self.tile_group], 'variant': self.tile_variant, 'pos': (self.mpos[0] + self.scroll[0], self.mpos[1] + self.scroll[1])})
            if event.button == 3:
                # remove tile
                self.right_clicking = True
            if self.shift:
                if event.button == 4:
                    self.tile_variant = (self.tile_variant - 1) % len(self.assets[self.tile_list[self.tile_group]])
                if event.button == 5:
                    self.tile_variant = (self.tile_variant + 1) % len(self.assets[self.tile_list[self.tile_group]])
            else:
                if event.button == 4:
                    self.tile_group = (self.tile_group - 1) % len(self.tile_list)
                    self.tile_variant = 0
                if event.button == 5:
                    self.tile_group = (self.tile_group + 1) % len(self.tile_list)
                    self.tile_variant = 0
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.clicking = False
            if event.button == 3:
                self.right_clicking = False

        if event.type == pygame.KEYDOWN:
                
            if event.key == pygame.K_g:
                self.ongrid = not self.ongrid
                self.current_layer = 'objects'
            if event.key == pygame.K_t:
                #self.tilemap.autotile()
                self.current_layer = 'tiles'
            if event.key == pygame.K_b:
                self.current_layer = 'meta_info'
            if event.key == pygame.K_o:
                self.tilemap.save('testmap')
            if event.key == pygame.K_LSHIFT:
                self.shift = True

            if event.key == pygame.K_LCTRL:
                self.ctrl = True

            if event.key == pygame.K_DOWN and self.shift:
                self.camera.cycle_zoom_level_backward()
            if event.key == pygame.K_UP and self.shift:
                self.camera.cycle_zoom_level_forward()
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LSHIFT:
                self.shift = False
            if event.key == pygame.K_LCTRL:
                self.ctrl = False

    def handle_hold_keys(self, dt):
        keys = pygame.key.get_pressed()
        mv_dir = Pos(int(keys[pygame.K_d]) - int(keys[pygame.K_a]), int(keys[pygame.K_s]) - int(keys[pygame.K_w]))
        mv_dir = mv_dir.normalize() if mv_dir.magnitude() > 1.0 else mv_dir
        cam_speed = 300
        self.camera.focus_pos.x += cam_speed * mv_dir.x * dt
        self.camera.focus_pos.y += cam_speed * mv_dir.y * dt

        #print(self.camera.focus_pos)
        #print(self.camera._cam_pos)

        if self.shift and self.ctrl:
            self.camera.zoom_value += self.mouse.wheel_dir / 20
            self.camera.zoom_value = pygame.math.clamp(self.camera.zoom_value, 0.5, 2)

    def _update_size_info(self):
        size_info = self.tilemap.calculate_size()
        self.map_size = size_info[0]     
        self.min_point = size_info[1]


    def update(self, dt):
        #self.display.fill((0, 0, 0))
        self.handle_hold_keys(dt)
        self.camera.update(dt)
       
        print(self.root.mouse_stack)
        if len(self.root.mouse_stack) == 1: # if the mouse is not on any ui elmenet then its on the level editor
                
            # TODO: clean later
            self.mpos = self.camera.get_cam_mouse_pos(pygame.mouse.get_pos())
            #self.mpos = (self.mpos[0] / SCALE, self.mpos[1] / SCALE) # mouse level relative pos
            # mouse level relative tile pos
            tile_pos = (int((self.mpos[0] ) // self.tilemap.tile_size), int((self.mpos[1] ) // self.tilemap.tile_size))
            # add tiles
            if self.clicking and self.tilemap.layers[self.current_layer]['type'] == 'tiles_layer':
                surf = self.assets[self.tile_list[self.tile_group]][self.tile_variant]
                pos = tile_pos 
                self.tilemap.add_element({'type': self.tile_list[self.tile_group],'variant': self.tile_variant, 'pos': pos}, self.current_layer)
                self._update_size_info()

            # add offgird tiles (objects)
            if self.mouse.l_down_once and self.tilemap.layers[self.current_layer]['type'] == 'objects_layer':
                surf = self.assets[self.tile_list[self.tile_group]][self.tile_variant]
                pos = self.mpos
                self.tilemap.add_element({'type': self.tile_list[self.tile_group],'variant': self.tile_variant, 'pos': pos}, self.current_layer)

            # remove tiles
            if self.mouse.r_down:
                layer = self.tilemap.layers[self.current_layer]
                # tiles
                if layer['type'] == 'tiles_layer':
                   tile_loc = str(tile_pos[0]) + ';' + str(tile_pos[1])
                   # remove tile from grid 
                   if tile_loc in layer['elements']:
                       del layer['elements'][tile_loc]
                       self._update_size_info()
                # objects
                if layer['type'] == 'objects_layer':
                   for tile in layer['elements'].copy():
                       tile_img = self.assets[tile['type']][tile['variant']]
                       tile_r = pygame.Rect(tile['pos'][0], tile['pos'][1], tile_img.get_width(), tile_img.get_height())
                       if tile_r.collidepoint(self.mpos):
                           layer['elements'].remove(tile)

        self.overlay.update(dt, self.mouse)

        super().update(dt)

    def draw_grid(self, surf):
        tile_size = TILE_SIZE 
        line_color = pygame.Color("#C5CAC7")
        line_color.a = 10
        tiles = self.map_size[0] // TILE_SIZE, self.map_size[1] // TILE_SIZE
        for i in range(tiles[0]+1):
            start_pos = (self.camera.get_cam_world_pos((self.min_point[0] + i*tile_size, self.min_point[1])))
            end_pos = self.camera.get_cam_world_pos((self.min_point[0] + i*tile_size, self.min_point[1] + self.map_size[1]))
            pygame.draw.line(surf, line_color, start_pos, end_pos)
        for i in range(tiles[1]+1):
            start_pos = (self.camera.get_cam_world_pos((self.min_point[0], self.min_point[1]+i*tile_size)))
            end_pos = self.camera.get_cam_world_pos((self.min_point[0]+self.map_size[0] , self.min_point[1]+i*tile_size))
            pygame.draw.line(surf, line_color, start_pos, end_pos)

    def draw(self):
       self.screen.fill("#262E2B")   
       
       # get images from assets ( the currently selected one  
       current_tile_img = self.assets[self.tile_list[self.tile_group]][self.tile_variant].copy()
       current_tile_img.set_alpha(100)

       # draw everything  
       for layer_name, layer in self.tilemap.layers.items():
           elements = layer['elements'].values() if isinstance(layer['elements'], dict) else layer['elements']
           for tile in elements:
               #print(f'drew {tile}')
               surf = self.assets[tile['type']][tile['variant']]
               pos = tile['pos'] if layer['type'] != 'tiles_layer' else (tile['pos'][0] * TILE_SIZE, tile['pos'][1] * TILE_SIZE)
               self.camera.add_to_draw(layer['index'],surf, pos)
       self.camera.draw_everything_on(self.screen)

       if self.show_grid:
           self.grid_surf.fill((0, 0, 0, 0))
           self.draw_grid(self.grid_surf)
       # tile position of mouse
       tile_pos = (int((self.mpos[0]) // self.tilemap.tile_size), int((self.mpos[1] ) // self.tilemap.tile_size))

       if len(self.root.mouse_stack) == 1: # if the mouse is not on any ui elmenet then its on the level editor
           # display ghost of tile at mouse pos
           if self.tilemap.layers[self.current_layer]['type'] == 'tiles_layer':
               self.camera.add_to_draw(99,current_tile_img, (tile_pos[0] * TILE_SIZE, tile_pos[1] * TILE_SIZE))
           elif self.tilemap.layers[self.current_layer]['type'] == 'objects_layer':
               self.camera.add_to_draw(99, current_tile_img, self.mpos) 

#       # show current selected img 
       self.screen.blit(current_tile_img, (5, 5))

       #self.overlay.draw(self.screen)

       #self.screen.blit(pygame.transform.scale2x(self.display), (0, 0))
       self.screen.blit(self.grid_surf, (0, 0))
       super().draw()
