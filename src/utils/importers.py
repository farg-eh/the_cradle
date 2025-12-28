import os
import pygame
import json
from src.settings import SCALE, conf

LANG = conf['LANG']

def get_abs_path(rel_path: str) -> str:
    """
    returns the absolute path of an input path

    Args:
        rel_path (str): relative path starting from the root directory of the project

    Returns:
        str: the absolute path 
    """
    p = os.path.abspath(os.path.dirname(__file__))  # check this section if u change the location of the file containing this func
    rel_path_list = rel_path.split("/")
    return os.path.abspath(os.path.join(p, "..", "..", *rel_path_list))

def import_font(path, size):
    return pygame.font.Font(get_abs_path(path), size=size)

def import_img(path, scale2x=False):
    img = pygame.image.load(get_abs_path(path)).convert_alpha()
    img.set_colorkey('black')  # color to be filled with transparency
    if scale2x:
        img = pygame.transform.scale2x(img)
    return img

def import_imgs(path, scale2x=False):
    images = []
    img_names = sorted(os.listdir(get_abs_path(path)))
    for img_name in img_names:
        images.append(import_img(path + '/' + img_name, scale2x))
    return images

def import_imgs_as_dict(path, scale2x=False, remove_ext=False):
    images = {}
    img_names = sorted(os.listdir(get_abs_path(path)))
    for img_name in img_names:
        img_n = img_name if not remove_ext else img_name.rsplit('.', maxsplit=2)[0]
        images[img_n] = import_img(path + '/' + img_name, scale2x)
    return images
        

def import_sound(rel_path):
    """returns either a (name:str, pygame.Sound) or a (name:str, list[pygame.Sound] depending on the path"""
    file_name = rel_path.split('/')[-1]
    sound_name = file_name.split('.')
    if len(sound_name) > 1:  # its a single file
        return sound_name[0], pygame.mixer.Sound(get_abs_path(rel_path))
    else:  # its a directory
        dir_list = sorted(os.listdir(get_abs_path(rel_path)), key=lambda x: int(x.split('.')[0]))
        return sound_name[0], [pygame.mixer.Sound(get_abs_path(rel_path + '/' + f_name)) for f_name in dir_list]



def import_txt_from_json(keys=""):
    # load json first
    path = get_abs_path(f"languages/{conf['LANG']}.json")
    with open(path, "r") as f:
        txt = json.load(f)
    # if no keys return the whole dict
    if not keys:
        return txt
    # if there is keys (its like a path ) then get a specifc part 
    else:
        keys = keys.split(".")
        for key in keys:
            if key.isdecimal():
                key = int(key)
            txt = txt[key]
        # miml code in this json will be an array of lines (for readability) so we have to convert it to a single line to be able to use it a mimlize it 
        if isinstance(txt, list) and len(txt) > 0 and isinstance(txt[0], str) and txt[0].startswith('>miml<'):
            txt = " ".join(txt)
        return txt

class TextLoader:
    def __init__(self, key_path=''):
        self.text = import_txt_from_json(keys=key_path)

    def get(self, keys=""):
        if not keys:
            return self.text
        txt = self.text
        for key in keys.split("."):
            if key.isdecimal():
                key = int(key)
            txt = txt[key]
         # miml code in this json will be an array of lines (for readability) so we have to convert it to a single line to be able to use it a mimlize it 
        if isinstance(txt, list) and len(txt) > 0 and isinstance(txt[0], str) and txt[0].startswith('>miml<'):
           txt = " ".join(txt)       
           return txt
        if isinstance(txt, str):
           return txt

            
