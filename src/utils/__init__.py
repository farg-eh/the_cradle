from .importers import get_abs_path, import_font, import_img, import_imgs, import_sound, import_txt_from_json, TextLoader,import_imgs_as_dict
from .timer import Timer, StopWatch
from .animation import Animation
from .structs import Pos, Rect
from .sound import SoundManager
from .lerp import oscilating_lerp, smooth_step_lerp
import pygame, math, random

# helper funcs
def get_abs_pos(rect, rel_pos):
    """finds the absolute position of a relative position inside a rect"""
    return rect.left + rel_pos[0], rect.top + rel_pos[1]
    
def get_rel_pos(rect, abs_pos):
    "finds the relative position of an absolute point for a specific rect"
    return abs_pos[0] - rect.left, abs_pos[1] - rect.top

def gen_sil_surf(img: pygame.Surface) -> pygame.Surface:
    """returns a white silhouette of a surface"""
    pixel_mask = pygame.mask.from_surface(img)
    sil = pixel_mask.to_surface()
    sil.set_colorkey("black") # to remove the black parts
    return sil

def rand_circular_pos(center: Pos, min_radius, max_radius, start_angle=90, angle_range=360) -> Pos:
    """returns a random position from a circular range"""
    # calculate random angle
    start_angle -= angle_range/2
    angle_range_rad = math.radians(angle_range)
    start_angle_rad = math.radians(start_angle)
    angle = start_angle_rad + (random.random() * angle_range_rad)
    # angle = random.random() * 2 * math.pi # from 0 to 2PI (0 to 360 but in radians)
    # random range
    radius = min_radius + ((max_radius - min_radius) * random.random())
    rand_x = center[0] + radius * math.cos(angle)
    rand_y = center[1] +  radius * math.sin(angle)
    return Pos(rand_x, rand_y)

