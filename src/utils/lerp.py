import pygame
import math

# lerp funcs
def oscilating_lerp(a: float | int, b: float | int, t: float) -> float:
    """returns a value smoothly iterpolated from a to b and back to a"""
    angle =  math.pi * t  # a pi is like 180 degrees and the t gets a precentage of that 180
    # the sine of this range of angles (0 to pi) gives a value from 0 to 1 to 0
    t = math.sin(angle) # sin of 0 is 0 and sin of 180 (pi) is 0 (meaning it goes form 0 to 1 and back to 0
    return pygame.math.lerp(a, b, t)

def smooth_step_lerp(a, b, t):
    t = t*t*(3 - 2 * t)
    return pygame.math.lerp(a, b, t)
