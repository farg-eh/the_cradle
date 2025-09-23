import pygame 
from src.utils import Rect

class SurfStretcher:
    def __init__(self):
        self.stretchables = {}
    
    # add a pygame surface that you want to be stretched 
    def add_stretchable(self, key: str, 
                         surf: pygame.Surface,
                         moving_area: Rect,
                         stretching_area: Rect
                         ):
        # first we capture the moving_area from the surface using the rect
        chopped_moving_area_surf = surf.subsurface(moving_area)
        # we need to place the chopped area in a new surface to properly copy it 
        moving_surf = pygame.Surface(chopped_moving_area_surf.size)
        moving_surf.blit(chopped_moving_area_surf)
        
        # now we do the same thing for the stretching area
        chopped_stretching_area = surf.subsurface(stretching_area)
        stretching_surf = pygame.Surface(chopped_stretching_area.size)
        stretching_surf.blit(chopped_stretching_area)
        
        # now we add it to the stretchables as a dict
        self.stretchables[key] = {
                "moving_surf": moving_surf,
                "moving_rect": moving_area,
                "stretching_surf": stretching_surf,
                "stretching_rect": stretching_area
                }

    def remove_stretchable(self, key: str):
        del self.stretchables[key]

    def stretch(self, key: str,  stretch_x: int = 0, stretch_y: int = 0):
        s = self.stretchables[key]
        # morving the moving rect
        s['moving_rect'].move_ip(stretch_x, 0)
        # stretching the stretchable area
        # surf stretching
        surf_size = s['stretching_surf'].size
        s['stretching_surf'] = pygame.transform.scale(s['stretching_surf'],
                               ( surf_size[0] + stretch_x,
                                surf_size[1] + stretch_y)
                                )
        # rect stretching
        temp_rect = s['stretching_rect'].copy()
        s['stretching_rect'].inflate_ip(stretch_x, stretch_y)
        if stretch_x > 0:
            s['stretching_rect'].left = temp_rect.left
        if stretch_x < 0:
            s['stretching_rect'].right = temp_rect.right
        if stretch_y >  0:
            s['stretching_rect'].top = temp_rect.top
        if  stretch_y < 0:
            s['stretching_rect'].bottom = temp_rect.bottom

    def draw(self, surf):
        if not self.stretchables: return
        print(self.stretchables)
        for _, s in self.stretchables.items():
            surf.blit(s['stretching_surf'], s['stretching_rect'])
            surf.blit(s['moving_surf'], s['moving_rect'])


def chop(surf:pygame.Surface, chop_area:Rect) -> pygame.Surface:
    """returns a cropped area from a surface"""
    # first we capture the area to be cropped
    chopped_area_surf = surf.subsurface(chop_area)
    # then we copy it since we dont want a reference 
    chopped_area_surf = chopped_area_surf.copy()
    return chopped_area_surf

def stretch_surf(surf, stretch_area, moving_area, stretch_x=0, stretch_y=0):
        """This function is used for when u want to stretch a surface only one time
        it stretches the surface by specifiying an setretchable area and a moving area that will move and not be disorted since the stretching area will take care of that
        NOTE: if you want to stretch something rapidly consider using the Stretchable class
        

        Args:
        surf (pygame.Surface): the surface u will select the stretch area and the moveing area from
        stretch_area (Rect): is the area that will be stretched to compensate for the movment of the moving area
        moveing_area (Rect): the area that is going to just move and not stretch 
        
    
        """
        surf = surf.copy()
        # first we create seperate surfaces for each area and rename area for rect for readablity 
        moving_surf = chop(surf, moving_area)
        moving_rect = moving_area
        stretching_surf = chop(surf, stretch_area)
        stretching_rect = stretch_area

        # now to moving stuff
        moving_rect.move_ip(stretch_x, stretch_y)

        # stretching surface
        stretching_surf =  pygame.transform.scale(stretching_surf,
                               ( stretching_surf.size[0] + stretch_x,
                                stretching_surf.size[1] + stretch_y)
                                )

        # stretching surface rect 
        temp_rect = stretching_rect.copy()
        stretching_rect.inflate_ip(stretch_x, stretch_y)
        if stretch_x > 0: 
            stretching_rect.left = temp_rect.left # anchoring the left side 
        if stretch_x < 0:
            stretching_rect.right = temp_rect.right
        if stretch_y > 0:
            stretching_rect.top = temp_rect.top
        if stretch_y < 0: 
            stretching_rect.bottom = temp_rect.bottom

        return [stretching_surf, stretching_rect, moving_surf, moving_rect]




class Stretchable:
    def __init__(self, surf: pygame.Surface, stretch_area: Rect, moving_area: Rect):
        """This class is used for when u want to stretch a surface more than one time

        Args:
        surf(pygame.Surface): the surface u will select the stretch area and the moveing area from
        stretch_area (Rect): is the area that will be stretched to compensate for the movment of the moving area
        moveing_area (Rect): the area that is going to just move and not stretch 

        """
        self.original_stretch_surf = chop(surf,stretch_area)
        self.original_stretch_rect = stretch_area
        self.stretch_rect = self.original_stretch_rect.copy()
        self.original_moving_rect = moving_area
        self.moving_rect = self.original_moving_rect.copy()
        self.original_moving_surf = chop(surf, moving_area)
        self._stretch_x = 0
        self._stretch_y = 0
        self.stretch_surf = self.original_stretch_surf.copy()
        self.moving_surf = self.original_moving_surf.copy()
        
        # union rect for both rects 
        self.rect = self.stretch_rect.union(self.moving_rect)

    # maybe i shoud make the amount connected to the class instead of inputed
    def set_stretch_x(self, amount):
        # first we stretch the surface 
        self.stretch_surf = pygame.transform.scale(self.original_stretch_surf, 
                                                   (self.original_stretch_surf.size[0] + amount,
                                                    self.original_stretch_surf.size[1]))
        # now the rect
        self.stretch_rect = self.original_stretch_rect.inflate(amount, 0)
        if amount > 0:  # means we are stretching to the right so we anchor the leftside
            self.stretch_rect.left = self.original_stretch_rect.left
        elif amount < 0:
            self.stretch_rect.right = self.original_stretch_rect.right

        # lets move the moving rect
        self.moving_rect = self.original_moving_rect.move(amount, 0)

    def draw(self, surf):
        # TODO: instead of drawing black surface behinde the stretchable
        # we should erase whats behind it 
        pygame.draw.rect(surf, 'black', self.rect)
        surf.blit(self.stretch_surf, self.stretch_rect)
        surf.blit(self.moving_surf, self.moving_rect)
       # pygame.draw.rect(surf, 'green', self.stretch_rect, 1)
       # pygame.draw.rect(surf, 'blue', self.moving_rect, 1)

            


        
