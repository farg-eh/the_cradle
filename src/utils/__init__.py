from .importers import get_abs_path, import_font, import_img, import_imgs, import_sound, import_txt_from_json, TextLoader
from .timer import Timer
from .animation import Animation
from .structs import Pos, Rect
from .sound import SoundManager
from .lerp import oscilating_lerp
# helper funcs
def get_abs_pos(rect, rel_pos):
    return rect.left + rel_pos[0], rect.top + rel_pos[1]
    
def get_rel_pos(rect, abs_pos):
    return abs_pos[0] - rect.left, abs_pos[1] - rect.top

