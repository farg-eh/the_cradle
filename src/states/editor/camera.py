import pygame
from src.tiles import Tilemap
from src.utils import Pos, Rect, smooth_step_lerp

# tile map imports
import json
from datetime import datetime
from src.utils import get_abs_path, Timer
from src.settings import TILE_SIZE, SW, SH




class Camera:
    def __init__(self) -> None:

        # zoom values
        self.zoom_levels = [1.0, 2.0, 0.5]
        self.curr_zoom_index = 0
        self.zoom_value = self.zoom_levels[self.curr_zoom_index]
        self.target_zoom_value = self.zoom_value
        self.prev_zoom_value = self.zoom_value

        # zoom transition
        self.zoom_timer = Timer(duration=500)

        # zoom surfs and rects
        self.zoom_surf = pygame.Surface((SW*2, SH*2),pygame.SRCALPHA) # 1280, 720 for zoom effect
        self.zoom_surf_size = Pos(*self.zoom_surf.size)
        self.zoom_rect = self.zoom_surf.get_rect(center = (SW/2, SH/2))
        self.scaled_zoom_surf = pygame.Surface((0, 0), pygame.SRCALPHA)
        self.scaled_zoom_rect = self.scaled_zoom_surf.get_rect(center = self.zoom_rect.center)
        self._update_scaled_surf()

        # buffer to draw all layers 
        self.things_to_draw = {} # layer_index : [{surface, pos}]

        # positions 
        self._cam_pos = Pos(0, 0)
        self.focus_pos = Pos(0, 0)

        # zoom surf (cam_surf) offset
        x, y = self.zoom_surf_size.x // 2 - SW//2, self.zoom_surf_size.y//2 - SH//2
        self.zoom_offset = Pos(x, y)

    def cycle_zoom_level_forward(self):
        if self.zoom_timer.active: return
        self.curr_zoom_index = (self.curr_zoom_index + 1)%len(self.zoom_levels)
        self.prev_zoom_value = self.target_zoom_value
        self.target_zoom_value = self.zoom_levels[self.curr_zoom_index]
        if self.zoom_value != self.target_zoom_value:
            self.zoom_timer.activate()


    def cycle_zoom_level_backward(self):
        print(0)
        if self.zoom_timer.active: return
        print('press')
        self.curr_zoom_index = (self.curr_zoom_index - 1)%len(self.zoom_levels)
        self.prev_zoom_value = self.target_zoom_value
        self.target_zoom_value = self.zoom_levels[self.curr_zoom_index]
        if self.zoom_value != self.target_zoom_value:
            print('press2')
            self.zoom_timer.activate()


    # screen to cam
    def get_cam_mouse_pos(self, mouse_pos):
        mpos = mouse_pos[0]/self.zoom_value, mouse_pos[1]/self.zoom_value
        offset = self._cam_pos - self.zoom_offset
        return (mpos[0] + offset.x)-self.scaled_zoom_rect.x/self.zoom_value , mpos[1] + offset.y - self.scaled_zoom_rect.y/self.zoom_value

    def get_cam_world_pos(self, world_pos):
        wx, wy = world_pos
        sx = self.scaled_zoom_rect.x + (wx - self._cam_pos.x + self.zoom_offset.x) * self.zoom_value
        sy = self.scaled_zoom_rect.y + (wy - self._cam_pos.y + self.zoom_offset.y) * self.zoom_value
        return sx, sy

    def _update_scaled_surf(self):
        self.scaled_zoom_surf = pygame.transform.scale(self.zoom_surf,self.zoom_surf_size * self.zoom_value) 
        self.scaled_zoom_rect = self.scaled_zoom_surf.get_rect(center = (SW/2, SH/2))

    def add_to_draw(self,layer_index, surf, pos: int|float):

        if self.things_to_draw.get(layer_index):
            self.things_to_draw[layer_index].append({'surf': surf, 'pos': pos})
        else:
            self.things_to_draw[layer_index] = [{'surf': surf, 'pos': pos}]

    def draw_everything_on(self, surf):
        self.zoom_surf.fill((0, 0, 0, 0))
        draw_list = self.things_to_draw.items()
        draw_list = sorted(draw_list, key=lambda x: x[0])
#        print('ok')
#        print(draw_list)
        for i, e_list in draw_list:  # _ = layer_index
            for e in e_list:
                #print(e)
                self.zoom_surf.blit(e['surf'], (e['pos'][0] - self._cam_pos[0] + self.zoom_offset.x, e['pos'][1] - self._cam_pos[1] + self.zoom_offset.y))
        # clear the draw buffer
        self.things_to_draw = {}
        self._update_scaled_surf()
        surf.blit(self.scaled_zoom_surf, self.scaled_zoom_rect)



    def _move(self, dt):
        # find the vector between a & b 
        #vec = self._cam_pos - self.focus_pos
        dist = self._cam_pos.distance_to(self.focus_pos)
        if dist < 1:
            self._cam_pos.x, self._cam_pos.y = self.focus_pos.x, self.focus_pos.y
            return
        # now we will use a smooth step function to map distance to speed
        max_speed = 600
        min_speed = 25
        #k = 0.8
        max_dist = 200 * self.zoom_value
        t = pygame.math.clamp( dist/max_dist, 0, 1)
        move_amount = smooth_step_lerp(min_speed, max_speed, t)
        self._cam_pos.move_towards_ip(self.focus_pos, move_amount*dt)

    def handle_transition_timer(self):
        if self.zoom_timer:
            t = self.zoom_timer.get_progress()
            self.zoom_value = pygame.math.lerp(self.prev_zoom_value, self.target_zoom_value, t)

        self.zoom_timer.update()


    def update(self, dt):
        self._move(dt)
        self.handle_transition_timer()



