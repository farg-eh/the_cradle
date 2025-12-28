import math

import pygame
from src.ui import Text
from src.states.state import State
from src.states.editor import Editor
from src.states.editor.camera import Tilemap2
from src.utils import import_imgs, import_img, Pos, Rect, Animation, import_imgs_as_dict, SoundManager
from src.settings import DW, DH, SW, SH
from src.settings import TILE_SIZE
from .camera import Camera
from .input_manager import InputManger
from .player import Player
from .drops import DropsManager
from .mini_game import CardsGame, FishingGame


class Game(State):
    def __init__(self, core, story='test_story'):
        super().__init__(core, state_name='game')
        self.sound_mgr = None # load assets will put SoundManager in it
        self.assets = self.load_assets()
        self.obj_animations = []
        self.obj_animations_setup()

        self.display = pygame.Surface((DW, DH))
        self.camera = Camera(self)

        player_pos = Pos(200, -200)
        self.player = Player(player_pos, self)
        self.player2 = Player(player_pos, self)
        self.projectiles = []

        self.input_mgr = InputManger(self)
        #default_level = 'palace_in_center'
        start_level = 'palace_in_center'
        # level
        self.level = Level(self, start_level, (-30, -150))  # -30, -150


        #self.pos = Pos(0, 0)
        #self.direction = Pos(0, 0)
        #self.speed = 300

        # hint text
        self.hint_text = Text("Hint Text", font_size="xbig", align='middle')
        self.root.add_child(self.hint_text)
        self.hint_text.move_to_by_center((SW/2, SH*0.92))

        # mini_games
        self.mini_game = None


    def set_hint_text(self, text:str):
        if not text or text=='':
            self.hint_text.hidden = True
        else:
            self.hint_text.hidden = False
            self.hint_text.change_text(text.title())

    def handle_meta_rects(self, curr_level, collided_rect, player):
        # todo use curr_level
        rect_name = collided_rect['name']
        self.set_hint_text(rect_name)
        # TODO flip the nested ifs inside out to get rid of the reapting lines for this seciton
        if rect_name == "sultan_talk":
            if player.input.interact:
                pass

        elif rect_name == 'teacher_talk':
            if player.input.interact:
                self.mini_game = CardsGame(self, player)

        elif rect_name == 'fisherman_talk':
            if player.input.interact:
                self.mini_game = FishingGame(self, player)

        elif rect_name == 'food_seller_talk':
            if player.input.interact:
                pass
        elif rect_name == 'weapon_seller_talk':
            if player.input.interact:
                pass

    def add_projectile(self, type, spawn_pos, shoot_angle_radis=0):
        direction =  Pos(math.cos(shoot_angle_radis), math.sin(shoot_angle_radis)) if not self.player.is_aiming else self.player.input.aim_dir
        if type == 'arrow':
            self.projectiles.append(Arrow(self, spawn_pos, direction, shoot_angle_radis))

    def load_assets(self):
        assets = {}
        # load maps tiles
        for tile_type in Editor.tile_list:
            assets[tile_type] = import_imgs(f"assets/imgs/tiles/{tile_type}")
        # load entity animations
        entity_type = ['human1', 'human2', 'guard1', 'guard2', 'slave1', 'slave2', 'oldman1', 'oldman2']
        actions = ['idle', 'run']
        for e_type in entity_type:
            assets[e_type] = {}
            for action in actions:
               assets[e_type][action] = Animation(f'assets/imgs/entities/{e_type}/{action}',duration=800, loop=True, autostart=True )

        # load human entity hands animations
        tools = ['empty', 'sword', 'bow']
        actions = ['idle', 'run', 'action']
        hand_types = ['back_hand', 'front_hand']
        hands = {}
        for tool in tools:
            for action in actions:
                for hand_type in hand_types:
                    key = f"{tool}-{action}-{hand_type}"
                    value = Animation(f'assets/imgs/hands/{tool}/{action}/{hand_type}')
                    hands[key] = value

        assets['hands'] = hands

        # projectiles
        projectiles = ['arrow', 'dead_arrow']
        for proj in projectiles:
            assets[proj] = import_img(f'assets/imgs/projectiles/{proj}.png')

        # tile anims
        anims = ['water', 'wind_wheel', 'granny', 'fisherman', 'noble', 'teacher', 'seller']
        anims_dict = {}
        for anim in anims:
            anims_dict[anim] = import_imgs(f'assets/imgs/tile_anims/{anim}')
        assets['anims'] = anims_dict

        # items
        assets['items'] = import_imgs_as_dict(f'assets/imgs/items', remove_ext=True)

        # load sounds
        self.sound_mgr = SoundManager([
                'sfx/pop',
            ], vol=self.core._sfx_vol)   # noqa

        return assets

    def obj_animations_setup(self):
        # water
        obj_animation = ObjAnimation(self, 'grass_water', 7, self.assets['anims']['water'], speed=6)
        self.obj_animations.append(obj_animation)
        # mill propler
        obj_animation = ObjAnimation(self, 'market', 40, self.assets['anims']['wind_wheel'], speed=16)
        self.obj_animations.append(obj_animation)

        # granny
        obj_animation = ObjAnimation(self, 'static_humans', 0, self.assets['anims']['granny'], speed=10)
        self.obj_animations.append(obj_animation)

        # noble
        obj_animation = ObjAnimation(self, 'static_humans', 1, self.assets['anims']['noble'], speed=10)
        self.obj_animations.append(obj_animation)

        # fisherman
        obj_animation = ObjAnimation(self, 'static_humans', 2, self.assets['anims']['fisherman'], speed=10)
        self.obj_animations.append(obj_animation)

        # teacher
        obj_animation = ObjAnimation(self, 'static_humans', 3, self.assets['anims']['teacher'], speed=10)
        self.obj_animations.append(obj_animation)

        # seller
        obj_animation = ObjAnimation(self, 'static_humans', 4, self.assets['anims']['seller'], speed=10)
        self.obj_animations.append(obj_animation)

    def switch_level(self, new_map_name):
        before_switch_tilemap_name  = self.level.tilemap.name
        self.level.map_rect = None
        self.level.game = None
        self.level = None
        self.level = Level(self, new_map_name, before_switch_tilemap_name)

    def handle_input(self, event):
        super().handle_input(event)
        self.input_mgr.handle_events(event)

    def draw(self):
        if not self.mini_game:
            self.level.draw()
        else:
            self.mini_game.draw(self.display)
            self.screen.blit(pygame.transform.scale2x(self.display, ))
        super().draw()

    def update(self, dt):
        super().update(dt)
        if self.mini_game:
            self.mini_game.update(dt)
        else:
            self.level.update(dt)
        # print('not colliding with map')
            

    def fixed_update(self, tick_dt):
        #self.get_input()
        self.set_hint_text('')
        if not self.mini_game:
            self.input_mgr.update_entity_input(self.player, 1)
            self.input_mgr.update_entity_input(self.player2, 2)
            self.input_mgr.update(tick_dt)
            self.level.fixed_update(tick_dt)
        # world animations
        for anim in self.obj_animations:
            anim.update(tick_dt)
            #print(anim.tile_type)

        if self.mini_game:
            self.mini_game.fixed_update(tick_dt)

        #self.mpos = self.camera.get_cam_mouse_pos(pygame.mouse.get_pos())

