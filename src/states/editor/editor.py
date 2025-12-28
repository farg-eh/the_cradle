import pygame
from src.states import State
from src.utils import import_imgs, get_abs_path, Pos, Rect, import_imgs_as_dict
from src.settings import SCALE, TILE_SIZE, SW, SH
from .camera import Tilemap2, Camera
from .overlay import Overlay
from src.ui import PopPanel, TextField

class Editor(State):
    # represents the folders containing assets
    tile_list = ['dark_grass', 'grass_water', 'road', 'decor', 'large_decor', 'sand', 'mat', 'dirt', 'market', 'palace_in', 'palace_in_walls', 'palace_out', 'carpet_red', 'carpet_green', 'carpet_blue', 'static_humans']
    def __init__(self, core, map_to_open="river_side_water"):
        super().__init__(core, 'editor')

        # tile info 
        self.tile_group = 0
        self.tile_variant = 0

        self.assets = self.load_assets()
        self.camera = Camera()
        
        # tile map load
        self.tilemap = Tilemap2(self)
        self.current_layer = list(self.tilemap.layers.keys())[0]
        map_to_open = map_to_open
        self.map_name = map_to_open if map_to_open else 'testmap'
        
        try:
            self.tilemap.load(self.map_name)
        except FileNotFoundError:
            pass

        # move the camera focus to the center of the map
        self.camera.focus_pos.x = self.tilemap.get_map_rect().centerx - SW/2
        self.camera.focus_pos.y = self.tilemap.get_map_rect().centery - SH/2

        self.scroll = [0, 0]
        self.clicking = False
        self.right_clicking = False
        self.shift = False
        self.ctrl = False
        self.ongrid = True
        self.mpos = (0, 0)

        # size
        map_rect = self.tilemap.get_map_rect()
        self.map_size = int(map_rect.width), int(map_rect.height)
        self.min_point = map_rect.topleft

        # grid
        self.show_grid = True
        self.grid_surf = pygame.Surface(self.screen.size, pygame.SRCALPHA)

        # overlay
        self.overlay = Overlay(self)

        # saving
        self.last_change_saved = True

        # undo redo 
        self.made_change = False # this is for tiles and it only registers after u release clicking the mouse 
        self.made_one_change = False # this if for outside actions such as deleting a layer 
        self.undo_stack = [self.tilemap.copy()]
        self.redo_stack = []


        # this is for drawing shapes
        self.curr_shape_type = 'rectangle'
        self.m_shape_pos1 = None
        self.m_shape_pos2 = None
        

    def load_assets(self):
        # import imgs 
        assets = {
                #'dark_grass': import_imgs("assets/imgs/tiles/dark_grass"),
                #'grass_water': import_imgs("assets/imgs/tiles/grass_water"),
                #"decor": import_imgs("assets/imgs/tiles/decor"),
                #"large_decor": import_imgs("assets/imgs/tiles/large_decor"),
                #'sand': import_imgs("assets/imgs/tiles/sand"),
                'icons': import_imgs_as_dict("assets/imgs/icons")
                }
        for tile_dir in self.tile_list:
            assets[tile_dir] = import_imgs(f"assets/imgs/tiles/{tile_dir}")

        return assets
    
    def handle_input(self, event):
        super().handle_input(event)
        #if event.type == pygame.KEYDOWN:
        #   if event.key == pygame.K_1:
        #       self.switch_state('menu')

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.clicking = True
                # add tile
               # if not self.ongrid:
               #     self.tilemap.offgrid_tiles.append({'type': self.tile_list[self.tile_group], 'variant': self.tile_variant, 'pos': (self.mpos[0] + self.scroll[0], self.mpos[1] + self.scroll[1])})
            if event.button == 3:
                # remove tile
                self.right_clicking = True
            if self.shift and self.root.mouse_stack and self.root.mouse_stack[-1] == self.root:
                if event.button == 4:
                    self.tile_group = (self.tile_group - 1) % len(self.tile_list)
                    self.tile_variant = 0
                if event.button == 5:
                    self.tile_group = (self.tile_group + 1) % len(self.tile_list)
                    self.tile_variant = 0
            elif self.root.mouse_stack and self.root.mouse_stack[-1] == self.root:
                if event.button == 4:
                    self.tile_variant = (self.tile_variant - 1) % len(self.assets[self.tile_list[self.tile_group]])
                if event.button == 5:
                    self.tile_variant = (self.tile_variant + 1) % len(self.assets[self.tile_list[self.tile_group]])

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.clicking = False
            if event.button == 3:
                self.right_clicking = False

        if event.type == pygame.KEYDOWN:
            if event.key >= pygame.K_1 <= pygame.K_9:
                #print(event.key - pygame.K_1)
                if self.overlay.items_dock.parent.hidden:
                    self.overlay.set_curr_tile(event.key - pygame.K_1)
                else:
                    self.overlay.set_dock_tile(event.key - pygame.K_1)
                
            if event.key == pygame.K_g:
                self.ongrid = not self.ongrid
                self.current_layer = 'objects'
            if event.key == pygame.K_t:
                #self.tilemap.autotile()
                self.current_layer = 'tiles'
            if event.key == pygame.K_b:
                self.current_layer = 'meta_info'
            if event.key == pygame.K_s and self.ctrl:
                self.tilemap.save(self.map_name)
                self.last_change_saved = True
            if event.key == pygame.K_LSHIFT:
                self.shift = True

            if event.key == pygame.K_LCTRL:
                self.ctrl = True

            if event.key == pygame.K_DOWN and self.shift:
                self.camera.cycle_zoom_level_backward()
            if event.key == pygame.K_UP and self.shift:
                self.camera.cycle_zoom_level_forward()

            if event.key == pygame.K_z and self.ctrl and not self.shift:
                self.undo_action()

            if event.key == pygame.K_z and self.ctrl and self.shift:
                self.redo_action()

            
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LSHIFT:
                self.shift = False
            if event.key == pygame.K_LCTRL:
                self.ctrl = False

    def handle_hold_keys(self, dt):
        keys = pygame.key.get_pressed()
        # WASD
        if self.root.mouse_stack and self.root.mouse_stack[-1] == self.root:
            mv_dir = Pos(int(keys[pygame.K_d]) - int(keys[pygame.K_a]), int(keys[pygame.K_s]) - int(keys[pygame.K_w]))
            mv_dir = mv_dir.normalize() if mv_dir.magnitude() > 1.0 else mv_dir # normalize movement vec so diagonal movement isntfaster than normal one
        else:
            mv_dir = Pos(0, 0)
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
        map_rect = self.tilemap.get_map_rect()
        self.map_size = int(map_rect.width), int(map_rect.height)
        self.min_point = map_rect.topleft


    def _handle_tiles_layers_update(self, mouse_tile_pos, curr_item, layer):
        # tile_pos
        if layer['type'] == 'tiles_layer':
            tile_loc = str(mouse_tile_pos[0]) + ';' + str(mouse_tile_pos[1])
            if curr_item == "pen":
                if self.mouse.l_down: # add item 

                    # cancel if its the same tile 
                    if self.tilemap.layers[self.current_layer]['elements'].get(tile_loc):
                        tile_to_change = self.tilemap.layers[self.current_layer]['elements'][tile_loc]
                        if tile_to_change['type'] == self.tile_list[self.tile_group] and tile_to_change['variant'] == self.tile_variant:
                            return

                    # add element to curr layer
                    self.tilemap.add_element({'type': self.tile_list[self.tile_group],'variant': self.tile_variant, 'pos': mouse_tile_pos}, self.current_layer)
                    # update map size 
                    self._update_size_info()
                    # register it as a change so its undo-able
                    self.made_change = True
                elif self.mouse.r_down: # remove item
                   # remove tile from curr layer if it exist in it
                   if tile_loc in layer['elements']:
                       del layer['elements'][tile_loc]
                       # update map size
                       self._update_size_info()
                       # register as an undo-able change
                       self.made_change = True

            elif curr_item == 'bucket':
                if self.mouse.l_down_once:
                    if self.tilemap.is_tile_pos_in_map(mouse_tile_pos):
                        # fill
                        tile = layer['elements'].get(tile_loc, {'type':None, 'variant':None, 'pos': mouse_tile_pos}).copy()  # tile clicked 
                        curr_tile = {'type': self.tile_list[self.tile_group], 'variant': self.tile_variant, 'pos': tile['pos']} # tile selected to paint with
                        self._bucket_fill(mouse_tile_pos, tile, curr_tile)
                        # register change
                        self.made_change = True

    def _handle_objects_layers_update(self, mouse_tile_pos, curr_item, layer):
        if layer['type'] == 'objects_layer':
            if curr_item == "pen":
                if self.mouse.l_down_once:
                    # add element
                    pos = self.mpos
                    self.tilemap.add_element({'type': self.tile_list[self.tile_group],'variant': self.tile_variant, 'pos': pos}, self.current_layer)
                    # register as undo-able action
                    self.made_change = True
                elif self.mouse.r_down: # remove item
                   # remove tile from curr layer if it exist in it
                   for tile in layer['elements'].copy():
                       tile_img = self.assets[tile['type']][tile['variant']]
                       tile_r = pygame.Rect(tile['pos'][0], tile['pos'][1], tile_img.get_width(), tile_img.get_height())
                       if tile_r.collidepoint(self.mpos):
                           layer['elements'].remove(tile)
                           self.made_change = True
            elif curr_item == 'bucket':
                pass
                # send a notification that bucket tool only works on layers of type tiles_layer

    def _handle_meta_info_layers_update(self, mouse_tile_pos, curr_item, layer):
        if layer['type'] == 'meta_info_layer':
            # TODO: instead of 'pen' i should have other shapes implemented
            if curr_item == "pen":
                # okay lets start
                if self.mouse.l_down_once:
                    self.m_shape_pos1 = Pos(*self.mpos)
                    self.m_shape_pos2 = None

                elif self.mouse.l_up_once:
                    self.m_shape_pos2 = Pos(self.mpos[0], self.mpos[1])
                    # here we should spawn the shape in the current layer
                    rect = Rect.from_2pos(self.m_shape_pos1, self.m_shape_pos2)
                    # TODO: i really should have other shapes implemented
                    # if the rect is big enough
                    if rect.width > 3 and rect.height > 3:
                        self.tilemap.add_element({'shape': 'rectangle', 'values': [*rect.topleft, *rect.size],
                                                  'name': None, 'pos': rect.topleft}, self.current_layer)
                        self.m_shape_pos1 = None
                        self.made_change = True

                # removing shapes 
                elif self.shift and self.mouse.r_up_once:
                    for shape in layer['elements']:
                        if Rect(*shape['values']).collidepoint(self.mpos):
                            layer['elements'].remove(shape)
                            self.made_change = True
                elif self.mouse.r_up_once:
                    for shape in layer['elements']:
                        if Rect(*shape['values']).collidepoint(self.mpos):
                            if shape['name'] == None:
                                shape['name'] = ''
                            tf = TextField(text=shape['name'], width=100, color="#b96d4a", placeholder="object name",text_color="#eec39a", selected_color="#bb3736" )
                            tf.func = lambda s=shape, tf=tf: s.update(name=tf.value)
                            pp, p, vl = PopPanel.with_empty_panel(tf, size=(150, 70))
                            tf.move_to_by_center((vl.padding_rect.width/2, vl.padding_rect.height/2))
                            self.root.add_child(pp)
                            self.made_change = True

            elif curr_item == 'bucket': 
                pass
                # send a notification that this doesnt work here 


    def _handle_tilemap_updates(self):
        if len(self.root.mouse_stack) == 1: # if the mouse is not on any ui elmenet then its on the level editor

            tile_pos = (int((self.mpos[0] ) // self.tilemap.tile_size), int((self.mpos[1] ) // self.tilemap.tile_size))
            curr_layer = self.tilemap.layers[self.current_layer]
            curr_item = self.overlay.selected_item

            # handle layers if the current tool can modify them
            if curr_item in ['pen', 'bucket']:
                self._handle_tiles_layers_update(tile_pos, curr_item, curr_layer)
                self._handle_objects_layers_update(tile_pos, curr_item, curr_layer)
                self._handle_meta_info_layers_update(tile_pos, curr_item, curr_layer)


    def add_layer(self, name, layer_type="tiles_layer"):
        if name in self.tilemap.layers:
            self.core.notifier.notify("Layer '{name}' already exists")
            return
        
        new_index = len(self.tilemap.layers)
        elements = {} if layer_type=="tiles_layer" else []
        self.tilemap.layers[name] = {
            'type': layer_type,
            'index': new_index,
            'elements': elements,
            'hidden': False
        }
        self.overlay._update_layers_elements()
        self.made_one_change = True

    def remove_layer(self, name):
        del self.tilemap.layers[name]
        self.current_layer = list(self.tilemap.layers.keys())[0]
        # re index layers to keep index order consistent
        for i, (layer_name, layer) in enumerate(sorted(list(self.tilemap.layers.items()), key=lambda x: x[1]['index'])):
            layer['index'] = i
        self.overlay._update_layers_elements()
        self.made_one_change = True

    def move_layer(self, name, direction='up'):
        layers = self.tilemap.layers
        layer = layers[name]
        current_index = layer['index']

        # get a list of (name, layer) pairs sorted by index
        sorted_layers = sorted(layers.items(), key=lambda x: x[1]['index'])
        max_index = len(sorted_layers) - 1

        if direction == 'up' and current_index > 0:
            # find the layer above and swap indexes
            for lname, ldata in layers.items():
                if ldata['index'] == current_index - 1:
                    ldata['index'], layer['index'] = layer['index'], ldata['index']
                    break

        elif direction == 'down' and current_index < max_index:
            # find the layer below and swap indexes
            for lname, ldata in layers.items():
                if ldata['index'] == current_index + 1:
                    ldata['index'], layer['index'] = layer['index'], ldata['index']
                    break

        else:
            self.core.notifier.notify(f"cant move this layer {direction}")
            return

        self.overlay._update_layers_elements()
        self.made_one_change = True

    def rename_layer(self, old_name, new_name):
        layers = self.tilemap.layers

        # ignore if its the same name 
        if old_name == new_name:
            return
        
        # prevent empty names
        if not new_name:
            self.core.notifier.notify(f"new layer name cannot be empty")

        # check if the old layer exists
        if old_name not in layers:
            self.core.notifier.notify(f"Layer '{old_name}' does not exist")
            return
        # prevent name conflicts
        if new_name in layers:
            self.core.notifier.notify(f"Layer '{new_name}' already exists")
            return

        # move the layer data under the new name
        layers[new_name] = layers.pop(old_name)
        # update current layer if it was the renamed one
        if self.current_layer == old_name:
            self.current_layer = new_name
        self.overlay._update_layers_elements()
        self.made_one_change = True

    def update(self, dt):
        #self.display.fill((0, 0, 0))
        self.handle_hold_keys(dt)
        self.camera.update(dt)
        self.overlay.update(dt, self.mouse)
        self.mpos = self.camera.get_cam_mouse_pos(pygame.mouse.get_pos())

        # handle tile map updates 
        self._handle_tilemap_updates()

        # handle undo state saving
        if ((self.mouse.l_up_once or self.mouse.r_up_once) and self.made_change) or self.made_one_change:
            self.undo_stack.append(self.tilemap.copy())
            #print(self.undo_stack)
            self.redo_stack.clear()
            self.made_change = False
            self.made_one_change = False
            self.last_change_saved = False

        #print(f"map size in tiles : {self.tilemap.get_size_in_tiles()}")
        if len(self.undo_stack) > 50:
            self.undo_stack = self.undo_stack[1:]

        if len(self.redo_stack) > 50:
            self.undo_stack = self.undo_stack[1:]


        super().update(dt)

    def undo_action(self):
        if len(self.undo_stack) <= 1: return
        self.redo_stack.append(self.undo_stack[-1].copy())
        self.undo_stack.pop()

        
        # FIXME: this is a hack to ignore changing the hiding state of layers (u can fix it by having a seperate editor state settings 
        # ~~~~~~~~~~~~~~~
        old_tilemap_layers = self.tilemap.layers.copy()
        hidden_col = [l['hidden'] for l in old_tilemap_layers.values()]
        self.tilemap = self.undo_stack[-1].copy()

        if len(hidden_col) == len(self.tilemap.layers):
            for i, v in enumerate(hidden_col):
                keys = list(self.tilemap.layers.keys())
                self.tilemap.layers[keys[i]]['hidden'] = v
        #~~~~~~~~~~~~~~~~~~~~~
        #self.tilemap = self.undo_stack[-1].copy()
        # TODO maybe i should find a better way here 
        # FIXME memory leak
        self.overlay._update_layers_elements()

    def redo_action(self):
        if len(self.redo_stack) == 0: return
        
        # FIXME: this is a hack to ignore changing the hiding state of layers (u can fix it by having a seperate editor state settings 
        # ~~~~~~~~~~~~~~~
        hidden_col = [l['hidden'] for l in self.tilemap.layers.values()]
        tilemap = self.redo_stack.pop()

        if len(hidden_col) == len(self.tilemap.layers):
            for i, v in enumerate(hidden_col):
                keys = list(self.tilemap.layers.keys())
                tilemap.layers[keys[i]]['hidden'] = v
        #~~~~~~~~~~~~~~~~~~~~~
        #tilemap = self.redo_stack.pop()
        self.undo_stack.append(tilemap)
        self.tilemap = tilemap
        # TODO maybe i should find a better way here 
        # FIXME memory leak
        self.overlay._update_layers_elements()


    # iterative version ( currently in use )
    def _bucket_fill(self, tile_pos, tile_to_change, new_tile):
        # cancel if ur trying to fill a tile with its own self (ex filling grass with grass)
        if tile_to_change['type'] == new_tile['type'] and tile_to_change['variant'] == new_tile['variant']: return
        layer = self.tilemap.layers[self.current_layer]
        # lets make it iterative instead of recursive 
        bucket_queue = []  # should be a queue will be filled with tiles to change posisions
        bucket_queue.append(tile_pos)

        while bucket_queue:
            curr_tile_pos = bucket_queue.pop()
            for t in self.tilemap.tiles_around(curr_tile_pos, self.current_layer, plus_pattern=True):
                # check if the current tile is the tile i wanna change (if its of the target type and varient then i want to change it)
                if t['type'] == tile_to_change['type'] and t['variant'] == tile_to_change['variant']:
                    # change it 
                    self.tilemap.add_element({'pos':t['pos'],'type': new_tile['type'],'variant': new_tile['variant']}, self.current_layer)
                    # if its not the selected tile of the + (the center one) then add it to the queue
                    if t['pos'] != curr_tile_pos:
                        bucket_queue.append(t['pos'])

    # recursive version just for reference 
    def _bucket_fill2(self, tile_pos, tile_to_change, new_tile):
        # cancel if ur trying to fill a tile with its own self (ex filling grass with grass)
        if tile_to_change['type'] == new_tile['type'] and tile_to_change['variant'] == new_tile['variant']: return
        layer = self.tilemap.layers[self.current_layer]

        for t in self.tilemap.tiles_around(tile_pos, self.current_layer, plus_pattern=True):
            #print(curr_tile_pos)
            # check if the current tile is the tile i wanna change 
            if t['type'] == tile_to_change['type'] and t['variant'] == tile_to_change['variant']:

                t['type'], t['variant'] = new_tile['type'], new_tile['variant']
                self.tilemap.add_element(t, self.current_layer)

                self._bucket_fill2(t['pos'], tile_to_change, new_tile)


    def draw_grid(self, surf):
        tile_size = TILE_SIZE 
        line_color = pygame.Color("#C5CAC7")  # grid color
        line_color.a = 35  # grid alpha
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
       if self.overlay.curr_item_box.og_img != current_tile_img:
           self.overlay.curr_item_box.change_image(current_tile_img)

       current_tile_img.set_alpha(150)


       # draw everything  

       #print(self.tilemap)
       for layer_name, layer in self.tilemap.layers.items():
           if layer.get('hidden'): 
               #print("hidden layer" + str(layer) + " : " + layer_name)
               continue
           elements = layer['elements'].values() if isinstance(layer['elements'], dict) else layer['elements']
           if layer['type'] == 'meta_info_layer':
               for shape in elements:
                   if shape['shape'] == 'rectangle':
                       rect = Rect(*shape['values'])
                       c  = pygame.Color("#C5CAC7") if not shape['name'] else pygame.Color("#856Ad7") # same as grid color
                       c2 = pygame.Color(c)
                       c2.a = 70
                       self.camera.add_to_draw(layer['index'], rect.get_surf(color=c2, border_color=c), rect.topleft)
           else:
               for tile in elements:
                   #print(f'drew {tile}')
                   surf = self.assets[tile['type']][tile['variant']]
                   pos = tile['pos'] if layer['type'] != 'tiles_layer' else (tile['pos'][0] * TILE_SIZE, tile['pos'][1] * TILE_SIZE)
                   self.camera.add_to_draw(layer['index'],surf, pos)
       self.camera.draw_everything_on(self.screen)

       # tile position of mouse
       tile_pos = (int((self.mpos[0]) // self.tilemap.tile_size), int((self.mpos[1] ) // self.tilemap.tile_size))

       if len(self.root.mouse_stack) == 1: # if the mouse is not on any ui elmenet then its on the level editor
           # display ghost of tile at mouse pos
           if self.tilemap.layers[self.current_layer]['type'] == 'tiles_layer':
               # 99 specifys the layer so this means that the transparent tile will alway show on top of everything 
               self.camera.add_to_draw(99,current_tile_img, (tile_pos[0] * TILE_SIZE, tile_pos[1] * TILE_SIZE))
           elif self.tilemap.layers[self.current_layer]['type'] == 'objects_layer':
               self.camera.add_to_draw(99, current_tile_img, self.mpos) 

#       # show current selected tile img 
       #self.screen.blit(current_tile_img, (5, 5))


       # draw the overlay
       self.overlay.draw(self.screen)

       #self.screen.blit(pygame.transform.scale2x(self.display), (0, 0))
       if self.show_grid:
           self.grid_surf.fill((0, 0, 0, 0))
           self.draw_grid(self.grid_surf)
           self.screen.blit(self.grid_surf, (0, 0))

       # draw selection
       if self.m_shape_pos1 and not self.m_shape_pos2:
           c  = pygame.Color("#f75402")  # orange
           c2 = pygame.Color(c)
           c2.a = 70
           p = self.camera.get_cam_world_pos(self.m_shape_pos1)
           r = Rect.from_2pos(p, self.mouse.pos)
           r.draw(self.screen, color=c2, border_color=c, draw_as_surf=True)
       super().draw()