class Entity(pygame.sprite.Sprite):
    def __init__(self, img, pos=(0,0), name='noname'):
        super().__init__()
        self.name = name
        self.pos = Pos(*pos)
        self.image: pygame.Surface = img
        self.rect: Rect = Rect(self.pos.x, self.pos.y, self.image.width, self.image.height)
        


class Level:
    def __init__(self, game, name):
        self.name = name 
        self.tilemap = Tilemap(game=game)

    
def pos2str(pos):
    return f"{pos[0]};{pos[1]}"

def str2pos(str_pos):
    pos = str_pos.split(";")
    return [int(pos[0]), int(pos[1])]

class Tilemap2:
    def __init__(self,game,  name="testmap") -> None:
        self.game = game
        self.name = name
        self.tile_size = TILE_SIZE
        self.layers = {
                "tiles": {'type': 'tiles_layer', 'index': 0, 'elements': {}},
                "objects": {'type': 'objects_layer', 'index':1, 'elements': []},
                "meta_info": {'type': 'meta_info_layer', 'index': 2, 'elements': []}
                }

        # maps has name last_saved and layers
        # layer has name, index,  type, elements 
        # elements have pos, type, variant
        # elements are dict for layers of type tiles_layer
        # elements are lists for layers of other types objects_layer, meta_info_layer
    def add_element(self, element, layer_name): # make sure to eneter a tile pos when adding a tile and not an absolute pos
        pos = element['pos']
        layer = self.layers[layer_name]
        if layer['type'] == 'tiles_layer':
            self.layers[layer_name]['elements'][pos2str(pos)] = element # loc :{'type': element['type'], 'variant': element['variant'], 'pos': element['pos']}
            print('added')
        elif layer['type'] == 'objects_layer':
            self.layers[layer_name]['elements'].append( element) # {'type': element['type'], 'variant': element['variant'], 'pos': element['pos']}
        elif layer['type'] == 'meta_info_layer':
            pass

    def remove_element(self, pos, layer_name):
        layer = self.layers[layer_name]
        if layer['type'] == 'tiles_layer':
           tile_loc = pos2str(pos)
           # remove tile from grid 
           if tile_loc in self.layers[layer_name]:
               del self.layers[layer_name]['elements'][tile_loc]

        elif layer['type'] == 'objects_layer':
           # remove off grid objects from 
           for loc, tile in self.layers[layer_name].items():
               tile_img = self.game.assets[tile['type']][tile['variant']]
               tile_r = pygame.Rect(tile['pos'][0], tile['pos'][1], tile_img.get_width(), tile_img.get_height())
               if tile_r.collidepoint(pos):
                   self.layers[layer_name]['elements'].remove(tile)

        elif layer['type'] == 'meta_info_layer':
            pass
    def tiles_around(self, pos, layer_name='tiles'): # the layer given must be of type  tiles_layer
        # this method returns a list of the tile at the pos and the tiles around it (3x3) 
        if self.layers['type'] != 'tiles_layer': 
            print("\033[93mWarning: your trying to check for tiles around in a none tiles_layer\033[0m")
            return []

        NEIGHBOR_OFFSETS = [(-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0), (0, 0), (-1, 1), (0, 1), (1, 1)]
        tiles = []
        tile_loc = (int(pos[0] // self.tile_size), int(pos[1] // self.tile_size))
        for offset in NEIGHBOR_OFFSETS:
            check_loc = pos2str((tile_loc[0] + offset[0], tile_loc[1] + offset[1]))
            if check_loc in self.layers[layer_name]:
                tiles.append(self.layers[layer_name]['elements'][check_loc])
        return tiles

    def physics_rects_around(self, pos, layer_name):
        PHYSICS_TILES = {'grass', 'stone'} # i dont have any physics tiles currently (collision tiles) these are just placeholders
        rects = []
        for tile in self.tiles_around(pos, layer_name=layer_name):
            if tile['type'] in PHYSICS_TILES:
                rects.append(pygame.Rect(tile['pos'][0] * self.tile_size, tile['pos'][1] * self.tile_size, self.tile_size, self.tile_size))
        return rects

    def calculate_size(self):
        # returns map size in tile 
        min_x, max_x, min_y, max_y = 0, 0, 0, 0
        for layer_name, layer in self.layers.items():
            if layer['type'] == 'tiles_layer':
                for _, tile in layer['elements'].items():
                    if tile['pos'][0] > max_x:
                        max_x = tile['pos'][0]
                    elif tile['pos'][0] < min_x:
                        min_x = tile['pos'][0]
                    if tile['pos'][1] > max_y:
                        max_y = tile['pos'][1]
                    elif tile['pos'][1] < min_y:
                        min_y = tile['pos'][1]
        return ((max_x - min_x)*TILE_SIZE,( max_y - min_y)*TILE_SIZE), (min_x*TILE_SIZE, min_y*TILE_SIZE), (max_x*TILE_SIZE, max_y*TILE_SIZE)

    def save(self, name=None):
        name= name if name else self.name # if u enter a name it will be saved with that name if not it will be saved with its original name
        #size_in_tiles = self.calculate_size()
        #size_in_pixels = size_in_tiles[0] * self.tile_size , size_in_tiles[1] * self.tile_size

        with open(get_abs_path(f'data/levels/{name}.json'), 'w') as f:
            json.dump({
                'name': name,
                'save_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'layers': self.layers
                }, f)
        
        self.game.core.notifier.notify(f"map saved as {name}")

    def load(self, map_name='testmap'):
        with open(get_abs_path(f'data/levels/{map_name}.json')) as f:
            map_data = json.load(f)
            self.name = map_data['name']
            self.save_data = map_data['save_date']
            self.layers = map_data['layers']
