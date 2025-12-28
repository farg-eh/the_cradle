import pygame
from typing import override
import random
import math

from src.settings import SCALE
from src.utils import Pos, Timer, gen_sil_surf, oscilating_lerp, rand_circular_pos
from .camera import Camera
from .enums import Items
from .player import Player



class DropsManager:
    def __init__(self, level):
        self.level = level
        self.drops = []
        self.player: Player = level.game.player  # must be assigned after the level setup

    def drop(self, pos, drop_type: Items, amount=1, dir_angle=-1):
        if not self.player:
            return

        for _ in range(amount):
            name = drop_type.get_str()
            surf = self.level.game.assets['items'][name]
            drop = Drop(pos, surf, self, drop_type, name=name+" drop", dir_angle=dir_angle)
            self.drops.append(drop)

    def check_collisions(self):
        if not self.player:
            return

        # clean dead drops
        self.drops = [drop for drop in self.drops if not drop.dead]
        for drop in self.drops:
            if self.player.hitbox.colliderect(drop.shadow.rect)\
                and drop.on_ground:
                drop.kill()
                #sound = random.choice(['pop0', 'pop1', 'pop2'])
                self.level.game.sound_mgr.play('pop', sound_list_method='random-no-repeat')
                #self.player.add_resource(drop.drop_type, sound=sound)

    def draw(self, camera:Camera, t):
        for drop in self.drops:
            surf, rect = drop.get_img_and_rect(t)
            camera.add_to_draw('objects', drop.shadow.img, drop.shadow.rect)
            camera.add_to_draw('objects', surf, rect, base_y=drop.shadow.rect.centery)

    def update(self, dt):
        self.check_collisions()
        for drop in self.drops:
            drop.update(dt)



