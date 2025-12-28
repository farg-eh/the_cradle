import pygame
from src.utils import Pos, smooth_step_lerp
from src.settings import DW, DH


class Camera:
    def __init__(self, game):
        self.game = game
        # camera position and focus
        self._cam_pos = Pos(0, 0)
        self.focus_pos = Pos(0, 0)

        # smooth camera lerp
        self.smooth_camera = False

        # drawing layers
        # background < objects (y-sorted) < ui
        self.things_to_draw = {
            "tiles": [],
            "objects": [],
            "top": []
        }

        # display offset for centering
        self.offset = Pos(DW/2, DH/2)
        self._prev_cam_pos = Pos(self._cam_pos.x, self._cam_pos.y)
    def get_cam_mouse_pos(self, mouse_pos):
        """convert screen mouse position to world position"""
        # mouse_pos is a tuple (x, y)
        mx, my = mouse_pos
        world_x = mx + (self._cam_pos.x - self.offset.x)
        world_y = my + (self._cam_pos.y - self.offset.y)
        return Pos(world_x, world_y)

    def get_cam_world_pos(self, world_pos):
        """convert a world position to screen position mostly for drawing"""
        wx, wy = world_pos
        screen_x = wx - self._cam_pos.x + self.offset.x
        screen_y = wy - self._cam_pos.y + self.offset.y
        return Pos(screen_x, screen_y)

    def set_focus(self, pos: Pos):
        self.focus_pos = pos

    def add_to_draw(self, layer_name, surf, pos, base_y=None):
        """add a surface and position to a specific layer"""
        if layer_name not in self.things_to_draw:
            raise ValueError(f"Invalid layer '{layer_name}'")

        if layer_name=='objects':
            by = pos[1] + surf.height * 0.7 if base_y is None else base_y
            self.things_to_draw[layer_name].append({'surf': surf, 'pos': pos, 'base_y': by}) # base_y will be used for Y sorting
        else:
            self.things_to_draw[layer_name].append({'surf': surf, 'pos': pos})

    def _move(self, dt):
        """smoothly move camera toward focus position"""
        if not self.smooth_camera:
            self._cam_pos.x, self._cam_pos.y = self.focus_pos.x, self.focus_pos.y
        dist = self._cam_pos.distance_to(self.focus_pos)
        if dist < 3:
            self._cam_pos.x, self._cam_pos.y = self.focus_pos.x, self.focus_pos.y
            return

        # Smooth speed adjustment
        max_speed = 600
        min_speed = 33 # 55
        max_dist = 230
        t = pygame.math.clamp(dist / max_dist, 0, 1)
        move_amount = smooth_step_lerp(min_speed, max_speed, t**2)
        self._cam_pos.move_towards_ip(self.focus_pos, move_amount * dt)

    def draw_everything_on(self, surf, t):
        """draw all layers with y-sorting on the objects layer"""
        lerped_cam_pos = self._prev_cam_pos.lerp(self._cam_pos, t)
        cam_pos = Pos(round(lerped_cam_pos[0]), round(lerped_cam_pos[1]))
        offset =  Pos(round(self.offset.x), round(self.offset.y))
        # background first
        for e in self.things_to_draw['tiles']:
            surf.blit(e['surf'], (
                round(e['pos'][0]) - cam_pos.x + offset.x,
                round(e['pos'][1]) - cam_pos.y + offset.y
            ))

        # sort object layer by Y (depth)
        sorted_objects = sorted(
            self.things_to_draw['objects'],
            key=lambda e: e['base_y']
        )

        for e in sorted_objects:
            surf.blit(e['surf'], (
                round(e['pos'][0]) - cam_pos.x + offset.x,
                round(e['pos'][1]) - cam_pos.y + offset.y
            ))

        # top at last
        for e in self.things_to_draw['top']:
            surf.blit(e['surf'], (
                round(e['pos'][0]) - cam_pos.x + offset.x,
                round(e['pos'][1]) - cam_pos.y + offset.y
            ))
        # draw UI last (no offset)
        #for e in self.things_to_draw['ui']:
        #    surf.blit(e['surf'], e['pos'])

        # clear after draw
        for key in self.things_to_draw:
            self.things_to_draw[key].clear()


    def clamp_to_map(self, map_rect):
        half_w = DW / 2
        half_h = DH / 2

        # Calculate the min and max positions for the camera center
        min_x = map_rect.left + half_w
        min_y = map_rect.top + half_h
        max_x = map_rect.right - half_w
        max_y = map_rect.bottom - half_h

        # Only clamp if map is larger than screen
        if map_rect.width > DW:
            self._cam_pos.x = max(min_x, min(self._cam_pos.x, max_x))
        else:
            # center horizontally
            self._cam_pos.x = map_rect.centerx

        if map_rect.height > DH:
            self._cam_pos.y = max(min_y, min(self._cam_pos.y, max_y))
        else:
            # center vertically
            self._cam_pos.y =map_rect.centery
    def update(self, dt):
        self._prev_cam_pos.x, self._prev_cam_pos.y = self._cam_pos.x, self._cam_pos.y
        self._move(dt)

