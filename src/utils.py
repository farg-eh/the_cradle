import os
import pygame

def get_abs_path(rel_path: str) -> str:
    """
    returns the absolute path of an input path

    Args:
        rel_path (str): relative path starting from the root directory of the project

    Returns:
        str: the absolute path 
    """
    p = os.path.abspath(os.path.dirname(__file__))
    rel_path_list = rel_path.split("/")
    return os.path.abspath(os.path.join(p, "..", *rel_path_list))

def import_img(path):
    img = pygame.image.load(get_abs_path(path)).convert()
    img.set_colorkey('black')  # color to be filled with transparency
    return img