class Drop:
    def __init__(self, pos, surf:pygame.Surface,
                 manager, drop_type,
                 name="unknown drop", dir_angle=-1):
        self.dead = False  # if True then the manager should remove it from self.drops
        k = 0.3  # a constant to tweak things
        # missing things
        self.surf = surf
        self.img_rect = self.surf.get_frect(topleft=pos)
        self.prev_img_rect = self.img_rect.copy()
        self.manager = manager

        # hitbox
        self.hitbox = self.img_rect.inflate(-surf.get_width() * 0.15,
                                            -surf.get_height() * 0.15)
        # identity
        self.name = name
        self.drop_type = drop_type

        # drop range
        self.min_radius = 60 * k * 1.4
        self.max_radius = 130 * k * 1.4
        self.dir_angle = 360 if dir_angle < 0 else dir_angle

        # positions
        self.throw_pos = Pos(*pos)  # this is to save the initial pos
        self.pos = Pos(*pos)
        self.prev_pos = self.pos.copy()
        self.item_pos = Pos(*pos) # item_pos is the same as pos but will have an offest on the y axies
        self.prev_item_pos = self.item_pos.copy()
        self.target_pos = Pos(*rand_circular_pos(pos, self.max_radius, self.min_radius)) # random
        # bounce pos is 70% of the distance to the target pos
        self.bounce_pos = self.item_pos.lerp(self.target_pos, 0.6)

        # speeds
        self.speed = 125 * k * 1.6
        self.after_bounce_speed = self.speed * 0.5

        # virtual height
        self.curr_height = 0
        self.max_height = 125 * k * 0.8
        self.bounce_max_height = self.max_height * 0.35

        # modifying values based on distance
        distance = self.throw_pos.distance_to(self.target_pos)
        limiter = (1 - distance/self.max_radius) * 0.8
        self.max_height -= self.max_height * limiter
        self.bounce_max_height -= self.bounce_max_height * limiter
        self.speed -= self.speed * limiter
        self.after_bounce_speed -= self.after_bounce_speed * limiter

        # state
        self.bounced = False    # will be true after the first bounce
        self.on_ground = False  # will be true after reaching the target_pos
        self.suprise_jump = False

        # timers
        self.suprise_jump_timer = Timer(random.randint(5000, 13000),
                                        autostart=True)
        self.jump_dur_timer = Timer(1900)

        # debug
        self.debug = False

        # shadow
        self.shadow = DropShadow(self)

        # moving toward the player
        self.player = manager.player
        self.pull_radius = 70 * k
        self.pull_speed = 425 * k

        # hovering
        self.hover_height = 130 *  k * 0.3# resambles a radius
        self.hover_speed = 140    # rate of change in angle
        self.hover_angle = 0    # to make the drop hover on the y axies

    def bounce_to(self, start_pos, target_pos, speed, max_height):
        # calculating stuff
        t = self.pos.distance_to(start_pos) / target_pos.distance_to(start_pos)
        offset = max_height * oscilating_lerp(0, 1, t)
        # moving
        self.pos.move_towards_ip(target_pos, speed)
        self.item_pos.x = self.pos.x
        # offsetting the y to simulate virtual height
        self.item_pos.y = self.pos.y - offset
        # updating the rect
        self.img_rect.center = self.item_pos
        return bool(int(t))  # 1 = reached goal

    def move(self, dt):
        if not self.bounced:
            # go to bounce position
            self.bounced = self.bounce_to(self.throw_pos,
                                          self.bounce_pos,  # first pos
                                          self.speed * dt,
                                          self.max_height)
        elif not self.on_ground:
            # go to target position
            self.on_ground = self.bounce_to(self.bounce_pos,
                                            self.target_pos,  # second and last pos
                                            self.after_bounce_speed * dt,
                                            self.bounce_max_height)
        else:
            # move toward the player
            target = pygame.Vector2(self.player.hitbox.center)
            distance = target.distance_to(self.pos)
            if distance < self.pull_radius:
                t = (1 - distance/self.pull_radius)**1.5  # ease-in
                speed = pygame.math.lerp(0, self.pull_speed, t)
                self.item_pos.move_towards_ip(target, speed * dt)
                # update stuff
                self.img_rect.center = self.item_pos
                self.pos = self.item_pos

            # hover and suprise_jump
            if not self.suprise_jump:
                height = self.hover_height
                speed = self.hover_speed
            else:
                height = self.hover_height * 2.4
                speed = self.hover_speed * 1.3

            # hover
            if self.hover_angle <= 180:
                self.hover_angle = self.hover_angle + speed * dt
                #print("HOVERING")
            else:
                self.hover_angle = 0
            angle = math.sin(math.radians(self.hover_angle))
            self.img_rect.centery = self.item_pos.y - (angle * height)
            # disable suprise_jump after 1 jump
            if self.hover_angle == 0 and self.suprise_jump:
                self.suprise_jump = False
                self.suprise_jump_timer.duration = random.randint(9000, 19000)
                self.suprise_jump_timer.activate()
        # update hitbox
        #self.img_rect.center = self.item_pos
        self.hitbox.center = self.img_rect.center


    def collision_check(self):
        pass

    def get_between_tick_rect(self, t):
        prev = Pos(*self.prev_img_rect.center)
        curr = Pos(*self.img_rect.center)
        interpolated_pos = prev.lerp(curr, t)
        rect = self.img_rect.copy()

        rect.center = interpolated_pos

        return rect

    def get_img_and_rect(self, t):
        surf = self.surf
        return surf, self.get_between_tick_rect(t)

    def draw(self,screen, camera_offset):
        pass
        #super().draw(screen, camera_offset=0)
        # if not self.debug:
        #     return
        # pygame.draw.circle(screen, 'cyan',
        #                    self.throw_pos + camera_offset, self.max_radius, 1)
        # pygame.draw.circle(screen, 'cyan',
        #                    self.throw_pos + camera_offset, self.min_radius, 1)
        # pygame.draw.circle(screen, 'brown',
        #                    self.target_pos + camera_offset, 3)
        # pygame.draw.circle(screen, 'red',
        #                    self.bounce_pos + camera_offset, 3)
        # pygame.draw.circle(screen, 'pink',
        #                    self.item_pos + camera_offset, 3)
        # pygame.draw.rect(screen, 'white',
        #                  (self.hitbox_rect.move(*camera_offset)), 1)
        # pygame.draw.rect(screen, 'gray',
        #                  (self.player.hitbox_rect.move(*camera_offset)), 1)
        # pygame.draw.circle(screen, 'black',
        #                    self.pos + camera_offset, 3)
        # pygame.draw.circle(screen, 'yellow',
        #                    self.player.hitbox_rect.center + camera_offset,
        #                    3)
        # pygame.draw.circle(screen, 'yellow',
        #                    self.player.hitbox_rect.center + camera_offset,
        #                    self.pull_radius, 1)

    def kill(self):
        #super().kill()
        #self.shadow.kill()
        self.dead = True
        pass

    def update(self, dt):
        self.prev_pos = self.pos.copy()
        self.prev_item_pos = self.item_pos.copy()
        self.prev_img_rect = self.img_rect.copy()
        self.move(dt)
        # suprise jump timers
        self.suprise_jump_timer.update()
        self.jump_dur_timer.update()
        if self.suprise_jump_timer.done and not self.suprise_jump:
            self.suprise_jump = True
            self.jump_dur_timer.activate()
            self.hover_angle = 0

        # shadow circle
        self.shadow.update(dt)

class DropShadow:
    def __init__(self, drop:Drop):
        self.surf = pygame.Surface((drop.img_rect.width*0.85,
                               drop.img_rect.height*0.55), pygame.SRCALPHA)
        self.surf.set_colorkey((0, 0, 0))
        self.img = self.surf.copy() # this one will be used for drawing (cuz it will be scaled)
        self.rect = self.surf.get_frect(topleft=(0, 0))
        pygame.draw.ellipse(self.surf, (1, 1, 1, 35), self.rect)
        self.drop = drop

    def update(self, dt):
        # follow the drop
        self.rect.centerx = self.drop.pos[0]
        self.rect.centery = self.drop.pos[1] + self.drop.img_rect.width/2

        # change size depending on how far the drop is from the groud
        max_size = self.surf.get_size()
        dist_from_floor = self.drop.pos.distance_to(self.drop.img_rect.center)
        max_dist = self.drop.max_height
        normalized_dist = 1 - dist_from_floor/max_dist
        if dist_from_floor <= max_dist:
            width = self.surf.width * normalized_dist
            height = self.surf.height * normalized_dist
            self.img = pygame.transform.scale(self.surf, (width, height))
            self.rect = self.img.get_frect(center=(self.drop.pos[0],
                        self.drop.pos[1] + self.drop.img_rect.width/2))