class Level:
    def __init__(self, game, level_name, player_spawn_pos):
        self.game = game
        self.player = game.player
        self.drops_mgr = DropsManager(level=self)

        self.camera = game.camera
        self.tilemap = Tilemap2(game)
        self.tilemap.load(level_name)  #
        self.tilemap.calculate_size()
        self.map_rect = self.tilemap.get_map_rect()

        self.meta_layers = {layer_name: layer for layer_name, layer in self.tilemap.layers.items() if
                            layer['type'] == 'meta_info_layer'}
        self.collision_rects = [Rect(*rect['values']) for rect in self.meta_layers['collision']['elements']]
        self.portals = {rect['name']: Rect(*rect['values']) for rect in self.meta_layers['portals']['elements']}
        self.meta_info_rects = {rect['name']: Rect(*rect['values']) for rect in self.meta_layers['meta_info']['elements']}
        # TODO make a self.spawners list like the above
        # self.portal_rects = [rect for rect in self.meta_layers['portals']]
        # setup
        if isinstance(player_spawn_pos, str):
            spawned_portal_rect = self.portals[player_spawn_pos]

            if spawned_portal_rect.height >= spawned_portal_rect.width:
                # move_to_pos = Pos(-40, 0) + spawned_portal_rect.midright  if spawned_portal_rect.x > self.map_rect.width/2 else Pos(40, 0) + spawned_portal_rect.midleft
                move_to_pos = Pos(-15, 0) + spawned_portal_rect.midleft if spawned_portal_rect.x > self.map_rect.x + self.map_rect.width/2 else Pos(15, 0) + spawned_portal_rect.midright
            else:
                move_to_pos = Pos(0, -15) + spawned_portal_rect.midtop if spawned_portal_rect.y > self.map_rect.y + self.map_rect.height/2 else Pos(0, 15) + spawned_portal_rect.midbottom
            player_spawn_pos = move_to_pos

        self.player.hitbox.center = player_spawn_pos
        self.player.update_rects()
        self.game.player2.hitbox.center = player_spawn_pos
        self.game.player2.update_rects()
        #assets['bg'] = import_img
        self.first_few_frames = -10


    def draw(self):
        # dont draw if its the first few frame
        if self.first_few_frames < 0:
            self.first_few_frames += 1
            return

        t = self.game.core.tick_prog

        for layer_name, layer in self.tilemap.layers.items():
            elements = layer['elements']
            if layer['type'] == 'tiles_layer':
                for tile_pos, tile in elements.items():
                    surf = self.game.assets[tile['type']][tile['variant']]
                    pos = tile['pos'][0]*TILE_SIZE, tile['pos'][1] * TILE_SIZE
                    self.camera.add_to_draw('tiles',surf, pos)
            elif layer['type'] == 'objects_layer':
                for tile in elements:
                    surf = self.game.assets[tile['type']][tile['variant']]
                    pos = tile['pos']
                    layer = 'objects' if not layer_name == 'objects_cover' else 'top'
                    self.camera.add_to_draw(layer, surf, pos) 


        # draw player ~~~~~~~~~~~~~~
        p_r = self.player.get_between_tick_rect(t)
        player_surf, player_display_rect = self.player.get_full_surf_with_draw_rect(p_r)
        self.camera.add_to_draw('objects', player_surf, player_display_rect)
        p_r = self.game.player2.get_between_tick_rect(t)
        player_surf, player_display_rect = self.game.player2.get_full_surf_with_draw_rect(p_r)
        self.camera.add_to_draw('objects', player_surf, player_display_rect)
        # draw projectiles
        for p in self.game.projectiles:
            self.camera.add_to_draw('objects', p.get_surf(), p.get_inbetween_pos(t))

        self.drops_mgr.draw(self.camera, t)

        self.game.display.fill('black')
        self.camera.draw_everything_on(self.game.display, t)

        self.game.screen.blit(pygame.transform.scale2x(self.game.display), (0, 0))

        # tile position of mouse
        #tile_pos = (int((self.mpos[0]) // self.tilemap.tile_size), int((self.mpos[1]) // self.tilemap.tile_size))

    def check_collisions(self):
        for portal_name, rect in self.portals.items():
            if rect.colliderect(self.player.hitbox):
                #print(f"\033[93m portal name:{portal_name} \033[0m")
                self.game.switch_level(portal_name)


        for rect_name, rect in self.meta_info_rects.items():
            if rect.colliderect(self.player.hitbox):
                r = {'name': rect_name, 'rect': rect}
                if self.game:
                    self.game.handle_meta_rects(self, r, self.player)
                else:
                    print('game doesnt exist?')

    def fixed_update(self, tick_dt):
        if not self.map_rect:
            return

        if self.game.level != self:
            self.game = None
            return

        for projectile in self.game.projectiles:
            projectile.update(tick_dt)
        self.player.update(tick_dt)
        self.game.player2.update(tick_dt)
        self.camera.set_focus(Pos(self.player.image_rect.centerx, self.player.image_rect.centery))
        self.camera.update(tick_dt)     # clamp player to map
        #print(f'\033[91m{self.player.hitbox}\0330m')
        #print(f'\033[93m{self.map_rect}\033[0m')
        self.camera.clamp_to_map(self.map_rect)
        self.player.clamp_to_map(self.map_rect)
        self.game.player2.clamp_to_map(self.map_rect)

        self.drops_mgr.update(tick_dt)

        self.check_collisions()


        # print(self.map_rect)


    def update(self, dt):
        #self.drops_mgr.update(dt)
        pass


