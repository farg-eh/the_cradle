import pygame
SW, SH = 640, 360 #640, 360
DW, DH = 320, 180
FRAMERATE = 0
TILE_SIZE = 16
SCALE = 2.0  # means the display will be half the screen dimentions
DEBUG = False
conf = {
        "LANG": 'ar'
        }
FONTS = {} # will be filled by main.py

GAME_CTRLS = {
    "mvup": [pygame.K_w, pygame.K_UP],
    "mvright": [pygame.K_d, pygame.K_RIGHT],
    "mvdown": [pygame.K_s, pygame.K_DOWN],
    "mvleft": [pygame.K_a, pygame.K_LEFT],
    "interact": [pygame.K_c, pygame.K_SPACE],
    "attack": [pygame.K_x, pygame.K_m],
    "cycle_items": [pygame.K_r],
    "inventory": [pygame.K_e],
    "start": [pygame.K_ESCAPE]
}
