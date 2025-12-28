import math

import pygame
from src.utils import Pos, Rect, smooth_step_lerp
from .input_manager import Input
from .hands import Hands
from .enums import Items

class Player:
    def __init__(self, pos, game, speed=60, e_type="human2"):
        # human entity type
        self.all_types = ['slave1', 'slave2', 'human1', 'human2', 'guard1', 'guard2', 'oldman1', 'oldman2']
        self.type_index = 3
        self.type = e_type
        self.animations = game.assets[e_type]
        # hand item types
        self.all_items = ['empty', 'sword', 'bow']
        self.item_index = 0
        self.curr_item = self.all_items[self.item_index]
        # for moving
        self.direction = Pos(0, 0)
        self.speed = speed
        self.game = game

        self.image_size = self.animations['run'][0].size
        self.image_rect = Rect(pos[0], pos[1], *self.image_size)
        self.hitbox = self.image_rect.inflate(-20, -19)
        self.prev_hitbox = self.hitbox.copy()

        self.state = "idle"
        self.animation_index = 0
        self.animation_speed = 12
        self.image = self.animations['idle'][0]
        self.flip = False

        # player input
        self.input = Input()
        self.actioning = False
        self.is_aiming = False
        self.aiming_angle = 0

        # hands !
        self.hands = Hands(self)
        self.shoot_angle = 0

        # delete later
        self.item =0

    def shoot_arrow(self):
        spawn_loc = self.image_rect.centerx - 4, self.image_rect.top - 5
        r = 20

        shoot_angle = self.shoot_angle + math.pi if self.flip else self.shoot_angle
        shoot_angle = self.aiming_angle if self.is_aiming else shoot_angle
        ang = shoot_angle
        spawn_loc = spawn_loc[0] + r * math.cos(ang), spawn_loc[1] + r * math.sin(ang) * -1
        self.game.add_projectile('arrow', spawn_loc, shoot_angle)

    def cycle_type(self):
        self.item_index = 0
        self.type_index += 1
        if self.type_index >= len(self.all_types):
            self.type_index = 0
        self.type = self.all_types[self.type_index]
        self.animations = self.game.assets[self.type]
        self.image = self.animations['idle'][0]
        color = self.image.get_at((16, 9))
        print(color)
        self.hands.change_color(color)
        self.hands = Hands(self, color)

    def cycle_item(self):
        self.item_index += 1
        if self.item_index >= len(self.all_items):
            self.item_index = 0
        self.curr_item = self.all_items[self.item_index]
        self.hands.change_tool(self.curr_item)

    def update_rects(self):
        self.image_rect.midbottom = self.hitbox.midbottom
        offset = 20
        self.image_rect.y += offset
        # self.image_rect.topleft = self.rect.topleft
        # self.hitbox.midbottom = self.image_rect.midbottom

    def handle_input(self):
        # direction handleing
        self.direction.x = self.input.move_dir.x
        self.direction.y = self.input.move_dir.y
        if self.direction.length_squared() > 0:
            self.direction = self.direction.normalize()

        # buttons
        #print(self.input)
        if self.input.cycle_items:
            self.cycle_type()
            print("pleassssseeeeee")

        if self.input.interact:
            self.cycle_item()

        if self.input.attack or self.input.attack_hold:
            self.actioning = True

        if self.input.inventory:
            item = Items(self.item)
            self.item += 1
            if self.item >=15:
                self.item = 0
            self.game.level.drops_mgr.drop(self.hitbox.center, item)


    def move_and_collide(self, dt):
        # move horizontally
        self.hitbox.x += self.direction.x * self.speed * dt
        for rect in self.game.level.collision_rects:
            if self.hitbox.colliderect(rect):
                if self.direction.x > 0:
                    self.hitbox.right = rect.left
                elif self.direction.x < 0:
                    self.hitbox.left = rect.right

        # move vertically
        self.hitbox.y += self.direction.y * self.speed * dt
        for rect in self.game.level.collision_rects:
            if self.hitbox.colliderect(rect):
                if self.direction.y > 0:
                    self.hitbox.bottom = rect.top
                elif self.direction.y < 0:
                    self.hitbox.top = rect.bottom

        self.update_rects()

    def clamp_to_map(self, map_rect):
        # clamp player to map
        if self.hitbox.left < map_rect.left:
            self.hitbox.left = map_rect.left
        elif self.hitbox.right > map_rect.right:
            self.hitbox.right = map_rect.right
        if self.hitbox.top < map_rect.top:
            self.hitbox.top = map_rect.top
        elif self.hitbox.bottom > map_rect.bottom:
            self.hitbox.bottom = map_rect.bottom
        self.update_rects()



    def update_animation(self, dt):
        if self.direction.length_squared() > 0:
            self.state = "run"
        else:
            self.state = "idle"

        if self.actioning:
            self.hands.state = 'action'
        else:
            self.hands.state = self.state

        frames = self.animations[self.state]
        # manually updating the animation
        if frames:
            self.animation_index += self.animation_speed * dt
            self.image = frames[int(self.animation_index) % len(frames)]
        #frames.update()
        #self.image = frames.curr_img()

        if self.direction.x < 0:
            self.flip = True
        elif self.direction.x > 0:
            self.flip = False

    def update(self, dt):
        self.prev_hitbox.center = self.hitbox.center
        self.handle_input()
        self.move_and_collide(dt)
        self.update_animation(dt)
        self.hands.update(dt)
        # handle input
        if self.game.input_mgr.input_method == "joystick":
            if self.input.aim_dir.magnitude() > 0:
                self.is_aiming = True
                self.aiming_angle = math.atan2(self.input.aim_dir[1], self.input.aim_dir[0])
            else:
                self.is_aiming = False
                self.aiming_angle = 0

        if self.hands.have_finished_cycle() and self.actioning:
            self.actioning = False
            if self.hands.tool == 'bow':
                self.shoot_arrow()



    def get_between_tick_rect(self, t):
        prev = Pos(*self.prev_hitbox.midbottom)
        curr = self.hitbox.midbottom

        interpolated_pos = prev.lerp(curr, t)

        # convert center to topleft
        x = interpolated_pos.x - self.image_rect.width / 2
        y = interpolated_pos.y - self.image_rect.height

        return Rect(x, y, self.image_rect.width, self.image_rect.height)

    def get_surf(self):
        if not self.image:
            print(f'\033[91mOkay for some reason the image is none \033[0m')

        return pygame.transform.flip(self.image, self.flip, False)

    def get_full_surf_with_draw_rect(self, img_rect:Rect):
        # returns a bigger surface containing the player and the hands with an offset rect for displaying it correctly
        # takes in the player image_rect as input ( the lerped version )
        back_surf = self.hands.get_back_surf().copy()
        front_surf = self.hands.get_front_surf().copy()
        player_surf = self.get_surf()

        # backsurf offset to center
        offset = back_surf.width//2 - player_surf.width//2, back_surf.height//2 - player_surf.height//2
        back_surf.blit(player_surf, offset)

        # some rotation if we are aiming
        if self.hands.tool == 'bow' and self.is_aiming:
            front_surf = pygame.transform.rotate(front_surf, math.degrees(self.aiming_angle))

        # frontsurf offset to center
        offset2 = back_surf.width//2 - front_surf.width//2, back_surf.height//2 - front_surf.height//2
        back_surf.blit(front_surf, offset2)
        rect2display = img_rect.move(-offset[0], -offset[1])

        return back_surf, rect2display

    # the get surf should be used instead and pass the current entity image to the camera to draw
    def draw(self, surface, offset=(0, 0)):
        img = pygame.transform.flip(self.image, self.flip, False)
        surface.blit(img, (self.image_rect.x - offset[0], self.image_rect.y - offset[1]))