class Arrow:
    speed = 100
    def __init__(self, game, pos, direction, angle):
        self.pos = Pos(*pos)
        self.prev_pos = self.pos.copy()
        self.game = game
        self.img = self.game.assets['arrow']
        self.direction = direction
        self.direction.y = self.direction.y * -1
        self.surf = self.img.copy() # for rotation
        self.surf = pygame.transform.rotate(self.surf, math.degrees(angle))

    def check_collisions(self):
        pass

    def get_surf(self):
       return self.surf

    def get_inbetween_pos(self, t):
        return self.prev_pos.lerp(self.pos, t)

    def update(self, tdt):
        self.prev_pos = self.pos.copy()
        self.pos += self.direction * self.speed * tdt

class ObjAnimation:
    def __init__(self, game, tile_type, tile_index, animation_frames, speed=12):
        self.game = game
        self.tile_type = tile_type
        self.tile_index = tile_index
        self.animation_dir = animation_frames
        self.speed = speed
        self.index: float = 0
        self.image_list = animation_frames
        self.curr_img = self.image_list[int(self.index)]
        self.len = len(self.image_list)


    def update(self, tdt):
        # note index is a float
        self.index = self.index + self.speed * tdt
        if self.index >= self.len:
            self.index = 0  

        self.curr_img = self.image_list[int(self.index)]
        self.game.assets[self.tile_type][self.tile_index] = self.curr_img
        

